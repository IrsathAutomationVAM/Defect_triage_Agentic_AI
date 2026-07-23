import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent import triage_defect


def test_triage_defect_returns_expected_fields():
    defect = {
        "bug_description": "Checkout button fails for guest users after payment confirmation.",
        "logs": "Error: 500 Internal Server Error at /checkout/confirm",
        "screenshot_notes": "Button remains disabled after payment screen.",
        "additional_comments": "Reported by customer after latest release."
    }

    result = triage_defect(defect)

    assert result["severity"] in {"critical", "high", "medium", "low"}
    assert result["priority"] in {"p0", "p1", "p2", "p3"}
    assert isinstance(result["missing_information"], list)
    assert 0.0 <= result["confidence_score"] <= 1.0
    assert isinstance(result["needs_human_review"], bool)
