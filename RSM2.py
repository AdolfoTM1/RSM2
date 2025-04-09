import streamlit as st
import requests
import xmlschema
from io import BytesIO
import json
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

# Configuración de la aplicación
st.set_page_config(page_title="Generador XML RSM2", layout="wide")
st.title("📋 Generador de XML para RSM2 con Validación")

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

# --- Generación de Formularios con Dropdowns ---
def generar_campo(elemento, path=""):
    """Genera campos de formulario según el tipo de elemento XSD, con dropdowns para enums"""
    nombre_completo = f"{path}_{elemento.name}" if path else elemento.name
    etiqueta = elemento.name.replace('_', ' ').title()
    
    # Verificar si es una enumeración
    if hasattr(elemento.type, 'enumeration'):
        opciones = elemento.type.enumeration
        return st.selectbox(etiqueta, options=opciones, key=nombre_completo)
    
    # Mapeo de tipos XSD a controles
    tipo = str(elemento.type.base_type) if elemento.type.is_simple() else 'complex'
    
    controles = {
        'string': lambda: st.text_input(etiqueta, key=nombre_completo),
        'normalizedString': lambda: st.text_input(etiqueta, key=nombre_completo),
        'boolean': lambda: st.checkbox(etiqueta, key=nombre_completo),
        'int': lambda: st.number_input(etiqueta, step=1, key=nombre_completo),
        'integer': lambda: st.number_input(etiqueta, step=1, key=nombre_completo),
        'long': lambda: st.number_input(etiqueta, step=1, key=nombre_completo),
        'decimal': lambda: st.number_input(etiqueta, step=0.01, format="%.2f", key=nombre_completo),
        'float': lambda: st.number_input(etiqueta, step=0.01, format="%.2f", key=nombre_completo),
        'double': lambda: st.number_input(etiqueta, step=0.01, format="%.2f", key=nombre_completo),
        'date': lambda: st.date_input(etiqueta, key=nombre_completo),
        'dateTime': lambda: st.datetime_input(etiqueta, key=nombre_completo),
        'complex': lambda: None  # Para tipos complejos manejados recursivamente
    }
    
    return controles.get(tipo, lambda: st.text_input(etiqueta, key=nombre_completo))()

def generar_formulario_complejo(elemento, path=""):
    """Genera formulario para elementos complejos con anidación"""
    datos = {}
    current_path = f"{path}_{elemento.name}" if path else elemento.name
    
    if elemento.type.is_complex():
        for child in elemento.type.content_type.iter_elements():
            if child.type.is_simple():
                datos[child.name] = generar_campo(child, current_path)
            else:
                # Llamada recursiva para elementos complejos anidados
                datos.update(generar_formulario_complejo(child, current_path))
    
    return datos

# --- Generación de XML ---
def generar_xml(schema, root_element, datos):
    """Genera XML estructurado con los datos del formulario"""
    def construir_elemento(parent, name, value):
        if isinstance(value, dict):
            sub_element = SubElement(parent, name)
            for k, v in value.items():
                construir_elemento(sub_element, k, v)
        else:
            element = SubElement(parent, name)
            element.text = str(value)
    
    root = Element(root_element)
    
    for key, value in datos.items():
        construir_elemento(root, key, value)
    
    # Formatear XML
    xml_str = tostring(root, encoding='unicode')
    xml_pretty = minidom.parseString(xml_str).toprettyxml(indent="    ")
    return xml_pretty

# --- Interfaz de Usuario Mejorada ---
def main():
    # Cargar configuración
    config = cargar_configuracion()
    esquemas = {e['nombre']: e for e in config['esquemas']}
    
    # Sidebar para configuración
    with st.sidebar:
        st.header("Configuración")
        esquema_seleccionado = st.selectbox(
            "Tipo de operación:",
            options=list(esquemas.keys())
        )
        
        modo_carga = st.radio(
            "Fuente del esquema:",
            ["Desde URL", "Desde archivo local"],
            horizontal=True
        )
        
        if st.button("📥 Cargar Esquema", type="primary"):
            with st.spinner(f"Cargando {esquema_seleccionado}..."):
                try:
                    if modo_carga == "Desde URL":
                        schema = cargar_xsd(esquemas[esquema_seleccionado]['url'])
                    else:
                        schema = cargar_xsd(esquemas[esquema_seleccionado]['archivo'])
                    
                    st.session_state.schema = schema
                    st.session_state.root_element = list(schema.elements.keys())[0]
                    st.success(f"✅ {esquema_seleccionado} cargado correctamente")
                    st.session_state.form_data = {}  # Resetear datos anteriores
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    # Panel principal
    if 'schema' in st.session_state:
        schema = st.session_state.schema
        root_element = st.session_state.root_element
        
        st.subheader(f"Formulario para {esquema_seleccionado}")
        st.caption("Complete los campos requeridos según el esquema XSD")
        
        with st.form("formulario_xml"):
            # Generar formulario completo
            root_schema_element = schema.elements[root_element]
            form_data = generar_formulario_complejo(root_schema_element)
            
            # Guardar datos en sesión para posible reutilización
            st.session_state.form_data = form_data
            
            if st.form_submit_button("🛠️ Generar XML", type="primary"):
                try:
                    xml_content = generar_xml(schema, root_element, form_data)
                    
                    # Validar contra el esquema
                    validation = schema.validate(BytesIO(xml_content.encode()))
                    if validation is None:
                        st.success("✅ XML válido según el esquema")
                        
                        # Mostrar XML con sintaxis coloreada
                        with st.expander("📄 Ver XML generado", expanded=True):
                            st.code(xml_content, language='xml')
                        
                        # Botón de descarga
                        st.download_button(
                            label="⬇️ Descargar XML",
                            data=xml_content,
                            file_name=f"{esquema_seleccionado.lower().replace(' ', '_')}.xml",
                            mime="application/xml"
                        )
                    else:
                        st.error("❌ Errores de validación encontrados")
                        for error in validation:
                            st.warning(f"- {error}")
                except Exception as e:
                    st.error(f"❌ Error al generar XML: {str(e)}")

if __name__ == "__main__":
    main()
