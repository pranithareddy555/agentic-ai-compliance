# API Reference

## Base URL
```text
http://127.0.0.1:8000
```

---

## 1) Health Check

### Request
```bash
curl http://127.0.0.1:8000/health
```

### Response
```json
{
  "status": "ok"
}
```

---

## 2) Ingest Regulations

### Endpoint
`POST /v1/knowledge/ingest`

### Request body
```json
{
  "folder_path": "data/regulations"
}
```

### Example
```bash
curl -X POST "http://127.0.0.1:8000/v1/knowledge/ingest" \
  -H "Content-Type: application/json" \
  -d '{"folder_path":"data/regulations"}'
```

### Example response
```json
{
  "ingested_files": 2,
  "ingested_chunks": 4,
  "collection_name": "financial_regulations",
  "backend": "chroma"
}
```

---

## 3) Run an Audit

### Endpoint
`POST /v1/audits/run`

### Option A: Use a file path
```json
{
  "policy_path": "data/policies/sample_non_compliant_policy.md",
  "require_human_approval": true,
  "regulation_focus": ["AML", "KYC", "Customer Due Diligence", "Risk Monitoring"]
}
```

### Option B: Send raw text directly
```json
{
  "policy_text": "Customer identity may be verified within 90 days after onboarding...",
  "require_human_approval": true
}
```

### Example response while waiting for review
```json
{
  "audit_id": "0c56d5d1-3fd5-468d-b2fd-0c5e3f0feaa0",
  "status": "waiting_for_human_review",
  "report": null,
  "human_review_request": {
    "audit_id": "0c56d5d1-3fd5-468d-b2fd-0c5e3f0feaa0",
    "message": "Awaiting compliance officer decision.",
    "report_preview": {
      "...": "..."
    }
  }
}
```

---

## 4) Fetch an Audit Record

### Endpoint
`GET /v1/audits/{audit_id}`

### Example
```bash
curl "http://127.0.0.1:8000/v1/audits/<AUDIT_ID>"
```

This returns the persisted record including current state and any available report payload.

---

## 5) Human Review Decision

### Endpoint
`POST /v1/audits/{audit_id}/human-review`

### Request body
```json
{
  "decision": "approved",
  "reviewer_name": "Compliance Officer",
  "reviewer_notes": "Findings are reasonable and may be issued for remediation."
}
```

### Example
```bash
curl -X POST "http://127.0.0.1:8000/v1/audits/<AUDIT_ID>/human-review" \
  -H "Content-Type: application/json" \
  -d '{"decision":"approved","reviewer_name":"Compliance Officer","reviewer_notes":"Approved for remediation."}'
```

### Example response
```json
{
  "audit_id": "0c56d5d1-3fd5-468d-b2fd-0c5e3f0feaa0",
  "status": "completed",
  "report": {
    "audit_id": "8ef2d4ec-9084-46bb-991b-63e7fd17b183",
    "created_at": "2026-04-20T12:30:00.000000",
    "overall_status": "FAIL",
    "executive_summary": "The uploaded policy was analyzed ...",
    "methodology": [
      "Document ingestion and policy normalization",
      "Semantic retrieval of regulatory context from the knowledge base",
      "Auditor review of policy clauses against retrieved rules",
      "Structured reporting with risk ratings and recommendations",
      "Optional human approval before release"
    ],
    "findings": [
      {
        "finding_id": "f1",
        "risk_level": "High",
        "policy_clause": "identity verification can be completed within 90 days ...",
        "violated_requirement": "...",
        "recommendation": "...",
        "rationale": "...",
        "evidence": []
      }
    ],
    "missing_information": [],
    "next_actions": [
      "Review all high-risk findings with a compliance officer",
      "Amend internal policy clauses and rerun the audit"
    ],
    "reviewer_notes": "Approved for remediation."
  },
  "human_review_request": null
}
```
