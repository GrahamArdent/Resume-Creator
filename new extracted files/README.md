# Resume System with LLM Keyword Integration

## Setup
1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and add your key:
   ```
   OPENAI_API_KEY=sk-xxxx
   ```

## Usage
```bash
python scripts/run_interactive_qna.py
```

- Paste your job description file path
- Enter company name
- Answer only new questions (others are remembered globally)

Outputs are saved in `outputs/<company>/`.
