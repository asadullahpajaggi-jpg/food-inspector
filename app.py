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
        # Prepare a compact, copyable report using Streamlit's built-in copy button.
        status = result["status"]
        if status == "HALAL":
            intro = "Based on the ingredients identified and the reference information available, the listed ingredients are generally considered permissible."
        elif status == "HARAM":
            intro = "The ingredient list includes an item identified as prohibited in this reference."
        elif status == "MASHKOOK":
            intro = "The ingredient list includes one or more ingredients whose source or production details need checking before a Halal conclusion can be made."
        else:
            intro = "We could not identify every ingredient in this list. Please check the unidentified items before making a Halal decision."
        report_lines = ["FOOD INSPECTOR — RESULT", "", status, "", intro, "", "Ingredient findings:"]
        for item in result["matches"]:
            report_lines.append("- " + item["name"] + ": " + item["reason"])
        if result["unknown"]:
            report_lines.extend(["", "Not identified:"] + ["- " + item for item in result["unknown"]])
        if label_report["advisories"]:
            report_lines.extend(["", "Precautionary label information:"] + ["- " + item for item in label_report["advisories"]])
        report_lines.extend(["", "This is an educational reference only, not Halal certification or a fatwa. Product-specific sourcing, processing, and contamination details may affect the assessment."])
        copy_report = "\\n".join(report_lines)

        st.markdown("## Ingredient assessment")
        counts = label_report["counts"]
        c1,c2,c3 = st.columns(3)
        c1.metric("HALAL", counts["HALAL"])
        c2.metric("MASHKOOK", counts["MASHKOOK"])
        c3.metric("HARAM", counts["HARAM"])
        st.markdown("### Result")
        st.markdown(intro)
        st.markdown("#### Ingredient findings")
        for item in result["matches"]:
            st.markdown("**" + item["name"] + " — " + item["status"] + "**")
            st.caption(item["reason"])
        if result["unknown"]:
            st.markdown("#### Not identified")
            st.write(", ".join(result["unknown"]))
        st.markdown("#### 📋 Copy report")
        st.code(copy_report, language=None)
        counts = label_report["counts"]
        c1,c2,c3 = st.columns(3)
        c1.metric("Generally Halal matches", counts["HALAL"])
        c2.metric("Doubtful matches", counts["MASHKOOK"])
        c3.metric("Haram matches", counts["HARAM"])
        if label_report["advisories"]:
            st.warning("Precautionary label statements detected separately (not treated as direct ingredients):")
            for advisory in label_report["advisories"]:
                st.write("• " + advisory)
            st.caption("These statements indicate possible exposure or shared-facility risk, not proof that the listed substance is a direct ingredient. Seek product-specific clarification.")
        st.subheader(result["status"])
        st.write(result["rule_explanation"])
        with st.expander("🧠 Technical reasoning (optional)", expanded=False):
            for step in result["trace"]:
                st.write("**Step " + str(step["step"]) + " · " + step["type"] + "** — " + step["detail"])
            st.caption("Rule fired: " + result["rule_id"] + " · Priority: " + str(result["priority"]))
        if result["status"] == "HARAM":
            st.error("A matched prohibited item was found in this reference dataset.")
        elif result["status"] == "MASHKOOK":
            st.warning("At least one matched item needs source, process, or scholarly confirmation. Exercise caution.")
        elif result["status"] == "UNKNOWN":
            st.info("The list contains unrecognized items, or no matching records. Unknown does not mean Halal or Haram.")
        elif result["status"] == "HALAL":
            st.success("All recognized list segments matched entries marked generally permissible in this reference database. This is not certification.")

        if result["matches"]:
            st.markdown("### Matched ingredients")
            for item in result["matches"]:
                with st.expander(f"{item['status']} · {item['name']}", expanded=True):
                    st.caption(item["type"])
                    st.write(item["reason"])
        if result["unknown"]:
            st.markdown("### ⚠️ Items needing identification")
            for item in result["unknown"]:
                st.write(f"• **{item}**")
            st.caption("These segments were not recognized in the current database. Please verify them; they are not automatically classified.")
            smart_suggestions = suggest_matches(result["unknown"])
            for suggestion in smart_suggestions:
                if suggestion["candidates"]:
                    st.markdown("**Possible matches for: " + suggestion["input"] + "**")
                    for candidate in suggestion["candidates"]:
                        st.write(candidate["name"] + " · " + candidate["status"] + " · Similarity " + str(candidate["similarity"]))
                        st.caption(candidate["reason"])
                else:
                    st.caption("No close suggestion found for: " + suggestion["input"])
        if not result["matches"] and not result["unknown"]:
            st.warning("No usable ingredient segments were detected.")
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
