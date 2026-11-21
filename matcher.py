import re
from knowledge_base import INGREDIENTS, E_CODES

def _clean(s):
    return re.sub(r"[^a-z0-9]+", " ", str(s).lower()).strip()

def _phrase_match(text, phrase):
    phrase = _clean(phrase)
    if not phrase:
        return False
    return re.search(r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])", text) is not None

def _records():
    records = []
    for code, data in E_CODES.items():
        records.append({"key":"ec:"+code, "name":code+" — "+data["name"], "status":data["status"], "reason":data["reason"], "type":"E-Code", "aliases":[code,data["name"]]+data.get("aliases",[])})
    for name, data in INGREDIENTS.items():
        records.append({"key":"ing:"+name, "name":name.replace("_"," ").title(), "status":data["status"], "reason":data["reason"], "type":"Ingredient/Product", "aliases":[name.replace("_"," ")]+data.get("aliases",[])})
    return records

RECORDS = _records()

def analyze_input(raw):
    # Split typical ingredient-list punctuation into individual segments.
    segments = [s.strip(" .:-()[]") for s in re.split(r"[,;\n\r•]+", str(raw)) if s.strip(" .:-()[]")]
    if not segments:
        segments = [str(raw).strip()]
    matches, unknown, seen = [], [], set()
    for segment in segments:
        normalized = _clean(segment)
        segment_hits = []
        for record in RECORDS:
            if any(_phrase_match(normalized, alias) for alias in record["aliases"] if alias):
                if record["key"] not in seen:
                    seen.add(record["key"])
                    matches.append({k:record[k] for k in ("name","status","reason","type")})
                segment_hits.append(record)
        if not segment_hits:
            # Remove common label phrases, then flag any remaining segment for review.
            residual = re.sub(r"\b(ingredients?|contains|may contain|made with)\b", "", normalized).strip()
            if residual:
                unknown.append(segment)

    statuses = {item["status"] for item in matches}
    if "HARAM" in statuses:
        overall = "HARAM"
    elif "MASHKOOK" in statuses:
        overall = "MASHKOOK"
    elif unknown:
        overall = "UNKNOWN"
    elif matches:
        overall = "HALAL"
    else:
        overall = "UNKNOWN"

    return {"status":overall, "matches":matches, "unknown":unknown, "segments":segments}
