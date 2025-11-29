
# TruthPulse AI Backend (Ultra Forgiving)

- Accepts many frontend payload shapes (text/claim/news/content/message)
- Has both `/api/analyze` and `/verify-claim`
- Truth-leaning: strong Wikipedia evidence pushes towards 'Likely True'

## Run

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open `http://localhost:8000/docs`.
