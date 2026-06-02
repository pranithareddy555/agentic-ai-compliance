from app.schemas import AuditRequest
from app.services.graph import ComplianceGraphService
from app.services.knowledge_base import KnowledgeBaseService


def test_mock_workflow_generates_review_request():
    kb = KnowledgeBaseService()
    kb.ingest_folder("data/regulations")

    service = ComplianceGraphService()
    response = service.run_audit(
        AuditRequest(
            policy_path="data/policies/sample_non_compliant_policy.md",
            require_human_approval=True,
        )
    )

    assert response.audit_id
    assert response.status in {"waiting_for_human_review", "completed"}
