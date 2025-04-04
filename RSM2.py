import streamlit as st
import xmlschema
import requests
from io import BytesIO
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)

# --- Configuración inicial ---
st.set_page_config(page_title="Generador de XML desde XSD", layout="wide")
st.title("📄 Generador de archivos XML desde esquemas XSD")

# --- Lista de esquemas disponibles ---
esquemas = {
    "Esquema A": "https://raw.githubusercontent.com/AdolfoTM1/RSM2/main/Anulada.xsd",
    "Esquema B": "https://raw.githubusercontent.com/tu_usuario/tu_repo/main/esquema_b.xsd",
    "Esquema C": "https://raw.githubusercontent.com/tu_usuario/tu_repo/main/esquema_c.xsd"
}

# --- Selección de esquema ---
esquema_seleccionado = st.selectbox("Selecciona un esquema XSD:", list(esquemas.keys()))
url_xsd = esquemas[esquema_seleccionado]

# --- Descargar y cargar esquema ---
schema = None  # Inicializamos la variable

try:
    # Descargar el XSD
    response = requests.get(url_xsd)
    response.raise_for_status()  # Lanza error si la descarga falla
    
    # Verificar que no sea una página HTML
    if b"<!DOCTYPE html>" in response.content[:100].lower():
        st.error("❌ Error: La URL no apunta a un XSD válido. ¿Usaste la URL raw de GitHub?")
        st.stop()
    
    # Cargar el esquema
    schema = xmlschema.XMLSchema(BytesIO(response.content))
    logging.info("XSD cargado correctamente")
    
except requests.exceptions.RequestException as e:
    st.error(f"❌ Error de conexión: {str(e)}")
    st.stop()
except xmlschema.XMLSchemaException as e:
    st.error(f"❌ Error en el esquema XSD: {str(e)}")
    st.stop()
except Exception as e:
    st.error(f"❌ Error inesperado: {str(e)}")
    st.stop()

# Verificar que el esquema se cargó correctamente
if schema is None:
    st.error("No se pudo cargar el esquema XSD")
    st.stop()

# Verificar que tenga elemento raíz
if schema.root_element is None:
    st.error("❌ El XSD no tiene un elemento raíz definido")
    st.stop()

# --- Obtener estructura base desde el esquema ---
try:
    root_name = schema.root_element.name
    
    # Generar ejemplo (compatible con versiones nuevas y antiguas de xmlschema)
    try:
        ejemplo = schema.example()  # Para versiones nuevas
    except AttributeError:
        ejemplo = schema.create_example()  # Para versiones antiguas
    
    estructura_base = schema.to_dict(ejemplo)
    
except Exception as e:
    st.error(f"❌ Error al generar la estructura base: {str(e)}")
    st.stop()

# --- Crear formulario dinámico ---
st.subheader("📝 Completa el formulario generado desde el esquema")

with st.form("Formulario XML"):
    user_data = {}
    for campo, valor in estructura_base.items():
        if isinstance(valor, int):
            user_input = st.number_input(campo, value=valor)
        elif isinstance(valor, bool):
            user_input = st.checkbox(campo, value=valor)
        else:
            user_input = st.text_input(campo, value=str(valor) if valor is not None else "")
        user_data[campo] = user_input

    submitted = st.form_submit_button("Generar XML")

# --- Procesar XML al enviar el formulario ---
if submitted:
    try:
        xml_generado = schema.encode(user_data, path=root_name)
        st.success("✅ Archivo XML generado correctamente")

        st.download_button(
            label="📥 Descargar archivo XML",
            data=xml_generado,
            file_name="archivo_generado.xml",
            mime="application/xml"
        )
    except Exception as e:
        st.error(f"❌ Error al generar el archivo XML: {str(e)}")
