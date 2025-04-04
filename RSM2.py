import streamlit as st
import requests
from io import BytesIO
import xmlschema

# Configuración
XSD_URL = "https://raw.githubusercontent.com/AdolfoTM1/RSM2/main/Anulada.xsd"

@st.cache_resource
def cargar_esquema():
    try:
        response = requests.get(XSD_URL, timeout=10)
        response.raise_for_status()
        
        if not response.content.startswith(b'<?xml'):
            st.error("❌ El archivo XSD no comienza con declaración XML válida")
            st.stop()
            
        return xmlschema.XMLSchema(BytesIO(response.content))
    except Exception as e:
        st.error(f"❌ Error al cargar XSD: {str(e)}")
        st.stop()

# Interfaz
st.title("Generador de XML")
schema = cargar_esquema()

# Generar formulario
with st.form("generador"):
    numero_control = st.text_input("Número de Control")
    if st.form_submit_button("Generar"):
        xml = f"""<?xml version="1.0"?>
<Operacion>
    <Datosoperacionanuladareporte Version="1.0">
        <NumeroDeControl>{numero_control}</NumeroDeControl>
    </Datosoperacionanuladareporte>
</Operacion>"""
        
        st.download_button(
            label="Descargar XML",
            data=xml,
            file_name="operacion.xml",
            mime="application/xml"
        )
