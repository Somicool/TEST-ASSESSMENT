#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG System for PDF Question Answering with Citations
Strict grounding - answers only from retrieved context, no hallucinations
"""

import os
import sys
import re
import json
import argparse
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import numpy as np
import faiss
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer


@dataclass
class Chunk:
    """Represents a text chunk with metadata"""
    text: str
    page_num: int
    chunk_id: int
    
    def get_citation(self) -> str:
        """Return citation format [p{page}:c{chunk}]"""
        return f"[p{self.page_num}:c{self.chunk_id}]"


class PDFProcessor:
    """Extracts and chunks text from PDF"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def clean_text(self, text: str) -> str:
        """Clean up repetitive headers, footers, and watermarks"""
        # Remove "STRICTLY CONFIDENTIAL" patterns (single or repeated)
        text = re.sub(r'STRICTLY\s+CONFIDENTIAL(\s*STRICTLY\s+CONFIDENTIAL)*', '', text, flags=re.IGNORECASE)
        
        # Remove navigation UI elements
        text = re.sub(r'Home\s+outline\s+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Hamburger\s+Menu\s+Icon\s+with\s+solid\s+fill\s*', '', text, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
        
        return text.strip()
    
    def extract_text_by_page(self, pdf_path: str) -> List[Tuple[int, str]]:
        """Extract text from PDF, returns list of (page_num, text)"""
        reader = PdfReader(pdf_path)
        pages = []
        for i, page in enumerate(reader.pages, start=1):
            try:
                text = page.extract_text()
                if text.strip():
                    # Clean the text before adding
                    cleaned_text = self.clean_text(text)
                    if cleaned_text:
                        pages.append((i, cleaned_text))
            except Exception as e:
                print(f"Warning: Failed to extract text from page {i}: {e}")
                continue
        return pages
    
    def chunk_text(self, text: str, page_num: int, start_chunk_id: int) -> List[Chunk]:
        """Split text into overlapping chunks"""
        chunks = []
        words = text.split()
        
        if not words:
            return chunks
        
        chunk_id = start_chunk_id
        start = 0
        
        while start < len(words):
            end = start + self.chunk_size
            chunk_words = words[start:end]
            chunk_text = ' '.join(chunk_words)
            
            chunks.append(Chunk(
                text=chunk_text,
                page_num=page_num,
                chunk_id=chunk_id
            ))
            
            chunk_id += 1
            start += self.chunk_size - self.chunk_overlap
        
        return chunks
    
    def process_pdf(self, pdf_path: str) -> List[Chunk]:
        """Extract and chunk entire PDF"""
        pages = self.extract_text_by_page(pdf_path)
        all_chunks = []
        chunk_counter = 0
        
        for page_num, text in pages:
            page_chunks = self.chunk_text(text, page_num, chunk_counter)
            all_chunks.extend(page_chunks)
            chunk_counter += len(page_chunks)
        
        return all_chunks


class VectorStore:
    """FAISS-based vector store for semantic search"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize with a sentence transformer model"""
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.chunks = []
        self.dimension = None
    
    def build_index(self, chunks: List[Chunk]):
        """Build FAISS index from chunks"""
        self.chunks = chunks
        
        # Generate embeddings
        texts = [chunk.text for chunk in chunks]
        embeddings = self.model.encode(texts, show_progress_bar=True)
        
        # Build FAISS index
        self.dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings.astype('float32'))
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[Chunk, float]]:
        """Search for most relevant chunks"""
        if self.index is None:
            return []
        
        # Encode and normalize query
        query_embedding = self.model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        results = []
        for idx, score in zip(indices[0], scores[0]):
            if idx < len(self.chunks):
                results.append((self.chunks[idx], float(score)))
        
        return results


class LLMInterface:
    """Interface for LLM - supports OpenAI, Gemini, and fallback"""
    
    def __init__(self, api_key: Optional[str] = None, gemini_key: Optional[str] = None):
        self.openai_key = api_key or os.getenv("OPENAI_API_KEY")
        self.gemini_key = gemini_key or os.getenv("GEMINI_API_KEY")
        self.use_openai = False
        self.use_gemini = False
        self.client = None
        self.model = None
        
        # Try Gemini first if key is provided
        if self.gemini_key:
            try:
                from google import genai
                from google.genai import types
                self.client = genai.Client(api_key=self.gemini_key)
                self.use_gemini = True
                print("✓ Using Gemini AI for answer generation")
                return
            except ImportError:
                print("⚠️  Warning: google-genai package not found")
                print("⚠️  Install with: pip install google-genai")
            except Exception as e:
                print(f"⚠️  Warning: Could not initialize Gemini: {e}")
        
        # Try OpenAI if Gemini not available
        if self.openai_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.openai_key)
                self.model = "gpt-4o-mini"
                self.use_openai = True
                print("✓ Using OpenAI for answer generation")
                return
            except ImportError:
                print("⚠️  Warning: openai package not found. Install with: pip install openai")
        
        # Fallback mode
        print("⚠️  No API key found. Running in FALLBACK mode (basic retrieval only)")
        print("💡 For better answers, set GEMINI_API_KEY or OPENAI_API_KEY environment variable")
    
    def generate_answer(self, query: str, context_chunks: List[Tuple[Chunk, float]], 
                       chat_history: List[Dict]) -> str:
        """Generate answer from context chunks"""
        
        # Build context with citations
        context_parts = []
        for i, (chunk, score) in enumerate(context_chunks, 1):
            citation = chunk.get_citation()
            context_parts.append(f"{citation} {chunk.text}")
        
        context = "\n\n".join(context_parts)
        
        # Build prompt
        system_prompt = """You are a precise document analyst. Answer questions ONLY using the provided context.

STRICT RULES:
1. Answer ONLY from the provided context chunks
2. Include citations [p{page}:c{chunk}] for every claim
3. If the answer is not in the context, respond EXACTLY: "Not found in the document."
4. Do NOT use external knowledge or make assumptions
5. Keep answers concise and factual
6. Use chat history for context but answer from retrieved chunks only"""

        user_prompt = f"""Context from document:
{context}

Question: {query}

Provide a short answer with citations [p{{page}}:c{{chunk}}]. If not found in context, say exactly: "Not found in the document." """

        if self.use_gemini:
            try:
                # Build conversation history for Gemini
                history_text = ""
                if chat_history:
                    history_text = "\n\nPrevious conversation:\n"
                    for msg in chat_history[-10:]:  # Last 5 Q&A pairs
                        role = "User" if msg['role'] == 'user' else "Assistant"
                        history_text += f"{role}: {msg['content']}\n"
                
                full_prompt = f"""{system_prompt}

{history_text}

{user_prompt}"""
                
                response = self.client.models.generate_content(
                    model='gemini-2.0-flash-exp',
                    contents=full_prompt
                )
                return response.text.strip()
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg or "quota" in error_msg.lower():
                    print(f"\n⚠️  Gemini API quota exceeded. Using fallback mode.\n")
                else:
                    print(f"Error calling Gemini API: {e}")
                return self._fallback_answer(context_chunks)
        
        elif self.use_openai:
            try:
                # Build messages with history
                messages = [{"role": "system", "content": system_prompt}]
                
                # Add relevant history (last 5 exchanges)
                for msg in chat_history[-10:]:  # Last 5 Q&A pairs
                    messages.append(msg)
                
                # Add current query
                messages.append({"role": "user", "content": user_prompt})
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.1,
                    max_tokens=500
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"Error calling OpenAI API: {e}")
                return self._fallback_answer(context_chunks)
        else:
            return self._fallback_answer(context_chunks)
    
    def _fallback_answer(self, context_chunks: List[Tuple[Chunk, float]]) -> str:
        """Simple fallback when LLM is not available"""
        if not context_chunks:
            return "Not found in the document."
        
        # Check if top result is relevant (threshold: 0.4 for better precision)
        top_chunk, score = context_chunks[0]
        if score < 0.4:
            return "Not found in the document."
        
        # Return top chunk with citation
        citation = top_chunk.get_citation()
        snippet = top_chunk.text[:200] + "..." if len(top_chunk.text) > 200 else top_chunk.text
        return f"{citation} {snippet}"


class RAGSystem:
    """Main RAG system orchestrator"""
    
    def __init__(self, pdf_path: str, chunk_size: int = 500, chunk_overlap: int = 100,
                 top_k: int = 5, gemini_key: Optional[str] = None, openai_key: Optional[str] = None):
        self.pdf_path = pdf_path
        self.top_k = top_k
        
        # Initialize components
        self.pdf_processor = PDFProcessor(chunk_size, chunk_overlap)
        self.vector_store = VectorStore()
        self.llm = LLMInterface(api_key=openai_key, gemini_key=gemini_key)
        
        # Chat history
        self.chat_history = []
        
        # Process PDF
        print(f"\n📄 Loading PDF: {pdf_path}")
        self.chunks = self.pdf_processor.process_pdf(pdf_path)
        print(f"✓ Extracted {len(self.chunks)} chunks from PDF")
        
        # Build index
        print(f"🔨 Building vector index...")
        self.vector_store.build_index(self.chunks)
        print(f"✓ Index ready with {len(self.chunks)} chunks\n")
    
    def answer_question(self, query: str) -> str:
        """Answer a question with retrieval debug info"""
        
        # Enhance query with recent context for multi-turn (fallback mode support)
        enhanced_query = query
        if self.chat_history and not (self.llm.use_openai or self.llm.use_gemini):
            # In fallback mode, enhance the query with last question for context
            # Only look at last user question (skip assistant responses)
            recent_user_msgs = [msg for msg in self.chat_history[-4:] if msg['role'] == 'user']
            if recent_user_msgs:
                last_question = recent_user_msgs[-1]['content']
                # Combine for better retrieval
                enhanced_query = f"{last_question} {query}"
        
        # Retrieve relevant chunks
        results = self.vector_store.search(enhanced_query, self.top_k)
        
        # Show retrieval debug
        print("\n" + "="*80)
        print("🔍 RETRIEVAL DEBUG")
        print("="*80)
        
        if not results:
            print("No relevant chunks found.")
            return "Not found in the document."
        
        for i, (chunk, score) in enumerate(results, 1):
            print(f"\n[Rank {i}] {chunk.get_citation()} | Score: {score:.4f}")
            snippet = chunk.text[:150] + "..." if len(chunk.text) > 150 else chunk.text
            print(f"Text: {snippet}")
        
        print("\n" + "="*80)
        print("💡 ANSWER")
        print("="*80)
        
        # Generate answer
        answer = self.llm.generate_answer(query, results, self.chat_history)
        
        # Update chat history
        self.chat_history.append({"role": "user", "content": query})
        self.chat_history.append({"role": "assistant", "content": answer})
        
        return answer
    
    def chat_loop(self):
        """Interactive chat loop"""
        print("\n" + "="*80)
        print("💬 RAG SYSTEM - CHAT MODE")
        print("="*80)
        print("Ask questions about the document. Type 'quit' or 'exit' to stop.")
        print("Type 'clear' to reset conversation history.")
        print("="*80 + "\n")
        
        while True:
            try:
                query = input("You: ").strip()
                
                if not query:
                    continue
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                if query.lower() == 'clear':
                    self.chat_history = []
                    print("✓ Conversation history cleared.\n")
                    continue
                
                answer = self.answer_question(query)
                print(f"\n{answer}\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")


def main():
    parser = argparse.ArgumentParser(
        description="RAG System for PDF Question Answering with Citations"
    )
    parser.add_argument(
        "pdf_path",
        nargs="?",
        default=None,
        help="Path to PDF file (e.g., ./doc.pdf)"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=500,
        help="Chunk size in words (default: 500)"
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=100,
        help="Chunk overlap in words (default: 100)"
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of chunks to retrieve (default: 5)"
    )
    
    args = parser.parse_args()
    
    # Check for PDF path
    if not args.pdf_path:
        print("Error: Please provide a PDF file path")
        print("Usage: python main.py <pdf_path>")
        print("Example: python main.py ./doc.pdf")
        sys.exit(1)
    
    if not os.path.exists(args.pdf_path):
        print(f"Error: PDF file not found: {args.pdf_path}")
        sys.exit(1)
    
    # Initialize and run RAG system
    try:
        rag = RAGSystem(
            pdf_path=args.pdf_path,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            top_k=args.top_k
        )
        rag.chat_loop()
    except Exception as e:
        print(f"Error initializing RAG system: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
