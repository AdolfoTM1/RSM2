import streamlit as st
import requests
import xmlschema
from io import BytesIO
import json
from pathlib import Path

# Configuración de la aplicación
st.set_page_config(page_title="Generador XML RSM2", layout="wide")
st.title("📋 Generador de XML para RSM2")

# --- Carga de Esquemas ---
def cargar_configuracion():
    """Carga la configuración de esquemas desde un archivo JSON"""
    try:
        with open('config/esquemas.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"❌ Error al cargar configuración: {str(e)}")
        st.stop()

def cargar_xsd(ruta_xsd):
    """Carga un esquema XSD desde archivo local o URL"""
    try:
        if ruta_xsd.startswith('http'):
            response = requests.get(ruta_xsd, timeout=10)
            response.raise_for_status()
            return xmlschema.XMLSchema(BytesIO(response.content))
        else:
            return xmlschema.XMLSchema(ruta_xsd)
    except Exception as e:
        st.error(f"❌ Error al cargar XSD: {str(e)}")
        st.stop()

# --- Interfaz de Usuario ---
def main():
    # Cargar configuración
    config = cargar_configuracion()
    esquemas = {e['nombre']: e for e in config['esquemas']}

    # Selección de esquema
    col1, col2 = st.columns(2)
    with col1:
        esquema_seleccionado = st.selectbox(
            "Seleccione el tipo de operación:",
            options=list(esquemas.keys())
        )

    with col2:
        modo_carga = st.radio(
            "Fuente del esquema:",
            ["Desde URL", "Desde archivo local"],
            horizontal=True
        )

    # Cargar el esquema seleccionado
    if st.button("Cargar Esquema"):
        with st.spinner(f"Cargando {esquema_seleccionado}..."):
            try:
                if modo_carga == "Desde URL":
                    schema = cargar_xsd(esquemas[esquema_seleccionado]['url'])
                else:
                    schema = cargar_xsd(esquemas[esquema_seleccionado]['archivo'])
                
                st.session_state.schema = schema
                st.success(f"✅ {esquema_seleccionado} cargado correctamente")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    # Generador de XML
    if 'schema' in st.session_state:
        schema = st.session_state.schema
        st.divider()
        st.subheader("Datos de la Operación")

        with st.form("formulario_xml"):
            # Campos dinámicos basados en el XSD
            datos = {}
            
            # Ejemplo para el esquema de anulación
            if "Anulación" in esquema_seleccionado:
                datos['NumeroDeControl'] = st.text_input("Número de Control", value="")
                datos['Version'] = "1.0"  # Valor fijo según XSD
            
            # Puedes agregar más condiciones para otros esquemas aquí
            
            if st.form_submit_button("Generar XML"):
                try:
                    # Construcción del XML
                    xml_content = f"""<?xml version="1.0"?>
<Operacion>
    <Datosoperacionanuladareporte Version="{datos['Version']}">
        <NumeroDeControl>{datos['NumeroDeControl']}</NumeroDeControl>
    </Datosoperacionanuladareporte>
</Operacion>"""
                    
                    # Validación contra el esquema
                    if schema.is_valid(BytesIO(xml_content.encode())):
                        st.success("✅ XML generado y validado correctamente")
                        
                        # Mostrar y permitir descargar el XML
                        st.code(xml_content, language='xml')
                        st.download_button(
                            label="⬇️ Descargar XML",
                            data=xml_content,
                            file_name=f"{esquema_seleccionado.lower().replace(' ', '_')}.xml",
                            mime="application/xml"
                        )
                    else:
                        st.error("❌ El XML generado no es válido según el esquema")
                except Exception as e:
                    st.error(f"❌ Error al generar XML: {str(e)}")

if __name__ == "__main__":
    main()
