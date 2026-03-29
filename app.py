import streamlit as st
import requests
import json
import pdfplumber
import io
import re
from datetime import datetime

st.set_page_config(
    page_title="Contract-to-Action Agent",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .main { background: #f5f4f0; }
    .block-container { padding: 1.5rem 2rem 3rem; max-width: 1100px; }

    .app-header {
        background: #1a1a18; border-radius: 16px; padding: 22px 28px;
        margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;
    }
    .app-header h1 { font-size: 22px; font-weight: 600; color: #fff; margin: 0 0 3px; }
    .app-header p  { font-size: 12px; color: #9a9a92; margin: 0; }
    .app-header-right { font-size: 10px; color: #5a5a54; text-align: right; font-family: 'DM Mono', monospace; line-height: 1.6; }

    .step-bar { display: flex; gap: 0; margin-bottom: 20px; border-radius: 10px; overflow: hidden; border: 0.5px solid rgba(0,0,0,0.1); }
    .step-item { flex: 1; padding: 10px 14px; background: white; font-size: 11px; font-weight: 600; color: #9a9a92; text-transform: uppercase; letter-spacing: .05em; border-right: 0.5px solid rgba(0,0,0,0.08); }
    .step-item:last-child { border-right: none; }
    .step-item.active { background: #1a1a18; color: white; }
    .step-item.done { background: #e1f5ee; color: #085041; }

    .card { background: white; border-radius: 12px; padding: 18px 20px; margin-bottom: 14px; border: 0.5px solid rgba(0,0,0,0.08); }
    .card-title { font-size: 13px; font-weight: 600; color: #1a1a18; margin-bottom: 10px; }

    .finding-card { background: white; border-radius: 10px; padding: 14px 16px; margin-bottom: 10px; border: 0.5px solid rgba(0,0,0,0.08); }
    .finding-high   { border-left: 3px solid #e24b4a; border-radius: 0 10px 10px 0; }
    .finding-medium { border-left: 3px solid #ef9f27; border-radius: 0 10px 10px 0; }
    .finding-low    { border-left: 3px solid #1d9e75; border-radius: 0 10px 10px 0; }
    .finding-info   { border-left: 3px solid #378add; border-radius: 0 10px 10px 0; }

    .badge { display: inline-block; font-size: 10px; font-weight: 600; padding: 2px 9px; border-radius: 20px; margin-bottom: 5px; letter-spacing: .03em; }
    .badge-high   { background: #fcebeb; color: #a32d2d; }
    .badge-medium { background: #faeeda; color: #633806; }
    .badge-low    { background: #e1f5ee; color: #085041; }
    .badge-info   { background: #e6f1fb; color: #0c447c; }
    .badge-purple { background: #eeedfe; color: #3c3489; }
    .badge-dark   { background: #1a1a18; color: white; }

    .metric-row { display: flex; gap: 8px; margin-bottom: 14px; }
    .metric-box { flex: 1; background: white; border-radius: 10px; padding: 12px; border: 0.5px solid rgba(0,0,0,0.08); text-align: center; }
    .metric-val { font-size: 22px; font-weight: 600; line-height: 1.1; color: #1a1a18; }
    .metric-lbl { font-size: 9px; color: #9a9a92; margin-top: 3px; text-transform: uppercase; letter-spacing: .04em; }

    .email-box { background: #f5f4f0; border-radius: 10px; padding: 16px 18px; font-size: 13px; line-height: 1.75; color: #1a1a18; border: 0.5px solid rgba(0,0,0,0.1); white-space: pre-wrap; font-family: 'DM Sans', sans-serif; }
    .email-field { font-size: 11px; font-weight: 600; color: #9a9a92; text-transform: uppercase; letter-spacing: .05em; margin-bottom: 3px; }

    .section-title { font-size: 10px; font-weight: 600; color: #9a9a92; text-transform: uppercase; letter-spacing: .06em; margin: 16px 0 8px; }

    .clause-box { background: #f5f4f0; border-radius: 8px; padding: 10px 13px; margin-bottom: 6px; font-size: 12px; color: #3a3a38; line-height: 1.55; border-left: 2px solid #d3d1c7; border-radius: 0 8px 8px 0; }
    .clause-label { font-size: 10px; font-weight: 600; color: #9a9a92; text-transform: uppercase; letter-spacing: .04em; margin-bottom: 3px; }

    .overcharge-box { background: #fcebeb; border-radius: 10px; padding: 14px 16px; border: 0.5px solid #f09595; margin-bottom: 10px; }
    .saving-box     { background: #e1f5ee; border-radius: 10px; padding: 14px 16px; border: 0.5px solid #5dcaa5; margin-bottom: 10px; }

    .stButton > button { background: #1a1a18; color: white; border: none; border-radius: 10px; padding: 10px 24px; font-size: 13px; font-weight: 500; font-family: 'DM Sans', sans-serif; width: 100%; }
    .stButton > button:hover { background: #3a3a38; border: none; }
    .stTextInput > div > div > input { border-radius: 10px; border: 0.5px solid rgba(0,0,0,0.15); font-family: 'DM Sans', sans-serif; font-size: 13px; padding: 10px 14px; }
    .stTextArea textarea { border-radius: 10px; border: 0.5px solid rgba(0,0,0,0.15); font-family: 'DM Sans', sans-serif; font-size: 13px; }
    .stFileUploader { border-radius: 10px; }

    .footer { font-size: 10px; color: #9a9a92; text-align: center; margin-top: 28px; font-family: 'DM Mono', monospace; }
    .tag-row { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 6px; }
    .tag { display: inline-block; font-size: 10px; padding: 2px 8px; border-radius: 20px; background: #f0efe9; color: #5a5a54; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_pdf_text(uploaded_file) -> str:
    """Extract text from uploaded PDF using pdfplumber."""
    try:
        pdf_bytes = uploaded_file.read()
        uploaded_file.seek(0)
        text_pages = []
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text() or ""
                # Also try to extract tables
                tables = page.extract_tables()
                table_text = ""
                for table in tables:
                    for row in table:
                        if row:
                            table_text += " | ".join([str(c) if c else "" for c in row]) + "\n"
                text_pages.append(f"--- Page {i+1} ---\n{page_text}\n{table_text}")
        full_text = "\n".join(text_pages)
        return full_text[:12000]  # cap at 12k chars to stay within token limits
    except Exception as e:
        return f"[PDF extraction error: {e}]"


def call_groq(system: str, user: str, groq_key: str, json_mode: bool = True) -> str:
    """Call Groq API and return raw response text."""
    payload = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        "temperature": 0.15,
        "max_tokens": 2000,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    headers = {
        "Authorization": f"Bearer {groq_key}",
        "Content-Type": "application/json",
    }
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers, json=payload, timeout=45
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


def parse_json_safe(raw: str) -> dict:
    """Parse JSON, stripping any accidental markdown fences."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


# ── Step 1: Extract obligations from contract ─────────────────────────────────

def extract_obligations(contract_text: str, groq_key: str) -> dict:
    system = """You are a senior procurement lawyer and supply chain contracts analyst.
Extract structured obligations from supplier contracts. Return JSON only, no preamble.

Return exactly:
{
  "supplier_name": "<name or 'Unknown'>",
  "contract_value": "<e.g. $2.4M annually or 'Not specified'>",
  "contract_duration": "<e.g. 24 months from Jan 2024 or 'Not specified'>",
  "pricing_tiers": [
    {"volume_from": "<e.g. 0>", "volume_to": "<e.g. 999 units>", "unit_price": "<e.g. $45.00>", "description": "<optional>"},
    ...
  ],
  "lead_times": [
    {"item": "<product or service>", "lead_time": "<e.g. 14 business days>", "penalty": "<if any>"}
  ],
  "penalty_clauses": [
    {"trigger": "<what causes the penalty>", "penalty": "<amount or % e.g. 2% per week>", "cap": "<max penalty if stated>"}
  ],
  "price_adjustment_clauses": [
    {"type": "<e.g. Annual CPI adjustment, Raw material index>", "mechanism": "<how it works>", "cap": "<max % if stated>"}
  ],
  "payment_terms": "<e.g. Net 30, 2/10 Net 30>",
  "volume_commitments": "<e.g. minimum 500 units/month or 'None'>",
  "key_obligations": ["<obligation 1>", "<obligation 2>", ...],
  "flags": ["<anything unusual, risky, or worth highlighting>"]
}"""

    user = f"""Extract all obligations from this contract text:

{contract_text}

Return valid JSON only."""

    raw = call_groq(system, user, groq_key, json_mode=True)
    return parse_json_safe(raw)


# ── Step 2: Cross-check invoice against contract ──────────────────────────────

def cross_check_invoice(contract_data: dict, invoice_text: str, groq_key: str) -> dict:
    system = """You are a procurement auditor specialising in contract compliance and overcharge detection.
Given contract terms and an invoice, identify discrepancies, overcharges, and compliance issues.
Return JSON only, no preamble.

Return exactly:
{
  "invoice_summary": {
    "supplier": "<name>",
    "invoice_number": "<number or 'Not found'>",
    "invoice_date": "<date or 'Not found'>",
    "invoice_total": "<total amount>",
    "line_items": [{"description": "<item>", "qty": "<qty>", "unit_price": "<price>", "total": "<total>"}]
  },
  "overcharges": [
    {
      "severity": "HIGH or MEDIUM or LOW",
      "item": "<what was overbilled>",
      "invoiced_amount": "<what they charged>",
      "contract_amount": "<what contract says>",
      "discrepancy": "<difference e.g. $1,200 overcharge>",
      "explanation": "<why this is a discrepancy>"
    }
  ],
  "missed_discounts": [
    {
      "clause": "<which contract clause applies>",
      "potential_saving": "<estimated saving>",
      "explanation": "<what discount was not applied>"
    }
  ],
  "compliance_issues": [
    {
      "severity": "HIGH or MEDIUM or LOW",
      "issue": "<what is non-compliant>",
      "contract_requirement": "<what the contract says>",
      "actual": "<what the invoice shows>"
    }
  ],
  "total_overcharge_estimate": "<total $ amount or range>",
  "total_saving_opportunity": "<total potential savings if all issues resolved>",
  "overall_verdict": "DISPUTE RECOMMENDED or NEGOTIATION RECOMMENDED or MINOR ISSUES or COMPLIANT",
  "verdict_summary": "<2-3 sentence plain English summary for a procurement manager>"
}"""

    user = f"""Contract terms extracted:
{json.dumps(contract_data, indent=2)}

Invoice text:
{invoice_text}

Cross-check and identify all discrepancies. Return JSON only."""

    raw = call_groq(system, user, groq_key, json_mode=True)
    return parse_json_safe(raw)


# ── Step 3: Draft the email ───────────────────────────────────────────────────

def draft_email(contract_data: dict, crosscheck: dict,
                buyer_name: str, buyer_company: str,
                supplier_contact: str, groq_key: str) -> dict:

    verdict = crosscheck.get("overall_verdict", "NEGOTIATION RECOMMENDED")
    tone = "formal dispute" if "DISPUTE" in verdict else "professional negotiation"

    system = f"""You are an expert procurement negotiator drafting a {tone} email to a supplier.
The email must be professional, specific, reference exact contract clauses and amounts, and request clear action.
Return JSON only with keys: "subject", "body"
The body should be a complete, ready-to-send email with proper greeting, paragraphs, and sign-off.
Do not use placeholders like [Your Name] — use the actual names provided."""

    user = f"""Draft a {tone} email based on these findings:

Buyer: {buyer_name} at {buyer_company}
Supplier contact: {supplier_contact}
Supplier: {contract_data.get('supplier_name', 'Supplier')}

Contract highlights:
- Payment terms: {contract_data.get('payment_terms', 'N/A')}
- Pricing tiers: {json.dumps(contract_data.get('pricing_tiers', []))}
- Penalty clauses: {json.dumps(contract_data.get('penalty_clauses', []))}

Overcharges found: {json.dumps(crosscheck.get('overcharges', []))}
Missed discounts: {json.dumps(crosscheck.get('missed_discounts', []))}
Compliance issues: {json.dumps(crosscheck.get('compliance_issues', []))}
Total overcharge estimate: {crosscheck.get('total_overcharge_estimate', 'Under review')}
Verdict: {verdict}

Write a complete professional email. Be specific about amounts and clause references.
Return JSON with keys "subject" and "body" only."""

    raw = call_groq(system, user, groq_key, json_mode=True)
    return parse_json_safe(raw)


# ── Session state init ────────────────────────────────────────────────────────

for key in ["step", "contract_data", "crosscheck_data", "email_data",
            "contract_text", "invoice_text"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "step" else 1


# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="app-header">
  <div>
    <h1>Contract-to-Action Agent</h1>
    <p>Upload a supplier contract + invoice — AI extracts obligations, flags overcharges, drafts your email</p>
  </div>
  <div class="app-header-right">3-step AI agent<br>Groq · Llama 4 · pdfplumber</div>
</div>
""", unsafe_allow_html=True)


# ── Step bar ──────────────────────────────────────────────────────────────────

step = st.session_state["step"]

def step_class(n):
    if n < step: return "done"
    if n == step: return "active"
    return ""

st.markdown(f"""
<div class="step-bar">
  <div class="step-item {step_class(1)}">1 — Upload &amp; Extract</div>
  <div class="step-item {step_class(2)}">2 — Cross-Check Invoice</div>
  <div class="step-item {step_class(3)}">3 — Draft Email</div>
</div>
""", unsafe_allow_html=True)


# ── API key ───────────────────────────────────────────────────────────────────

with st.expander("⚙️  Groq API key — free at console.groq.com", expanded=st.session_state.get("groq_key") is None):
    gk = st.text_input("Groq API key", type="password",
                        value=st.session_state.get("groq_key", ""),
                        placeholder="gsk_...")
    if gk:
        st.session_state["groq_key"] = gk

st.markdown("---")


# ════════════════════════════════════════════════════════════════════════════════
# STEP 1 — Upload & Extract obligations
# ════════════════════════════════════════════════════════════════════════════════

if step == 1:
    st.markdown('<div class="section-title">Upload documents</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card"><div class="card-title">Supplier contract (PDF)</div>',
                    unsafe_allow_html=True)
        contract_file = st.file_uploader("Contract PDF", type=["pdf"], label_visibility="collapsed",
                                          key="contract_upload")
        st.markdown('</div>', unsafe_allow_html=True)
        if contract_file:
            st.success(f"Loaded: {contract_file.name} ({contract_file.size // 1024} KB)")

    with col2:
        st.markdown('<div class="card"><div class="card-title">Recent invoice (PDF)</div>',
                    unsafe_allow_html=True)
        invoice_file = st.file_uploader("Invoice PDF", type=["pdf"], label_visibility="collapsed",
                                         key="invoice_upload")
        st.markdown('</div>', unsafe_allow_html=True)
        if invoice_file:
            st.success(f"Loaded: {invoice_file.name} ({invoice_file.size // 1024} KB)")

    # Demo mode if no files uploaded
    st.markdown('<div class="section-title" style="margin-top:16px">No PDFs yet? Use demo data</div>',
                unsafe_allow_html=True)

    use_demo = st.checkbox("Use built-in demo contract + invoice (automotive OEM supplier scenario)")

    DEMO_CONTRACT = """SUPPLIER AGREEMENT — CONFIDENTIAL

Parties: BrightPath Auto Components GmbH ("Supplier") and Meridian Motors AG ("Buyer")
Contract Number: MM-2024-0471
Effective Date: 1 January 2024 | Duration: 24 months

1. PRICING AND VOLUME TIERS
Unit prices for Part No. MP-7741 (Brake Caliper Assembly) are as follows:
- Tier 1: 0 – 499 units/month: EUR 87.50 per unit
- Tier 2: 500 – 999 units/month: EUR 79.00 per unit  
- Tier 3: 1,000+ units/month: EUR 71.50 per unit
Volume is calculated on a rolling 3-month average.

2. LEAD TIME AND DELIVERY
Standard lead time: 10 business days from confirmed purchase order.
Express orders (< 5 business days): EUR 8.00 surcharge per unit, capped at EUR 4,000 per order.
Late delivery penalty: 1.5% of order value per week of delay, maximum 12%.

3. PAYMENT TERMS
Net 45 days from invoice date. Early payment discount: 2% if paid within 10 days (2/10 Net 45).
Late payment interest: ECB base rate + 5%.

4. PRICE ADJUSTMENT
Annual adjustment on 1 January based on German PPI (Manufacturing) index.
Maximum annual increase: 3.5%. Supplier must provide 90 days written notice.
No retroactive price adjustments permitted.

5. MINIMUM VOLUME COMMITMENT
Buyer commits to minimum 400 units/month averaged over each calendar quarter.
Shortfall penalty: EUR 15.00 per unit below minimum.

6. QUALITY AND RETURNS
Defect rate above 0.5% triggers quality review. Supplier bears full cost of returns
and replacements for defects confirmed by Buyer's quality team.

7. EXCLUSIVITY
Supplier agrees not to supply Part No. MP-7741 to BMW Group or Stellantis during contract term.
"""

    DEMO_INVOICE = """INVOICE

BrightPath Auto Components GmbH
Industriestrasse 44, 70565 Stuttgart, Germany
VAT ID: DE 289 456 721

Bill To: Meridian Motors AG, Munich
Invoice Number: BP-INV-2024-0892
Invoice Date: 15 March 2024
Due Date: 30 April 2024

LINE ITEMS:
---------------------------------------------------------------------------
Part No. MP-7741 (Brake Caliper Assembly)
Quantity: 620 units
Unit Price: EUR 87.50
Subtotal: EUR 54,250.00

Express Delivery Surcharge (order placed 3 business days lead time)
Flat charge: EUR 6,200.00

Price Adjustment (retroactive Jan-Feb 2024, PPI increase 2.1%)
Amount: EUR 2,890.00

---------------------------------------------------------------------------
Subtotal:              EUR 63,340.00
VAT (19%):             EUR 12,034.60
TOTAL DUE:             EUR 75,374.60

Payment: Please remit to IBAN DE89 3704 0044 0532 0130 00
"""

    st.markdown("---")

    if st.button("Extract contract obligations", use_container_width=True):
        groq_key = st.session_state.get("groq_key", "")
        if not groq_key:
            st.warning("Please enter your Groq API key above.")
            st.stop()

        if use_demo:
            contract_text = DEMO_CONTRACT
            invoice_text  = DEMO_INVOICE
        elif contract_file and invoice_file:
            with st.spinner("Reading PDFs..."):
                contract_text = extract_pdf_text(contract_file)
                invoice_text  = extract_pdf_text(invoice_file)
        else:
            st.warning("Please upload both PDFs or check 'Use demo data'.")
            st.stop()

        with st.spinner("Agent step 1/3 — extracting obligations from contract..."):
            try:
                contract_data = extract_obligations(contract_text, groq_key)
                st.session_state["contract_data"]  = contract_data
                st.session_state["contract_text"]  = contract_text
                st.session_state["invoice_text"]   = invoice_text
                st.session_state["step"] = 2
                st.rerun()
            except Exception as e:
                st.error(f"Extraction failed: {e}")


# ════════════════════════════════════════════════════════════════════════════════
# STEP 2 — Show obligations + cross-check invoice
# ════════════════════════════════════════════════════════════════════════════════

elif step == 2:
    cd = st.session_state["contract_data"]

    # Contract summary
    st.markdown('<div class="section-title">Contract obligations extracted</div>', unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    for col, val, lbl in [
        (m1, cd.get("supplier_name", "—"), "Supplier"),
        (m2, cd.get("contract_value", "—"), "Contract value"),
        (m3, cd.get("payment_terms", "—"), "Payment terms"),
        (m4, str(len(cd.get("pricing_tiers", []))) + " tiers", "Pricing tiers"),
    ]:
        col.markdown(f"""
        <div class="metric-box">
          <div class="metric-val" style="font-size:16px;line-height:1.3">{val}</div>
          <div class="metric-lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns(2)

    with left:
        # Pricing tiers
        if cd.get("pricing_tiers"):
            st.markdown('<div class="section-title">Pricing tiers</div>', unsafe_allow_html=True)
            for tier in cd["pricing_tiers"]:
                st.markdown(f"""
                <div class="clause-box">
                  <div class="clause-label">Volume: {tier.get('volume_from','?')} – {tier.get('volume_to','?')}</div>
                  <strong>{tier.get('unit_price','?')}</strong> per unit
                  {' — ' + tier['description'] if tier.get('description') else ''}
                </div>""", unsafe_allow_html=True)

        # Penalty clauses
        if cd.get("penalty_clauses"):
            st.markdown('<div class="section-title">Penalty clauses</div>', unsafe_allow_html=True)
            for p in cd["penalty_clauses"]:
                st.markdown(f"""
                <div class="finding-card finding-medium">
                  <span class="badge badge-medium">Penalty</span>
                  <div style="font-size:12px;color:#3a3a38;margin-top:4px">
                    <strong>Trigger:</strong> {p.get('trigger','?')}<br>
                    <strong>Penalty:</strong> {p.get('penalty','?')}
                    {' (cap: ' + p['cap'] + ')' if p.get('cap') else ''}
                  </div>
                </div>""", unsafe_allow_html=True)

    with right:
        # Lead times
        if cd.get("lead_times"):
            st.markdown('<div class="section-title">Lead times</div>', unsafe_allow_html=True)
            for lt in cd["lead_times"]:
                st.markdown(f"""
                <div class="clause-box">
                  <div class="clause-label">{lt.get('item','?')}</div>
                  {lt.get('lead_time','?')}
                  {' — <em>' + lt['penalty'] + '</em>' if lt.get('penalty') else ''}
                </div>""", unsafe_allow_html=True)

        # Price adjustment clauses
        if cd.get("price_adjustment_clauses"):
            st.markdown('<div class="section-title">Price adjustment clauses</div>', unsafe_allow_html=True)
            for pa in cd["price_adjustment_clauses"]:
                st.markdown(f"""
                <div class="clause-box">
                  <div class="clause-label">{pa.get('type','?')}</div>
                  {pa.get('mechanism','?')}
                  {' — cap: ' + pa['cap'] if pa.get('cap') else ''}
                </div>""", unsafe_allow_html=True)

        # Flags
        if cd.get("flags"):
            st.markdown('<div class="section-title">Flags for attention</div>', unsafe_allow_html=True)
            for flag in cd["flags"]:
                st.markdown(f"""
                <div class="finding-card finding-info">
                  <span class="badge badge-info">Flag</span>
                  <div style="font-size:12px;color:#3a3a38;margin-top:4px">{flag}</div>
                </div>""", unsafe_allow_html=True)

    # Key obligations
    if cd.get("key_obligations"):
        st.markdown('<div class="section-title">Key obligations</div>', unsafe_allow_html=True)
        cols = st.columns(2)
        for i, ob in enumerate(cd["key_obligations"]):
            with cols[i % 2]:
                st.markdown(f'<div class="clause-box">• {ob}</div>', unsafe_allow_html=True)

    st.markdown("---")
    if st.button("Cross-check invoice against contract →", use_container_width=True):
        groq_key = st.session_state.get("groq_key", "")
        with st.spinner("Agent step 2/3 — auditing invoice against contract terms..."):
            try:
                crosscheck = cross_check_invoice(
                    st.session_state["contract_data"],
                    st.session_state["invoice_text"],
                    groq_key
                )
                st.session_state["crosscheck_data"] = crosscheck
                st.session_state["step"] = 3
                st.rerun()
            except Exception as e:
                st.error(f"Cross-check failed: {e}")

    if st.button("← Start over", use_container_width=False):
        for k in ["step","contract_data","crosscheck_data","email_data","contract_text","invoice_text"]:
            st.session_state[k] = None if k != "step" else 1
        st.rerun()


# ════════════════════════════════════════════════════════════════════════════════
# STEP 3 — Findings + email draft
# ════════════════════════════════════════════════════════════════════════════════

elif step == 3:
    cc = st.session_state["crosscheck_data"]
    cd = st.session_state["contract_data"]

    # Verdict banner
    verdict = cc.get("overall_verdict", "UNDER REVIEW")
    verdict_color = {
        "DISPUTE RECOMMENDED":      "#fcebeb",
        "NEGOTIATION RECOMMENDED":  "#faeeda",
        "MINOR ISSUES":             "#e6f1fb",
        "COMPLIANT":                "#e1f5ee",
    }.get(verdict, "#f0efe9")
    verdict_text_color = {
        "DISPUTE RECOMMENDED":      "#a32d2d",
        "NEGOTIATION RECOMMENDED":  "#633806",
        "MINOR ISSUES":             "#0c447c",
        "COMPLIANT":                "#085041",
    }.get(verdict, "#5a5a54")

    st.markdown(f"""
    <div style="background:{verdict_color};border-radius:12px;padding:16px 20px;
                margin-bottom:16px;border:0.5px solid {verdict_text_color}33">
      <div style="font-size:11px;font-weight:600;color:{verdict_text_color};
                  text-transform:uppercase;letter-spacing:.05em;margin-bottom:5px">
        Verdict: {verdict}
      </div>
      <div style="font-size:13px;color:#1a1a18;line-height:1.6">
        {cc.get('verdict_summary','')}
      </div>
    </div>""", unsafe_allow_html=True)

    # Summary metrics
    inv = cc.get("invoice_summary", {})
    m1, m2, m3, m4 = st.columns(4)
    for col, val, lbl in [
        (m1, inv.get("invoice_total", "—"), "Invoice total"),
        (m2, cc.get("total_overcharge_estimate", "—"), "Overcharge estimate"),
        (m3, cc.get("total_saving_opportunity", "—"), "Saving opportunity"),
        (m4, str(len(cc.get("overcharges",[])) + len(cc.get("compliance_issues",[]))), "Issues found"),
    ]:
        col.markdown(f"""
        <div class="metric-box">
          <div class="metric-val" style="font-size:15px;line-height:1.4">{val}</div>
          <div class="metric-lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([1.1, 0.9])

    with left:
        # Overcharges
        if cc.get("overcharges"):
            st.markdown('<div class="section-title">Overcharges detected</div>', unsafe_allow_html=True)
            for oc in cc["overcharges"]:
                sev = oc.get("severity","MEDIUM")
                bc = {"HIGH":"badge-high","MEDIUM":"badge-medium","LOW":"badge-low"}.get(sev,"badge-info")
                fc = {"HIGH":"finding-high","MEDIUM":"finding-medium","LOW":"finding-low"}.get(sev,"finding-info")
                st.markdown(f"""
                <div class="finding-card {fc}">
                  <span class="badge {bc}">{sev}</span>
                  <span style="font-size:12px;font-weight:600;margin-left:6px">{oc.get('item','')}</span>
                  <div style="display:flex;gap:16px;margin-top:7px;font-size:12px">
                    <div><span style="color:#9a9a92">Invoiced:</span> <strong>{oc.get('invoiced_amount','?')}</strong></div>
                    <div><span style="color:#9a9a92">Contract:</span> <strong>{oc.get('contract_amount','?')}</strong></div>
                    <div><span style="color:#a32d2d;font-weight:600">{oc.get('discrepancy','')}</span></div>
                  </div>
                  <div style="font-size:11px;color:#5a5a54;margin-top:5px">{oc.get('explanation','')}</div>
                </div>""", unsafe_allow_html=True)

        # Missed discounts
        if cc.get("missed_discounts"):
            st.markdown('<div class="section-title">Missed discounts / savings</div>', unsafe_allow_html=True)
            for md in cc["missed_discounts"]:
                st.markdown(f"""
                <div class="saving-box">
                  <div style="font-size:12px;font-weight:600;color:#085041;margin-bottom:4px">
                    Potential saving: {md.get('potential_saving','?')}
                  </div>
                  <div style="font-size:11px;color:#3a3a38">{md.get('explanation','')}</div>
                  <div style="font-size:10px;color:#9a9a92;margin-top:4px">Clause: {md.get('clause','')}</div>
                </div>""", unsafe_allow_html=True)

    with right:
        # Compliance issues
        if cc.get("compliance_issues"):
            st.markdown('<div class="section-title">Compliance issues</div>', unsafe_allow_html=True)
            for ci in cc["compliance_issues"]:
                sev = ci.get("severity","MEDIUM")
                bc = {"HIGH":"badge-high","MEDIUM":"badge-medium","LOW":"badge-low"}.get(sev,"badge-info")
                fc = {"HIGH":"finding-high","MEDIUM":"finding-medium","LOW":"finding-low"}.get(sev,"finding-info")
                st.markdown(f"""
                <div class="finding-card {fc}">
                  <span class="badge {bc}">{sev}</span>
                  <div style="font-size:12px;font-weight:600;margin-top:4px">{ci.get('issue','')}</div>
                  <div style="font-size:11px;color:#5a5a54;margin-top:4px">
                    <strong>Contract requires:</strong> {ci.get('contract_requirement','')}<br>
                    <strong>Invoice shows:</strong> {ci.get('actual','')}
                  </div>
                </div>""", unsafe_allow_html=True)

        # Invoice line items
        if inv.get("line_items"):
            st.markdown('<div class="section-title">Invoice line items</div>', unsafe_allow_html=True)
            for item in inv["line_items"]:
                st.markdown(f"""
                <div class="clause-box">
                  <div style="display:flex;justify-content:space-between;align-items:center">
                    <span style="font-weight:500">{item.get('description','')}</span>
                    <span style="font-weight:600;color:#1a1a18">{item.get('total','')}</span>
                  </div>
                  <div style="font-size:11px;color:#9a9a92;margin-top:2px">
                    {item.get('qty','')} × {item.get('unit_price','')}
                  </div>
                </div>""", unsafe_allow_html=True)

    # Email draft section
    st.markdown("---")
    st.markdown('<div class="section-title">Generate dispute / negotiation email</div>', unsafe_allow_html=True)

    e1, e2, e3 = st.columns(3)
    with e1:
        buyer_name = st.text_input("Your name", value="Sarah Chen", placeholder="Your full name")
    with e2:
        buyer_company = st.text_input("Your company", value="Meridian Motors AG", placeholder="Company name")
    with e3:
        supplier_contact = st.text_input("Supplier contact", value="Thomas Braun, BrightPath Auto", placeholder="Name, Company")

    if st.button("Draft email →", use_container_width=True):
        groq_key = st.session_state.get("groq_key", "")
        with st.spinner("Agent step 3/3 — drafting professional email..."):
            try:
                email_data = draft_email(
                    cd, cc, buyer_name, buyer_company, supplier_contact, groq_key
                )
                st.session_state["email_data"] = email_data
                st.rerun()
            except Exception as e:
                st.error(f"Email draft failed: {e}")

    # Show email if generated
    if st.session_state.get("email_data"):
        ed = st.session_state["email_data"]
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="card">
          <div class="email-field">Subject</div>
          <div style="font-size:14px;font-weight:600;margin-bottom:14px;padding:8px 12px;
                      background:#f5f4f0;border-radius:8px">{ed.get('subject','')}</div>
          <div class="email-field">Body</div>
          <div class="email-box">{ed.get('body','').replace('<','&lt;').replace('>','&gt;')}</div>
        </div>""", unsafe_allow_html=True)

        # Copy button
        email_text = f"Subject: {ed.get('subject','')}\n\n{ed.get('body','')}"
        st.download_button(
            "Download email as .txt",
            data=email_text,
            file_name=f"supplier_dispute_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            use_container_width=True
        )

    if st.button("← Start over", use_container_width=False):
        for k in ["step","contract_data","crosscheck_data","email_data","contract_text","invoice_text"]:
            st.session_state[k] = None if k != "step" else 1
        st.rerun()


# ── Footer ────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="footer">
  Contract-to-Action Agent · Streamlit + Groq AI · HEC Paris MiM · IIT Kharagpur
</div>""", unsafe_allow_html=True)
