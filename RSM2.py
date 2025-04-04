import streamlit as st
import requests
import json
import os
from io import BytesIO
import xmlschema
from pathlib import Path

# --- Configuración ---
CONFIG_FILE = "config/esquemas.json"
SCHEMAS_DIR = "schemas"

# --- Funciones de carga ---
def cargar_configuracion():
    """Carga el archivo de configuración de esquemas"""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"❌ Error al cargar configuración: {str(e)}")
        st.stop()

def cargar_xsd(ruta_o_url):
    """Carga un XSD desde archivo local o URL"""
    try:
        if ruta_o_url.startswith('http'):
            response = requests.get(ruta_o_url, timeout=10)
            response.raise_for_status()
            return xmlschema.XMLSchema(BytesIO(response.content))
        else:
            ruta_completa = os.path.join(SCHEMAS_DIR, ruta_o_url)
            return xmlschema.XMLSchema(ruta_completa)
    except Exception as e:
        st.error(f"❌ Error al cargar XSD: {str(e)}")
        st.stop()

# --- Interfaz ---
st.set_page_config(page_title="Gestor de Esquemas XML", layout="wide")
st.title("📁 Generador XML con Esquemas Externos")

# Cargar configuración
config = cargar_configuracion()
esquemas_disponibles = {e['nombre']: e for e in config['esquemas']}

# Selección de esquema
esquema_seleccionado = st.selectbox(
    "Selecciona un esquema:",
    options=list(esquemas_disponibles.keys())
    
esquema_info = esquemas_disponibles[esquema_seleccionado]

# Modo de carga
modo_carga = st.radio(
    "Fuente del esquema:",
    ["Desde URL", "Desde archivo local"],
    horizontal=True)

# Cargar XSD
if st.button("Cargar Esquema"):
    with st.spinner(f"Cargando {esquema_seleccionado}..."):
        if modo_carga == "Desde URL":
            schema = cargar_xsd(esquema_info['url'])
        else:
            schema = cargar_xsd(esquema_info['archivo'])
        
        st.session_state.schema = schema
        st.success(f"✅ {esquema_seleccionado} cargado correctamente")

# Generador de XML
if 'schema' in st.session_state:
    schema = st.session_state.schema
    
    st.divider()
    st.subheader("Generar XML")
    
    # Obtener estructura del esquema
    ejemplo = schema.example() if hasattr(schema, 'example') else schema.create_example()
    estructura = schema.to_dict(ejemplo)
    
    # Generar formulario dinámico
    with st.form("generador_xml"):
        datos = {}
        for campo, valor in estructura.items():
            if isinstance(valor, bool):
                datos[campo] = st.checkbox(campo, value=valor)
            elif isinstance(valor, (int, float)):
                datos[campo] = st.number_input(campo, value=valor)
            else:
                datos[campo] = st.text_input(campo, value=str(valor) if valor else "")
        
        if st.form_submit_button("Generar XML"):
            try:
                xml_generado = schema.encode(datos, path=schema.root_element.name)
                
                st.success("✅ XML generado correctamente")
                st.download_button(
                    label="⬇️ Descargar XML",
                    data=xml_generado,
                    file_name=f"{esquema_seleccionado.lower().replace(' ', '_')}.xml",
                    mime="application/xml"
                )
                
                st.code(xml_generado.decode('utf-8'), language='xml')
            except Exception as e:
                st.error(f"❌ Error al generar XML: {str(e)}")
