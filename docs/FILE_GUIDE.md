# File-by-File Guide

This document explains the purpose of every important file so a new engineer can understand the repository quickly.

---

## Root files

### `README.md`
The main onboarding guide.
Use this first for:
- project overview
- setup
- demo flow
- technology rationale

### `requirements.txt`
Python dependencies needed to run the project.

### `.env.example`
Template environment variables file.

### `main.py`
Tiny entry module that exposes the FastAPI app.

---

## `app/`

### `app/main.py`
Creates the FastAPI application and registers routes.

### `app/config.py`
Loads environment variables and centralizes application settings.

### `app/schemas.py`
Defines all typed data models:
- ingest requests
- audit requests
- evidence items
- findings
- reports
- review actions
- persisted audit records

This file is important because it standardizes how data moves through the whole system.

---

## `app/api/`

### `app/api/routes.py`
Contains the REST endpoints:
- `/health`
- `/v1/knowledge/ingest`
- `/v1/audits/run`
- `/v1/audits/{audit_id}`
- `/v1/audits/{audit_id}/human-review`

---

## `app/services/`

### `app/services/knowledge_base.py`
Responsible for:
- reading regulation files
- chunking content
- storing chunks in a retriever backend
- returning relevant evidence items for a query

It uses:
- Chroma if available
- a simple local cosine-similarity fallback if Chroma is unavailable

### `app/services/llm.py`
Contains two LLM backends.

#### `MockLLMService`
Local deterministic reviewer for demos.

#### `OpenAILLMService`
Real LLM-backed reviewer using:
- summarization
- structured finding extraction
- report generation

### `app/services/graph.py`
The most important file in the project.

This file:
- defines the LangGraph workflow state
- builds the agent graph
- implements every agent node
- controls routing decisions
- handles pause/resume for human approval

### `app/services/report_store.py`
Persists audit records to JSON files.

---

## `app/utils/`

### `app/utils/text.py`
Low-level utilities for:
- loading text files
- normalization
- chunking
- candidate clause extraction

---

## `data/`

### `data/regulations/`
Contains mock regulation files for the knowledge base.

### `data/policies/`
Contains sample internal policies that you can audit immediately.

---

## `docs/`

### `docs/ARCHITECTURE.md`
Detailed system design explanation.

### `docs/API_REFERENCE.md`
Detailed API examples and request/response payloads.

### `docs/RUNBOOK.md`
How to run, test, troubleshoot, and demo the project.

### `docs/architecture_diagram.mmd`
Editable Mermaid diagram source.

### `docs/architecture_diagram.png`
Rendered visual architecture diagram.

---

## `tests/`

### `tests/test_mock_workflow.py`
Simple smoke test verifying that the workflow can run and produce an audit response.

---

## What a new engineer should read first

Recommended order:
1. `README.md`
2. `docs/ARCHITECTURE.md`
3. `docs/FILE_GUIDE.md`
4. `app/schemas.py`
5. `app/services/graph.py`
6. `docs/API_REFERENCE.md`
7. `docs/RUNBOOK.md`
