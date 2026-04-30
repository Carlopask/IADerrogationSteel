import streamlit as st
import pandas as pd
from PIL import Image
import json # Importante para manejar la respuesta de la IA
from google import genai

# Configuración de la página web
st.set_page_config(page_title="Análisis de Desviaciones de Lámina", layout="wide")

st.title("📊 Análisis de Desviaciones de Lámina")
st.write("Sube las capturas de pantalla de BASELINE y ALTERNATIVE para generar la comparativa y el dictamen.")

# --- SECCIÓN 1: CARGA DE ARCHIVOS (Modificada para 2 imágenes) ---
st.subheader("1. Subir Capturas de Pantalla")
col1, col2 = st.columns(2) # Creamos dos columnas para organizar los cargadores

with col1:
    uploaded_baseline = st.file_uploader("Sube la captura de BASELINE (Actual)", type=["png", "jpg", "jpeg"], key="baseline")
    if uploaded_baseline:
        image_baseline = Image.open(uploaded_baseline)
        st.image(image_baseline, caption="Imagen BASELINE cargada", use_column_width=True)

with col2:
    uploaded_alternative = st.file_uploader("Sube la captura de ALTERNATIVE (Propuesta)", type=["png", "jpg", "jpeg"], key="alternative")
    if uploaded_alternative:
        image_alternative = Image.open(uploaded_alternative)
        st.image(image_alternative, caption="Imagen ALTERNATIVE cargada", use_column_width=True)


# --- SECCIÓN 2: PROCESAMIENTO CON IA ---
# Solo mostramos el botón si ambas imágenes han sido cargadas
if uploaded_baseline and uploaded_alternative:
    if st.button("Procesar Análisis Comparativo", type="primary"):
        with st.status("Analizando imágenes y extrayendo datos con Gemini...", expanded=True) as status:
            st.write("Conectando con el motor de IA...")
            
            try:
                # Inicializamos el cliente de forma segura utilizando Streamlit Secrets
                api_key = st.secrets["GEMINI_API_KEY"]
                client = genai.Client(api_key=api_key)
                
                # --- PROMPT AVANZADO PARA OBTENER JSON ESTRUCTURADO ---
                # Le damos instrucciones muy precisas a Gemini sobre el formato de salida.
                prompt = """
                Analiza las dos imágenes proporcionadas: la primera es 'BASELINE' (situación actual) y la segunda es 'ALTERNATIVE' (propuesta de desviación).
                Extrae la información técnica de ambas y genera ÚNICAMENTE una respuesta en formato JSON puro, sin texto adicional, siguiendo esta estructura exacta:

                {
                  "parametros": [
                    {"parametro": "Descripción del rollo", "baseline": "valor", "alternative": "valor"},
                    {"parametro": "Normas equivalentes", "baseline": "valor", "alternative": "valor"},
                    {"parametro": "Espesor", "baseline": "valor", "alternative": "valor"},
                    {"parametro": "Largo de rollo", "baseline": "valor", "alternative": "valor"},
                    {"parametro": "Yield Strength", "baseline": "valor", "alternative": "valor"},
                    {"parametro": "Tensile strength", "baseline": "valor", "alternative": "valor"},
                    {"parametro": "% Elongation", "baseline": "valor", "alternative": "valor"}
                  ],
                  "quimica": {
                    "elementos": ["C", "Mn", "P", "S", "Si", "Al", "V", "Ti", "Cr", "Mo", "N", "B", "Cu", "Sn", "Ca", "Ni", "Cb"],
                    "baseline": ["valor_C", "valor_Mn", ...],
                    "alternative": ["valor_C", "valor_Mn", ...]
                  }
                }

                Instrucciones adicionales:
                1. Si un valor no está presente en la imagen, usa una cadena vacía "".
                2. Asegúrate de que los valores numéricos se extraigan correctamente.
                3. Para la composición química, mantén estrictamente el orden de los elementos indicados en la lista 'elementos'.
                """
                
                # Llamada a Gemini pasando AMBAS imágenes en la lista 'contents'
                # Gemini asume que la primera es baseline y la segunda alternative por el orden en el prompt
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[image_baseline, image_alternative, prompt]
                )
                
                # --- EXTRACCIÓN Y LIMPIEZA DE DATOS (NUEVO) ---
                # A veces Gemini envuelve el JSON en bloques de código markdown ```json ... ```, hay que limpiarlo.
                json_response_text = response.text.replace("```json", "").replace("```", "").strip()
                
                # Convertimos la cadena de texto JSON en un objeto diccionario de Python
                datos_analisis = json.loads(json_response_text)
                
                # Guardamos los datos en la "sesión" de Streamlit para que no se borren al interactuar
                st.session_state['datos_analisis'] = datos_analisis
                
                status.update(label="Análisis completado exitosamente", state="complete")
                
            except json.JSONDecodeError:
                st.error("Error: La IA no devolvió un formato JSON válido. Intenta procesar de nuevo.")
                st.stop()
            except Exception as e:
                st.error(f"Ocurrió un error inesperado: {e}")
                st.stop()

# --- SECCIÓN 3: VISUALIZACIÓN DE RESULTADOS (Modificada para llenar tablas) ---
# Verificamos si ya tenemos datos procesados en la sesión
if 'datos_analisis' in st.session_state:
    datos = st.session_state['datos_analisis']
    
    st.divider() # Línea divisoria visual

    # --- TABLA 1: PARÁMETROS GENERALES ---
    st.subheader("2. Comparativa de Descripción y Parámetros del Rollo")
    
    # Creamos el DataFrame directamente desde la lista 'parametros' del JSON
    df_params = pd.DataFrame(datos['parametros'])
    
    # Capitalizamos los nombres de las columnas para que se vean mejor
    df_params.columns = ['Parámetro', 'Baseline (Actual)', 'Alternative (Propuesta)']
    
    # Calculamos el checkbox de "Idéntico" automáticamente comparando las columnas
    df_params['Idéntico (Check)'] = df_params['Baseline (Actual)'].str.strip() == df_params['Alternative (Propuesta)'].str.strip()
    
    # Mostramos la tabla formateada
    st.dataframe(df_params, use_column_width=True, hide_index=True)
    
    
    # --- TABLA 2: COMPOSICIÓN QUÍMICA ---
    st.subheader("3. Comparativa de Composición Química (%)")
    
    quimica = datos['quimica']
    
    # Estructuramos los datos químicos para crear el DataFrame
    data_chem = {
        "Elemento": quimica['elementos'],
        "Baseline (Actual)": quimica['baseline'],
        "Alternative (Propuesta)": quimica['alternative']
    }
    df_chem = pd.DataFrame(data_chem)
    
    # Mostramos la tabla química
    st.dataframe(df_chem, use_column_width=True, hide_index=True)
    
    
    # --- SECCIÓN 4: CONCLUSIÓN Y DICTAMEN (Lógica por definir) ---
    st.divider()
    st.subheader("4. Conclusión y Dictamen Automático")
    st.info("💡 Análisis preliminar basado en reglas de negocio (Lógica de aprobación aún no implementada completamente):")
    
    # Espacio reservado para la lógica de validación (Paso 3 de tu requerimiento original)
    # Por ahora mostramos un mensaje genérico.
    criterios_aprobacion = True # Placeholder
    
    if not criterios_aprobacion:
        st.error("❌ Estatus Recomendado: NO APROBAR")
        st.write("Motivos detectados automáticamente...")
    else:
        st.success("✔️ Estatus Recomendado: APROBAR")
        st.write("La desviación parece cumplir con los criterios básicos extraídos.")

else:
    # Mensaje si no se han cargado/procesado imágenes aún
    if not (uploaded_baseline and uploaded_alternative):
        st.warning("⚠️ Por favor, sube ambas imágenes (Baseline y Alternative) para comenzar el análisis.")
