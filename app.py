import streamlit as st
import html
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
.hero { overflow-wrap:anywhere; }
[data-testid="column"] { min-width:0; }
@media (max-width: 640px) { .hero { padding:1.4rem 1rem; border-radius:18px; } .hero h1 { font-size:2rem; } .block-container { padding-top:1rem; } }
div.stButton > button { background:#16764a; color:white; border:0; border-radius:12px; min-height:3rem; font-weight:700; }
div.stButton > button:hover { background:#105c39; color:white; }
</style>
""", unsafe_allow_html=True)


# URL-backed navigation keeps the selected checker mode shareable and supports browser history.
def navigate(page, mode=None):
    st.query_params.clear()
    if page != "home":
        st.query_params["page"] = page
    if mode:
        st.query_params["mode"] = mode
    st.rerun()

page = st.query_params.get("page", "home")
checker_mode = st.query_params.get("mode", "ingredients")
if page not in {"home", "checker", "about", "guide", "how", "developer"}:
    page = "home"
if checker_mode not in {"ingredients", "ecode", "scanner"}:
    checker_mode = "ingredients"

summary = knowledge_base_summary()
should_check = False
text_input = ""

if page == "home":
    st.markdown("""
    <div class="hero">
      <h1>🍽️ Food Inspector</h1>
      <p>Halal Food &amp; E-Code Checker</p>
      <p><b>Assalam-o-Alaikum!</b> Check food ingredients with a clear, educational reference.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Choose your inspection method")
    st.caption("Select one option. All three options use the same Ingredients Checker page.")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 🥗")
        st.markdown("**Ingredient Check**")
        st.caption("Analyze a single ingredient or a complete ingredient list.")
        if st.button("Check Ingredients", key="home_ingredients", use_container_width=True):
            navigate("checker", "ingredients")
    with c2:
        st.markdown("### 🔢")
        st.markdown("**E-Code Check**")
        st.caption("Look up food additive codes such as E471 or E441.")
        if st.button("Check E-Codes", key="home_ecodes", use_container_width=True):
            navigate("checker", "ecode")
    with c3:
        st.markdown("### 📷")
        st.markdown("**Product Scanner**")
        st.caption("Product image, barcode and QR inspection are planned for a future stage.")
        if st.button("Open Scanner", key="home_scanner", use_container_width=True):
            navigate("checker", "scanner")

    st.markdown("---")
    st.markdown("### Explore Food Inspector")
    n1, n2, n3 = st.columns(3)
    with n1:
        if st.button("📘 Ingredient Guide", key="home_guide", use_container_width=True):
            navigate("guide")
    with n2:
        if st.button("⚙️ How It Works", key="home_how", use_container_width=True):
            navigate("how")
    with n3:
        if st.button("ℹ️ About", key="home_about", use_container_width=True):
            navigate("about")

    st.caption("Project maintenance")
    if st.button("🛠️ Developer Dashboard", key="home_developer"):
        navigate("developer")

elif page == "checker":
    back_col, title_col = st.columns([1, 5])
    with back_col:
        if st.button("← Back", key="checker_back"):
            navigate("home")
    mode_titles = {
        "ingredients": ("🥗 Ingredient Checker", "Enter one ingredient or paste a complete ingredient list."),
        "ecode": ("🔢 E-Code Checker", "Enter an E-Code or multiple E-Codes separated by commas."),
        "scanner": ("📷 Product Scanner", "Product scanning will be introduced in a future update.")
    }
    title, description = mode_titles[checker_mode]
    with title_col:
        st.markdown("### " + title)
    st.caption(description)

    if checker_mode == "scanner":
        st.info("Product Scanner is coming soon.")
        st.write("The planned scanner will support product-label images and, where product data is available, barcode or QR-code lookup.")
        st.caption("No product is scanned or verified in this preview.")
    else:
        if checker_mode == "ingredients":
            text_input = st.text_area(
                "Ingredient list",
                placeholder="Example: Sugar, Salt, E471, Gelatin...",
                height=140,
                key="ingredient_input"
            )
            st.caption("You can enter a single ingredient or paste the full ingredient list from a product label.")
            check_label = "🔍 Analyze Ingredients"
        else:
            text_input = st.text_input(
                "Food additive code(s)",
                placeholder="Example: E471 or E471, E441",
                key="ecode_input"
            )
            st.caption("Enter one E-Code or a comma-separated list of E-Codes.")
            check_label = "🔍 Check E-Code"
        should_check = st.button(check_label, use_container_width=True, key="run_checker")
elif page == "about":
    if st.button("← Back", key="about_back"):
        navigate("home")
    st.markdown("## About Food Inspector")
    st.write("Food Inspector is an educational Halal food ingredient and E-Code analysis project. It uses a curated knowledge base, ingredient matching and a rule-based decision layer to explain preliminary results.")
    st.markdown("**Project Developer**")
    st.write("Asad Ullah Muzammil")
    st.markdown("""
    <div class="panel">
      <b>Important Disclaimer</b><br><br>
      Food Inspector is an educational reference only. It is not Halal certification
      and does not issue a fatwa. Ingredient sources, manufacturing processes,
      contamination risks and scholarly assessments may differ. Verify uncertain
      products with a qualified authority or trusted certification body.
    </div>
    """, unsafe_allow_html=True)
elif page == "guide":
    if st.button("← Back", key="guide_back"):
        navigate("home")
    st.markdown("## Ingredient & Status Guide")
    st.markdown("""
    - **HALAL:** Generally permissible based on the available ingredient information.
    - **HARAM:** Identified as prohibited in the current reference records.
    - **MASHKOOK:** Source, processing or scholarly assessment requires confirmation.
    - **UNKNOWN:** The ingredient could not be identified in the current knowledge base.
    """)
    st.info("A status is an educational indication, not product certification. For meat-derived ingredients, source and proper Zabiha slaughter may be essential.")
elif page == "how":
    if st.button("← Back", key="how_back"):
        navigate("home")
    st.markdown("## How Food Inspector Works")
    st.markdown("""
    1. **Input:** The user enters an ingredient, ingredient list or E-Code.
    2. **Matching:** The system compares the text with known ingredient names, aliases and E-Code records.
    3. **Decision:** A rule-based decision layer evaluates recognized statuses and unidentified items.
    4. **Explanation:** The result displays the preliminary assessment, ingredient-level reasons and optional reasoning trace.
    """)
    st.caption("Matching and rule-based reasoning support educational analysis; they do not replace expert review or certification.")
elif page == "developer":
    if st.button("← Back", key="developer_back"):
        navigate("home")
    st.markdown("## Developer Dashboard")
    st.caption("Technical inspection tools are kept separate from the public checker.")


if should_check:
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
        disclaimer = "This is an educational reference, not Halal certification or a fatwa."
        # Build a readable structured report while keeping the copy button's plain-text output.
        status_class = {"HALAL": "halal", "MASHKOOK": "mashkook", "HARAM": "haram", "UNKNOWN": "unknown"}.get(status, "unknown")
        card_parts = [
            '<div class="overall ' + status_class + '"><div class="overall-label">OVERALL ASSESSMENT</div><div class="overall-status">' + html.escape(status) + '</div><div class="overall-intro">' + html.escape(intro) + '</div></div>'
        ]
        plain_parts = [intro]
        for item in result["matches"]:
            item_name = item["name"]
            item_status = item["status"]
            item_reason = item["reason"].rstrip(". ")
            item_class = {"HALAL": "halal", "MASHKOOK": "mashkook", "HARAM": "haram"}.get(item_status, "unknown")
            card_parts.append(
                '<div class="ingredient"><div class="ingredient-heading"><strong>' + html.escape(item_name) +
                '</strong><span class="status ' + item_class + '">' + html.escape(item_status) +
                '</span></div><div class="reason">' + html.escape(item_reason) + '</div></div>'
            )
            plain_parts.append(item_name + " (" + item_status + "): " + item_reason + ".")
        if result["unknown"]:
            unknown_text = ", ".join(result["unknown"])
            card_parts.append(
                '<div class="unknown"><strong>Needs identification</strong><div>' +
                html.escape(unknown_text) + '</div><div class="reason">These ingredients could not be identified in the current reference database.</div></div>'
            )
            plain_parts.append("Other unidentified ingredients also need checking: " + unknown_text + ".")
        card_parts.append('<div class="disclaimer">' + html.escape(disclaimer) + '</div>')
        main_report = "\n\n".join(plain_parts)
        report_text = main_report + "\n\n" + disclaimer
        st.markdown("## Ingredient assessment")
        st.markdown("### Result")
        import streamlit.components.v1 as components
        import json
        safe_report = json.dumps(report_text)
        result_html = """
        <style>
          * { box-sizing:border-box; }
          #card { font-family:Arial,sans-serif; background:#fff; color:#202124; border:1px solid #d8dee5; border-radius:14px; padding:16px; line-height:1.55; overflow-wrap:anywhere; }
          .overall { border-radius:11px; padding:14px; margin-bottom:12px; border:1px solid #d8dee5; background:#f7f9fb; }
          .overall-label { font-size:11px; letter-spacing:1px; font-weight:700; color:#596579; }
          .overall-status { font-size:20px; font-weight:800; margin:3px 0 5px; }
          .overall-intro { font-size:14px; }
          .ingredient { border:1px solid #e1e5ea; border-radius:10px; padding:12px; margin:9px 0; background:#fff; }
          .ingredient-heading { display:flex; align-items:center; justify-content:space-between; gap:10px; flex-wrap:wrap; }
          .ingredient-heading strong { font-size:15px; }
          .status { font-size:11px; font-weight:800; border-radius:20px; padding:4px 9px; }
          .halal { color:#17643b; background:#e7f5ec; }
          .mashkook { color:#805500; background:#fff3d5; }
          .haram { color:#a32222; background:#fdeaea; }
          .unknown { color:#6541a5; background:#f1eafe; }
          .reason { font-size:13px; color:#4b5563; margin-top:7px; }
          .unknown { border:1px solid #e2d5fa; border-radius:10px; padding:12px; margin-top:10px; }
          .unknown strong { display:block; margin-bottom:4px; }
          .disclaimer { border-top:1px solid #e5e7eb; margin-top:14px; padding-top:11px; color:#6b7280; font-size:12px; }
          #copyResult { position:absolute; top:12px; right:12px; border:0; background:#f1f3f4; color:#202124; border-radius:8px; padding:6px 9px; cursor:pointer; font-size:17px; }
          #copyMsg { font-size:12px; color:#17643b; margin-left:8px; }
        </style>
        <div id="card" style="position:relative;padding-top:48px;">
          <button id="copyResult" title="Copy result" aria-label="Copy result">📋</button>
          <div id="resultText">MAIN_HTML_PLACEHOLDER</div>
          <div id="copyMsg"></div>
        </div>
        <script>
          const report = REPORT_PLACEHOLDER;
          const cardHtml = MAIN_HTML_PLACEHOLDER;
          document.getElementById('resultText').innerHTML = cardHtml;
          document.getElementById('copyResult').onclick=async()=>{try{await navigator.clipboard.writeText(report);document.getElementById('copyMsg').textContent='Copied';}catch(e){document.getElementById('copyMsg').textContent='Copy unavailable';}};
        </script>
        """.replace("REPORT_PLACEHOLDER", safe_report).replace("MAIN_HTML_PLACEHOLDER", json.dumps("".join(card_parts)))
        result_height = min(1500, max(420, 220 + len(card_parts) * 105 + sum(len(x["reason"]) for x in result["matches"]) * 0.25))
        components.html(result_html, height=int(result_height))
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

elif page == "developer":
    with st.expander("Knowledge Base Preview", expanded=True):
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

st.markdown("<p style='text-align:center;color:#789084;font-size:12px'>Food Inspector · Halal Food Awareness &amp; Ingredient Analysis</p>", unsafe_allow_html=True)
