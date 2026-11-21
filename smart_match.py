"""Suggestion-only fuzzy ingredient matching; suggestions never affect decisions."""
from difflib import SequenceMatcher
from matcher import RECORDS, _clean

def suggest_matches(unknown_segments, limit=3, threshold=0.72):
    suggestions=[]
    aliases=[]
    for record in RECORDS:
        for alias in record.get("aliases",[]):
            cleaned=_clean(alias)
            if cleaned and len(cleaned)>2:
                aliases.append((cleaned,record))
    for segment in unknown_segments:
        query=_clean(segment)
        if not query: continue
        ranked=[]
        for alias,record in aliases:
            # Avoid weak matching against very short inputs or unrelated long strings.
            score=SequenceMatcher(None,query,alias).ratio()
            if score>=threshold:
                ranked.append((score,record,alias))
        ranked.sort(key=lambda x:x[0],reverse=True)
        seen=set(); choices=[]
        for score,record,alias in ranked:
            key=record["key"]
            if key in seen: continue
            seen.add(key)
            choices.append({"name":record["name"],"status":record["status"],"reason":record["reason"],"matched_alias":alias,"similarity":round(score,3)})
            if len(choices)>=limit: break
        suggestions.append({"input":segment,"candidates":choices})
    return suggestions
