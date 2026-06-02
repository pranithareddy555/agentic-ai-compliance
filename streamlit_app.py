from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
import streamlit as st

ROOT = Path(__file__).resolve().parent
DEFAULT_API_BASE = "http://127.0.0.1:8000"
SAMPLE_POLICY_PATH = ROOT / "data" / "policies"
REGULATIONS_PATH = ROOT / "data" / "regulations"

st.set_page_config(
    page_title="Agentic AI Compliance Automation",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .stApp {
        background:
          radial-gradient(circle at top left, rgba(113, 183, 255, 0.16), transparent 26%),
          radial-gradient(circle at top right, rgba(92, 225, 166, 0.12), transparent 22%),
          linear-gradient(180deg, #07111f 0%, #0b1527 100%);
      }
      .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
      [data-testid="stSidebar"] { background: rgba(8, 15, 27, 0.92); border-right: 1px solid rgba(148, 163, 184, 0.18); }
      .hero { padding: 2rem; border-radius: 28px; background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(7, 17, 31, 0.95)); border: 1px solid rgba(148, 163, 184, 0.18); box-shadow: 0 24px 80px rgba(0, 0, 0, 0.24); }
      .hero-kicker { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.4rem 0.8rem; border-radius: 999px; background: rgba(92, 225, 166, 0.12); color: #7ff0bf; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; font-size: 0.72rem; }
      .hero h1 { margin: 0.8rem 0 0.5rem; font-size: clamp(2.2rem, 4vw, 4rem); line-height: 0.95; color: #eef5ff; }
      .hero p { margin: 0; max-width: 72ch; color: #b7c5db; font-size: 1.02rem; line-height: 1.65; }
      .pill-row { display: flex; flex-wrap: wrap; gap: 0.75rem; margin-top: 1.25rem; }
      .pill { padding: 0.6rem 0.9rem; border-radius: 999px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(148, 163, 184, 0.16); color: #d8e6fb; font-size: 0.88rem; }
      .section-card { padding: 1.1rem 1.2rem; border-radius: 18px; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(148, 163, 184, 0.14); }
      .metric-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0.9rem; }
      @media (max-width: 900px) { .metric-grid { grid-template-columns: 1fr; } }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_api_base() -> str:
    return st.session_state.get("api_base", DEFAULT_API_BASE).rstrip("/")


def api_get(path: str) -> requests.Response:
    return requests.get(f"{get_api_base()}{path}", timeout=120)


def api_post(path: str, payload: Dict[str, Any]) -> requests.Response:
    return requests.post(f"{get_api_base()}{path}", json=payload, timeout=240)


def load_sample_policies() -> Dict[str, str]:
    samples: Dict[str, str] = {}
    if SAMPLE_POLICY_PATH.exists():
        for file in sorted(SAMPLE_POLICY_PATH.glob("*.txt")):
            samples[file.name] = file.read_text(encoding="utf-8")
    return samples


def render_report(report: Dict[str, Any]) -> None:
    st.subheader("Compliance Report")

    c1, c2, c3 = st.columns(3)
    c1.metric("Audit ID", report.get("audit_id", "-"))
    c2.metric("Overall Status", report.get("overall_status", "-"))
    c3.metric("Findings", len(report.get("findings", [])))

    st.markdown("### Executive Summary")
    st.write(report.get("executive_summary", "No summary available."))

    methodology = report.get("methodology", [])
    if methodology:
        st.markdown("### Methodology")
        for item in methodology:
            st.markdown(f"- {item}")

    findings = report.get("findings", [])
    st.markdown("### Findings")
    if not findings:
        st.success("No findings were generated for this run.")
    else:
        for idx, finding in enumerate(findings, start=1):
            with st.expander(f"Finding {idx} · {finding.get('risk_level', 'Unknown')} risk", expanded=True):
                st.write(f"**Policy clause:** {finding.get('policy_clause', '-')}")
                st.write(f"**Violated requirement:** {finding.get('violated_requirement', '-')}")
                st.write(f"**Recommendation:** {finding.get('recommendation', '-')}")
                st.write(f"**Rationale:** {finding.get('rationale', '-')}")

                evidence = finding.get("evidence", [])
                if evidence:
                    st.write("**Supporting evidence:**")
                    for ev in evidence:
                        st.markdown(
                            f"- **{ev.get('title', 'Untitled')}** ({ev.get('source_name', 'unknown')})"
                            f": {ev.get('excerpt', '')}"
                        )

    missing = report.get("missing_information", [])
    if missing:
        st.markdown("### Missing Information")
        for item in missing:
            st.markdown(f"- {item}")

    next_actions = report.get("next_actions", [])
    if next_actions:
        st.markdown("### Next Actions")
        for item in next_actions:
            st.markdown(f"- {item}")


def render_json_download(label: str, payload: Dict[str, Any], filename: str) -> None:
    st.download_button(
        label=label,
        data=json.dumps(payload, indent=2),
        file_name=filename,
        mime="application/json",
    )


def page_header() -> None:
    st.markdown(
        """
        <div class="hero">
          <div class="hero-kicker">Agentic AI Compliance Platform</div>
          <h1>Automated regulatory review for finance teams.</h1>
          <p>
            This dashboard is the polished front-end for the FastAPI + LangGraph backend.
            Ingest regulations, run policy audits, inspect evidence, and complete human approval
            without touching Swagger.
          </p>
          <div class="pill-row">
            <div class="pill">Researcher Agent</div>
            <div class="pill">Auditor Agent</div>
            <div class="pill">Reporting Agent</div>
            <div class="pill">Human-in-the-loop review</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")


with st.sidebar:
    st.header("Connection")
    st.caption("Point this UI at the local FastAPI server running on port 8000.")
    api_base_input = st.text_input("FastAPI base URL", value=st.session_state.get("api_base", DEFAULT_API_BASE))
    st.session_state["api_base"] = api_base_input.rstrip("/")

    if st.button("Check API Health", use_container_width=True):
        try:
            response = api_get("/health")
            response.raise_for_status()
            st.success(f"Backend reachable: {response.json().get('status', 'ok')}")
        except Exception as exc:  # pragma: no cover
            st.error(f"Could not reach backend: {exc}")

    st.divider()
    st.markdown("### Quick Start")
    st.markdown("1. Start FastAPI on port 8000")
    st.markdown("2. Start this Streamlit app on port 8501")
    st.markdown("3. Ingest regulations")
    st.markdown("4. Run an audit")
    st.markdown("5. Submit human approval or rejection")

page_header()

col1, col2, col3 = st.columns(3)
col1.markdown('<div class="section-card"><strong>FastAPI</strong><br/>REST API for compliance workflows and human review.</div>', unsafe_allow_html=True)
col2.markdown('<div class="section-card"><strong>LangGraph</strong><br/>Stateful multi-agent routing with self-correction loops.</div>', unsafe_allow_html=True)
col3.markdown('<div class="section-card"><strong>Pydantic</strong><br/>Strict structured outputs for reports and evidence.</div>', unsafe_allow_html=True)

st.write("")

samples = load_sample_policies()

home_tab, ingest_tab, audit_tab, review_tab, retrieve_tab = st.tabs(
    ["Overview", "Ingest Knowledge", "Run Audit", "Human Review", "Fetch Saved Audit"]
)

with home_tab:
    st.markdown("### What this app does")
    st.write(
        "This UI sits on top of the backend API and lets a non-technical user work through the full "
        "regulatory compliance flow without using Swagger."
    )

    col1, col2, col3 = st.columns(3)
    col1.info("**Researcher Agent** retrieves relevant regulations from the knowledge base.")
    col2.info("**Auditor Agent** checks the uploaded policy against the retrieved rules.")
    col3.info("**Reporter Agent** creates the structured compliance report and pauses for review.")

    st.markdown("### Recommended Demo Flow")
    st.markdown(
        "- Ingest the regulations in `data/regulations`\n"
        "- Run the included sample policy or paste your own policy text\n"
        "- Review the generated report\n"
        "- Approve or reject the audit in the Human Review tab"
    )

with ingest_tab:
    st.subheader("Knowledge Base Ingestion")
    folder_path = st.text_input("Regulations folder path", value=str(REGULATIONS_PATH))

    if st.button("Ingest Regulations", type="primary"):
        try:
            response = api_post("/v1/knowledge/ingest", {"folder_path": folder_path})
            response.raise_for_status()
            payload = response.json()
            st.success("Knowledge base ingestion completed.")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Files", payload.get("ingested_files", 0))
            c2.metric("Chunks", payload.get("ingested_chunks", 0))
            c3.metric("Collection", payload.get("collection_name", "-"))
            c4.metric("Backend", payload.get("backend", "-"))
            render_json_download("Download ingest result", payload, "knowledge_ingest_result.json")
        except requests.HTTPError as exc:
            detail = exc.response.text if exc.response is not None else str(exc)
            st.error(f"Ingestion failed: {detail}")
        except Exception as exc:  # pragma: no cover
            st.error(f"Ingestion failed: {exc}")

with audit_tab:
    st.subheader("Run Policy Audit")

    sample_names = ["Custom policy text"] + list(samples.keys())
    selected_sample = st.selectbox("Choose a sample or paste your own", options=sample_names)

    default_policy = ""
    if selected_sample != "Custom policy text":
        default_policy = samples[selected_sample]

    policy_text = st.text_area(
        "Policy text",
        value=default_policy,
        height=260,
        placeholder="Paste the internal policy draft here...",
    )

    focus_csv = st.text_input(
        "Regulation focus areas (comma separated)",
        value="AML, KYC, Customer Due Diligence, Risk Monitoring",
    )
    max_loops = st.slider("Max research loops", min_value=1, max_value=5, value=2)
    require_human_approval = st.checkbox("Require human approval before finalizing", value=True)
    if require_human_approval:
        st.info("When enabled, the workflow will pause and return a human review request instead of auto-finalizing the report.")
    else:
        st.warning("When disabled, the workflow will finish the audit immediately without a human review pause.")

    if st.button("Run Audit", type="primary"):
        try:
            payload = {
                "policy_text": policy_text,
                "regulation_focus": [item.strip() for item in focus_csv.split(",") if item.strip()],
                "max_research_loops": max_loops,
                "require_human_approval": require_human_approval,
            }
            response = api_post("/v1/audits/run", payload)
            response.raise_for_status()
            result = response.json()
            st.session_state["latest_audit_response"] = result
            st.success(f"Audit run completed. Audit ID: {result.get('audit_id')}")
            st.caption(f"Approval mode: {'human review required' if require_human_approval else 'auto-finalize'}")

            st.markdown("### Workflow Response")
            st.json(result)
            render_json_download(
                "Download workflow response",
                result,
                f"audit_workflow_{result.get('audit_id', 'response')}.json",
            )

            report = result.get("report")
            if not report:
                report = (result.get("human_review_request") or {}).get("report_preview")

            if report:
                render_report(report)
            else:
                st.warning("No report payload was returned.")

        except requests.HTTPError as exc:
            detail = exc.response.text if exc.response is not None else str(exc)
            st.error(f"Audit failed: {detail}")
        except Exception as exc:  # pragma: no cover
            st.error(f"Audit failed: {exc}")

with review_tab:
    st.subheader("Human Review")
    default_audit_id = ""
    latest = st.session_state.get("latest_audit_response")
    if latest:
        default_audit_id = latest.get("audit_id", "")

    audit_id = st.text_input("Audit ID", value=default_audit_id)
    reviewer_name = st.text_input("Reviewer name", value="Compliance Officer")
    decision = st.radio("Decision", options=["approved", "rejected"], horizontal=True)
    reviewer_notes = st.text_area("Reviewer notes", height=120)

    if st.button("Submit Human Review", type="primary"):
        if not audit_id:
            st.error("Audit ID is required.")
        else:
            try:
                payload = {
                    "decision": decision,
                    "reviewer_name": reviewer_name,
                    "reviewer_notes": reviewer_notes or None,
                }
                response = api_post(f"/v1/audits/{audit_id}/human-review", payload)
                response.raise_for_status()
                result = response.json()
                st.success("Human review submitted successfully.")
                st.json(result)
                if result.get("report"):
                    render_report(result["report"])
            except requests.HTTPError as exc:
                detail = exc.response.text if exc.response is not None else str(exc)
                st.error(f"Human review failed: {detail}")
            except Exception as exc:  # pragma: no cover
                st.error(f"Human review failed: {exc}")

with retrieve_tab:
    st.subheader("Fetch Saved Audit")
    lookup_audit_id = st.text_input("Saved audit ID")
    if st.button("Load Audit"):
        if not lookup_audit_id:
            st.error("Please enter an audit ID.")
        else:
            try:
                response = api_get(f"/v1/audits/{lookup_audit_id}")
                response.raise_for_status()
                record = response.json()
                st.json(record)
                if record.get("report"):
                    render_report(record["report"])
                elif record.get("human_review_request", {}).get("report_preview"):
                    render_report(record["human_review_request"]["report_preview"])
            except requests.HTTPError as exc:
                detail = exc.response.text if exc.response is not None else str(exc)
                st.error(f"Could not load audit: {detail}")
            except Exception as exc:  # pragma: no cover
                st.error(f"Could not load audit: {exc}")
