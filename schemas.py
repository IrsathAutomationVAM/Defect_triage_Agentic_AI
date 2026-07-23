from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class DefectInput:
    bug_description: str
    logs: str = ""
    screenshot_notes: str = ""
    additional_comments: str = ""

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "DefectInput":
        return cls(
            bug_description=str(payload.get("bug_description", "")).strip(),
            logs=str(payload.get("logs", "")).strip(),
            screenshot_notes=str(payload.get("screenshot_notes", "")).strip(),
            additional_comments=str(payload.get("additional_comments", "")).strip(),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DefectTriageResult:
    severity: str
    priority: str
    module_impact: str
    suggested_owner: str
    missing_information: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    needs_human_review: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "DefectTriageResult":
        return cls(
            severity=str(payload.get("severity", "medium")).lower(),
            priority=str(payload.get("priority", "p2")).lower(),
            module_impact=str(payload.get("module_impact", "unknown")).strip(),
            suggested_owner=str(payload.get("suggested_owner", "platform team")).strip(),
            missing_information=list(payload.get("missing_information", []) or []),
            confidence_score=float(payload.get("confidence_score", 0.0)),
            needs_human_review=bool(payload.get("needs_human_review", True)),
        )
