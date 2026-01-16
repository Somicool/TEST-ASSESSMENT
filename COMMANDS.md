# Quick Command Reference

## Installation (One-time Setup)

```bash
# Clone the repository
git clone https://github.com/Somicool/TEST-ASSESSMENT.git
cd TEST-ASSESSMENT

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Running the System

### Option 1: Basic Mode (No AI)
```bash
python main.py your_document.pdf
```

### Option 2: With Gemini AI (Recommended)
```bash
# Windows PowerShell
$env:GEMINI_API_KEY="your-api-key-here"
$env:HF_HUB_OFFLINE="1"
python main.py your_document.pdf

# Linux/macOS
export GEMINI_API_KEY="your-api-key-here"
export HF_HUB_OFFLINE="1"
python main.py your_document.pdf
```

### Option 3: With OpenAI
```bash
# Windows PowerShell
$env:OPENAI_API_KEY="sk-your-key"
$env:HF_HUB_OFFLINE="1"
python main.py your_document.pdf

# Linux/macOS
export OPENAI_API_KEY="sk-your-key"
export HF_HUB_OFFLINE="1"
python main.py your_document.pdf
```

## Testing

```bash
# Run acceptance tests
$env:HF_HUB_OFFLINE="1"
python acceptance_tests.py your_document.pdf

# Test "not found" behavior
python test_not_found.py
```

## Dependencies Summary

- `pypdf` - PDF text extraction
- `faiss-cpu` - Vector search
- `sentence-transformers` - Text embeddings
- `numpy` - Numerical operations
- `google-genai` (optional) - Gemini AI
- `openai` (optional) - OpenAI GPT

**First run:** Downloads ~90MB embedding model (cached for future runs)

## Troubleshooting

**Problem:** Module not found  
**Solution:** `pip install -r requirements.txt`

**Problem:** Gemini quota exceeded  
**Solution:** System auto-switches to fallback mode

**Problem:** Unicode errors on Windows  
**Solution:** Use Windows Terminal (not cmd.exe)

## Support

- GitHub: https://github.com/Somicool/TEST-ASSESSMENT
- Issues: https://github.com/Somicool/TEST-ASSESSMENT/issues
