from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    chunk_id: str = Field(default_factory=lambda: str(uuid4()))
    source_name: str
    title: str
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeIngestRequest(BaseModel):
    folder_path: str = Field(
        default="data/regulations",
        description="Local folder containing .md or .txt regulation files.",
    )


class KnowledgeIngestResponse(BaseModel):
    ingested_files: int
    ingested_chunks: int
    collection_name: str
    backend: str


class AuditRequest(BaseModel):
    policy_text: Optional[str] = None
    policy_path: Optional[str] = Field(
        default=None,
        description="Optional local path to a sample policy text file.",
    )
    regulation_focus: List[str] = Field(
        default_factory=lambda: ["AML", "KYC", "Customer Due Diligence", "Risk Monitoring"],
    )
    require_human_approval: bool = True
    max_research_loops: int = Field(default=2, ge=1, le=5)

    def resolved_policy_text(self) -> str:
        if self.policy_text:
            return self.policy_text
        if self.policy_path:
            from pathlib import Path

            return Path(self.policy_path).read_text(encoding="utf-8")
        raise ValueError("Either policy_text or policy_path must be provided.")


class EvidenceItem(BaseModel):
    source_name: str
    title: str
    excerpt: str
    similarity: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ComplianceFinding(BaseModel):
    finding_id: str = Field(default_factory=lambda: str(uuid4()))
    risk_level: Literal["Low", "Medium", "High"]
    policy_clause: str
    violated_requirement: str
    recommendation: str
    rationale: str
    evidence: List[EvidenceItem] = Field(default_factory=list)


class ComplianceReport(BaseModel):
    audit_id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    overall_status: Literal["PASS", "FAIL", "NEEDS_REVIEW"]
    executive_summary: str
    methodology: List[str]
    findings: List[ComplianceFinding]
    missing_information: List[str] = Field(default_factory=list)
    next_actions: List[str] = Field(default_factory=list)
    reviewer_notes: Optional[str] = None


class HumanReviewDecision(BaseModel):
    decision: Literal["approved", "rejected"]
    reviewer_name: str
    reviewer_notes: Optional[str] = None


class HumanReviewResponse(BaseModel):
    audit_id: str
    status: Literal["approved", "rejected"]
    reviewer_name: str
    reviewer_notes: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class WorkflowResponse(BaseModel):
    audit_id: str
    status: Literal["completed", "waiting_for_human_review"]
    report: Optional[ComplianceReport] = None
    human_review_request: Optional[Dict[str, Any]] = None


class AuditRecord(BaseModel):
    audit_id: str
    status: str
    state: Dict[str, Any]
    report: Optional[ComplianceReport] = None
    human_review_request: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
