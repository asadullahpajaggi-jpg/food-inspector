"""Structural audit and deterministic tests for the decision layer and knowledge base."""
from knowledge_base import INGREDIENTS, E_CODES, FACTS
from decision_engine import RULES, decide

VALID_STATUSES = {"HALAL", "HARAM", "MASHKOOK"}

def audit_rules_and_data():
    issues, warnings = [], []
    ids = [r.get("id") for r in RULES]
    if len(ids) != len(set(ids)): issues.append("Duplicate rule IDs.")
    if any(not r.get("id") or not r.get("when") or not r.get("conclusion") for r in RULES): issues.append("Rule has missing required fields.")
    if any(r.get("conclusion") not in VALID_STATUSES | {"UNKNOWN"} for r in RULES): issues.append("Rule conclusion has invalid status.")
    priorities = [r.get("priority") for r in RULES]
    if any(not isinstance(p, int) for p in priorities): issues.append("Rule priority must be an integer.")
    elif len(priorities) != len(set(priorities)): warnings.append("Rule priorities are not unique.")
    for category, records in (("ingredient", INGREDIENTS), ("E-Code", E_CODES)):
        for key, rec in records.items():
            if rec.get("status") not in VALID_STATUSES: issues.append(f"{category} {key}: invalid/missing status.")
            if not rec.get("reason"): warnings.append(f"{category} {key}: missing explanation.")
            if not isinstance(rec.get("aliases", []), list): issues.append(f"{category} {key}: aliases must be a list.")
    fact_ids = [f.get("id") for f in FACTS]
    if len(fact_ids) != len(set(fact_ids)): issues.append("Duplicate fact IDs.")
    if any(not f.get("id") or not f.get("name") for f in FACTS): issues.append("Fact missing ID or name.")
    tests = [
        ("HARAM precedence", {"matches":[{"status":"HALAL"},{"status":"HARAM"}],"unknown":[]}, "HARAM", "R1"),
        ("MASHKOOK precedence", {"matches":[{"status":"HALAL"},{"status":"MASHKOOK"}],"unknown":[]}, "MASHKOOK", "R2"),
        ("Unknown segments", {"matches":[{"status":"HALAL"}],"unknown":["mystery"]}, "UNKNOWN", "R3"),
        ("All halal", {"matches":[{"status":"HALAL"},{"status":"HALAL"}],"unknown":[]}, "HALAL", "R4"),
        ("Empty input", {"matches":[],"unknown":[]}, "UNKNOWN", "R5"),
    ]
    results=[]
    for name, sample, expected, rule_id in tests:
        actual=decide(sample)
        passed=actual.get("status")==expected and actual.get("rule_id")==rule_id
        results.append({"name":name,"expected":expected,"actual":actual.get("status"),"rule":actual.get("rule_id"),"passed":passed})
        if not passed: issues.append(f"Decision test failed: {name}.")
    return {"issues":issues,"warnings":warnings,"tests":results,"rule_count":len(RULES),"fact_count":len(FACTS),"ingredient_count":len(INGREDIENTS),"ecode_count":len(E_CODES),"rules":RULES}

def audit_summary():
    return audit_rules_and_data()
