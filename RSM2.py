import streamlit as st
import xmlschema
import requests
from io import BytesIO
import logging

# Configura logging
logging.basicConfig(level=logging.INFO)

# --- Configuración inicial ---
st.set_page_config(page_title="Generador de XML desde XSD", layout="wide")
st.title("📄 Generador de archivos XML desde esquemas XSD")

# --- Lista de esquemas disponibles ---
esquemas = {
    "Esquema A": "https://raw.githubusercontent.com/AdolfoTM1/RSM2/main/Anulada.xsd",
    "Esquema B": "https://raw.githubusercontent.com/tu_usuario/tu_repo/main/esquema_b.xsd"
}

# --- Selección de esquema ---
esquema_seleccionado = st.selectbox("Selecciona un esquema XSD:", list(esquemas.keys()))
url_xsd = esquemas[esquema_seleccionado]

# --- Descargar y cargar esquema ---
schema = None
try:
    # Verificar URL
    if not url_xsd.startswith('https://raw.githubusercontent.com'):
        st.error("❌ URL incorrecta. Debe usar la URL 'raw' de GitHub")
        st.stop()
    
    # Descargar contenido
    response = requests.get(url_xsd, timeout=10)
    response.raise_for_status()
    
    # Verificar que sea un XSD válido
    if not response.content.startswith(b'<?xml'):
        st.error("❌ El contenido no es un archivo XML válido")
        st.stop()
    
    # Cargar esquema
    schema = xmlschema.XMLSchema(BytesIO(response.content))
    logging.info("XSD cargado correctamente")
    
    # Verificar elemento raíz
    if not hasattr(schema, 'root_element') or schema.root_element is None:
        st.error("❌ El XSD no tiene un elemento raíz definido")
        st.stop()

except requests.exceptions.RequestException as e:
    st.error(f"❌ Error de conexión: {str(e)}")
    st.stop()
except xmlschema.XMLSchemaException as e:
    st.error(f"❌ Error en el XSD: {str(e)}")
    st.stop()
except Exception as e:
    st.error(f"❌ Error inesperado: {str(e)}")
    st.stop()

# --- Solo continuar si schema se cargó correctamente ---
if schema is None:
    st.error("No se pudo cargar el esquema XSD")
    st.stop()

# --- Generar formulario ---
try:
    # Obtener estructura base
    root_name = schema.root_element.name
    ejemplo = schema.example() if hasattr(schema, 'example') else schema.create_example()
    estructura_base = schema.to_dict(ejemplo)

    # Crear formulario
    with st.form("xml_form"):
        user_data = {}
        for campo, valor in estructura_base.items():
            if isinstance(valor, int):
                user_data[campo] = st.number_input(campo, value=valor)
            elif isinstance(valor, bool):
                user_data[campo] = st.checkbox(campo, value=valor)
            else:
                user_data[campo] = st.text_input(campo, value=str(valor) if valor else "")
        
        if st.form_submit_button("Generar XML"):
            try:
                xml = schema.encode(user_data, path=root_name)
                st.download_button(
                    label="Descargar XML",
                    data=xml,
                    file_name="generado.xml",
                    mime="application/xml"
                )
            except Exception as e:
                st.error(f"Error al generar XML: {str(e)}")

except Exception as e:
    st.error(f"❌ Error al procesar el esquema: {str(e)}")
