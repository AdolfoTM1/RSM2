import streamlit as st
import xmlschema
import requests
from io import BytesIO

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
try:
    # Verifica si hay elemento raíz
    if schema.root_element is None:
        raise ValueError("El XSD no tiene un elemento raíz definido")
    
    root_name = schema.root_element.name
    
    # Usa el método correcto para generar el ejemplo
    try:
        ejemplo = schema.example()  # Para versiones nuevas de xmlschema
    except AttributeError:
        ejemplo = schema.create_example()  # Para versiones antiguas
        
    estructura_base = schema.to_dict(ejemplo)
    
except Exception as e:
    st.error(f"Error al procesar el esquema: {str(e)}")
    st.stop()

# --- Obtener estructura base desde el esquema ---
root_name = schema.root_element.name
estructura_base = schema.to_dict(schema.create_example())

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
        st.error(f"❌ Error al generar el archivo XML: {e}")
