import streamlit as st
import google.generativeai as genai
import json
import re
import smtplib
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from PIL import Image
import io
import base64

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Steel Deviation Analyzer",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# CUSTOM CSS — Industrial dark theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&family=Barlow:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Barlow', sans-serif;
    background-color: #0e1117;
    color: #d4d8e2;
}

/* Header */
.main-header {
    background: linear-gradient(135deg, #1a1f2e 0%, #0e1117 60%, #1c2233 100%);
    border-bottom: 2px solid #3a6bc4;
    padding: 2rem 2.5rem 1.5rem;
    margin: -1rem -1rem 2rem -1rem;
    position: relative;
    overflow: hidden;
}
.main-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(
        90deg,
        transparent,
        transparent 40px,
        rgba(58,107,196,0.03) 40px,
        rgba(58,107,196,0.03) 41px
    );
}
.main-header h1 {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.8rem;
    font-weight: 700;
    color: #e8eaf0;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin: 0;
    position: relative;
}
.main-header h1 span {
    color: #3a6bc4;
}
.main-header p {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75rem;
    color: #5a6880;
    letter-spacing: 0.15em;
    margin: 0.3rem 0 0 0;
    position: relative;
}

/* Section label */
.section-label {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    color: #3a6bc4;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    border-left: 3px solid #3a6bc4;
    padding-left: 0.75rem;
    margin: 1.5rem 0 1rem 0;
}

/* Cards */
.card {
    background: #141921;
    border: 1px solid #1e2a3a;
    border-radius: 4px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

/* Status badges */
.badge-approved {
    display: inline-block;
    background: rgba(34,197,94,0.15);
    border: 1px solid #22c55e;
    color: #22c55e;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    font-size: 0.95rem;
    letter-spacing: 0.1em;
    padding: 0.35rem 1.2rem;
    border-radius: 2px;
    text-transform: uppercase;
}
.badge-rejected {
    display: inline-block;
    background: rgba(239,68,68,0.15);
    border: 1px solid #ef4444;
    color: #ef4444;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    font-size: 0.95rem;
    letter-spacing: 0.1em;
    padding: 0.35rem 1.2rem;
    border-radius: 2px;
    text-transform: uppercase;
}

/* Metric box */
.metric-box {
    background: #0d1219;
    border: 1px solid #1e2a3a;
    border-top: 2px solid #3a6bc4;
    padding: 1rem 1.2rem;
    border-radius: 3px;
    text-align: center;
}
.metric-box .label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    color: #4a5568;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}
.metric-box .value {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: #e8eaf0;
    margin-top: 0.2rem;
}

/* Conclusion box */
.conclusion-box {
    background: #0d1219;
    border: 1px solid #1e2a3a;
    border-left: 3px solid #3a6bc4;
    padding: 1.2rem 1.5rem;
    border-radius: 3px;
    font-size: 0.92rem;
    line-height: 1.7;
    color: #b0b8cc;
}
.conclusion-box h4 {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem;
    color: #3a6bc4;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin: 0 0 0.6rem 0;
}

/* Step indicator */
.step-dot {
    display: inline-block;
    width: 24px;
    height: 24px;
    background: #3a6bc4;
    border-radius: 50%;
    text-align: center;
    line-height: 24px;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    font-size: 0.8rem;
    color: white;
    margin-right: 0.5rem;
}

/* Streamlit overrides */
.stButton > button {
    background: #3a6bc4 !important;
    color: white !important;
    border: none !important;
    border-radius: 3px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    padding: 0.5rem 2rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: #2d5299 !important;
    transform: translateY(-1px) !important;
}
.stFileUploader {
    border: 1px dashed #1e2a3a !important;
    border-radius: 4px !important;
    background: #0d1219 !important;
}
div[data-testid="stDataFrame"] {
    border: 1px solid #1e2a3a !important;
    border-radius: 4px !important;
}
.stTextInput > div > input {
    background: #0d1219 !important;
    border: 1px solid #1e2a3a !important;
    color: #d4d8e2 !important;
    border-radius: 3px !important;
    font-family: 'Share Tech Mono', monospace !important;
}
.stTextInput > div > input:focus {
    border-color: #3a6bc4 !important;
    box-shadow: 0 0 0 1px #3a6bc4 !important;
}
.stTextArea > div > textarea {
    background: #0d1219 !important;
    border: 1px solid #1e2a3a !important;
    color: #d4d8e2 !important;
}

/* Divider */
.steel-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #3a6bc4, transparent);
    margin: 2rem 0;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>⚙ Steel <span>Deviation</span> Analyzer</h1>
    <p>// AI-POWERED MATERIAL CERTIFICATION REVIEW SYSTEM // POWERED BY GEMINI 2.5 FLASH</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# GEMINI SETUP
# ─────────────────────────────────────────────
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    GEMINI_READY = True
except Exception:
    GEMINI_READY = False
    st.warning("⚠️ GEMINI_API_KEY no encontrada en st.secrets. Configúrala en Streamlit Cloud → Settings → Secrets.")

# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

def extract_text_from_pdf(uploaded_file) -> str:
    """Extract text from PDF using Gemini's vision capability."""
    try:
        import fitz  # PyMuPDF — fallback text extraction
        pdf_bytes = uploaded_file.read()
        uploaded_file.seek(0)
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except ImportError:
        # If PyMuPDF not available, send PDF pages as images to Gemini
        return _extract_text_via_gemini_vision(uploaded_file)
    except Exception as e:
        return f"[Error extrayendo texto: {e}]"


def _extract_text_via_gemini_vision(uploaded_file) -> str:
    """Send PDF pages as images to Gemini for OCR."""
    try:
        import fitz
        pdf_bytes = uploaded_file.read()
        uploaded_file.seek(0)
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        all_text = []
        for page_num in range(min(len(doc), 10)):  # limit to 10 pages
            page = doc[page_num]
            pix = page.get_pixmap(dpi=150)
            img_bytes = pix.tobytes("png")
            img_b64 = base64.b64encode(img_bytes).decode()
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content([
                {
                    "inline_data": {
                        "mime_type": "image/png",
                        "data": img_b64
                    }
                },
                "Extrae todo el texto de esta imagen de certificado de acero. Incluye todos los valores numéricos, unidades y encabezados exactamente como aparecen."
            ])
            all_text.append(response.text)
        doc.close()
        return "\n\n".join(all_text)
    except Exception as e:
        return f"[Error en extracción visual: {e}]"


def analyze_with_gemini(baseline_text: str, alternatives: list[dict], baseline_code: str, alternative_codes: list[str]) -> dict:
    """
    Send all texts to Gemini and get structured analysis back.
    alternatives: list of {"code": str, "text": str}
    Returns dict with structured data.
    """
    model = genai.GenerativeModel("gemini-2.5-flash")

    alternatives_section = ""
    for i, alt in enumerate(alternatives):
        alternatives_section += f"""
--- ALTERNATIVE #{i+1} ---
Código de parte referencia: {alt['code']}
Texto del certificado:
{alt['text']}
"""

    prompt = f"""
Eres un experto en acero plano, normas de calidad para lámina de acero y certificados de material.
Tu tarea es analizar la desviación de material entre un documento Baseline y uno o varios documentos Alternative.

=== BASELINE ===
Código de parte referencia: {baseline_code}
Texto del certificado:
{baseline_text}

=== ALTERNATIVES ===
{alternatives_section}

=== INSTRUCCIONES ===

1. Extrae los siguientes parámetros generales de CADA documento:
   - descripcion_mercaderia (ej: CINTA FRIA RECOCIDA TENSONIVELADA)
   - norma_calidad (ej: TER/DS1656 TERNIFORM)
   - pieza
   - colada
   - espesor (con unidad, ej: 0.80 mm)
   - ancho (con unidad, ej: 1200 mm)
   - yield_strength (con unidad, ej: 140-270 MPa)
   - tensile_strength (con unidad, ej: 270-370 MPa)
   - elongacion (con unidad, ej: 38%)

2. Extrae la composición química de CADA documento con los elementos: C, Mn, P, S, Si, Al, V, Ti, Cr, Mo, N, B, Cu, Sn, Ca, Ni, Cb.
   Si un elemento no está presente, usa null.

3. Evalúa la desviación según estas reglas de aprobación:
   - NO aprobar si las normas de calidad no son equivalentes.
   - NO aprobar si el espesor Alternative es MENOR que el Baseline.
   - NO aprobar si la composición química tiene MÁS porcentaje de Carbono (C) en Alternative vs Baseline.
   - NO aprobar si es acero fosforizado (P > 0.04%) y el fósforo Alternative es MENOR que el Baseline.

4. Por cada alternative, emite:
   - approved: true/false
   - rejection_reasons: lista de strings (vacía si aprobado)
   - conclusion_general: resumen ejecutivo de la desviación (2-4 oraciones)
   - differences: lista de diferencias principales
   - similarities: lista de similitudes principales

Responde ÚNICAMENTE con un JSON válido con esta estructura exacta:
{{
  "baseline": {{
    "code": "{baseline_code}",
    "general": {{
      "descripcion_mercaderia": "",
      "norma_calidad": "",
      "pieza": "",
      "colada": "",
      "espesor": "",
      "ancho": "",
      "yield_strength": "",
      "tensile_strength": "",
      "elongacion": ""
    }},
    "quimica": {{
      "C": null, "Mn": null, "P": null, "S": null, "Si": null, "Al": null,
      "V": null, "Ti": null, "Cr": null, "Mo": null, "N": null, "B": null,
      "Cu": null, "Sn": null, "Ca": null, "Ni": null, "Cb": null
    }}
  }},
  "alternatives": [
    {{
      "code": "",
      "general": {{
        "descripcion_mercaderia": "",
        "norma_calidad": "",
        "pieza": "",
        "colada": "",
        "espesor": "",
        "ancho": "",
        "yield_strength": "",
        "tensile_strength": "",
        "elongacion": ""
      }},
      "quimica": {{
        "C": null, "Mn": null, "P": null, "S": null, "Si": null, "Al": null,
        "V": null, "Ti": null, "Cr": null, "Mo": null, "N": null, "B": null,
        "Cu": null, "Sn": null, "Ca": null, "Ni": null, "Cb": null
      }},
      "approved": true,
      "rejection_reasons": [],
      "conclusion_general": "",
      "differences": [],
      "similarities": []
    }}
  ]
}}
"""

    response = model.generate_content(prompt)
    raw = response.text.strip()

    # Clean potential markdown code fences
    raw = re.sub(r"^```(?:json)?", "", raw, flags=re.MULTILINE).strip()
    raw = re.sub(r"```$", "", raw, flags=re.MULTILINE).strip()

    return json.loads(raw)


def build_general_table(analysis: dict) -> pd.DataFrame:
    """Build General Parameters DataFrame from analysis dict."""
    params = [
        ("Descripción de la mercadería", "descripcion_mercaderia"),
        ("Norma de calidad", "norma_calidad"),
        ("Pieza", "pieza"),
        ("Colada", "colada"),
        ("Espesor", "espesor"),
        ("Ancho", "ancho"),
        ("Yield Strength", "yield_strength"),
        ("Tensile Strength", "tensile_strength"),
        ("% Elongación", "elongacion"),
    ]

    baseline_code = analysis["baseline"]["code"]
    rows = []
    for label, key in params:
        row = {"Parámetro": label}
        val = analysis["baseline"]["general"].get(key)
        row[f"Baseline\n({baseline_code})"] = val if val else ""
        for alt in analysis["alternatives"]:
            alt_code = alt["code"]
            val_alt = alt["general"].get(key)
            row[f"Alternative\n({alt_code})"] = val_alt if val_alt else ""
        rows.append(row)

    return pd.DataFrame(rows)


def build_chemistry_table(analysis: dict) -> pd.DataFrame:
    """Build Chemical Composition DataFrame from analysis dict."""
    elements = ["C", "Mn", "P", "S", "Si", "Al", "V", "Ti",
                "Cr", "Mo", "N", "B", "Cu", "Sn", "Ca", "Ni", "Cb"]

    baseline_code = analysis["baseline"]["code"]
    rows = []

    # Baseline row
    b_row = {"Material": f"Baseline ({baseline_code})"}
    for el in elements:
        val = analysis["baseline"]["quimica"].get(el)
        b_row[el] = val if val is not None else ""
    rows.append(b_row)

    # Alternative rows
    for alt in analysis["alternatives"]:
        a_row = {"Material": f"Alternative ({alt['code']})"}
        for el in elements:
            val = alt["quimica"].get(el)
            a_row[el] = val if val is not None else ""
        rows.append(a_row)

    df = pd.DataFrame(rows)
    df = df.set_index("Material")
    return df


def send_email(recipient: str, subject: str, body_html: str, analysis: dict):
    """Send analysis results via email using SMTP from st.secrets."""
    try:
        smtp_host = st.secrets.get("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(st.secrets.get("SMTP_PORT", 587))
        smtp_user = st.secrets["SMTP_USER"]
        smtp_pass = st.secrets["SMTP_PASS"]

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = smtp_user
        msg["To"] = recipient

        msg.attach(MIMEText(body_html, "html"))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, recipient, msg.as_string())
        return True, None
    except KeyError as e:
        return False, f"Secret SMTP faltante: {e}. Configura SMTP_USER y SMTP_PASS en st.secrets."
    except Exception as e:
        return False, str(e)


def build_email_html(analysis: dict, general_df: pd.DataFrame, chem_df: pd.DataFrame) -> str:
    """Build a formatted HTML email body."""
    baseline_code = analysis["baseline"]["code"]

    alt_sections = ""
    for alt in analysis["alternatives"]:
        status_color = "#22c55e" if alt["approved"] else "#ef4444"
        status_text = "APROBADO ✔" if alt["approved"] else "RECHAZADO ✖"
        reasons_html = ""
        if alt.get("rejection_reasons"):
            reasons_html = "<ul>" + "".join(f"<li>{r}</li>" for r in alt["rejection_reasons"]) + "</ul>"
        diffs_html = "<ul>" + "".join(f"<li>{d}</li>" for d in alt.get("differences", [])) + "</ul>"
        sims_html = "<ul>" + "".join(f"<li>{s}</li>" for s in alt.get("similarities", [])) + "</ul>"

        alt_sections += f"""
        <h3 style="color:#3a6bc4;">Alternative: {alt['code']}</h3>
        <p><strong>Estado:</strong> <span style="color:{status_color};font-weight:bold;">{status_text}</span></p>
        {"<p><strong>Razones de rechazo:</strong></p>" + reasons_html if reasons_html else ""}
        <p><strong>Conclusión:</strong> {alt.get('conclusion_general','')}</p>
        <p><strong>Diferencias:</strong></p>{diffs_html}
        <p><strong>Similitudes:</strong></p>{sims_html}
        <hr>
        """

    general_html = general_df.to_html(index=False, border=0,
                                       classes="table",
                                       table_id="general_table")
    chem_html = chem_df.to_html(border=0, classes="table", table_id="chem_table")

    return f"""
    <html><head><style>
    body{{font-family:Arial,sans-serif;background:#f5f5f5;color:#222;padding:20px;}}
    h1{{color:#1a3a6e;}} h2{{color:#3a6bc4;}}
    .table{{border-collapse:collapse;width:100%;margin:1rem 0;font-size:12px;}}
    .table td,.table th{{border:1px solid #ccc;padding:6px 10px;}}
    .table th{{background:#1a3a6e;color:white;}}
    </style></head><body>
    <h1>⚙ Steel Deviation Analyzer — Reporte</h1>
    <p><strong>Baseline:</strong> {baseline_code}</p>
    <h2>Parámetros Generales</h2>
    {general_html}
    <h2>Composición Química</h2>
    {chem_html}
    <h2>Resultados por Alternative</h2>
    {alt_sections}
    <p style="color:#888;font-size:11px;">Generado por Steel Deviation Analyzer · Powered by Gemini 2.5 Flash</p>
    </body></html>
    """


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "general_df" not in st.session_state:
    st.session_state.general_df = None
if "chem_df" not in st.session_state:
    st.session_state.chem_df = None

# ─────────────────────────────────────────────
# STEP 1 — INPUT FORM
# ─────────────────────────────────────────────
st.markdown('<div class="section-label"><span class="step-dot">1</span> Carga de Documentos</div>', unsafe_allow_html=True)

with st.container():
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**📄 Baseline**")
        baseline_file = st.file_uploader(
            "Certificado de material de referencia (PDF)",
            type=["pdf"],
            key="baseline_uploader",
            label_visibility="collapsed"
        )
        baseline_code = st.text_input(
            "Código de parte — Baseline",
            placeholder="Ej: P/N 12345-A",
            key="baseline_code"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**📂 Alternative(s)**")
        alternative_files = st.file_uploader(
            "Certificados alternativos (uno o varios PDF)",
            type=["pdf"],
            accept_multiple_files=True,
            key="alt_uploader",
            label_visibility="collapsed"
        )
        alternative_codes_raw = st.text_input(
            "Códigos de parte — Alternatives (separados por coma)",
            placeholder="Ej: P/N 67890-B, P/N 67890-C",
            key="alt_codes"
        )
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
recipient_email = st.text_input(
    "📧 Correo electrónico para envío de resultados",
    placeholder="nombre@empresa.com",
    key="email"
)
st.markdown('</div>', unsafe_allow_html=True)

# Parse alternative codes
alternative_codes = [c.strip() for c in alternative_codes_raw.split(",") if c.strip()] if alternative_codes_raw else []

# ─────────────────────────────────────────────
# VALIDATION + ANALYZE BUTTON
# ─────────────────────────────────────────────
ready = (
    GEMINI_READY
    and baseline_file is not None
    and len(alternative_files) > 0
    and baseline_code.strip() != ""
    and len(alternative_codes) > 0
    and recipient_email.strip() != ""
)

if not ready:
    missing = []
    if not GEMINI_READY: missing.append("API Key de Gemini")
    if not baseline_file: missing.append("PDF Baseline")
    if not alternative_files: missing.append("PDF(s) Alternative")
    if not baseline_code.strip(): missing.append("Código Baseline")
    if not alternative_codes: missing.append("Código(s) Alternative")
    if not recipient_email.strip(): missing.append("Correo electrónico")
    if missing:
        st.markdown(f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.75rem;color:#4a5568;margin:0.5rem 0;">// Pendiente: {" · ".join(missing)}</div>', unsafe_allow_html=True)

st.markdown('<div class="steel-divider"></div>', unsafe_allow_html=True)

col_btn, _ = st.columns([1, 3])
with col_btn:
    analyze_clicked = st.button("⚙ Analizar Desviación", disabled=not ready, use_container_width=True)

# ─────────────────────────────────────────────
# STEP 2 — ANALYSIS
# ─────────────────────────────────────────────
if analyze_clicked and ready:
    with st.spinner("Extrayendo texto de los certificados..."):
        baseline_text = extract_text_from_pdf(baseline_file)

        alternatives_data = []
        for i, alt_file in enumerate(alternative_files):
            code = alternative_codes[i] if i < len(alternative_codes) else f"ALT-{i+1}"
            text = extract_text_from_pdf(alt_file)
            alternatives_data.append({"code": code, "text": text})

    with st.spinner("Analizando con Gemini 2.5 Flash..."):
        try:
            analysis = analyze_with_gemini(
                baseline_text,
                alternatives_data,
                baseline_code,
                alternative_codes
            )
            general_df = build_general_table(analysis)
            chem_df = build_chemistry_table(analysis)

            st.session_state.analysis = analysis
            st.session_state.general_df = general_df
            st.session_state.chem_df = chem_df

        except json.JSONDecodeError as e:
            st.error(f"Error parseando respuesta de Gemini: {e}. Intenta de nuevo.")
            st.stop()
        except Exception as e:
            st.error(f"Error en análisis: {e}")
            st.stop()

# ─────────────────────────────────────────────
# STEP 3 — RESULTS DISPLAY
# ─────────────────────────────────────────────
if st.session_state.analysis is not None:
    analysis = st.session_state.analysis
    general_df = st.session_state.general_df
    chem_df = st.session_state.chem_df

    st.markdown('<div class="steel-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label"><span class="step-dot">2</span> Parámetros Generales</div>', unsafe_allow_html=True)
    st.dataframe(general_df, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-label"><span class="step-dot">3</span> Composición Química</div>', unsafe_allow_html=True)
    st.dataframe(chem_df, use_container_width=True)

    # ── Approval status per alternative ──
    st.markdown('<div class="section-label"><span class="step-dot">4</span> Veredicto por Alternative</div>', unsafe_allow_html=True)

    for alt in analysis["alternatives"]:
        with st.container():
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"**Alternative: `{alt['code']}`**")
                if alt.get("rejection_reasons"):
                    for reason in alt["rejection_reasons"]:
                        st.markdown(f"› {reason}")
            with c2:
                if alt["approved"]:
                    st.markdown('<div class="badge-approved">✔ Aprobado</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="badge-rejected">✖ Rechazado</div>', unsafe_allow_html=True)

        st.markdown("---")

    # ── Conclusions ──
    st.markdown('<div class="section-label"><span class="step-dot">5</span> Conclusiones</div>', unsafe_allow_html=True)

    for alt in analysis["alternatives"]:
        st.markdown(f'<div class="conclusion-box"><h4>Alternative — {alt["code"]}</h4>'
                    f'<strong>Resumen:</strong> {alt.get("conclusion_general","")}<br><br>'
                    f'<strong>Diferencias:</strong><br>' + "<br>".join(f"• {d}" for d in alt.get("differences", [])) +
                    f'<br><br><strong>Similitudes:</strong><br>' + "<br>".join(f"• {s}" for s in alt.get("similarities", [])) +
                    "</div>", unsafe_allow_html=True)
        st.markdown("")

    # ─────────────────────────────────────────────
    # STEP 4 — SEND EMAIL
    # ─────────────────────────────────────────────
    st.markdown('<div class="steel-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label"><span class="step-dot">6</span> Envío de Resultados</div>', unsafe_allow_html=True)

    col_mail, _ = st.columns([1, 3])
    with col_mail:
        if st.button("📧 Enviar por correo", use_container_width=True):
            email_html = build_email_html(analysis, general_df, chem_df)
            baseline_code_val = analysis["baseline"]["code"]
            subject = f"Steel Deviation Report — Baseline: {baseline_code_val}"

            with st.spinner("Enviando correo..."):
                success, error = send_email(
                    st.session_state.get("email_val", recipient_email),
                    subject,
                    email_html,
                    analysis
                )

            if success:
                st.success(f"✅ Reporte enviado a **{recipient_email}** correctamente.")
            else:
                st.error(f"❌ Error enviando correo: {error}")
