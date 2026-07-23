from __future__ import annotations

from typing import Any, Dict

from workflow import OllamaClient, triage_defect

"""Windows-friendly entry point for the defect triage agent."""


def run_triage(defect: Dict[str, Any], client: OllamaClient | None = None) -> Dict[str, Any]:
    return triage_defect(defect, client=client)


if __name__ == "__main__":
    sample_defect = {
        "bug_description": "Checkout page shows a 500 after payment confirmation.",
        "logs": "Traceback: internal error in checkout confirm endpoint",
        "screenshot_notes": "User sees a blank confirmation screen",
        "additional_comments": "Affects customers in production",
    }
    print(run_triage(sample_defect))
