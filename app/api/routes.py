from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas import (
    AuditRequest,
    HumanReviewDecision,
    HumanReviewResponse,
    KnowledgeIngestRequest,
    KnowledgeIngestResponse,
    WorkflowResponse,
)
from app.services.graph import ComplianceGraphService
from app.services.knowledge_base import KnowledgeBaseService
from app.services.report_store import AuditStore

router = APIRouter()
knowledge_service = KnowledgeBaseService()
graph_service = ComplianceGraphService()
audit_store = AuditStore()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/v1/knowledge/ingest", response_model=KnowledgeIngestResponse)
def ingest_knowledge(request: KnowledgeIngestRequest) -> KnowledgeIngestResponse:
    return knowledge_service.ingest_folder(request.folder_path)


@router.post("/v1/audits/run", response_model=WorkflowResponse)
def run_audit(request: AuditRequest) -> WorkflowResponse:
    try:
        return graph_service.run_audit(request)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/v1/audits/{audit_id}")
def get_audit(audit_id: str) -> dict:
    try:
        return audit_store.load_record(audit_id).model_dump(mode="json")
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/v1/audits/{audit_id}/human-review", response_model=WorkflowResponse)
def human_review(audit_id: str, decision: HumanReviewDecision) -> WorkflowResponse:
    try:
        return graph_service.resume_with_human_review(
            audit_id=audit_id,
            human_decision=decision.model_dump(mode="json"),
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
