# Architecture Deep Dive

## 1. End-to-end flow

The project is designed as a **multi-agent compliance pipeline**.

### Step-by-step lifecycle
1. A client uploads or references an internal policy document.
2. The policy text is normalized.
3. The **Researcher Agent** queries the regulation knowledge base.
4. The **Auditor Agent** compares policy clauses against retrieved regulations.
5. If the auditor feels evidence is weak or incomplete, the graph loops back.
6. When the review is strong enough, the **Reporting Agent** creates a strict report.
7. The workflow pauses for a human reviewer.
8. A human approves or rejects the result.
9. The final report is persisted for traceability.

---

## 2. Architecture components

### A. API Layer (`FastAPI`)
Purpose:
- expose the system through REST endpoints
- validate incoming requests
- return typed responses

Why this matters:
- the frontend or reviewers need a simple API entry point
- FastAPI automatically documents endpoints with Swagger
- typed response models reduce accidental schema drift

---

### B. Orchestration Layer (`LangGraph`)
Purpose:
- manage the agent workflow and transitions
- support conditional routing
- support human-in-the-loop pause / resume patterns

Graph nodes:
- `researcher`
- `auditor`
- `reporter`
- `human_review`

Routing behavior:
- `researcher -> auditor`
- `auditor -> researcher` when evidence is insufficient
- `auditor -> reporter` when enough evidence exists
- `reporter -> human_review` if approval is required
- `human_review -> END`

Interrupts are a core LangGraph capability for pause-and-resume human review flows. citeturn614721search4turn614721search16

---

### C. Knowledge Base Layer (`Chroma` or local fallback)
Purpose:
- store regulation chunks
- retrieve relevant clauses for auditing

What gets stored:
- regulation title
- source file name
- chunk text
- metadata such as chunk index

Why chunking is needed:
large regulation documents are easier to retrieve accurately when split into smaller semantically meaningful pieces.

Chroma supports persistent local clients for development and testing, which is why it is a good fit for this project’s local MVP. citeturn614721search2turn614721search6

---

### D. LLM Layer
Two implementations are packaged:

#### 1. `MockLLMService`
- runs locally
- uses deterministic rule matching
- intended for setup validation, demos, and grading safety

#### 2. `OpenAILLMService`
- uses an OpenAI chat model
- supports structured function-style output for findings
- better represents the intended AI behavior of the project

---

### E. Structured Output Layer (`Pydantic`)
Purpose:
- enforce the exact shape of the compliance report
- make outputs reliable for frontend/API consumers

The final report includes:
- overall status
- executive summary
- methodology
- findings
- evidence
- missing information
- next actions

Pydantic provides explicit validation tools like `model_validate_json()` and strict validation modes that help keep outputs schema-safe. citeturn614721search3turn614721search7turn614721search19

---

### F. Persistence Layer
What is persisted:
- audit ID
- workflow state
- report payload
- review status
- reviewer notes

Current implementation:
- JSON files stored under `storage/audits/`

Why this is useful:
- easy debugging
- transparent for demos
- lets you inspect every audit after execution

---

## 3. State model overview

The workflow state holds:

- `audit_id`
- `policy_text`
- `regulation_focus`
- `research_loop_count`
- `max_research_loops`
- `retrieved_evidence`
- `findings`
- `missing_information`
- `require_human_approval`
- `human_decision`
- `final_report`
- `human_review_request`

This shared state is what allows agents to collaborate rather than operate in isolation.

---

## 4. Why this design satisfies the project brief

### Requirement: Multi-Agent Orchestrator
Satisfied through distinct nodes with separate responsibilities.

### Requirement: Agentic Routing
Satisfied through the conditional loop from Auditor back to Researcher.

### Requirement: Tool Calling / Structured Output
Satisfied in OpenAI mode through tool-style finding extraction and in all modes through strict Pydantic report models.

### Requirement: Human-in-the-Loop
Satisfied by pause/resume workflow and approval endpoint.

### Requirement: Backend API
Satisfied through FastAPI endpoints.

### Requirement: Architecture Diagram
Included in `docs/architecture_diagram.*`

---

## 5. Production extensions you could add later

- PDF and DOCX ingestion
- Jurisdiction-based retrieval filters
- User authentication and RBAC
- Better evidence citation with page/section references
- Persistent graph state in Redis/Postgres
- Asynchronous job execution
- Frontend dashboard for reviewers
- Multi-tenant knowledge base separation
- Legal hold and evidence export features
