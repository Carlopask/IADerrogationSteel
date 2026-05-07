import streamlit as st
import google.generativeai as genai
import json
import re
import smtplib
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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
    background: repeating-linear-gradient(90deg,transparent,transparent 40px,rgba(58,107,196,0.03) 40px,rgba(58,107,196,0.03) 41px);
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
.main-header h1 span { color: #3a6bc4; }
.main-header p {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75rem;
    color: #5a6880;
    letter-spacing: 0.15em;
    margin: 0.3rem 0 0 0;
    position: relative;
}
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
.card {
    background: #141921;
    border: 1px solid #1e2a3a;
    border-radius: 4px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
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
.diag-ok {
    background: rgba(34,197,94,0.08);
    border: 1px solid #1a4a2e;
    border-left: 3px solid #22c55e;
    border-radius: 3px;
    padding: 0.5rem 0.8rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    color: #4ade80;
    margin: 0.3rem 0;
}
.diag-warn {
    background: rgba(234,179,8,0.08);
    border: 1px solid #3a2e00;
    border-left: 3px solid #eab308;
    border-radius: 3px;
    padding: 0.5rem 0.8rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    color: #fde047;
    margin: 0.3rem 0;
}
.diag-err {
    background: rgba(239,68,68,0.08);
    border: 1px solid #3a0e0e;
    border-left: 3px solid #ef4444;
    border-radius: 3px;
    padding: 0.5rem 0.8rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    color: #f87171;
    margin: 0.3rem 0;
}
.conclusion-box {
    background: #0d1219;
    border: 1px solid #1e2a3a;
    border-left: 3px solid #3a6bc4;
    padding: 1.2rem 1.5rem;
    border-radius: 3px;
    font-size: 0.92rem;
    line-height: 1.7;
    color: #b0b8cc;
    margin-bottom: 1rem;
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
.step-dot {
    display: inline-block;
    width: 24px; height: 24px;
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
.steel-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #3a6bc4, transparent);
    margin: 2rem 0;
}
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
.stButton > button:hover { background: #2d5299 !important; }
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


# ─────────────────────────────────────────────────────────────────────────────
# PDF EXTRACTION — ESTRATEGIA EN 3 CAPAS
#
#  Capa 1: PyMuPDF extracción de texto nativo
#          → Rápido. Funciona en PDFs con texto real (vectorial).
#          → Falla en PDFs escaneados (imágenes) o PDFs con tablas gráficas.
#
#  Capa 2: PyMuPDF renderiza páginas como imagen → Gemini Vision (OCR)
#          → Para PDFs escaneados donde la Capa 1 devuelve texto vacío o muy corto.
#          → Alta resolución (200 dpi) para mejor precisión en números pequeños.
#
#  Capa 3: Gemini File API — sube el PDF binario directamente a Gemini
#          → Para PDFs complejos que ni Capa 1 ni Capa 2 resuelven bien.
#          → Gemini puede interpretar la estructura del PDF nativo.
#
#  Umbral: si el texto extraído tiene menos de MIN_USEFUL_CHARS caracteres,
#  se considera fallido y se pasa a la siguiente capa.
# ─────────────────────────────────────────────────────────────────────────────

MIN_USEFUL_CHARS = 200


def _layer1_native_text(pdf_bytes: bytes) -> str:
    """Capa 1: Texto nativo con PyMuPDF."""
    try:
        import fitz
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        pages_text = []
        for page in doc:
            pages_text.append(page.get_text())
        doc.close()
        return "\n".join(pages_text).strip()
    except ImportError:
        return ""
    except Exception:
        return ""


def _layer2_vision_ocr(pdf_bytes: bytes) -> str:
    """
    Capa 2: Cada página se convierte en imagen PNG de alta resolución
    y se envía a Gemini Vision para OCR especializado en certificados de acero.
    """
    try:
        import fitz
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        model = genai.GenerativeModel("gemini-2.5-flash")
        pages_text = []
        for page_num in range(min(len(doc), 8)):
            pix = doc[page_num].get_pixmap(dpi=200)
            img_b64 = base64.b64encode(pix.tobytes("png")).decode()
            response = model.generate_content([
                {
                    "inline_data": {
                        "mime_type": "image/png",
                        "data": img_b64
                    }
                },
                (
                    "Eres un experto en certificados de calidad de acero plano. "
                    "Extrae TODO el contenido visible en esta imagen exactamente como aparece: "
                    "encabezados de tablas, valores numéricos con sus decimales, unidades de medida, "
                    "símbolos químicos y sus porcentajes, normas de calidad, números de colada, "
                    "dimensiones (espesor, ancho), propiedades mecánicas (yield, tensile, elongación), "
                    "y cualquier código, referencia o número de parte. "
                    "Si hay tablas, extrae cada celda con su encabezado correspondiente. "
                    "Responde ÚNICAMENTE con el texto extraído, sin comentarios ni explicaciones."
                )
            ])
            pages_text.append(f"--- Página {page_num + 1} ---\n{response.text.strip()}")
        doc.close()
        return "\n\n".join(pages_text)
    except ImportError:
        return ""
    except Exception:
        return ""


def _layer3_file_api(pdf_bytes: bytes) -> str:
    """
    Capa 3: Sube el PDF a Gemini File API y solicita extracción completa.
    Gemini lee el PDF de forma nativa, incluyendo tablas y estructura.
    """
    try:
        import tempfile, os, time
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name

        uploaded = genai.upload_file(path=tmp_path, mime_type="application/pdf")

        # Esperar hasta que el archivo esté activo (máx 20 segundos)
        for _ in range(10):
            f = genai.get_file(uploaded.name)
            if f.state.name == "ACTIVE":
                break
            time.sleep(2)

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content([
            uploaded,
            (
                "Eres un experto en certificados de calidad de acero plano. "
                "Extrae TODA la información de este certificado de material: "
                "tipo de producto, norma de calidad, número de parte/pieza, número de colada, "
                "dimensiones (espesor y ancho con unidades), propiedades mecánicas "
                "(yield strength, tensile strength, elongación con unidades), "
                "composición química completa (C, Mn, P, S, Si, Al, V, Ti, Cr, Mo, N, B, Cu, Sn, Ca, Ni, Cb), "
                "y cualquier referencia, código o nota relevante. "
                "Presenta los datos de forma estructurada con encabezados claros. "
                "Responde ÚNICAMENTE con los datos extraídos, sin comentarios adicionales."
            )
        ])

        os.unlink(tmp_path)
        try:
            genai.delete_file(uploaded.name)
        except Exception:
            pass

        return response.text.strip()
    except Exception as e:
        return f"[Capa3 error: {e}]"


def extract_pdf_with_diagnosis(uploaded_file) -> tuple:
    """
    Extrae texto de un PDF usando estrategia en 3 capas.
    Retorna (texto_extraído: str, diagnóstico: dict).
    """
    filename = uploaded_file.name
    pdf_bytes = uploaded_file.read()
    uploaded_file.seek(0)

    diag = {
        "filename": filename,
        "method": None,
        "chars": 0,
        "warning": None,
        "ok": False,
    }

    # ── Capa 1 ──
    text = _layer1_native_text(pdf_bytes)
    if len(text) >= MIN_USEFUL_CHARS:
        diag.update(method="Texto nativo (PyMuPDF)", chars=len(text), ok=True)
        return text, diag

    # ── Capa 2 ──
    diag["warning"] = "Texto nativo insuficiente → usando OCR visual por páginas."
    text = _layer2_vision_ocr(pdf_bytes)
    if len(text) >= MIN_USEFUL_CHARS:
        diag.update(method="OCR visual — Gemini Vision", chars=len(text), ok=True)
        return text, diag

    # ── Capa 3 ──
    diag["warning"] = "OCR visual insuficiente → usando Gemini File API."
    text = _layer3_file_api(pdf_bytes)
    diag["method"] = "Gemini File API"
    diag["chars"] = len(text)
    if len(text) >= MIN_USEFUL_CHARS:
        diag["ok"] = True
    else:
        diag["ok"] = False
        diag["warning"] = (
            "No se pudo extraer texto suficiente con ningún método. "
            "El PDF puede estar protegido, dañado o ser de muy baja resolución."
        )
    return text, diag


def render_diag(diag: dict):
    """Muestra el estado de extracción de un PDF en la UI."""
    fname = diag["filename"]
    method = diag.get("method", "—")
    chars = diag.get("chars", 0)
    warn = diag.get("warning")

    if diag["ok"] and not warn:
        st.markdown(
            f'<div class="diag-ok">✔ <b>{fname}</b> · {method} · {chars:,} caracteres extraídos</div>',
            unsafe_allow_html=True
        )
    elif diag["ok"] and warn:
        st.markdown(
            f'<div class="diag-warn">⚠ <b>{fname}</b> · {method} · {chars:,} chars<br>{warn}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="diag-err">✖ <b>{fname}</b> · {warn}</div>',
            unsafe_allow_html=True
        )


# ─────────────────────────────────────────────────────────────────────────────
# GEMINI ANALYSIS
#
# Mejoras en el prompt para el problema de "código no coincide":
#  1. El código es REFERENCIA DE BÚSQUEDA, no un filtro estricto.
#  2. Si no hay coincidencia exacta → usar la info más similar del documento.
#  3. Gemini reporta en "codigo_encontrado" qué referencia usó realmente.
#  4. Instrucción explícita: NUNCA dejar campos vacíos si el dato existe.
# ─────────────────────────────────────────────────────────────────────────────

def analyze_with_gemini(
    baseline_text: str,
    alternatives: list,
    baseline_code: str,
) -> dict:
    model = genai.GenerativeModel("gemini-2.5-flash")

    alternatives_section = ""
    for i, alt in enumerate(alternatives):
        alternatives_section += f"""
--- ALTERNATIVE #{i+1} ---
Nombre del archivo PDF (será el título en las tablas): {alt['code']}
Texto completo del certificado:
{alt['text']}
"""

    prompt = f"""
Eres un experto en acero plano, lámina de acero, normas de calidad y certificados de material.
Analiza la desviación de material entre el certificado Baseline y los certificados Alternative.

=== BASELINE ===
Código de parte (proporcionado por el usuario): {baseline_code}
Texto del certificado:
{baseline_text}

=== ALTERNATIVES ===
{alternatives_section}

════════════════════════════════════════
REGLAS DE EXTRACCIÓN (MUY IMPORTANTE)
════════════════════════════════════════

Para el BASELINE:
• El código "{baseline_code}" es una REFERENCIA DE BÚSQUEDA, no un filtro estricto.
• Si encuentras ese código exacto en el documento → úsalo para localizar los datos de esa pieza.
• Si NO lo encuentras exacto → busca el código o referencia más similar en el documento
  (mismos dígitos parciales, mismo prefijo, referencia adyacente en la misma tabla).
• Si no hay ninguna coincidencia → extrae los datos del bloque de información principal.
• Registra en "codigo_encontrado" exactamente qué código o referencia localizaste en el documento.

Para cada ALTERNATIVE:
• El campo "code" ya contiene el nombre del archivo PDF — úsalo TAL CUAL en el JSON de respuesta.
• NO cambies el valor de "code"; es el identificador que aparecerá en las tablas.
• Extrae TODA la información disponible en el certificado, sin filtrar por ningún código específico.
• Si el certificado tiene varias piezas o coladas, extrae los datos de la sección principal o más destacada.

Para TODOS los documentos:
• NUNCA dejes un campo vacío si el dato existe en el documento.
• Si un valor aparece como rango (ej: 0.02-0.06), usa el valor máximo.
• Si aparece como "máx. X" o "<X", usa X como valor numérico.

════════════════════════════════════════
DATOS A EXTRAER DE CADA DOCUMENTO
════════════════════════════════════════

1. PARÁMETROS GENERALES:
   - descripcion_mercaderia: tipo de acero/producto (ej: CINTA FRIA RECOCIDA TENSONIVELADA, HR PICKLED, CR FULL HARD)
   - norma_calidad: norma o especificación del material (ej: TER/DS1656, EN 10130, ASTM A1008, JIS G3141)
   - pieza: número de pieza o parte encontrado en el documento
   - colada: número de colada, heat number o número de lote
   - espesor: con unidad exacta (ej: 0.80 mm, 1.2 mm)
   - ancho: con unidad exacta (ej: 1200 mm, 48 in)
   - yield_strength: límite de fluencia con unidad (ej: 140-270 MPa, o valor real medido)
   - tensile_strength: resistencia a la tracción con unidad
   - elongacion: porcentaje de elongación (ej: 38%, A80=40%)

2. COMPOSICIÓN QUÍMICA:
   Elementos: C, Mn, P, S, Si, Al, V, Ti, Cr, Mo, N, B, Cu, Sn, Ca, Ni, Cb
   • Solo valores numéricos (sin el símbolo %).
   • Si el elemento no aparece en el documento, usa null.

════════════════════════════════════════
REGLAS DE APROBACIÓN (solo para Alternatives)
════════════════════════════════════════

Rechazar si alguna de estas condiciones es verdadera:
  a) Las normas de calidad no son equivalentes (familias o especificaciones distintas).
  b) El espesor del Alternative es MENOR que el espesor del Baseline.
  c) El contenido de Carbono (C) en Alternative es 30% MAYOR que en Baseline.
  d) Es acero fosforizado (P > 0.04% en cualquiera) Y el fósforo Alternative es MENOR que el Baseline.

Por cada Alternative:
  - approved: true / false
  - rejection_reasons: lista de strings con la razón específica (lista vacía si aprobado)
  - conclusion_general: 2-4 oraciones resumiendo la desviación
  - differences: lista de diferencias concretas entre Alternative y Baseline
  - similarities: lista de similitudes relevantes

════════════════════════════════════════
FORMATO DE RESPUESTA
════════════════════════════════════════

Responde ÚNICAMENTE con JSON válido. Sin texto adicional. Sin bloques markdown (sin ```).

{{
  "baseline": {{
    "code": "{baseline_code}",
    "codigo_encontrado": "",
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
      "code": "(usa exactamente el nombre del archivo que se proporcionó)",
      "codigo_encontrado": "",
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
    raw = re.sub(r"^```(?:json)?[\s]*", "", raw, flags=re.MULTILINE).strip()
    raw = re.sub(r"[\s]*```$", "", raw, flags=re.MULTILINE).strip()

    return json.loads(raw)


# ─────────────────────────────────────────────
# TABLE BUILDERS
# ─────────────────────────────────────────────

def build_general_table(analysis: dict) -> pd.DataFrame:
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
        row[f"Baseline ({baseline_code})"] = val if val else ""
        for alt in analysis["alternatives"]:
            val_alt = alt["general"].get(key)
            row[f"Alternative ({alt['code']})"] = val_alt if val_alt else ""
        rows.append(row)
    return pd.DataFrame(rows)


def build_chemistry_table(analysis: dict) -> pd.DataFrame:
    elements = ["C", "Mn", "P", "S", "Si", "Al", "V", "Ti",
                "Cr", "Mo", "N", "B", "Cu", "Sn", "Ca", "Ni", "Cb"]
    rows = []
    b_row = {"Material": f"Baseline ({analysis['baseline']['code']})"}
    for el in elements:
        val = analysis["baseline"]["quimica"].get(el)
        b_row[el] = val if val is not None else ""
    rows.append(b_row)
    for alt in analysis["alternatives"]:
        a_row = {"Material": f"Alternative ({alt['code']})"}
        for el in elements:
            val = alt["quimica"].get(el)
            a_row[el] = val if val is not None else ""
        rows.append(a_row)
    return pd.DataFrame(rows).set_index("Material")


# ─────────────────────────────────────────────
# EMAIL
# ─────────────────────────────────────────────

def send_email(recipient: str, subject: str, body_html: str):
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
    baseline_code = analysis["baseline"]["code"]
    alt_sections = ""
    for alt in analysis["alternatives"]:
        status_color = "#22c55e" if alt["approved"] else "#ef4444"
        status_text = "APROBADO ✔" if alt["approved"] else "RECHAZADO ✖"
        reasons_html = ("<ul>" + "".join(f"<li>{r}</li>" for r in alt["rejection_reasons"]) + "</ul>") if alt.get("rejection_reasons") else ""
        diffs_html = "<ul>" + "".join(f"<li>{d}</li>" for d in alt.get("differences", [])) + "</ul>"
        sims_html = "<ul>" + "".join(f"<li>{s}</li>" for s in alt.get("similarities", [])) + "</ul>"
        alt_sections += f"""
        <h3 style="color:#3a6bc4;">Alternative: {alt['code']}</h3>
        <p><strong>Estado:</strong> <span style="color:{status_color};font-weight:bold;">{status_text}</span></p>
        {"<p><strong>Razones de rechazo:</strong></p>" + reasons_html if reasons_html else ""}
        <p><strong>Conclusión:</strong> {alt.get('conclusion_general','')}</p>
        <p><strong>Diferencias:</strong></p>{diffs_html}
        <p><strong>Similitudes:</strong></p>{sims_html}<hr>"""
    return f"""
    <html><head><style>
    body{{font-family:Arial,sans-serif;background:#f5f5f5;color:#222;padding:20px;}}
    h1{{color:#1a3a6e;}} h2{{color:#3a6bc4;}}
    table{{border-collapse:collapse;width:100%;margin:1rem 0;font-size:12px;}}
    td,th{{border:1px solid #ccc;padding:6px 10px;}}
    th{{background:#1a3a6e;color:white;}}
    </style></head><body>
    <h1>⚙ Steel Deviation Analyzer — Reporte</h1>
    <p><strong>Baseline:</strong> {baseline_code}</p>
    <h2>Parámetros Generales</h2>{general_df.to_html(index=False,border=0)}
    <h2>Composición Química</h2>{chem_df.to_html(border=0)}
    <h2>Resultados por Alternative</h2>{alt_sections}
    <p style="color:#888;font-size:11px;">Generado por Steel Deviation Analyzer · Powered by Gemini 2.5 Flash</p>
    </body></html>"""


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
for key in ["analysis", "general_df", "chem_df", "diagnostics"]:
    if key not in st.session_state:
        st.session_state[key] = None


# ─────────────────────────────────────────────
# STEP 1 — INPUT FORM
# ─────────────────────────────────────────────
st.markdown('<div class="section-label"><span class="step-dot">1</span> Carga de Documentos</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1], gap="large")
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**📄 Baseline**")
    baseline_file = st.file_uploader(
        "Certificado de material de referencia (PDF)",
        type=["pdf"], key="baseline_uploader", label_visibility="collapsed"
    )
    baseline_code = st.text_input(
        "Código de parte — Baseline",
        placeholder="Ej: P/N 12345-A", key="baseline_code"
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**📂 Alternative(s)**")
    st.caption("El nombre de cada PDF se usará como título en las tablas.")
    alternative_files = st.file_uploader(
        "Certificados alternativos (uno o varios PDF)",
        type=["pdf"], accept_multiple_files=True,
        key="alt_uploader", label_visibility="collapsed"
    )
    # Preview de archivos cargados
    if alternative_files:
        for f in alternative_files:
            fname_display = f.name.replace(".pdf", "").replace("_", " ").replace("-", " ")
            st.markdown(
                f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.7rem;'
                f'color:#3a6bc4;padding:2px 0;">📄 {fname_display}</div>',
                unsafe_allow_html=True
            )
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
recipient_email = st.text_input(
    "📧 Correo electrónico para envío de resultados",
    placeholder="nombre@empresa.com", key="email"
)
st.markdown('</div>', unsafe_allow_html=True)

# Los "códigos" de los alternatives ahora son los nombres de los archivos PDF (sin extensión)
def pdf_name_to_label(filename: str) -> str:
    """Convierte 'Certificado_Proveedor_X.pdf' → 'Certificado Proveedor X'"""
    name = filename
    if name.lower().endswith(".pdf"):
        name = name[:-4]
    return name.replace("_", " ").replace("-", " ")

# Validation
ready = (
    GEMINI_READY
    and baseline_file is not None
    and len(alternative_files) > 0
    and baseline_code.strip() != ""
    and recipient_email.strip() != ""
)

if not ready:
    missing = []
    if not GEMINI_READY: missing.append("API Key de Gemini")
    if not baseline_file: missing.append("PDF Baseline")
    if not alternative_files: missing.append("PDF(s) Alternative")
    if not baseline_code.strip(): missing.append("Código Baseline")
    if not recipient_email.strip(): missing.append("Correo electrónico")
    if missing:
        st.markdown(
            f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.75rem;color:#4a5568;margin:0.5rem 0;">'
            f'// Pendiente: {" · ".join(missing)}</div>',
            unsafe_allow_html=True
        )

st.markdown('<div class="steel-divider"></div>', unsafe_allow_html=True)

col_btn, _ = st.columns([1, 3])
with col_btn:
    analyze_clicked = st.button("⚙ Analizar Desviación", disabled=not ready, use_container_width=True)


# ─────────────────────────────────────────────
# STEP 2 — EXTRACTION + ANALYSIS
# ─────────────────────────────────────────────
if analyze_clicked and ready:
    diagnostics = []

    with st.spinner("Extrayendo texto del certificado Baseline..."):
        baseline_text, b_diag = extract_pdf_with_diagnosis(baseline_file)
        diagnostics.append(("Baseline", b_diag))

    alternatives_data = []
    for i, alt_file in enumerate(alternative_files):
        # El identificador de cada alternative ES el nombre del PDF
        pdf_label = pdf_name_to_label(alt_file.name)
        with st.spinner(f"Extrayendo texto de Alternative #{i+1}: {alt_file.name}..."):
            alt_text, a_diag = extract_pdf_with_diagnosis(alt_file)
            diagnostics.append((f"Alternative #{i+1} — {alt_file.name}", a_diag))
            alternatives_data.append({
                "code": pdf_label,          # label visible en tablas = nombre del PDF
                "filename": alt_file.name,  # nombre original para diagnóstico
                "text": alt_text
            })

    st.session_state.diagnostics = diagnostics

    # Warn if any extraction failed completely
    failed = [label for label, d in diagnostics if not d["ok"]]
    if failed:
        st.error(
            f"⚠️ Extracción fallida en: {', '.join(failed)}. "
            "Se intentará el análisis con el texto disponible. "
            "Revisa el panel de Diagnóstico para más detalles."
        )

    with st.spinner("Analizando con Gemini 2.5 Flash..."):
        try:
            analysis = analyze_with_gemini(
                baseline_text, alternatives_data, baseline_code
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
# DIAGNOSTICS PANEL
# Siempre visible después de un análisis.
# Permite al usuario saber exactamente qué pasó
# con la extracción de cada PDF.
# ─────────────────────────────────────────────
if st.session_state.diagnostics:
    with st.expander("🔍 Diagnóstico de extracción de PDF", expanded=False):
        st.markdown(
            '<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.7rem;color:#4a5568;margin-bottom:0.8rem;">'
            '// Método de extracción utilizado por documento. '
            'Verde = extracción exitosa · Amarillo = fallback utilizado · Rojo = extracción fallida.</div>',
            unsafe_allow_html=True
        )
        for label, diag in st.session_state.diagnostics:
            st.markdown(f"**{label}**")
            render_diag(diag)

        if st.session_state.analysis:
            st.markdown("---")
            st.markdown(
                '<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.7rem;color:#4a5568;">'
                '// Referencia encontrada en cada documento</div>',
                unsafe_allow_html=True
            )
            b_found = st.session_state.analysis["baseline"].get("codigo_encontrado", "")
            st.caption(f"Baseline — buscado: `{st.session_state.analysis['baseline']['code']}` · encontrado en doc: `{b_found or 'no detectado'}`")
            for alt in st.session_state.analysis.get("alternatives", []):
                a_found = alt.get("codigo_encontrado", "")
                st.caption(f"Alternative '{alt['code']}' — referencia encontrada en doc: `{a_found or 'no aplicable'}`")


# ─────────────────────────────────────────────
# STEP 3 — RESULTS DISPLAY
# ─────────────────────────────────────────────
if st.session_state.analysis is not None:
    analysis = st.session_state.analysis
    general_df = st.session_state.general_df
    chem_df = st.session_state.chem_df

    st.markdown('<div class="steel-divider"></div>', unsafe_allow_html=True)

    # ── Baseline code match advisory ──
    b_found = analysis["baseline"].get("codigo_encontrado", "")
    if b_found and b_found.strip().lower() != baseline_code.strip().lower():
        st.info(
            f"ℹ️ **Baseline:** El código buscado era `{baseline_code}`. "
            f"La referencia más cercana encontrada en el documento fue `{b_found}`. "
            f"Los datos extraídos corresponden a esa referencia."
        )

    # ── Table 1: General Parameters ──
    st.markdown('<div class="section-label"><span class="step-dot">2</span> Parámetros Generales</div>', unsafe_allow_html=True)
    st.dataframe(general_df, use_container_width=True, hide_index=True)

    # ── Table 2: Chemical Composition ──
    st.markdown('<div class="section-label"><span class="step-dot">3</span> Composición Química</div>', unsafe_allow_html=True)
    st.dataframe(chem_df, use_container_width=True)

    # ── Verdict ──
    st.markdown('<div class="section-label"><span class="step-dot">4</span> Veredicto por Alternative</div>', unsafe_allow_html=True)
    for alt in analysis["alternatives"]:
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
        diffs = "<br>".join(f"• {d}" for d in alt.get("differences", [])) or "—"
        sims = "<br>".join(f"• {s}" for s in alt.get("similarities", [])) or "—"
        st.markdown(
            f'<div class="conclusion-box">'
            f'<h4>Alternative — {alt["code"]}</h4>'
            f'<strong>Resumen:</strong> {alt.get("conclusion_general","")}<br><br>'
            f'<strong>Diferencias:</strong><br>{diffs}<br><br>'
            f'<strong>Similitudes:</strong><br>{sims}'
            f'</div>',
            unsafe_allow_html=True
        )

    # ── Send Email ──
    st.markdown('<div class="steel-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label"><span class="step-dot">6</span> Envío de Resultados</div>', unsafe_allow_html=True)
    col_mail, _ = st.columns([1, 3])
    with col_mail:
        if st.button("📧 Enviar por correo", use_container_width=True):
            email_html = build_email_html(analysis, general_df, chem_df)
            subject = f"Steel Deviation Report — Baseline: {analysis['baseline']['code']}"
            with st.spinner("Enviando correo..."):
                success, error = send_email(recipient_email, subject, email_html)
            if success:
                st.success(f"✅ Reporte enviado a **{recipient_email}** correctamente.")
            else:
                st.error(f"❌ Error enviando correo: {error}")
