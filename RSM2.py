import streamlit as st
import xml.etree.ElementTree as ET
import requests
from io import BytesIO

# Configura la app
st.set_page_config(page_title="Editor XML", layout="wide")

# Menú de esquemas
esquemas = {
    "Esquema A": "https://raw.githubusercontent.com/tu_usuario/tu_repo/main/esquema_a.xml",
    "Esquema B": "https://raw.githubusercontent.com/tu_usuario/tu_repo/main/esquema_b.xml",
    "Esquema C": "https://raw.githubusercontent.com/tu_usuario/tu_repo/main/esquema_c.xml",
    "Esquema D": "https://raw.githubusercontent.com/tu_usuario/tu_repo/main/esquema_d.xml",
    "Esquema E": "https://raw.githubusercontent.com/tu_usuario/tu_repo/main/esquema_e.xml"
}

st.title("Editor de Archivos XML")

esquema_seleccionado = st.selectbox("Selecciona un esquema XML", list(esquemas.keys()))

# Descargar y parsear el XML
url_xml = esquemas[esquema_seleccionado]
response = requests.get(url_xml)
tree = ET.parse(BytesIO(response.content))
root = tree.getroot()

# Mostrar formulario dinámico
st.subheader("Formulario generado desde el XML")

nuevos_valores = {}
for child in root:
    valor = st.text_input(f"{child.tag}", value=child.text or "")
    nuevos_valores[child.tag] = valor

# Botón para generar nuevo XML
if st.button("Generar nuevo XML"):
    for child in root:
        if child.tag in nuevos_valores:
            child.text = nuevos_valores[child.tag]

    new_xml = BytesIO()
    tree.write(new_xml, encoding="utf-8", xml_declaration=True)
    st.download_button(
        label="Descargar archivo XML",
        data=new_xml.getvalue(),
        file_name="nuevo_archivo.xml",
        mime="application/xml"
    )
