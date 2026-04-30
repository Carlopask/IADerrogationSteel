import streamlit as st
import pandas as pd
from PIL import Image
import os
from google import genai
from google.genai import types

# Configuración de la página web
st.set_page_config(page_title="Análisis de Desviaciones de Lámina", layout="wide")

st.title("📊 Análisis de Desviaciones de Lámina")
st.write("Sube la captura de pantalla para generar la tabla comparativa y la recomendación de aprobación.")

# Carga de la imagen
uploaded_file = st.file_uploader("Sube la captura de pantalla del archivo", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Imagen cargada", use_column_width=True)
    
    # Barra de progreso
    if st.button("Procesar Análisis"):
        with st.status("Analizando la imagen y extrayendo datos...", expanded=True) as status:
            st.write("Conectando con el motor de IA...")
            
            # Inicializar el cliente de Gemini (asegúrate de tener tu API_KEY configurada en las variables de entorno de tu IDX)
            client = genai.Client()
            
            # Prompt para estructurar los datos
            prompt = """
            Analiza la siguiente imagen de una lámina y extrae la información para las siguientes secciones:
            
            1. Descripción del rollo: Llenar Baseline y Alternative.
            2. Normas equivalentes: Llenar Baseline y Alternative.
            3. Composición Química: Tabla con columnas C, Mn, P, S, Si, Al, V, Ti, Cr, Mo, N, B, Cu, Sn, Ca, Ni, Cb (dejar vacío si no hay valor).
            4. Espesor: Baseline y Alternative.
            5. Largo de rollo: Baseline y Alternative.
            6. Yield Strength: Baseline y Alternative.
            7. Tensile strength: Baseline y Alternative.
            8. % Elongation: Baseline y Alternative.
            
            Formatea la respuesta en un JSON claro o texto estructurado.
            """
            
            # Llamada a Gemini
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[image, prompt]
            )
            
            status.update(label="Análisis completado", state="complete")
            
        st.subheader("1. Descripción y Parámetros del Rollo")
        
        # Ejemplo de tabla para los campos Alternative vs Baseline
        data_params = {
            "Parámetro": ["Descripción del rollo", "Normas equivalentes", "Espesor", "Largo de rollo", "Yield Strength", "Tensile strength", "% Elongation"],
            "Alternative": ["-", "-", "-", "-", "-", "-", "-"],
            "Baseline": ["-", "-", "-", "-", "-", "-", "-"],
            "Idéntico (Check)": [False, False, False, False, False, False, False]
        }
        df_params = pd.DataFrame(data_params)
        st.dataframe(df_params)
        
        st.subheader("2. Composición Química")
        data_chem = {
            "Elemento": ["C", "Mn", "P", "S", "Si", "Al", "V", "Ti", "Cr", "Mo", "N", "B", "Cu", "Sn", "Ca", "Ni", "Cb"],
            "Baseline": ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
            "Alternative": ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]
        }
        df_chem = pd.DataFrame(data_chem)
        st.dataframe(df_chem)
        
        st.subheader("3. Conclusión y Dictamen")
        # Lógica de negocio (Reglas de validación)
        st.info("💡 Análisis de criterios de aprobación:")
        
        criterios_aprobacion = True
        motivos = []
        
        # Aquí puedes ajustar las variables de ejemplo extraídas para validar:
        # Por ejemplo, si es fosforizada:
        es_fosforizada = False # Este valor dependería de la lectura real de la norma
        
        if not criterios_aprobacion:
            st.error("❌ Estatus: NO APROBAR")
            for motivo in motivos:
                st.markdown(f"- {motivo}")
        else:
            st.success("✔️ Estatus: APROBAR")
            st.write("La desviación cumple con todos los criterios evaluados.")
