import streamlit as st
from knowledge_base import INGREDIENTS, E_CODES, FACTS, knowledge_base_summary
from matcher import analyze_input
from decision_engine import decide
from rule_audit import audit_rules_and_data
from smart_match import suggest_matches
from label_analysis import analyze_label

st.set_page_config(page_title="Food Inspector | Halal & E-Code Checker", page_icon="🍽️", layout="centered")

st.markdown("""
<style>
/* Theme-aware styling */
.stApp { background: var(--background-color); color: var(--text-color); }
.block-container { max-width: 900px; padding-top: 2rem; }
[data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li, .stCaption, label, [data-testid="stMetricLabel"], [data-testid="stMetricValue"] { color: var(--text-color); }
.hero { padding: 2rem 1.6rem; border-radius: 24px; background: linear-gradient(135deg,#0c5135,#16805a); color: white; text-align:center; margin-bottom:1.5rem; box-shadow:0 12px 35px rgba(12,81,53,.15); }
.hero h1 { color:white !important; font-size:2.5rem; margin-bottom:.3rem; }
.hero p { color:#e2f4e9 !important; }
.panel { background:var(--secondary-background-color); color:var(--text-color); padding:1.2rem 1.4rem; border:1px solid rgba(128,128,128,.25); border-radius:18px; }
.panel b { color:var(--text-color); }
div.stButton > button { background:#16764a; color:white; border:0; border-radius:12px; min-height:3rem; font-weight:700; }
div.stButton > button:hover { background:#105c39; color:white; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>🍽️ Food Inspector</h1>
<p>Halal Food & E-Code Checker</p>
<p><b>Assalam-o-Alaikum!</b> Welcome to your ingredient checking assistant.</p>
</div>
""", unsafe_allow_html=True)

summary = knowledge_base_summary()
m1,m2,m3 = st.columns(3)
m1.metric("Ingredient Records", summary["ingredient_records"])
m2.metric("E-Code Records", summary["e_code_records"])
m3.metric("Knowledge Facts", summary["total_facts"])

st.markdown("### 🔎 Check an Ingredient or E-Code")
st.write("Enter a food ingredient, product ingredient list, or E-Code.")
text_input = st.text_area("Ingredients / E-Codes", placeholder="Example: E471, gelatin, whey, chicken, or paste an ingredient list...", height=140)
st.caption("Enter a single ingredient, an E-Code, or a complete ingredient list.")

if st.button("🔍 Check Status", use_container_width=True):
    if not text_input.strip():
        st.warning("Bhai, please enter an ingredient or E-Code first.")
    else:
        label_report = analyze_label(text_input)
        parsed = label_report["parsed"]
        decision = label_report["decision"]
        result = {**parsed, **decision}
        status = result["status"]
        intro = {
            "HALAL": "Based on the ingredients identified, this ingredient list is generally considered permissible.",
            "HARAM": "This ingredient list contains an ingredient identified as prohibited in the reference.",
            "MASHKOOK": "This ingredient list contains an ingredient whose source or processing needs confirmation.",
            "UNKNOWN": "Some ingredients could not be identified, so the list needs further checking."
        }.get(status, "The ingredient list needs further checking.")
        findings = "; ".join(item["name"] + " (" + item["status"] + "): " + item["reason"] for item in result["matches"])
        if result["unknown"]:
            findings += ("; " if findings else "") + "Unidentified: " + ", ".join(result["unknown"])
        report_text = intro + (" " + findings if findings else "") + " This is an educational reference, not Halal certification or a fatwa."
        st.markdown("## Ingredient assessment")
        st.markdown("### Result")
        import streamlit.components.v1 as components
        import json
        safe_report = json.dumps(report_text)
        html_template = """
        <div style="font-family:sans-serif;position:relative;background:#ffffff;color:#202124;border:1px solid #c8cdd2;border-radius:12px;padding:20px 52px 22px 18px;line-height:1.7;overflow-wrap:anywhere;min-height:150px;">
          <button id="copyResult" title="Copy result" aria-label="Copy result" style="position:absolute;top:10px;right:10px;border:0;background:#f1f3f4;color:#202124;border-radius:8px;padding:6px;cursor:pointer;font-size:18px;">📋</button>
          <div id="resultText" style="color:#202124 !important;font-size:16px;font-weight:400;white-space:normal;"></div><span id="copyMsg" style="font-size:12px;color:#202124;"></span>
        </div>
        <script>
          const report = REPORT_PLACEHOLDER;
          document.getElementById('resultText').textContent=report;
          document.getElementById('copyResult').onclick=async()=>{try{await navigator.clipboard.writeText(report);document.getElementById('copyMsg').textContent='Copied';}catch(e){document.getElementById('copyMsg').textContent='Copy unavailable';}};
        </script>
        """.replace("REPORT_PLACEHOLDER", safe_report)
        components.html(html_template, height=800)
        counts = label_report["counts"]
        c1,c2,c3 = st.columns(3)
        c1.metric("HALAL", counts["HALAL"])
        c2.metric("MASHKOOK", counts["MASHKOOK"])
        c3.metric("HARAM", counts["HARAM"])
        if label_report["advisories"]:
            st.warning("Precautionary label statements detected separately:")
            for advisory in label_report["advisories"]:
                st.write("• " + advisory)
        with st.expander("🧠 Technical reasoning (optional)", expanded=False):
            for step in result["trace"]:
                st.write("**Step " + str(step["step"]) + " · " + step["type"] + "** — " + step["detail"])
            st.caption("Rule fired: " + result["rule_id"] + " · Priority: " + str(result["priority"]))
        if result["unknown"]:
            st.caption("Unidentified items: " + ", ".join(result["unknown"]))
            for suggestion in suggest_matches(result["unknown"]):
                for candidate in suggestion.get("candidates", []):
                    st.write(candidate["name"] + " · " + candidate["status"])
        st.caption("This parser separates typical comma, semicolon and line-separated lists. Complex ingredient descriptions may still require manual review.")

st.markdown("---")
st.markdown("### 📘 Status categories")
st.markdown("""
- **HALAL:** Generally permissible based on available ingredient information.
- **HARAM:** Identified as prohibited.
- **MASHKOOK:** Source, process, or scholarly assessment requires caution.
- **UNKNOWN:** Ingredient could not be matched; more information is needed.
""")
st.markdown("""
<div class="panel">
<b>🕌 A note of caution</b><br><br>
This educational reference is not a fatwa or Halal certification. Sources, processing,
certification, and scholarly opinions may differ. For beef or chicken, Halal status
requires proper Zabiha slaughter and avoidance of prohibited contamination.
</div>
""", unsafe_allow_html=True)
st.markdown("<br><p style='text-align:center;color:#567066'>Food Inspector · Halal Food Awareness & Ingredient Analysis</p>",unsafe_allow_html=True)

with st.expander("Knowledge Base Preview (Developer Preview)"):
    st.write("Reference database counts and example records.")
    st.write("Some classifications are intentionally cautious or source-dependent.")
    st.json({"summary":summary,"example_e_codes":list(E_CODES)[:12],"example_ingredients":list(INGREDIENTS)[:12]})


with st.expander("🛠️ Developer Audit · Stage 6"):
    audit = audit_rules_and_data()
    st.metric("Rules inspected", audit["rule_count"])
    st.metric("Knowledge facts inspected", audit["fact_count"])
    if audit["issues"]:
        st.error("Audit issues detected")
        for issue in audit["issues"]:
            st.write("• " + issue)
    else:
        st.success("No structural errors detected by this audit.")
    if audit["warnings"]:
        st.warning("Warnings")
        for warning in audit["warnings"]:
            st.write("• " + warning)
    st.markdown("#### Automated decision tests")
    for test in audit["tests"]:
        st.write(("✅ PASS" if test["passed"] else "❌ FAIL") + " · " + test["name"] + " · Expected " + test["expected"] + " / Got " + test["actual"] + " (" + test["rule"] + ")")
    st.markdown("#### Rule register")
    for rule in sorted(audit["rules"], key=lambda r: r["priority"], reverse=True):
        st.write(rule["id"] + " · Priority " + str(rule["priority"]) + " · " + rule["when"] + " → " + rule["conclusion"])
        st.caption(rule["explanation"])
