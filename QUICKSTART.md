# Quick Start Guide

## Installation (5 minutes)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   This will download ~90MB of models on first run (cached for future use).

2. **Verify installation:**
   ```bash
   python test_rag.py
   ```
   
   All tests should pass ✅

## Usage

### Option 1: Use Your Own PDF

```bash
python main.py ./your_document.pdf
```

### Option 2: Create a Sample PDF for Testing

```bash
# Install optional PDF library
pip install fpdf2

# Create sample PDF
python create_sample_pdf.py

# Run RAG system
python main.py sample_document.pdf
```

## Sample Questions for Testing

Try these questions with the sample PDF:

**Should work (found in document):**
- What was the revenue in Q4 2023?
- Who founded the company?
- What products were launched in 2023?
- What is the strategic focus for 2024?
- How many customers does TechCorp serve?

**Should refuse (not in document):**
- What about flying cars?
- Tell me about quantum computing
- What is the weather today?

Expected response: "Not found in the document."

## Expected Output

```
📄 Loading PDF: sample_document.pdf
✓ Extracted 15 chunks from PDF
🔨 Building vector index...
✓ Index ready with 15 chunks

================================================================================
💬 RAG SYSTEM - CHAT MODE
================================================================================
Ask questions about the document. Type 'quit' or 'exit' to stop.
Type 'clear' to reset conversation history.
================================================================================

You: What was the revenue in Q4 2023?

================================================================================
🔍 RETRIEVAL DEBUG
================================================================================

[Rank 1] [p2:c5] | Score: 0.8234
Text: Q4 2023 revenue reached $2.4 billion, representing a 15% year-over-year increase...

================================================================================
💡 ANSWER
================================================================================

Q4 2023 revenue was $2.4 billion [p2:c5].
```

## Using with OpenAI (Optional)

For better quality answers:

1. **Get API key** from https://platform.openai.com/api-keys

2. **Set environment variable:**
   ```bash
   # Windows PowerShell
   $env:OPENAI_API_KEY="sk-..."
   
   # Linux/Mac
   export OPENAI_API_KEY="sk-..."
   ```

3. **Install OpenAI package:**
   ```bash
   pip install openai
   ```

4. **Run as normal:**
   ```bash
   python main.py your_document.pdf
   ```

The system will automatically use OpenAI when available, or fall back to basic retrieval mode.

## Troubleshooting

### Import Error
```bash
# Make sure you're in the right directory
cd adani

# Reinstall dependencies
pip install -r requirements.txt
```

### PDF Not Found
```bash
# Use absolute path
python main.py "C:\Users\YourName\Documents\report.pdf"
```

### Out of Memory
```bash
# Reduce chunk size and retrieval count
python main.py doc.pdf --chunk-size 300 --top-k 3
```

## Next Steps

- Try with your own PDFs (reports, contracts, policies)
- Adjust chunk size for better results
- Enable OpenAI for higher quality answers
- Experiment with top-k parameter

## Support

For issues or questions, check:
- README.md for detailed documentation
- Test output from `python test_rag.py`
- Retrieval debug output shows what chunks were found
