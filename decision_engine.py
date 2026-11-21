"""Rule-based preliminary decision layer with an explicit, user-readable reasoning trace."""
RULES = [
 {"id":"R1","when":"HARAM matched","conclusion":"HARAM","priority":100,"explanation":"A prohibited ingredient was found in the reference records."},
 {"id":"R2","when":"MASHKOOK matched and no HARAM","conclusion":"MASHKOOK","priority":80,"explanation":"At least one recognized ingredient needs source, process, or scholarly confirmation."},
 {"id":"R3","when":"Unknown segments exist and no HARAM or MASHKOOK","conclusion":"UNKNOWN","priority":60,"explanation":"Some list segments could not be identified in the current knowledge base."},
 {"id":"R4","when":"All segments recognized as HALAL","conclusion":"HALAL","priority":40,"explanation":"All recognized items are marked generally permissible in the current reference."},
 {"id":"R5","when":"No useful recognized input","conclusion":"UNKNOWN","priority":10,"explanation":"There is insufficient recognized information."},
]

def decide(parsed):
    matches = parsed.get("matches", [])
    unknown = parsed.get("unknown", [])
    statuses = {m.get("status") for m in matches}

    if "HARAM" in statuses:
        rule = RULES[0]
    elif "MASHKOOK" in statuses:
        rule = RULES[1]
    elif unknown:
        rule = RULES[2]
    elif matches and statuses == {"HALAL"}:
        rule = RULES[3]
    else:
        rule = RULES[4]

    match_details = [
        str(m.get("name", "Unnamed item")) + " [" + str(m.get("status", "UNSPECIFIED")) +
        "; " + str(m.get("type", "record")) + "]"
        for m in matches
    ]
    matched_text = "; ".join(match_details) if match_details else "No recognized ingredients or E-Codes."
    unknown_text = "; ".join(str(item) for item in unknown) if unknown else "None."

    trace = [
        {"step":1,"type":"Input parsing","detail":"The input was split into " + str(len(parsed.get("segments", []))) + " segment(s); " + str(len(matches)) + " recognized record(s) and " + str(len(unknown)) + " unidentified segment(s) were reported."},
        {"step":2,"type":"Recognized evidence","detail":matched_text},
        {"step":3,"type":"Unidentified input","detail":unknown_text},
        {"step":4,"type":"Decision rule","detail":"Rule " + rule["id"] + " (priority " + str(rule["priority"]) + ") selected because: " + rule["when"] + ". " + rule["explanation"]},
        {"step":5,"type":"Preliminary conclusion","detail":"The rule layer returned " + rule["conclusion"] + ". This is a knowledge-base-based educational assessment, not certification or a fatwa."}
    ]
    return {"status":rule["conclusion"],"rule_id":rule["id"],"rule_explanation":rule["explanation"],"trace":trace,"priority":rule["priority"]}
