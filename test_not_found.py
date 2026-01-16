"""
Test script to verify "Not found in the document." behavior
"""
import os
import sys
from main import RAGSystem

# Set environment for offline mode
os.environ['HF_HUB_OFFLINE'] = '1'

def test_not_found_behavior():
    """Test that off-topic questions get 'Not found' responses"""
    
    pdf_path = r"c:\Users\Soham\OneDrive\Desktop\AEL_Earnings_Presentation_Q2-FY26.pdf"
    
    print("=" * 80)
    print("TESTING 'NOT FOUND' BEHAVIOR")
    print("=" * 80)
    
    # Initialize RAG system (without LLM to avoid quota issues)
    rag = RAGSystem(pdf_path=pdf_path, top_k=5)
    
    # Questions that SHOULD return "Not found in the document."
    off_topic_questions = [
        "What is quantum computing?",
        "Who is the CEO of Apple?",
        "What is the weather today?",
        "Tell me about Tesla's revenue",
        "What is machine learning?",
        "How do I cook pasta?",
        "What is the capital of France?",
    ]
    
    # Questions that SHOULD be answered
    valid_questions = [
        "What was the total income in Q2 FY26?",
        "What is EBITDA?",
        "Tell me about airports",
    ]
    
    print("\n" + "=" * 80)
    print("OFF-TOPIC QUESTIONS (should return 'Not found')")
    print("=" * 80)
    
    for q in off_topic_questions:
        print(f"\nQ: {q}")
        answer = rag.answer_question(q)
        print(f"A: {answer[:150]}...")
        
        # Check if "Not found" is in the answer
        if "not found in the document" in answer.lower():
            print("✅ PASS - Correctly refused")
        else:
            print("❌ FAIL - Should have said 'Not found'")
    
    print("\n" + "=" * 80)
    print("VALID QUESTIONS (should return answers with citations)")
    print("=" * 80)
    
    for q in valid_questions:
        print(f"\nQ: {q}")
        answer = rag.answer_question(q)
        print(f"A: {answer[:200]}...")
        
        # Check if citation exists or got real answer
        if "not found in the document" in answer.lower():
            print("⚠️  WARNING - Might have missed valid content")
        elif "[p" in answer and ":c" in answer:
            print("✅ PASS - Has citations")
        else:
            print("✅ INFO - Answered (fallback mode)")

if __name__ == "__main__":
    test_not_found_behavior()
