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

def _segments(raw):
    # Normalize common label wording and punctuation without treating explanatory text as an ingredient.
    text = re.sub(r"(?i)\b(ingredients?|ingredient list)\s*[:：]", "", str(raw))
    text = re.sub(r"(?i)\b(may contain|contains traces of)\b", " ", text)
    return [s.strip(" .:-()[]{}") for s in re.split(r"[,;\n\r•]+", text) if s.strip(" .:-()[]{}")]

def analyze_input(raw):
    segments = _segments(raw)
    if not segments:
        segments = [str(raw).strip()]
    matches, unknown, seen = [], [], set()
    for segment in segments:
        normalized = _clean(segment)
        # Collect the actual alias hit and span to prefer a more specific phrase.
        hits = []
        for record in RECORDS:
            for alias in record["aliases"]:
                phrase = _clean(alias)
                if not phrase:
                    continue
                for m in re.finditer(r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])", normalized):
                    hits.append((m.start(), m.end(), len(phrase), record))
        # Suppress a shorter overlapping hit when a longer matched phrase is more specific.
        selected = []
        for hit in sorted(hits, key=lambda h: (h[2], h[1]-h[0]), reverse=True):
            start, end, length, record = hit
            if any(start >= a and end <= b and (b-a) > (end-start) for a,b,_ in selected):
                continue
            selected.append((start,end,record))
        segment_hits = []
        for _,_,record in selected:
            if record["key"] not in seen:
                seen.add(record["key"])
                matches.append({k:record[k] for k in ("name","status","reason","type")})
            segment_hits.append(record)
        if not segment_hits:
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
