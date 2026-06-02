# Project Brief Mapping

This document maps the internship brief directly to the implementation in this repository.

## Executive Problem Statement
**Brief expectation:** Automatically compare internal business documents against changing regulatory frameworks and flag potential violations.

**Repository implementation:**
- Policy ingestion through API
- Regulation ingestion into local knowledge base
- Agentic audit workflow
- Structured compliance report with findings and recommendations

---

## Business Objective
**Brief expectation:** Reduce audit time and improve adherence.

**Repository implementation:**
- FastAPI endpoint to trigger audits quickly
- Reusable knowledge base for regulations
- Consistent Pydantic report schema for downstream review

---

## KPI from brief
**Brief expectation:** Valid, deeply structured compliance reports without missing required sections.

**Repository implementation:**
- Final report enforced by `ComplianceReport` Pydantic schema
- Findings enforced by `ComplianceFinding` schema
- Response models in FastAPI make API output consistent

---

## Personas from brief

### Compliance Officer
**Expected workflow:** Uploads policy and receives gap analysis

**Repository implementation:**  
`POST /v1/audits/run` + `POST /v1/audits/{audit_id}/human-review`

### Software Developer
**Expected workflow:** Queries the AI to understand regulatory changes

**Repository implementation:**  
The retrieval and summarization layer is present in the Researcher / LLM services and can be extended into a dedicated Q&A endpoint easily.

---

## MVP Requirements

### 1. Multi-Agent Orchestrator
Implemented in:
- `app/services/graph.py`

### 2. Distinct Agent Personas
Implemented in:
- Researcher node
- Auditor node
- Reporter node

### 3. State Management
Implemented in:
- `WorkflowState` inside `graph.py`

### 4. Tool Calling / Structured Output
Implemented in:
- `OpenAILLMService.generate_findings()` with function-style tool schema
- Pydantic schemas for final validation

### 5. Autonomous re-query / self-correction
Implemented in:
- conditional route from auditor back to researcher

### 6. Human-in-the-Loop pause
Implemented in:
- LangGraph `interrupt(...)`
- review endpoint to resume the workflow

### 7. Backend API
Implemented in:
- `app/api/routes.py`

### 8. Architecture diagram
Implemented in:
- `docs/architecture_diagram.mmd`
- `docs/architecture_diagram.png`

---

## Four-week roadmap coverage

### Week 1
- regulation loading
- persona definition

### Week 2
- graph-based orchestration
- conditional routing loop

### Week 3
- structured risk findings
- anomaly/risk flag output

### Week 4
- human approval pause
- API wrapping
- architecture documentation
