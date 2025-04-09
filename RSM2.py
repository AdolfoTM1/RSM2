import streamlit as st
import requests
import xmlschema
from io import BytesIO
import json
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from datetime import datetime

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

# --- Formateo de Valores para XML ---
def formatear_valor_para_xml(tipo, valor):
    """Convierte valores a formato adecuado para XML según su tipo"""
    if valor is None:
        return ""
    
    if tipo in {'decimal', 'float', 'double'}:
        # Formatear montos con 2 decimales
        return f"{float(valor):.2f}"
    elif tipo == 'date':
        # Formatear fecha como YYYY-MM-DD
        return valor.strftime("%Y-%m-%d")
    elif tipo == 'dateTime':
        # Formatear fecha/hora como ISO 8601
        return valor.isoformat()
    elif tipo == 'boolean':
        # Convertir booleanos a lowercase
        return str(valor).lower()
    else:
        return str(valor)

# --- Generación de Campos del Formulario ---
def generar_campo(elemento, path=""):
    """Genera campos de formulario según el tipo de elemento XSD"""
    nombre_completo = f"{path}_{elemento.name}" if path else elemento.name
    etiqueta = elemento.name.replace('_', ' ').title()
    tipo = str(elemento.type.base_type) if elemento.type.is_simple() else 'complex'
    
    # Manejar enumeraciones (dropdowns)
    if hasattr(elemento.type, 'enumeration'):
        opciones = elemento.type.enumeration
        return st.selectbox(etiqueta, options=opciones, key=nombre_completo)
    
    # Campos específicos con manejo especial
    if tipo in {'decimal', 'float', 'double'}:
        # Campo de monto con validación
        valor = st.number_input(
            etiqueta, 
            min_value=0.0, 
            step=0.01, 
            format="%.2f", 
            key=nombre_completo
        )
        return float(valor) if valor is not None else 0.0
    
    elif tipo == 'date':
        # Campo de fecha con formato adecuado
        fecha = st.date_input(etiqueta, key=nombre_completo)
        return fecha if fecha else datetime.now().date()
    
    elif tipo == 'dateTime':
        # Campo de fecha y hora
        datetime_val = st.datetime_input(etiqueta, key=nombre_completo)
        return datetime_val if datetime_val else datetime.now()
    
    elif tipo == 'boolean':
        # Checkbox para booleanos
        return st.checkbox(etiqueta, key=nombre_completo)
    
    else:
        # Campo de texto genérico
        return st.text_input(etiqueta, key=nombre_completo)

def generar_formulario_complejo(elemento, path=""):
    """Genera formulario para elementos complejos con anidación"""
    datos = {}
    current_path = f"{path}_{elemento.name}" if path else elemento.name
    
    if elemento.type.is_complex():
        for child in elemento.type.content_type.iter_elements():
            if child.type.is_simple():
                datos[child.name] = generar_campo(child, current_path)
            else:
                datos.update(generar_formulario_complejo(child, current_path))
    
    return datos

# --- Generación de XML con Tipado Correcto ---
def generar_xml(schema, root_element, datos):
    """Genera XML estructurado con los datos del formulario"""
    def construir_elemento(parent, name, value, element_def=None):
        if isinstance(value, dict):
            sub_element = SubElement(parent, name)
            for k, v in value.items():
                construir_elemento(sub_element, k, v)
        else:
            element = SubElement(parent, name)
            # Obtener el tipo del elemento del esquema si está disponible
            tipo = None
            if element_def and element_def.type.is_simple():
                tipo = str(element_def.type.base_type)
            
            # Formatear el valor según su tipo
            element.text = formatear_valor_para_xml(tipo, value)
    
    root = Element(root_element)
    root_schema_element = schema.elements[root_element]
    
    # Construir estructura XML manteniendo referencia a los elementos del esquema
    for key, value in datos.items():
        child_element = next(
            (e for e in root_schema_element.type.content_type.iter_elements() 
             if e.name == key), None)
        construir_elemento(root, key, value, child_element)
    
    # Formatear XML
    xml_str = tostring(root, encoding='unicode')
    xml_pretty = minidom.parseString(xml_str).toprettyxml(indent="    ")
    return xml_pretty

# --- Interfaz de Usuario ---
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
                    st.session_state.form_data = {}
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
