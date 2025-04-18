import streamlit as st
import xmlschema
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from datetime import datetime
import json

# Configuración de la aplicación
st.set_page_config(page_title="Generador XML Universal", layout="wide")
st.title("📋 Generador de XML para Múltiples Esquemas")

# --- Funciones de Utilidad Mejoradas ---
def get_element_type(element):
    """Obtiene el tipo de elemento XSD de manera segura para cualquier versión de xmlschema"""
    if hasattr(element, 'type'):
        if element.type.is_simple():
            base_type = str(getattr(element.type, 'base_type', 'string'))
            if 'long' in base_type.lower():
                return 'long'
            elif 'int' in base_type.lower():
                return 'int'
            elif 'dateTime' in base_type:
                return 'dateTime'
            elif 'date' in base_type:
                return 'date'
            elif 'boolean' in base_type:
                return 'boolean'
            elif 'decimal' in base_type or 'float' in base_type or 'double' in base_type:
                return 'decimal'
        return 'complex'
    return 'string'

def format_xml_value(value, xsd_type):
    """Formatea valores para XML según su tipo XSD"""
    if value is None or value == "":
        return None
    
    if xsd_type in {'decimal', 'float', 'double'}:
        return f"{float(value):.2f}"
    elif xsd_type in {'long', 'int', 'integer'}:
        return str(int(value))
    elif xsd_type == 'date':
        if isinstance(value, str):
            try:
                day, month, year = map(int, value.split('/'))
                return f"{year:04d}-{month:02d}-{day:02d}"
            except:
                return None
        else:
            return value.strftime("%Y-%m-%d")
    elif xsd_type == 'dateTime':
        if isinstance(value, str):
            try:
                if ' ' in value:
                    date_part, time_part = value.split(' ')
                    day, month, year = map(int, date_part.split('/'))
                    hours, minutes = map(int, time_part.split(':'))
                    return f"{year:04d}-{month:02d}-{day:02d}T{hours:02d}:{minutes:02d}:00"
                else:
                    day, month, year = map(int, value.split('/'))
                    return f"{year:04d}-{month:02d}-{day:02d}T00:00:00"
            except:
                return None
        else:
            return value.isoformat()
    elif xsd_type == 'boolean':
        return str(value).lower()
    return str(value)

# --- Carga de Esquemas Mejorada ---
def load_config():
    try:
        with open('config/esquemas.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"❌ Error al cargar configuración: {str(e)}")
        st.stop()

def load_xsd(xsd_path):
    try:
        return xmlschema.XMLSchema(xsd_path)
    except Exception as e:
        st.error(f"❌ Error al cargar XSD: {str(e)}")
        st.stop()

# --- Generación de Formularios Adaptable ---
def create_input_field(element, path="", parent_element=None):
    """Crea campos de entrada según el tipo XSD con manejo de atributos"""
    try:
        field_id = f"{path}_{element.name}" if path else element.name
        label = element.name.replace('_', ' ').title()
        xsd_type = get_element_type(element)

        # Determinar si el campo es obligatorio
        is_required = getattr(element, 'min_occurs', 0) > 0 or (
            hasattr(element, 'is_nillable') and not element.is_nillable())

        # Campos con enumeraciones (dropdowns)
        if hasattr(element.type, 'enumeration') and element.type.enumeration:
            try:
                options = [str(e.value) if hasattr(e, 'value') else str(e) for e in element.type.enumeration]
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

        # Campos según tipo XSD
        if xsd_type in {'decimal', 'float', 'double'}:
            return st.number_input(
                label,
                value=0.0 if is_required else None,
                step=0.01,
                format="%.2f",
                key=field_id
            )
        elif xsd_type in {'long', 'int', 'integer'}:
            return st.number_input(
                label,
                value=0 if is_required else None,
                step=1,
                key=field_id
            )
        elif xsd_type == 'date':
            return st.text_input(
                label + " (dd/mm/yyyy)",
                value=datetime.now().strftime("%d/%m/%Y") if is_required else "",
                placeholder="dd/mm/yyyy",
                key=field_id
            )
        elif xsd_type == 'dateTime':
            return st.text_input(
                label + " (dd/mm/yyyy hh:mm)",
                value=datetime.now().strftime("%d/%m/%Y %H:%M") if is_required else "",
                placeholder="dd/mm/yyyy hh:mm",
                key=field_id
            )
        elif xsd_type == 'boolean':
            return st.checkbox(
                label, 
                value=False if is_required else None,
                key=field_id
            )
        else:
            return st.text_input(
                label, 
                value="" if is_required else None,
                key=field_id
            )
    except Exception as e:
        st.error(f"Error al crear campo para {element.name}: {str(e)}")
        return st.text_input(label if 'label' in locals() else element.name, key=field_id)

def build_universal_form(schema, element, path="", parent_element=None):
    """Construye formulario adaptable a cualquier esquema XSD"""
    form_data = {}
    current_path = f"{path}_{element.name}" if path else element.name

    # Manejar atributos requeridos
    if hasattr(element.type, 'attributes'):
        for attr_name, attr in element.type.attributes.items():
            if attr.use == 'required':
                # Crear campo para el atributo (prefijado con @)
                attr_field_id = f"{current_path}_@{attr_name}"
                default_value = attr.fixed if hasattr(attr, 'fixed') else "1.0"
                
                st.text_input(f"Atributo {attr_name} (requerido)", 
                            value=default_value,
                            key=attr_field_id)
                
                form_data[f"@{attr_name}"] = st.session_state.get(attr_field_id, default_value)

    # Construir campos normales
    if element.type.is_complex():
        for child in element.type.content_type.iter_elements():
            if child.type.is_simple():
                value = create_input_field(child, current_path, element)
                if value is not None and value != "":
                    form_data[child.name] = value
            else:
                child_data = build_universal_form(schema, child, current_path, element)
                if child_data:
                    form_data[child.name] = child_data
    else:
        value = create_input_field(element, current_path, parent_element)
        if value is not None and value != "":
            form_data[element.name] = value

    return form_data

# --- Generación de XML Universal ---
def generate_universal_xml(schema, root_name, form_data):
    """Genera XML válido para cualquier esquema XSD"""
    def add_element(parent, name, value, element_def=None):
        if isinstance(value, dict):
            node = SubElement(parent, name)
            
            # Primero procesar atributos
            for k, v in value.items():
                if k.startswith('@'):  # Es un atributo
                    node.set(k[1:], str(v))
            
            # Luego elementos normales
            for k, v in value.items():
                if not k.startswith('@'):
                    child_element = schema.elements.get(f"{name}_{k}") if schema else None
                    add_element(node, k, v, child_element)
        else:
            element = SubElement(parent, name)
            if value is not None and str(value) != "":
                xsd_type = get_element_type(element_def) if element_def else None
                formatted_value = format_xml_value(value, xsd_type)
                if formatted_value is not None:
                    element.text = formatted_value

    # 1. Analizar el esquema para determinar la estructura requerida
    root_element = schema.elements[root_name]
    
    # 2. Crear el elemento raíz del tipo específico
    main_root = Element(root_name)
    
    # 3. Si el esquema espera un envoltorio Operacion, lo creamos
    needs_operacion_wrapper = any(
        name.startswith('Operacion') 
        for name in schema.elements.keys() 
        if name != root_name
    )
    
    if needs_operacion_wrapper:
        # Crear el envoltorio Operacion con atributo Version
        operacion_root = Element("Operacion")
        operacion_root.set("Version", "1.0")
        operacion_root.append(main_root)
        final_root = operacion_root
    else:
        # Si no necesita envoltorio, usar el elemento principal directamente
        # pero verificar si necesita atributos
        if hasattr(root_element.type, 'attributes'):
            for attr_name, attr in root_element.type.attributes.items():
                if attr.use == 'required':
                    main_root.set(attr_name, attr.fixed if hasattr(attr, 'fixed') else "1.0")
        final_root = main_root
    
    # 4. Añadir el contenido principal del formulario
    for field, value in form_data.items():
        if not field.startswith('@'):  # Los atributos ya se manejan aparte
            schema_element = next(
                (e for e in root_element.type.content_type.iter_elements()
                 if e.name == field), None)
            add_element(main_root, field, value, schema_element)
    
    # 5. Generar el XML final
    xml_str = tostring(final_root, encoding='unicode')
    return minidom.parseString(xml_str).toprettyxml(indent="    ")

# --- Interfaz Principal Mejorada ---
def main():
    config = load_config()
    schemas = {s['nombre']: s for s in config['esquemas']}

    with st.sidebar:
        st.header("Configuración")
        selected_schema = st.selectbox(
            "Seleccione el tipo de operación:",
            options=list(schemas.keys())
        )

        if st.button("Cargar Esquema", type="primary"):
            with st.spinner(f"Cargando {selected_schema}..."):
                try:
                    schema_config = schemas[selected_schema]
                    schema = load_xsd(schema_config['url'] if schema_config.get('url') else schema_config['archivo'])
                    
                    st.session_state.schema = schema
                    st.session_state.root_element = list(schema.elements.keys())[0]
                    
                    # Mostrar información del esquema
                    root_elem = schema.elements[st.session_state.root_element]
                    if hasattr(root_elem.type, 'attributes'):
                        required_attrs = [f"{name} (valor fijo: {attr.fixed})" 
                                         for name, attr in root_elem.type.attributes.items() 
                                         if attr.use == 'required']
                        if required_attrs:
                            st.info("Atributos requeridos en el elemento raíz:\n- " + "\n- ".join(required_attrs))
                    
                    st.success(f"✅ {selected_schema} cargado correctamente")
                except Exception as e:
                    st.error(f"❌ Error al cargar esquema: {str(e)}")

    if 'schema' in st.session_state:
        schema = st.session_state.schema
        root_element = st.session_state.root_element

        st.subheader(f"Formulario para {selected_schema}")
        
        with st.form("xml_form"):
            form_data = build_universal_form(schema, schema.elements[root_element])
            
            if st.form_submit_button("Generar XML"):
                try:
                    xml_content = generate_universal_xml(schema, root_element, form_data)
                    
                    # Validación estricta
                    validation_errors = schema.validate(xml_content)
                    if validation_errors is None:
                        st.success("✅ XML generado y validado correctamente")
                        
                        with st.expander("Ver XML generado", expanded=True):
                            st.code(xml_content, language='xml')
                        
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
