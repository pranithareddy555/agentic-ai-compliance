from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, TypedDict
from uuid import uuid4

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from app.schemas import AuditRecord, AuditRequest, ComplianceReport, WorkflowResponse
from app.services.knowledge_base import KnowledgeBaseService
from app.services.llm import get_llm_service
from app.services.report_store import AuditStore
from app.utils.text import extract_candidate_clauses


class WorkflowState(TypedDict, total=False):
    audit_id: str
    policy_text: str
    regulation_focus: List[str]
    research_loop_count: int
    max_research_loops: int
    retrieved_evidence: List[Dict[str, Any]]
    findings: List[Dict[str, Any]]
    missing_information: List[str]
    require_human_approval: bool
    human_decision: Optional[Dict[str, Any]]
    final_report: Optional[Dict[str, Any]]
    human_review_request: Optional[Dict[str, Any]]


class ComplianceGraphService:
    def __init__(self) -> None:
        self.knowledge_base = KnowledgeBaseService()
        self.llm = get_llm_service()
        self.store = AuditStore()
        self.checkpointer = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(WorkflowState)

        builder.add_node("researcher", self.researcher_node)
        builder.add_node("auditor", self.auditor_node)
        builder.add_node("reporter", self.reporter_node)
        builder.add_node("human_review", self.human_review_node)

        builder.add_edge(START, "researcher")
        builder.add_edge("researcher", "auditor")

        builder.add_conditional_edges(
            "auditor",
            self.route_after_audit,
            {
                "researcher": "researcher",
                "reporter": "reporter",
            },
        )

        builder.add_conditional_edges(
            "reporter",
            self.route_after_report,
            {
                "human_review": "human_review",
                "end": END,
            },
        )

        builder.add_edge("human_review", END)

        return builder.compile(checkpointer=self.checkpointer)

    def researcher_node(self, state: WorkflowState) -> WorkflowState:
        focus_query = " ".join(state.get("regulation_focus", []))
        clauses = extract_candidate_clauses(state["policy_text"])
        query = f"{focus_query} {' '.join(clauses[:4])}".strip()

        evidence = self.knowledge_base.query(query, n_results=5)
        current_loop_count = state.get("research_loop_count", 0)

        return {
            "retrieved_evidence": [item.model_dump(mode="json") for item in evidence],
            "research_loop_count": current_loop_count + 1,
        }

    def auditor_node(self, state: WorkflowState) -> WorkflowState:
        from app.schemas import EvidenceItem

        evidence_models = state.get("retrieved_evidence", [])
        evidence_count = len(evidence_models)

        evidence = [EvidenceItem.model_validate(item) for item in evidence_models]
        findings = self.llm.generate_findings(
            policy_text=state["policy_text"],
            evidence=evidence,
            focus_areas=state.get("regulation_focus", []),
        )

        missing_information: List[str] = []

        if evidence_count < 2:
            missing_information.append(
                "Insufficient regulatory evidence retrieved to support a confident decision."
            )

        if not findings and state.get("research_loop_count", 0) <= 1:
            missing_information.append(
                "No strong finding detected on early pass; re-query for more context."
            )

        return {
            "findings": [item.model_dump(mode="json") for item in findings],
            "missing_information": missing_information,
        }

    def route_after_audit(self, state: WorkflowState) -> Literal["researcher", "reporter"]:
        loop_count = state.get("research_loop_count", 0)
        max_loops = state.get("max_research_loops", 2)
        missing_info = state.get("missing_information", [])

        if missing_info and loop_count < max_loops:
            return "researcher"

        return "reporter"

    def reporter_node(self, state: WorkflowState) -> WorkflowState:
        from app.schemas import ComplianceFinding

        findings = [
            ComplianceFinding.model_validate(item)
            for item in state.get("findings", [])
        ]

        report = self.llm.generate_report(
            findings=findings,
            missing_information=state.get("missing_information", []),
        )
        payload = report.model_dump(mode="json")

        if state.get("require_human_approval", True):
            return {
                "final_report": payload,
                "human_review_request": {
                    "message": "Human approval is required before finalizing the compliance report.",
                    "audit_id": state["audit_id"],
                    "suggested_action": "Review findings and submit approval or rejection via the API.",
                },
            }

        return {"final_report": payload}

    def route_after_report(self, state: WorkflowState) -> Literal["human_review", "end"]:
        if state.get("require_human_approval", True):
            return "human_review"
        return "end"

    def human_review_node(self, state: WorkflowState) -> WorkflowState:
        decision = interrupt(
            {
                "audit_id": state["audit_id"],
                "message": "Awaiting compliance officer decision.",
                "report_preview": state.get("final_report"),
            }
        )
        return {"human_decision": decision}

    def run_audit(self, request: AuditRequest) -> WorkflowResponse:
        audit_id = str(uuid4())
        config = {
            "configurable": {"thread_id": audit_id},
            "recursion_limit": 50,
        }

        initial_state: WorkflowState = {
            "audit_id": audit_id,
            "policy_text": request.resolved_policy_text(),
            "regulation_focus": request.regulation_focus,
            "research_loop_count": 0,
            "max_research_loops": request.max_research_loops,
            "require_human_approval": request.require_human_approval,
        }

        result = self.graph.invoke(initial_state, config=config)
        report_payload = result.get("final_report")
        report = ComplianceReport.model_validate(report_payload) if report_payload else None

        human_review_request = None
        status = "completed"

        if request.require_human_approval:
            status = "waiting_for_human_review"
            human_review_request = {
                "audit_id": audit_id,
                "message": "Awaiting compliance officer decision.",
                "report_preview": report.model_dump(mode="json") if report else None,
            }

        record = AuditRecord(
            audit_id=audit_id,
            status=status,
            state=result,
            report=report if status == "completed" else None,
            human_review_request=human_review_request,
        )
        self.store.save_record(record)

        return WorkflowResponse(
            audit_id=audit_id,
            status=status,
            report=report if status == "completed" else None,
            human_review_request=record.human_review_request,
        )

    def resume_with_human_review(self, audit_id: str, human_decision: Dict[str, Any]) -> WorkflowResponse:
        record = self.store.load_record(audit_id)
        config = {
            "configurable": {"thread_id": audit_id},
            "recursion_limit": 50,
        }

        result = self.graph.invoke(Command(resume=human_decision), config=config)

        report_payload = result.get("final_report") or record.state.get("final_report")
        report = ComplianceReport.model_validate(report_payload) if report_payload else None

        record.state = result
        record.report = report
        record.status = human_decision["decision"]
        record.human_review_request = None
        self.store.save_record(record)

        return WorkflowResponse(
            audit_id=audit_id,
            status="completed",
            report=report,
            human_review_request=None,
        )
