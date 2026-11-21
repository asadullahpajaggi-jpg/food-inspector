import streamlit as st
from knowledge_base import INGREDIENTS, E_CODES, FACTS, knowledge_base_summary
from matcher import analyze_input

st.set_page_config(page_title="Food Inspector | Halal & E-Code Checker", page_icon="🍽️", layout="centered")

st.markdown("""
<style>
.stApp { background: linear-gradient(180deg,#f4fbf7 0%,#ffffff 45%); }
.block-container { max-width: 900px; padding-top: 2rem; }
.hero { padding: 2rem 1.6rem; border-radius: 24px; background: linear-gradient(135deg,#0c5135,#16805a); color: white; text-align:center; margin-bottom:1.5rem; box-shadow:0 12px 35px rgba(12,81,53,.15); }
.hero h1 { color:white; font-size:2.5rem; margin-bottom:.3rem; }
.hero p { color:#e2f4e9; }
.panel { background:white; padding:1.2rem 1.4rem; border:1px solid #e4eee8; border-radius:18px; }
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
        result = analyze_input(text_input)
        st.markdown("## Preliminary assessment")
        st.subheader(result["status"])
        if not result["matches"]:
            st.warning("No recognized ingredient or E-Code was found. This does not mean the product is Halal or Haram. Please check the spelling or ask a qualified scholar.")
        else:
            st.write(f"Found {len(result['matches'])} matching reference item(s):")
            for item in result["matches"]:
                with st.expander(f"{item['status']} · {item['name']}", expanded=True):
                    st.caption(item["type"])
                    st.write(item["reason"])
            if result["status"] == "HARAM":
                st.error("At least one matched item is marked HARAM in this reference database.")
            elif result["status"] == "MASHKOOK":
                st.warning("At least one matched item needs source, process, or scholarly confirmation. Exercise caution.")
            elif result["status"] == "HALAL":
                st.success("All recognized items in this input are marked generally permissible in this reference database. This is not certification.")
        st.caption("Matching is based on known names and aliases. It does not yet verify every word in an ingredient list, product formulation, or cross-contamination.")

st.markdown("---")
st.markdown("### 📘 Status categories")
st.markdown("""
- **HALAL:** Generally permissible based on available ingredient information.
- **HARAM:** Identified as prohibited.
- **MASHKOOK:** Source, process, or scholarly assessment requires caution.
- **UNKNOWN:** No recognized matching reference was found.
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
