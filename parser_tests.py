"""Stage 9 parser regression test lab for Food Inspector.

Run with: python parser_tests.py
These tests exercise matcher behavior only; they are not halal rulings.
"""
from matcher import analyze_input

TEST_CASES = [
    {"name":"Plain permitted ingredient", "input":"salt", "expected":"HALAL"},
    {"name":"Explicit prohibited pork", "input":"pork", "expected":"HARAM"},
    {"name":"Pork fat alias", "input":"pork fat", "expected":"HARAM"},
    {"name":"Doubtful gelatin", "input":"gelatin", "expected":"MASHKOOK"},
    {"name":"E-code E441", "input":"E441", "expected":"MASHKOOK"},
    {"name":"Unknown stays unknown", "input":"unlisted mystery ingredient xyz", "expected":"UNKNOWN"},
    {"name":"Mixed halal and haram", "input":"salt, pork", "expected":"HARAM"},
    {"name":"Mixed halal and doubtful", "input":"salt, gelatin", "expected":"MASHKOOK"},
    {"name":"Chicken requires confirmation", "input":"chicken", "expected":"MASHKOOK"},
    {"name":"Label prefix", "input":"Ingredients: salt, sugar", "expected":"MASHKOOK"},
    {"name":"Specific pig gelatin phrase", "input":"porcine gelatin", "expected":"HARAM"},
    {"name":"E471 doubtful", "input":"E471", "expected":"MASHKOOK"},
    {"name":"Recognized list plus unknown", "input":"salt, xyz additive", "expected":"UNKNOWN"},
    {"name":"Empty input", "input":"", "expected":"UNKNOWN"},
]

def run_tests():
    results = []
    for test in TEST_CASES:
        actual = analyze_input(test["input"])["status"]
        results.append({**test, "actual":actual, "passed":actual == test["expected"]})
    return results

if __name__ == "__main__":
    results = run_tests()
    print("Food Inspector Parser Test Lab")
    print("=" * 35)
    for result in results:
        label = "PASS" if result["passed"] else "FAIL"
        print(f'{label}: {result["name"]} | expected={result["expected"]} | actual={result["actual"]}')
    passed = sum(r["passed"] for r in results)
    print(f"\nSummary: {passed}/{len(results)} tests passed")
    if passed != len(results):
        raise SystemExit(1)
