"""Repeatable, curated performance evaluation for Food Inspector's matcher and decision layer."""
import time
from matcher import analyze_input
from decision_engine import decide

CASES = [
    {"name":"Single recognized ingredient","input":"Sugar","recognized":["Sugar"],"unknown":[],"status":"HALAL"},
    {"name":"Simple list","input":"Sugar, Salt","recognized":["Sugar","Salt"],"unknown":[],"status":"HALAL"},
    {"name":"Plant oil","input":"Olive Oil","recognized":["Olive Oil"],"unknown":[],"status":"HALAL"},
    {"name":"Unrecognized code","input":"E999","recognized":[],"unknown":["E999"],"status":"UNKNOWN"},
    {"name":"Recognized plus unknown","input":"Sugar, E999","recognized":["Sugar"],"unknown":["E999"],"status":"UNKNOWN"},
    {"name":"Source-dependent gelatin","input":"Gelatin","recognized":["E441 — Gelatin"],"unknown":[],"status":"MASHKOOK"},
    {"name":"E-Code gelatin","input":"E441","recognized":["E441 — Gelatin"],"unknown":[],"status":"MASHKOOK"},
    {"name":"Haram precedence","input":"Sugar, Pork","recognized":["Sugar","Pork"],"unknown":[],"status":"HARAM"},
    {"name":"Mixed uncertainty","input":"Sugar, Gelatin, E999","recognized":["Sugar","E441 — Gelatin"],"unknown":["E999"],"status":"MASHKOOK"},
    {"name":"Whitespace handling","input":"  Sugar   ,   Salt  ","recognized":["Sugar","Salt"],"unknown":[],"status":"HALAL"},
    {"name":"Plant-based fat","input":"Vegetable Tallow","recognized":["Vegetable Tallow"],"unknown":[],"status":"HALAL"},
    {"name":"Oil coverage","input":"Coconut Oil","recognized":["Coconut Oil"],"unknown":[],"status":"HALAL"},
]

def run_performance_evaluation():
    rows=[]
    durations=[]
    for case in CASES:
        start=time.perf_counter()
        parsed=analyze_input(case["input"])
        decision=decide(parsed)
        elapsed=(time.perf_counter()-start)*1000
        durations.append(elapsed)
        got_names=[m["name"] for m in parsed.get("matches",[])]
        expected_names=case["recognized"]
        recognition_ok=(got_names==expected_names)
        unknown_ok=(parsed.get("unknown",[])==case["unknown"])
        decision_ok=(decision.get("status")==case["status"])
        rows.append({"name":case["name"],"input":case["input"],"expected_status":case["status"],"actual_status":decision.get("status"),"recognized_expected":expected_names,"recognized_actual":got_names,"unknown_expected":case["unknown"],"unknown_actual":parsed.get("unknown",[]),"recognition_pass":recognition_ok,"unknown_pass":unknown_ok,"decision_pass":decision_ok,"passed":recognition_ok and unknown_ok and decision_ok,"time_ms":elapsed})
    passed=sum(1 for r in rows if r["passed"])
    return {"rows":rows,"total":len(rows),"passed":passed,"failed":len(rows)-passed,"pass_rate":(passed/len(rows)*100 if rows else 0),"mean_ms":sum(durations)/len(durations) if durations else 0,"min_ms":min(durations) if durations else 0,"max_ms":max(durations) if durations else 0}
