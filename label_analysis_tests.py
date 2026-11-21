"""Focused tests for the Stage 10 label analyzer. Run: python label_analysis_tests.py"""
from label_analysis import analyze_label

CASES = [
    ("salt, sugar", "HALAL", 0),
    ("salt, gelatin", "MASHKOOK", 0),
    ("salt, pork", "HARAM", 0),
    ("salt; may contain pork", "HALAL", 1),
    ("salt; contains traces of gelatin", "HALAL", 1),
    ("may contain pork", "UNKNOWN", 1),
]

if __name__ == "__main__":
    failed = 0
    for raw, expected, advisory_count in CASES:
        result = analyze_label(raw)
        actual = result["decision"]["status"]
        passed = actual == expected and len(result["advisories"]) == advisory_count
        print(("PASS" if passed else "FAIL") + " | " + raw + " | expected=" + expected + " got=" + actual + " | advisory=" + str(len(result["advisories"])))
        failed += not passed
    print("Tests:", len(CASES), "Passed:", len(CASES)-failed, "Failed:", failed)
