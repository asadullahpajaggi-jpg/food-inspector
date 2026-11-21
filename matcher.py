import re
from knowledge_base import INGREDIENTS, E_CODES

def _clean(s):
    return re.sub(r"[^a-z0-9]+", " ", str(s).lower()).strip()

def _phrase_match(text, phrase):
    phrase = _clean(phrase)
    if not phrase:
        return False
    # Match normalized phrases at word boundaries, not inside unrelated words.
    return re.search(r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])", text) is not None

def analyze_input(raw):
    text = _clean(raw)
    found = []
    seen = set()

    for code, data in E_CODES.items():
        candidates = [code, data.get("name", "")] + data.get("aliases", [])
        if any(_phrase_match(text, c) for c in candidates if c):
            key = ("e_code", code)
            if key not in seen:
                seen.add(key)
                found.append({"name": code + " — " + data["name"], "status": data["status"], "reason": data["reason"], "type": "E-Code"})

    for name, data in INGREDIENTS.items():
        candidates = [name.replace("_", " ")] + data.get("aliases", [])
        if any(_phrase_match(text, c) for c in candidates if c):
            key = ("ingredient", name)
            if key not in seen:
                seen.add(key)
                found.append({"name": name.replace("_", " ").title(), "status": data["status"], "reason": data["reason"], "type": "Ingredient/Product"})

    # Deduplicate records whose aliases point to the same E-Code ingredient.
    status = "UNKNOWN"
    if found:
        statuses = {item["status"] for item in found}
        if "HARAM" in statuses:
            status = "HARAM"
        elif "MASHKOOK" in statuses:
            status = "MASHKOOK"
        else:
            status = "HALAL"

    return {"status": status, "matches": found}
