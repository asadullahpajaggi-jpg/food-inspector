"""Rule-based preliminary decision layer."""
RULES = [
 {"id":"R1","when":"HARAM matched","conclusion":"HARAM","priority":100,"explanation":"A prohibited ingredient was found in the reference records."},
 {"id":"R2","when":"MASHKOOK matched and no HARAM","conclusion":"MASHKOOK","priority":80,"explanation":"At least one recognized ingredient needs source, process, or scholarly confirmation."},
 {"id":"R3","when":"Unknown segments exist and no HARAM or MASHKOOK","conclusion":"UNKNOWN","priority":60,"explanation":"Some list segments could not be identified in the current knowledge base."},
 {"id":"R4","when":"All segments recognized as HALAL","conclusion":"HALAL","priority":40,"explanation":"All recognized items are marked generally permissible in the current reference."},
 {"id":"R5","when":"No useful recognized input","conclusion":"UNKNOWN","priority":10,"explanation":"There is insufficient recognized information."},
]
def decide(parsed):
 matches=parsed.get("matches",[])
 unknown=parsed.get("unknown",[])
 statuses={m.get("status") for m in matches}
 if "HARAM" in statuses: rule=RULES[0]
 elif "MASHKOOK" in statuses: rule=RULES[1]
 elif unknown: rule=RULES[2]
 elif matches and statuses=={"HALAL"}: rule=RULES[3]
 else: rule=RULES[4]
 trace=[
  {"step":1,"type":"Parsing","detail":"Recognized "+str(len(matches))+" match(es) and "+str(len(unknown))+" unknown segment(s)."},
  {"step":2,"type":"Fact evaluation","detail":"Matched statuses: "+(", ".join(sorted(statuses)) if statuses else "none")+"."},
  {"step":3,"type":"Rule firing","detail":rule["id"]+" fired: "+rule["when"]+"."},
  {"step":4,"type":"Conclusion","detail":"Preliminary conclusion: "+rule["conclusion"]+"."}
 ]
 return {"status":rule["conclusion"],"rule_id":rule["id"],"rule_explanation":rule["explanation"],"trace":trace,"priority":rule["priority"]}
