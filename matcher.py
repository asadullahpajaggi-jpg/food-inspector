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
    text = re.sub(r"(?i)\b(ingredients?|ingredient list)\s*[:：]", "", str(raw))
    text = re.sub(r"(?i)\b(may contain|contains traces of)\b", " ", text)
    return [s.strip(" .:-()[]{}") for s in re.split(r"[,;\n\r•]+", text) if s.strip(" .:-()[]{}")]

def analyze_input(raw):
    segments = _segments(raw)
    if not segments:
        segments = [str(raw).strip()]
    matches, unknown, seen_records, seen_unknown = [], [], set(), set()
    for segment in segments:
        normalized = _clean(segment)
        hits = []
        for record in RECORDS:
            for alias in record["aliases"]:
                phrase = _clean(alias)
                if not phrase:
                    continue
                for m in re.finditer(r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])", normalized):
                    hits.append((m.start(), m.end(), len(phrase), record))
        # Prefer the longest phrase. On equal spans, prefer the E-Code record;
        # otherwise prefer the more specific (shorter-key) ingredient record.
        hits.sort(key=lambda h: (h[2], h[3]["type"] == "E-Code", -len(h[3]["key"])), reverse=True)
        selected = []
        for start, end, _, record in hits:
            if any(start < old_end and end > old_start for old_start, old_end, _ in selected):
                continue
            selected.append((start, end, record))
        segment_hits = []
        for _, _, record in selected:
            if record["key"] not in seen_records:
                seen_records.add(record["key"])
                matches.append({k:record[k] for k in ("name","status","reason","type")})
            segment_hits.append(record)
        if not segment_hits:
            residual = re.sub(r"\b(ingredients?|contains|may contain|made with)\b", "", normalized).strip()
            if residual and residual not in seen_unknown:
                seen_unknown.add(residual)
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
