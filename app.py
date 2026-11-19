import streamlit as st

st.set_page_config(
    page_title="Food Inspector | Halal & E-Code Checker",
    page_icon="🍽️",
    layout="centered",
)

st.markdown("""
<style>
:root { --green: #16764a; }
.stApp { background: linear-gradient(180deg, #f4fbf7 0%, #ffffff 45%); }
.block-container { max-width: 900px; padding-top: 2.2rem; }
.hero {
    padding: 2rem 1.6rem; border-radius: 24px;
    background: linear-gradient(135deg, #0c5135, #16805a);
    color: white; text-align: center; margin-bottom: 1.5rem;
    box-shadow: 0 12px 35px rgba(12,81,53,.15);
}
.hero h1 { color: white; font-size: 2.5rem; margin-bottom: .3rem; }
.hero p { color: #e2f4e9; font-size: 1.05rem; }
.panel {
    background: white; padding: 1.25rem 1.4rem;
    border: 1px solid #e4eee8; border-radius: 18px;
    box-shadow: 0 5px 18px rgba(20,60,40,.05);
}
.note { color: #567066; font-size: .92rem; }
div.stButton > button {
    background: #16764a; color: white; border: 0;
    border-radius: 12px; min-height: 3rem; font-weight: 700;
}
div.stButton > button:hover { background: #105c39; color: white; border: 0; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>🍽️ Food Inspector</h1>
    <p>Halal Food & E-Code Checker</p>
    <p><b>Assalam-o-Alaikum!</b> Welcome to your ingredient checking assistant.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("### 🔎 Check an Ingredient or E-Code")
st.write(
    "Enter a food ingredient, product ingredient list, or E-Code. "
    "The expert system will help assess its Halal status."
)

ingredient_text = st.text_area(
    "Ingredients / E-Codes",
    placeholder="Example: E471, gelatin, whey, chicken, or paste the ingredients list here...",
    height=150,
    key="ingredient_input",
)

st.caption("You can enter one item or paste a complete ingredient list.")

if st.button("🔍 Check Status", use_container_width=True):
    if not ingredient_text.strip():
        st.warning("Bhai, please enter an ingredient or E-Code first.")
    else:
        st.info(
            "The analysis engine is being developed. In the next stage, "
            "this input will be analyzed using our knowledge base and reasoning rules."
        )

st.markdown("---")
st.markdown("### 📘 How Food Inspector will work")
st.markdown("""
- **HALAL:** Ingredients assessed as permissible, subject to relevant conditions.
- **HARAM:** Ingredients identified as impermissible based on established evidence.
- **MASHKOOK:** Ingredients with uncertain sources or differing assessments, requiring caution.
""")

st.markdown("""
<div class="panel">
<b>🕌 A note of caution</b><br><br>
This project is an educational expert system and is not a substitute for a
qualified scholar or Darul Ifta. Ingredient sources, manufacturing processes,
certification, and scholarly opinions may differ. For meat such as beef or
chicken, Halal status also depends on proper Zabiha slaughter.
</div>
""", unsafe_allow_html=True)

st.markdown("<br><p class='note' style='text-align:center'>Food Inspector · Halal Food Awareness & Ingredient Analysis</p>", unsafe_allow_html=True)
