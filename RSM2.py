import streamlit as st
import requests
from io import BytesIO
import xmlschema
import re

# --- Configuración de la página ---
st.set_page_config(page_title="Generador XML desde XSD", layout="wide")
st.title("📄 Generador de XML desde XSD")

# --- Función mejorada para cargar XSD ---
def cargar_esquema(url):
    try:
        # Validación de URL
        if not url.startswith('https://raw.githubusercontent.com/'):
            st.error("❌ URL debe ser de raw.githubusercontent.com")
            st.stop()

        # Descargar contenido
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Detección de HTML (error común)
        if b"<!DOCTYPE html>" in response.content[:1000].lower():
            st.error("""
            ❌ Se descargó una página HTML en lugar del XSD.
            Solución: Asegúrate de usar la URL RAW:
            Ejemplo: https://raw.githubusercontent.com/usuario/repo/main/archivo.xsd
            """)
            st.stop()

        # Validación de XML
        contenido = response.content.decode('utf-8-sig').strip()
        if not re.match(r'^\s*<\?xml', contenido):
            st.error(f"""
            ❌ El archivo no es un XML válido.
            Primeras líneas recibidas:
            {contenido[:200]}
            """)
            st.stop()

        return xmlschema.XMLSchema(BytesIO(response.content))

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error de conexión: {str(e)}")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error inesperado: {str(e)}")
        st.stop()

# --- Lista de esquemas ---
esquemas = {
    "Esquema Anulación": "https://raw.githubusercontent.com/AdolfoTM1/RSM2/main/Anulada.xsd"
}

# --- Interfaz de usuario ---
esquema_seleccionado = st.selectbox("Selecciona un esquema XSD:", list(esquemas.keys()))
url_xsd = esquemas[esquema_seleccionado]

# --- Carga del esquema ---
schema = cargar_esquema(url_xsd)

# Verificación adicional del esquema
if not hasattr(schema, 'root_element') or schema.root_element is None:
    st.error("❌ El XSD no tiene elemento raíz. Asegúrate de que tenga un elemento global.")
    st.stop()

# --- Generación del formulario ---
try:
    root_name = schema.root_element.name
    ejemplo = schema.example() if hasattr(schema, 'example') else schema.create_example()
    estructura = schema.to_dict(ejemplo)

    with st.form("formulario_xml"):
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
                xml = schema.encode(datos, path=root_name)
                st.success("✅ XML generado correctamente")
                
                st.download_button(
                    label="⬇️ Descargar XML",
                    data=xml,
                    file_name="documento.xml",
                    mime="application/xml"
                )
            except Exception as e:
                st.error(f"❌ Error al generar XML: {str(e)}")

except Exception as e:
    st.error(f"❌ Error al procesar el esquema: {str(e)}")
