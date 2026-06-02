from __future__ import annotations

import json
import re
from typing import Any

from app.config import settings
from app.schemas import ComplianceFinding, ComplianceReport, EvidenceItem

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None


class BaseLLMService:
    def summarize_regulatory_changes(self, question: str, evidence: list[EvidenceItem]) -> str:
        raise NotImplementedError

    def generate_findings(
        self,
        policy_text: str,
        evidence: list[EvidenceItem],
        focus_areas: list[str],
    ) -> list[ComplianceFinding]:
        raise NotImplementedError

    def generate_report(
        self,
        findings: list[ComplianceFinding],
        missing_information: list[str],
    ) -> ComplianceReport:
        raise NotImplementedError


class MockLLMService(BaseLLMService):
    """Rule-based fallback so the project works without an external model.
    This is not a replacement for a real LLM, but it keeps the workflow runnable.
    """

    RULE_PATTERNS = [
        {
            "pattern": r"within\s+90\s+days|after\s+onboarding|account\s+activation.*identity|onboard(?:ing)?\s+without\s+.*identification|identity verification can be completed later",
            "risk": "High",
            "requirement": "Customer identity must be verified before or at onboarding for higher-risk scenarios.",
            "recommendation": "Require identity verification before account activation and block delayed verification except approved low-risk exceptions.",
            "rationale": "Delayed verification creates AML/KYC exposure during onboarding.",
        },
        {
            "pattern": r"reviewed\s+monthly|monthly\s+review|once\s+a\s+year|annually|annual(?:ly)?\s+screening|suspicious activity.*monthly|sanctions screening.*year",
            "risk": "High",
            "requirement": "Suspicious activity monitoring and sanctions/PEP screening should be timely and risk-based, not deferred to infrequent manual review.",
            "recommendation": "Implement near-real-time monitoring thresholds and alert escalation workflows.",
            "rationale": "Infrequent review can miss urgent suspicious activity signals.",
        },
        {
            "pattern": r"retain(?:ed)?\s+for\s+12\s+months|delete(?:d)?\s+after\s+12\s+months|one\s+year|1\s+year|12-month",
            "risk": "Medium",
            "requirement": "Retention periods for AML/KYC records are generally multi-year and should align with regulatory retention obligations.",
            "recommendation": "Update retention controls to maintain required records for the mandated duration and add legal-hold logic.",
            "rationale": "Under-retention weakens auditability and regulatory defensibility.",
        },
        {
            "pattern": r"judgment.*high-value|enhanced due diligence.*necessary|optional|may be skipped|need not|not required",
            "risk": "Medium",
            "requirement": "High-risk customers should have explicit enhanced due diligence rules and mandatory escalation criteria.",
            "recommendation": "Add clear escalation triggers and mandatory review steps for high-risk customers.",
            "rationale": "Relying on judgment alone makes high-risk handling inconsistent and difficult to audit.",
        },
        {
            "pattern": r"share.*for internal convenience|personal devices|access controls.*only when a problem is reported|can be shared across teams",
            "risk": "Medium",
            "requirement": "Customer personal data should be restricted to authorized personnel under least-privilege controls.",
            "recommendation": "Limit data access to approved personnel and require routine access reviews.",
            "rationale": "Loose access handling increases privacy and confidentiality risk.",
        },
    ]

    def summarize_regulatory_changes(self, question: str, evidence: list[EvidenceItem]) -> str:
        excerpts = " ".join([e.excerpt for e in evidence[:3]])
        return (
            f"Based on the retrieved regulatory context, the main themes related to '{question}' "
            f"are customer due diligence, risk-based monitoring, record retention, and escalation controls. "
            f"Key supporting excerpts: {excerpts[:400]}"
        )

    def generate_findings(
        self,
        policy_text: str,
        evidence: list[EvidenceItem],
        focus_areas: list[str],
    ) -> list[ComplianceFinding]:
        findings: list[ComplianceFinding] = []
        lowered = policy_text.lower()

        for rule in self.RULE_PATTERNS:
            match = re.search(rule["pattern"], lowered)
            if match:
                clause = policy_text[max(0, match.start() - 40): min(len(policy_text), match.end() + 120)].strip()
                findings.append(
                    ComplianceFinding(
                        risk_level=rule["risk"],
                        policy_clause=clause,
                        violated_requirement=rule["requirement"],
                        recommendation=rule["recommendation"],
                        rationale=rule["rationale"],
                        evidence=evidence[:2],
                    )
                )

        if not findings:
            broad_signals = {
                "delay_verification": any(phrase in lowered for phrase in ["verify after onboarding", "completed within 90 days", "onboard immediately"]),
                "infrequent_screening": any(phrase in lowered for phrase in ["once a year", "annually", "monthly"]),
                "short_retention": any(phrase in lowered for phrase in ["12 months", "1 year", "delete"]),
                "weak_privacy": any(phrase in lowered for phrase in ["personal devices", "internal convenience", "access controls are reviewed only when a problem is reported"]),
            }
            if sum(bool(value) for value in broad_signals.values()) >= 2:
                findings.append(
                    ComplianceFinding(
                        risk_level="High",
                        policy_clause=policy_text[:260],
                        violated_requirement="Multiple AML/KYC and privacy controls appear too weak or too infrequent to satisfy a conservative compliance baseline.",
                        recommendation="Strengthen onboarding verification, screening frequency, retention, and access control language before approval.",
                        rationale="The policy contains several risk indicators that would usually trigger escalation in a real compliance review.",
                        evidence=evidence[:2],
                    )
                )

        if not findings and any(term.lower() in lowered for term in ["anonymous accounts", "no verification", "skip due diligence"]):
            findings.append(
                ComplianceFinding(
                    risk_level="High",
                    policy_clause=policy_text[:220],
                    violated_requirement="Identity verification and due diligence controls appear insufficient.",
                    recommendation="Add mandatory KYC onboarding checks and transaction monitoring controls.",
                    rationale="The policy language suggests missing baseline AML/KYC safeguards.",
                    evidence=evidence[:2],
                )
            )

        return findings

    def generate_report(
        self,
        findings: list[ComplianceFinding],
        missing_information: list[str],
    ) -> ComplianceReport:
        status = "PASS"
        if missing_information:
            status = "NEEDS_REVIEW"
        if findings:
            status = "FAIL"

        summary = (
            "The uploaded policy was analyzed against the retrieved regulatory context using "
            "a multi-agent workflow. "
        )
        if findings:
            summary += f"The system identified {len(findings)} potential compliance gap(s) requiring remediation."
        else:
            summary += "No direct gaps were detected in the current run, but human review remains recommended."

        return ComplianceReport(
            overall_status=status,
            executive_summary=summary,
            methodology=[
                "Document ingestion and policy normalization",
                "Semantic retrieval of regulatory context from the knowledge base",
                "Auditor review of policy clauses against retrieved rules",
                "Structured reporting with risk ratings and recommendations",
                "Optional human approval before release",
            ],
            findings=findings,
            missing_information=missing_information,
            next_actions=[
                "Review all high-risk findings with a compliance officer",
                "Amend internal policy clauses and rerun the audit",
                "Expand the knowledge base with additional jurisdiction-specific regulations",
            ],
        )


class OpenAILLMService(BaseLLMService):
    def __init__(self) -> None:
        if OpenAI is None:
            raise RuntimeError("openai package is not installed.")
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required for openai mode.")
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    def summarize_regulatory_changes(self, question: str, evidence: list[EvidenceItem]) -> str:
        context = "\n\n".join(f"- {e.title}: {e.excerpt}" for e in evidence)
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a regulatory research analyst. Summarize only what is supported "
                        "by the provided evidence. Keep the answer concise and practical."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Question: {question}\n\nEvidence:\n{context}",
                },
            ],
        )
        return response.choices[0].message.content or ""

    def generate_findings(
        self,
        policy_text: str,
        evidence: list[EvidenceItem],
        focus_areas: list[str],
    ) -> list[ComplianceFinding]:
        context = "\n\n".join(f"- {e.title} ({e.source_name}): {e.excerpt}" for e in evidence)
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "emit_compliance_findings",
                    "description": "Return structured compliance findings extracted from the policy review.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "findings": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "risk_level": {"type": "string", "enum": ["Low", "Medium", "High"]},
                                        "policy_clause": {"type": "string"},
                                        "violated_requirement": {"type": "string"},
                                        "recommendation": {"type": "string"},
                                        "rationale": {"type": "string"},
                                    },
                                    "required": [
                                        "risk_level",
                                        "policy_clause",
                                        "violated_requirement",
                                        "recommendation",
                                        "rationale",
                                    ],
                                },
                            }
                        },
                        "required": ["findings"],
                    },
                },
            }
        ]
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            tools=tools,
            tool_choice={"type": "function", "function": {"name": "emit_compliance_findings"}},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are the Auditor Agent in a compliance workflow. Review the uploaded policy "
                        "against the regulatory evidence. Only cite risks supported by the evidence. "
                        "Return findings through the tool call only."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Focus areas: {', '.join(focus_areas)}\n\n"
                        f"Policy:\n{policy_text}\n\nRegulatory evidence:\n{context}"
                    ),
                },
            ],
        )
        tool_calls = response.choices[0].message.tool_calls or []
        if not tool_calls:
            return []

        args = json.loads(tool_calls[0].function.arguments)
        findings: list[ComplianceFinding] = []
        for raw in args.get("findings", []):
            findings.append(
                ComplianceFinding(
                    risk_level=raw["risk_level"],
                    policy_clause=raw["policy_clause"],
                    violated_requirement=raw["violated_requirement"],
                    recommendation=raw["recommendation"],
                    rationale=raw["rationale"],
                    evidence=evidence[:2],
                )
            )
        return findings

    def generate_report(
        self,
        findings: list[ComplianceFinding],
        missing_information: list[str],
    ) -> ComplianceReport:
        payload = {
            "findings": [f.model_dump(mode="json") for f in findings],
            "missing_information": missing_information,
        }
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are the Reporting Agent. Produce a concise executive summary and action plan "
                        "for a compliance officer. Return valid JSON matching the requested schema."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(payload),
                },
            ],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        parsed = json.loads(content)

        return ComplianceReport(
            overall_status=parsed.get(
                "overall_status",
                "FAIL" if findings else ("NEEDS_REVIEW" if missing_information else "PASS"),
            ),
            executive_summary=parsed.get(
                "executive_summary",
                "Compliance review completed. See findings and next actions.",
            ),
            methodology=parsed.get(
                "methodology",
                [
                    "Policy ingestion",
                    "Regulation retrieval",
                    "Clause-level audit review",
                    "Structured report generation",
                ],
            ),
            findings=findings,
            missing_information=missing_information,
            next_actions=parsed.get(
                "next_actions",
                [
                    "Validate findings with a human compliance reviewer",
                    "Remediate policy gaps",
                    "Rerun the audit after updates",
                ],
            ),
        )


def get_llm_service() -> BaseLLMService:
    if settings.llm_mode.lower() == "openai":
        return OpenAILLMService()
    return MockLLMService()
