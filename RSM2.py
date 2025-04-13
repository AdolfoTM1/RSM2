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
st.title("📋 Generador de XML para RSM2")

# --- Funciones de Utilidad ---
def get_element_type(element):
    """Obtiene el tipo de elemento XSD de manera segura"""
    if element.type.is_simple():
        base_type = str(element.type.base_type)
        # Manejar tipos derivados como long, int, etc.
        if 'long' in base_type.lower():
            return 'long'
        elif 'int' in base_type.lower():
            return 'int'
        return base_type
    return 'complex'

def format_xml_value(value, xsd_type):
    """Formatea valores para XML según su tipo XSD"""
    if value is None:
        return None  # Para elementos nillable

    if xsd_type in {'decimal', 'float', 'double'}:
        return f"{float(value):.2f}"
    elif xsd_type in {'long', 'int', 'integer'}:
        return str(int(value))
    elif xsd_type == 'date':
        return value.strftime("%Y-%m-%d")
    elif xsd_type == 'dateTime':
        return value.isoformat()
    elif xsd_type == 'boolean':
        return str(value).lower()
    return str(value)

# --- Carga de Esquemas ---
def load_config():
    try:
        with open('config/esquemas.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"❌ Error al cargar configuración: {str(e)}")
        st.stop()

def load_xsd(xsd_path):
    try:
        if xsd_path.startswith('http'):
            response = requests.get(xsd_path, timeout=10)
            response.raise_for_status()
            return xmlschema.XMLSchema(BytesIO(response.content))
        return xmlschema.XMLSchema(xsd_path)
    except Exception as e:
        st.error(f"❌ Error al cargar XSD: {str(e)}")
        st.stop()

# --- Generación de Formularios ---
def create_input_field(element, path=""):
    """Crea campos de entrada según el tipo XSD"""
    try:
        field_id = f"{path}_{element.name}" if path else element.name
        label = element.name.replace('_', ' ').title()
        xsd_type = get_element_type(element)

        # Determinar si el campo es obligatorio
        is_required = (element.min_occurs is not None and element.min_occurs > 0) or not element.is_nillable()

        # Campos con enumeraciones (dropdowns)
        if hasattr(element.type, 'enumeration') and element.type.enumeration:
            try:
                # Convertir las enumeraciones a strings
                options = [str(e.value) for e in element.type.enumeration]
                default_idx = 0 if any("Elegir..." in opt for opt in options) else None
                return st.selectbox(
                    label, 
                    options=options,
                    index=default_idx,
                    key=field_id
                )
            except Exception as e:
                st.warning(f"Error al procesar enumeraciones para {label}: {str(e)}")
                return st.text_input(label, key=field_id)

        # Campos numéricos decimales
        elif xsd_type in {'decimal', 'float', 'double'}:
            return st.number_input(
                label,
                value=0.0 if is_required else None,
                step=0.01,
                format="%.2f",
                key=field_id
            )
        
        # Campos enteros (long, int)
        elif xsd_type in {'long', 'int', 'integer'}:
            return st.number_input(
                label,
                value=0 if is_required else None,
                step=1,
                key=field_id
            )

        # Campos de fecha
        elif xsd_type == 'date':
            return st.date_input(
                label, 
                value=datetime.now().date() if is_required else None,
                key=field_id
            )

        # Campos de fecha y hora
        elif xsd_type == 'dateTime':
            return st.datetime_input(
                label, 
                value=datetime.now() if is_required else None,
                key=field_id
            )

        # Campos booleanos
        elif xsd_type == 'boolean':
            return st.checkbox(
                label, 
                value=False if is_required else None,
                key=field_id
            )

        # Campos de texto (por defecto)
        else:
            return st.text_input(
                label, 
                value="" if is_required else None,
                key=field_id
            )
    except Exception as e:
        st.error(f"Error al crear campo para {element.name}: {str(e)}")
        return None
        
def build_form(schema, element, path=""):
    """Construye formulario dinámico basado en XSD"""
    form_data = {}
    current_path = f"{path}_{element.name}" if path else element.name

    if element.type.is_complex():
        # Manejar elementos complejos
        for child in element.type.content_type.iter_elements():
            if child.type.is_simple():
                form_data[child.name] = create_input_field(child, current_path)
            else:
                # Manejar sub-elementos complejos
                child_data = build_form(schema, child, current_path)
                if child_data:  # Solo añadir si hay datos
                    form_data[child.name] = child_data
    else:
        # Manejar elementos simples
        form_data[element.name] = create_input_field(element, current_path)

    return form_data

# --- Generación de XML ---
def generate_xml(schema, root_name, form_data):
    """Genera XML a partir de los datos del formulario"""
    def add_element(parent, name, value, element_def=None):
        if isinstance(value, dict):
            node = SubElement(parent, name)
            for k, v in value.items():
                child_element = schema.elements.get(f"{name}_{k}") if schema else None
                add_element(node, k, v, child_element)
        else:
            element = SubElement(parent, name)
            xsd_type = get_element_type(element_def) if element_def else None
            formatted_value = format_xml_value(value, xsd_type)
            if formatted_value is not None:
                element.text = formatted_value

    root = Element(root_name)
    root_element = schema.elements[root_name]

    for field, value in form_data.items():
        schema_element = next(
            (e for e in root_element.type.content_type.iter_elements()
             if e.name == field), None)
        add_element(root, field, value, schema_element)

    xml_str = tostring(root, encoding='unicode')
    return minidom.parseString(xml_str).toprettyxml(indent="    ")

# --- Interfaz Principal ---
def main():
    # Configuración inicial
    config = load_config()
    schemas = {s['nombre']: s for s in config['esquemas']}

    # Sidebar para selección de esquema
    with st.sidebar:
        st.header("Configuración")
        selected_schema = st.selectbox(
            "Tipo de operación:",
            options=list(schemas.keys())
        )

        load_method = st.radio(
            "Fuente del esquema:",
            ["Desde URL", "Desde archivo local"],
            horizontal=True)

        if st.button("Cargar Esquema", type="primary"):
            with st.spinner(f"Cargando {selected_schema}..."):
                try:
                    xsd_source = (
                        schemas[selected_schema]['url'] if load_method == "Desde URL"
                        else schemas[selected_schema]['archivo']
                    )
                    schema = load_xsd(xsd_source)
                    st.session_state.schema = schema
                    st.session_state.root_element = list(schema.elements.keys())[0]
                    st.success(f"✅ {selected_schema} cargado correctamente")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    # Panel principal del formulario
    if 'schema' in st.session_state:
        schema = st.session_state.schema
        root_element = st.session_state.root_element

        st.subheader(f"Formulario para {selected_schema}")

        with st.form("xml_form"):
            # Construir formulario dinámico
            root_schema_element = schema.elements[root_element]
            form_data = build_form(schema, root_schema_element)

            if st.form_submit_button("Generar XML"):
                try:
                    xml_content = generate_xml(schema, root_element, form_data)

                    # Validación del XML
                    validation_errors = schema.validate(BytesIO(xml_content.encode()))
                    if validation_errors is None:
                        st.success("✅ XML generado y validado correctamente")

                        # Mostrar XML
                        with st.expander("Ver XML generado", expanded=True):
                            st.code(xml_content, language='xml')

                        # Descarga del XML
                        st.download_button(
                            label="Descargar XML",
                            data=xml_content,
                            file_name=f"{selected_schema.lower().replace(' ', '_')}.xml",
                            mime="application/xml"
                        )
                    else:
                        st.error("❌ Errores de validación encontrados")
                        for error in validation_errors:
                            st.warning(f"- {error}")
                except Exception as e:
                    st.error(f"❌ Error al generar XML: {str(e)}")

if __name__ == "__main__":
    main()
