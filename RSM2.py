import streamlit as st
import xmlschema
import requests
from io import BytesIO
import xml.etree.ElementTree as ET

# Diccionario con URLs a tus archivos .xsd en GitHub
esquemas = {
    "Esquema A": "https://github.com/AdolfoTM1/RSM2/blob/main/Anulada_v1.0.xsd",
    "Esquema B": "https://raw.githubusercontent.com/tu_usuario/tu_repo/main/esquema_b.xsd",
    "Esquema C": "https://raw.githubusercontent.com/tu_usuario/tu_repo/main/esquema_c.xsd"
}

st.title("Generador XML basado en XSD")

esquema_seleccionado = st.selectbox("Selecciona un esquema XSD", list(esquemas.keys()))
url_xsd = esquemas[esquema_seleccionado]

# Descargar el esquema XSD desde GitHub
response = requests.get(url_xsd)
schema = xmlschema.XMLSchema(BytesIO(response.content))

# Generar estructura base
st.subheader("Formulario generado a partir del esquema")

# Vamos a generar el formulario desde el primer elemento definido
root_element = schema.elements[schema.root_element.name]
default_data = schema.to_dict(schema.create_example())

user_data = {}

# Mostrar inputs dinámicamente
for key, value in default_data.items():
    user_input = st.text_input(key, str(value) if value is not None else "")
    user_data[key] = user_input

# Crear XML al presionar botón
if st.button("Generar XML"):
    # Validar y generar
    try:
        xml_content = schema.encode(user_data, path=schema.root_element.name)
        st.success("XML generado exitosamente ✅")

        st.download_button(
            label="Descargar archivo XML",
            data=xml_content,
            file_name="archivo_generado.xml",
            mime="application/xml"
        )
    except Exception as e:
        st.error(f"Ocurrió un error al generar el XML: {e}")
