# Agentic AI for Regulatory Compliance Automation

A complete, engineer-style reference project for **Project 2: Agentic AI for Regulatory Compliance Automation**.  
This repository demonstrates how to build a **multi-agent compliance workflow** using:

- **FastAPI** for REST APIs
- **LangGraph** for stateful orchestration and routing
- **Pydantic** for strict structured output
- **ChromaDB** (with a local fallback retriever) for regulation retrieval
- **Human-in-the-loop** approval before finalizing a report

---

## 1) What problem this project solves

Financial regulations change often. Internal company policies do not always keep up.  
Manual review is expensive, slow, and error-prone.

This project automates the first-pass compliance review by:

1. Ingesting regulatory guidance into a searchable knowledge base
2. Reviewing uploaded policy text against those regulations
3. Looping back for more evidence when the current evidence is not sufficient
4. Producing a **strictly structured compliance report**
5. Pausing for **human approval** before finalizing the audit

---

## 2) What is implemented in this repository

### Included features
- Multi-agent workflow with the personas requested in the project brief
- Researcher Agent
- Auditor Agent
- Reporting Agent
- Conditional routing / self-correction loop
- Knowledge base ingestion endpoint
- Compliance audit endpoint
- Human-review approval endpoint
- Sample regulations and sample policies
- Detailed documentation
- Architecture diagram
- Demo-safe fallback mode (`LLM_MODE=mock`) so you can run it locally first

### Supported runtime modes
#### A. Mock Mode (default)
- No external API key needed
- Uses deterministic local logic for demo and grading
- Best for first-time setup and walkthroughs

#### B. OpenAI Mode
- Uses an OpenAI model for summarization and structured findings
- Enables real LLM behavior with tool-calling style output

---

## 3) Repository structure

```text
agentic_ai_compliance_project/
├── app/
│   ├── api/
│   │   └── routes.py
│   ├── services/
│   │   ├── graph.py
│   │   ├── knowledge_base.py
│   │   ├── llm.py
│   │   └── report_store.py
│   ├── utils/
│   │   └── text.py
│   ├── config.py
│   ├── main.py
│   └── schemas.py
├── data/
│   ├── policies/
│   └── regulations/
├── docs/
├── tests/
├── .env.example
├── main.py
├── README.md
└── requirements.txt
```

---

## 4) Quick start

### Step 1: Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 2: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Create your environment file
```bash
cp .env.example .env
```

### Step 4: Start the API
```bash
uvicorn app.main:app --reload
```

API docs:
- Swagger UI: `http://127.0.0.1:8000/docs`

---

## 5) First demo run

### A. Ingest the regulation files
```bash
curl -X POST "http://127.0.0.1:8000/v1/knowledge/ingest" \
  -H "Content-Type: application/json" \
  -d '{"folder_path":"data/regulations"}'
```

### B. Run an audit using the sample non-compliant policy
```bash
curl -X POST "http://127.0.0.1:8000/v1/audits/run" \
  -H "Content-Type: application/json" \
  -d '{"policy_path":"data/policies/sample_non_compliant_policy.md","require_human_approval":true}'
```

The response will return:
- an `audit_id`
- a status (usually `waiting_for_human_review`)
- a human review request payload

### C. Approve the report
Replace `<AUDIT_ID>` with the returned ID.
```bash
curl -X POST "http://127.0.0.1:8000/v1/audits/<AUDIT_ID>/human-review" \
  -H "Content-Type: application/json" \
  -d '{"decision":"approved","reviewer_name":"Mounika","reviewer_notes":"Reviewed and approved for demo."}'
```

### D. Retrieve the saved audit record
```bash
curl "http://127.0.0.1:8000/v1/audits/<AUDIT_ID>"
```

---

## 6) Agent definitions

### Researcher Agent
Responsible for retrieving the most relevant regulations from the knowledge base based on the uploaded policy and the requested regulatory focus.

### Auditor Agent
Responsible for checking policy clauses against retrieved evidence and determining:
- possible violations
- risk level
- rationale
- recommendations

### Reporting Agent
Responsible for formatting the final output into a strict structure defined by Pydantic.

### Human Reviewer
A real person (for example, a compliance officer) who approves or rejects the AI-generated report before it is finalized.

---

## 7) How the self-correcting loop works

1. The system retrieves regulations
2. The Auditor checks whether the evidence is sufficient
3. If evidence is weak or unclear, the workflow routes back to the Researcher
4. The Researcher retrieves more context
5. The Auditor retries
6. Once sufficient, the Reporter creates the final report

This is the “agentic routing” requirement from the project brief.

---

## 8) Human-in-the-loop design

The graph intentionally pauses before final completion.  
This mirrors a realistic compliance workflow, because AI should assist the review, not make final legal decisions alone.

LangGraph's interrupt pattern is the conceptual basis for this pause-and-resume flow.

---

## 9) Why these technologies fit the brief

- **FastAPI** provides typed REST endpoints and strong response validation through response models.
- **LangGraph** is designed for durable orchestration, interrupts, and human-in-the-loop agent workflows.
- **Pydantic** provides strict validation utilities such as `model_validate_json()` and strict configuration patterns for structured outputs.
- **Chroma** supports both in-memory and persistent local clients, which makes it a practical local vector database for this project.

---

## 10) Documentation index

- `docs/ARCHITECTURE.md` → system design and workflow explanation
- `docs/FILE_GUIDE.md` → what every file does
- `docs/API_REFERENCE.md` → request/response examples
- `docs/RUNBOOK.md` → run, test, troubleshoot, demo checklist
- `docs/architecture_diagram.mmd` → editable Mermaid diagram
- `docs/architecture_diagram.png` → rendered architecture image

---
