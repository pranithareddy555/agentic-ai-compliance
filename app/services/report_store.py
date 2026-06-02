from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from app.config import settings
from app.schemas import AuditRecord, ComplianceReport, HumanReviewResponse


class AuditStore:
    def __init__(self, root: Path = None) -> None:
        self.root = root or settings.audit_store_dir
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, audit_id: str) -> Path:
        return self.root / f"{audit_id}.json"

    def save_record(self, record: AuditRecord) -> None:
        record.updated_at = datetime.utcnow()
        self._path(record.audit_id).write_text(
            record.model_dump_json(indent=2),
            encoding="utf-8",
        )

    def load_record(self, audit_id: str) -> AuditRecord:
        path = self._path(audit_id)
        if not path.exists():
            raise FileNotFoundError(f"Audit record not found: {audit_id}")
        return AuditRecord.model_validate_json(path.read_text(encoding="utf-8"))

    def update_human_review(
        self,
        audit_id: str,
        response: HumanReviewResponse,
        report: ComplianceReport,
    ) -> AuditRecord:
        record = self.load_record(audit_id)
        report.reviewer_notes = response.reviewer_notes
        record.status = response.status
        record.report = report
        record.human_review_request = None
        record.state["human_decision"] = response.model_dump(mode="json")
        self.save_record(record)
        return record
