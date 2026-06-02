# Runbook

## 1. Goal of this runbook
This document explains exactly how to run, verify, test, and demonstrate the project on a MacBook.

---

## 2. Prerequisites

Recommended:
- Python 3.11+
- Terminal access
- Internet access for `pip install`
- Optional: OpenAI API key if you want real LLM behavior

Check Python:
```bash
python3 --version
```

---

## 3. Local setup on macOS

### Create virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install packages
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Create env file
```bash
cp .env.example .env
```

---

## 4. Choose your mode

### Mock mode (recommended first)
Keep:
```env
LLM_MODE=mock
```

Use this when:
- you want the project running quickly
- you want to verify the API and graph
- you do not want to configure external model access yet

### OpenAI mode
Edit `.env`:
```env
LLM_MODE=openai
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4.1-mini
```

Use this when:
- you want real LLM-driven findings and summaries
- you want to demonstrate tool-style structured output

---

## 5. Start the server
```bash
uvicorn app.main:app --reload
```

You should see the app on:
```text
http://127.0.0.1:8000
```

Swagger UI:
```text
http://127.0.0.1:8000/docs
```

---

## 6. Demo checklist

### Step A — Ingest regulations
Use Swagger or:
```bash
curl -X POST "http://127.0.0.1:8000/v1/knowledge/ingest" \
  -H "Content-Type: application/json" \
  -d '{"folder_path":"data/regulations"}'
```

Expected:
- file count > 0
- chunk count > 0

### Step B — Run sample audit
```bash
curl -X POST "http://127.0.0.1:8000/v1/audits/run" \
  -H "Content-Type: application/json" \
  -d '{"policy_path":"data/policies/sample_non_compliant_policy.md","require_human_approval":true}'
```

Expected:
- an `audit_id`
- usually `waiting_for_human_review`

### Step C — Submit approval
```bash
curl -X POST "http://127.0.0.1:8000/v1/audits/<AUDIT_ID>/human-review" \
  -H "Content-Type: application/json" \
  -d '{"decision":"approved","reviewer_name":"Demo Reviewer","reviewer_notes":"Approved during local demo."}'
```

### Step D — Fetch persisted audit record
```bash
curl "http://127.0.0.1:8000/v1/audits/<AUDIT_ID>"
```

---

## 7. Running tests
```bash
pytest -q
```

---

## 8. Troubleshooting

### Problem: `ModuleNotFoundError: langgraph`
Cause:
- dependencies not installed

Fix:
```bash
pip install -r requirements.txt
```

### Problem: `OPENAI_API_KEY is required`
Cause:
- `LLM_MODE=openai` but key not configured

Fix:
- either set the key
- or switch back to `LLM_MODE=mock`

### Problem: Chroma import/setup issue
Fix:
- the project includes a simple fallback retriever
- the app can still run in demo mode while you troubleshoot Chroma

### Problem: Nothing returned in audit
Fix:
- make sure you ingest regulations first
- use the sample non-compliant policy to verify the pipeline
- confirm the API is running at port 8000

---

## 9. Suggested presentation/demo flow

1. Explain the business problem
2. Show the architecture diagram
3. Show the regulation files
4. Start the API
5. Ingest regulations
6. Run the audit
7. Show the human review pause
8. Approve via API
9. Retrieve the final saved audit record
10. Explain how the loop and structured reporting satisfy the project brief
