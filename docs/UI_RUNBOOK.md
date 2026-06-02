# UI Runbook

This project now includes a Streamlit user interface so you do not need to use Swagger for the normal demo flow.

## What the UI includes

- knowledge-base ingestion screen
- policy audit form
- compliance report rendering
- human approval / rejection form
- saved audit lookup

## Fastest way to start everything

From the project root:

```bash
chmod +x run_ui.sh
./run_ui.sh
```

That script will:

1. create a local virtual environment if needed
2. install dependencies
3. start the FastAPI backend on `http://127.0.0.1:8000`
4. start the Streamlit UI on `http://localhost:8501`

## Manual startup

In terminal 1:

```bash
source venv/bin/activate
export MODE=mock
uvicorn app.main:app --reload
```

In terminal 2:

```bash
source venv/bin/activate
streamlit run streamlit_app.py
```

## Recommended demo flow

1. open `http://localhost:8501`
2. go to **Ingest Knowledge**
3. ingest the regulations folder
4. go to **Run Audit**
5. run a policy review
6. go to **Human Review** and submit approval or rejection

## Notes

- The default UI expects the FastAPI backend at `http://127.0.0.1:8000`
- The sidebar lets you change the backend URL if needed
- For offline demo mode, keep `MODE=mock`
- For real model mode, set `MODE=openai` and provide `OPENAI_API_KEY`
