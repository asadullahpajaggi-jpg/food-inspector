"""Structured product-label analysis helpers for Food Inspector."""
import re
from matcher import analyze_input
from decision_engine import decide

_ADVISORY = re.compile(r"(?i)(?:may contain|contains traces of|made in a facility that may process)\s+([^.;\n]+)")

def analyze_label(raw):
    text = str(raw or "").strip()
    advisories = []
    def capture(match):
        advisories.append(match.group(0).strip())
        return " "
    main_text = _ADVISORY.sub(capture, text)
    parsed = analyze_input(main_text)
    decision = decide(parsed)
    counts = {status: sum(1 for item in parsed.get("matches", []) if item.get("status") == status)
              for status in ("HALAL", "MASHKOOK", "HARAM")}
    return {
        "parsed": parsed,
        "decision": decision,
        "counts": counts,
        "advisories": advisories,
        "summary": ("Found " + str(len(parsed.get("matches", []))) + " recognized ingredient(s), "
                    + str(len(parsed.get("unknown", []))) + " unidentified segment(s)."),
    }
