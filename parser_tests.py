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
    {"name":"Label prefix", "input":"Ingredients: salt, sugar", "expected":"HALAL"},
    {"name":"Specific pig gelatin phrase", "input":"porcine gelatin", "expected":"HARAM"},
    {"name":"E471 doubtful", "input":"E471", "expected":"MASHKOOK"},
    {"name":"Recognized list plus unknown", "input":"salt, xyz additive", "expected":"UNKNOWN"},
    {"name":"Empty input", "input":"", "expected":"UNKNOWN"},

    {"name":"Specific oil not reduced to generic soy", "input":"Soybean Oil", "expected":"HALAL"},
    {"name":"Specific oil not reduced to generic corn", "input":"Corn Oil", "expected":"HALAL"},
    {"name":"Specific oil not reduced to generic rice", "input":"Rice Bran Oil", "expected":"HALAL"},
    {"name":"Common plant oils recognized", "input":"Olive Oil, Sunflower Oil, Canola Oil, Sesame Oil", "expected":"HALAL"},
    {"name":"Repeated unknowns deduplicated", "input":"E999, e999, E999, Salt", "expected":"UNKNOWN"},
    {"name":"E471 and common name produce one result", "input":"E471, Mono Diglycerides", "expected":"MASHKOOK"},
    {"name":"Tallow is source-sensitive", "input":"Tallow", "expected":"MASHKOOK"},
    {"name":"Beef tallow is not generic beef", "input":"Beef Tallow", "expected":"MASHKOOK"},
    {"name":"Vegetable tallow is not generic vegetables", "input":"Vegetable Tallow", "expected":"HALAL"},
    {"name":"Wine is not duplicated through alcohol beverage alias", "input":"Wine", "expected":"HARAM"},
    {"name":"Mixed doubtful and unknown remains cautious", "input":"Gelatin, E999", "expected":"MASHKOOK"},
    {"name":"Expanded plant oil coverage", "input":"Flaxseed Oil, Walnut Oil, Almond Oil, Hazelnut Oil, Safflower Oil, Cottonseed Oil, Palm Kernel Oil, Macadamia Oil", "expected":"HALAL"},

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
