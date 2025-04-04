import streamlit as st
from lxml import etree
from datetime import datetime
import xml.etree.ElementTree as ET
from io import StringIO

# Diccionario para almacenar los esquemas cargados
SCHEMAS = {
    "Operaciones de compra/venta de bienes inmuebles": "schema1.xsd",  # Este sería el esquema que proporcionaste
    # Agregar los otros 4 esquemas cuando los tengas
}

def parse_schema(schema_content):
    """Extrae las opciones permitidas de un esquema XSD"""
    options = {}
    root = ET.fromstring(schema_content)
    
    # Extraer enumeraciones para cada elemento
    for elem in root.findall(".//{http://www.w3.org/2001/XMLSchema}element"):
        elem_name = elem.get("name")
        if elem_name:
            restrictions = elem.find(".//{http://www.w3.org/2001/XMLSchema}restriction")
            if restrictions is not None:
                enum_values = [e.get("value") for e in restrictions.findall(".//{http://www.w3.org/2001/XMLSchema}enumeration")]
                if enum_values:
                    options[elem_name] = enum_values
    
    return options

def create_xml_operacion_inmuebles(data):
    """Crea XML para operaciones de compra/venta de bienes inmuebles"""
    root = etree.Element("Operacion")
    operaciones = etree.SubElement(root, "Operaciones_de_compra_yX85Xo_venta_de_bienes_inmuebles", Version="1.0")

    # Datos de la operación
    fecha_operacion = etree.SubElement(operaciones, "Fecha_de_la_operaci93n")
    fecha_operacion.text = data["fecha_operacion"].isoformat()

    tipo_moneda_origen = etree.SubElement(operaciones, "Tipo_de_moneda_de_origen")
    tipo_moneda_origen.text = data["tipo_moneda_origen"]

    if data["tipo_moneda_origen"] == "Otro":
        tipo_moneda_extranjera = etree.SubElement(operaciones, "Tipo_de_moneda_extranjera")
        tipo_moneda_extranjera.text = data["tipo_moneda_extranjera"]
        
        monto_pesos = etree.SubElement(operaciones, "Monto_total_de_la_operaci93n_equivalente_en_Pesos")
        monto_pesos.text = str(data["monto_pesos"])

    monto_total = etree.SubElement(operaciones, "Monto_total_de_la_operaci93n_en_moneda_de_origen")
    monto_total.text = str(data["monto_total_moneda_origen"])

    # Datos del inmueble
    etree.SubElement(operaciones, "Nomenclatura_catastral_o_matr92cula_del_inmueble_transferido").text = data["nomenclatura"]
    etree.SubElement(operaciones, "Provincia_del_inmueble").text = data["provincia"]
    etree.SubElement(operaciones, "Localidad_del_inmueble").text = data["localidad"]
    etree.SubElement(operaciones, "Calle_del_inmueble").text = data["calle"]
    etree.SubElement(operaciones, "N94mero_del_inmueble").text = data["numero"]

    if data["piso"]:
        etree.SubElement(operaciones, "Piso_del_inmueble").text = data["piso"]
    if data["departamento"]:
        etree.SubElement(operaciones, "Departamento_del_inmueble").text = data["departamento"]
    if data["codigo_postal"]:
        etree.SubElement(operaciones, "C93digo_postal_del_inmueble").text = data["codigo_postal"]

    # Formas de pago
    for forma_pago_data in data["formas_pago"]:
        formas_pago_element = etree.SubElement(operaciones, "FORMAS_DE_PAGO")
        forma_de_pago = etree.SubElement(formas_pago_element, "Forma_de_pago")
        forma_de_pago.text = forma_pago_data["forma_de_pago"]

        if forma_pago_data["forma_de_pago"] == "Activo Virtual":
            etree.SubElement(formas_pago_element, "Tipo_de_activo_virtual").text = forma_pago_data["tipo_activo_virtual"]
        elif forma_pago_data["forma_de_pago"] == "Otra":
            etree.SubElement(formas_pago_element, "Otra").text = forma_pago_data["otra"]

        etree.SubElement(formas_pago_element, "Tipo_de_moneda_de_origen_del_pago").text = forma_pago_data["tipo_moneda_pago"]
        
        if forma_pago_data["tipo_moneda_pago"] == "Otro":
            etree.SubElement(formas_pago_element, "Tipo_de_moneda_extranjera_de_origen_del_pago").text = forma_pago_data["tipo_moneda_extranjera_pago"]
            etree.SubElement(formas_pago_element, "Monto_Pagado_de_la_operaci93n_equivalente_en_Pesos").text = str(forma_pago_data["monto_pesos_pago"])

        etree.SubElement(formas_pago_element, "Monto_Pagado_de_la_operaci93n_en_moneda_de_origen").text = str(forma_pago_data["monto_moneda_pago"])

    # Compradores y vendedores
    for persona in data["personas"]:
        persona_element = etree.SubElement(operaciones, "IDENTIFICACI98N_DEL_COMPRADOR_Y_VENDEDOR")
        etree.SubElement(persona_element, "Rol_en_la_Operaci93n88CompradorVendedor").text = persona["rol"]
        etree.SubElement(persona_element, "Tipo_de_Persona88CompradorVendedor").text = persona["tipo"]
        
        if persona["tipo"] == "Persona Humana":
            etree.SubElement(persona_element, "N94mero_de_CUITX85XCUIL88Persona_Humana").text = persona["cuit"]
            etree.SubElement(persona_element, "Apellidos88PersonaHumana").text = persona["apellido"]
            etree.SubElement(persona_element, "Nombres88PersonaHumana").text = persona["nombre"]
            etree.SubElement(persona_element, "Tipo_de_Documento88PersonaHumana").text = persona["tipo_doc"]
            etree.SubElement(persona_element, "N94mero_de_Documento88PersonaHumana").text = persona["nro_doc"]
            etree.SubElement(persona_element, "Nacionalidad88PersonaHumana").text = persona["nacionalidad"]
            etree.SubElement(persona_element, "Fecha_de_nacimiento88PersonaHumana").text = persona["fecha_nacimiento"].isoformat()
            etree.SubElement(persona_element, "Es_PEP88PersonaHumana").text = str(persona["es_pep"]).lower()
            
        elif persona["tipo"] == "Persona Jurídica":
            etree.SubElement(persona_element, "Denominaci93n88Persona_Juridica").text = persona["denominacion"]
            etree.SubElement(persona_element, "N94mero_de_CUITX85XCUIL88Persona_Juridica").text = persona["cuit"]
            
        elif persona["tipo"] == "Persona Humana Extranjera":
            etree.SubElement(persona_element, "N94mero_de_CDI88Persona_Humana").text = persona["cdi"]
            etree.SubElement(persona_element, "Apellidos88PersonaHumanaExtranjera").text = persona["apellido"]
            etree.SubElement(persona_element, "Nombres88PersonaHumanaExtranjera").text = persona["nombre"]
            etree.SubElement(persona_element, "Tipo_de_Documento88PersonaHumanaExtranjera").text = persona["tipo_doc"]
            etree.SubElement(persona_element, "N94mero_de_Documento88PersonaHumanaExtranjera").text = persona["nro_doc"]
            etree.SubElement(persona_element, "Nacionalidad88PersonaHumanaExtranjera").text = persona["nacionalidad"]
            etree.SubElement(persona_element, "Fecha_de_nacimiento88PersonaHumanaExtranjera").text = persona["fecha_nacimiento"].isoformat()
            etree.SubElement(persona_element, "Es_PEP88PersonaHumanaExtranjera").text = str(persona["es_pep"]).lower()
            
        # Campos comunes
        etree.SubElement(persona_element, "Porcentaje88CompradorVendedor").text = persona["porcentaje"]
        etree.SubElement(persona_element, "Pa92s88CompradorVendedor").text = persona["pais"]
        
        if persona["pais"] == "Argentina":
            etree.SubElement(persona_element, "Provincia88CompradorVendedor").text = persona["provincia"]
            etree.SubElement(persona_element, "Localidad88CompradorVendedor").text = persona["localidad"]
        else:
            etree.SubElement(persona_element, "Otro_pa92s88CompradorVendedor").text = persona["otro_pais"]
            etree.SubElement(persona_element, "ProvinciaX85XEstado88CompradorVendedor").text = persona["provincia_extranjera"]
            etree.SubElement(persona_element, "LocalidadX85XCiudad88CompradorVendedor").text = persona["localidad_extranjera"]

        # Dirección
        etree.SubElement(persona_element, "Calle88CompradorVendedor").text = persona["calle"]
        etree.SubElement(persona_element, "N94mero88CompradorVendedor").text = persona["numero"]
        
        if persona["piso"]:
            etree.SubElement(persona_element, "Piso88CompradorVendedor").text = persona["piso"]
        if persona["departamento"]:
            etree.SubElement(persona_element, "Departamento88CompradorVendedor").text = persona["departamento"]
        if persona["codigo_postal"]:
            etree.SubElement(persona_element, "C93digo_Postal88CompradorVendedor").text = persona["codigo_postal"]
        if persona["codigo_area"]:
            etree.SubElement(persona_element, "C93digo_de_90rea_telef93nico88CompradorVendedor").text = persona["codigo_area"]
        if persona["telefono"]:
            etree.SubElement(persona_element, "Tel91fono88CompradorVendedor").text = persona["telefono"]
        if persona["email"]:
            etree.SubElement(persona_element, "Direcci93n_de_correo_electr93nico88CompradorVendedor").text = persona["email"]

    # Rectificación (si aplica)
    if data.get("rectificacion_numero"):
        rectificacion = etree.SubElement(root, "Rectificaci93n_Operaci93n_Original")
        etree.SubElement(rectificacion, "Numero_Control_Operaci93n_Original").text = str(data["rectificacion_numero"])

    return etree.tostring(root, pretty_print=True, encoding="utf-8", xml_declaration=True).decode("utf-8")

def main():
    st.title("Generador de XML para UIF")
    
    # Selección de esquema
    schema_option = st.selectbox("Seleccione el tipo de operación", list(SCHEMAS.keys()))
    
    if schema_option == "Operaciones de compra/venta de bienes inmuebles":
        with st.form("operacion_inmuebles_form"):
            st.header("Datos de la Operación")
            fecha_operacion = st.date_input("Fecha de la operación", datetime.today())
            
            col1, col2 = st.columns(2)
            with col1:
                tipo_moneda_origen = st.selectbox("Tipo de moneda de origen", ["Peso Argentino", "Otro"])
                tipo_moneda_extranjera = ""
                monto_pesos = 0
                
                if tipo_moneda_origen == "Otro":
                    tipo_moneda_extranjera = st.text_input("Tipo de moneda extranjera")
                    monto_pesos = st.number_input("Monto total equivalente en Pesos", value=0)
                
                monto_total_moneda_origen = st.number_input("Monto total en moneda de origen", value=0)
            
            st.header("Datos del Inmueble")
            nomenclatura = st.text_input("Nomenclatura catastral o matrícula")
            
            col1, col2 = st.columns(2)
            with col1:
                provincia = st.selectbox("Provincia", [
                    "CABA", "Buenos Aires", "Catamarca", "Córdoba", "Corrientes", "Chaco", 
                    "Chubut", "Entre Ríos", "Formosa", "Jujuy", "La Pampa", "La Rioja", 
                    "Mendoza", "Misiones", "Neuquén", "Río Negro", "Salta", "San Juan", 
                    "San Luis", "Santa Cruz", "Santa Fé", "Santiago Del Estero", "Tucumán", 
                    "Tierra del Fuego"
                ])
                localidad = st.text_input("Localidad")
            with col2:
                calle = st.text_input("Calle")
                numero = st.text_input("Número")
            
            piso = st.text_input("Piso (opcional)")
            departamento = st.text_input("Departamento (opcional)")
            codigo_postal = st.text_input("Código postal (opcional)")
            
            # Formas de pago
            st.header("Formas de Pago")
            formas_pago = []
            
            if st.button("Agregar Forma de Pago"):
                formas_pago.append({
                    "forma_de_pago": "Efectivo",
                    "tipo_activo_virtual": "",
                    "otra": "",
                    "tipo_moneda_pago": "Peso Argentino",
                    "tipo_moneda_extranjera_pago": "",
                    "monto_pesos_pago": 0,
                    "monto_moneda_pago": 0
                })
            
            for i, fp in enumerate(formas_pago):
                st.subheader(f"Forma de Pago {i+1}")
                with st.expander(f"Forma de Pago {i+1}", expanded=True):
                    fp["forma_de_pago"] = st.selectbox(
                        "Forma de pago", 
                        ["Efectivo", "Transferencia", "Cheque", "Activo Virtual", "Otra"],
                        key=f"forma_pago_{i}"
                    )
                    
                    if fp["forma_de_pago"] == "Activo Virtual":
                        fp["tipo_activo_virtual"] = st.text_input(
                            "Tipo de activo virtual",
                            key=f"tipo_activo_{i}"
                        )
                    elif fp["forma_de_pago"] == "Otra":
                        fp["otra"] = st.text_input(
                            "Otra forma de pago",
                            key=f"otra_pago_{i}"
                        )
                    
                    fp["tipo_moneda_pago"] = st.selectbox(
                        "Tipo de moneda de origen del pago",
                        ["Peso Argentino", "Otro"],
                        key=f"tipo_moneda_pago_{i}"
                    )
                    
                    if fp["tipo_moneda_pago"] == "Otro":
                        fp["tipo_moneda_extranjera_pago"] = st.text_input(
                            "Tipo de moneda extranjera",
                            key=f"moneda_extranjera_{i}"
                        )
                        fp["monto_pesos_pago"] = st.number_input(
                            "Monto equivalente en Pesos",
                            value=0,
                            key=f"monto_pesos_{i}"
                        )
                    
                    fp["monto_moneda_pago"] = st.number_input(
                        "Monto pagado en moneda de origen",
                        value=0,
                        key=f"monto_moneda_{i}"
                    )
            
            # Compradores y vendedores
            st.header("Compradores y Vendedores")
            personas = []
            
            if st.button("Agregar Persona"):
                personas.append({
                    "rol": "Comprador",
                    "tipo": "Persona Humana",
                    "cuit": "",
                    "apellido": "",
                    "nombre": "",
                    "tipo_doc": "Documento Nacional de Identidad",
                    "nro_doc": "",
                    "nacionalidad": "Argentina",
                    "fecha_nacimiento": datetime.today(),
                    "es_pep": False,
                    "denominacion": "",
                    "cdi": "",
                    "porcentaje": "100",
                    "pais": "Argentina",
                    "provincia": "CABA",
                    "localidad": "",
                    "otro_pais": "",
                    "provincia_extranjera": "",
                    "localidad_extranjera": "",
                    "calle": "",
                    "numero": "",
                    "piso": "",
                    "departamento": "",
                    "codigo_postal": "",
                    "codigo_area": "",
                    "telefono": "",
                    "email": ""
                })
            
            for i, persona in enumerate(personas):
                st.subheader(f"Persona {i+1}")
                with st.expander(f"Persona {i+1}", expanded=True):
                    persona["rol"] = st.selectbox(
                        "Rol",
                        ["Comprador", "Vendedor"],
                        key=f"rol_{i}"
                    )
                    
                    persona["tipo"] = st.selectbox(
                        "Tipo de persona",
                        ["Persona Humana", "Persona Jurídica", "Persona Humana Extranjera"],
                        key=f"tipo_persona_{i}"
                    )
                    
                    if persona["tipo"] == "Persona Humana":
                        col1, col2 = st.columns(2)
                        with col1:
                            persona["cuit"] = st.text_input(
                                "CUIT/CUIL",
                                value="99-99999999-9",
                                key=f"cuit_{i}"
                            )
                            persona["apellido"] = st.text_input(
                                "Apellidos",
                                key=f"apellido_{i}"
                            )
                            persona["nombre"] = st.text_input(
                                "Nombres",
                                key=f"nombre_{i}"
                            )
                        with col2:
                            persona["tipo_doc"] = st.selectbox(
                                "Tipo de documento",
                                ["Documento Nacional de Identidad", "Libreta de Enrolamiento", 
                                 "Libreta Cívica", "Cédula Mercosur", "Pasaporte"],
                                key=f"tipo_doc_{i}"
                            )
                            persona["nro_doc"] = st.text_input(
                                "Número de documento",
                                key=f"nro_doc_{i}"
                            )
                            persona["nacionalidad"] = st.text_input(
                                "Nacionalidad",
                                value="Argentina",
                                key=f"nacionalidad_{i}"
                            )
                        
                        persona["fecha_nacimiento"] = st.date_input(
                            "Fecha de nacimiento",
                            datetime.today(),
                            key=f"fecha_nac_{i}"
                        )
                        persona["es_pep"] = st.checkbox(
                            "Es PEP",
                            key=f"pep_{i}"
                        )
                    
                    elif persona["tipo"] == "Persona Jurídica":
                        persona["denominacion"] = st.text_input(
                            "Denominación",
                            key=f"denominacion_{i}"
                        )
                        persona["cuit"] = st.text_input(
                            "CUIT",
                            key=f"cuit_juridica_{i}"
                        )
                    
                    elif persona["tipo"] == "Persona Humana Extranjera":
                        col1, col2 = st.columns(2)
                        with col1:
                            persona["cdi"] = st.text_input(
                                "CDI",
                                key=f"cdi_{i}"
                            )
                            persona["apellido"] = st.text_input(
                                "Apellidos",
                                key=f"apellido_ext_{i}"
                            )
                            persona["nombre"] = st.text_input(
                                "Nombres",
                                key=f"nombre_ext_{i}"
                            )
                        with col2:
                            persona["tipo_doc"] = st.selectbox(
                                "Tipo de documento",
                                ["Documento Nacional de Identidad", "Libreta de Enrolamiento", 
                                 "Libreta Cívica", "Cédula Mercosur", "Pasaporte"],
                                key=f"tipo_doc_ext_{i}"
                            )
                            persona["nro_doc"] = st.text_input(
                                "Número de documento",
                                key=f"nro_doc_ext_{i}"
                            )
                            persona["nacionalidad"] = st.text_input(
                                "Nacionalidad",
                                key=f"nacionalidad_ext_{i}"
                            )
                        
                        persona["fecha_nacimiento"] = st.date_input(
                            "Fecha de nacimiento",
                            datetime.today(),
                            key=f"fecha_nac_ext_{i}"
                        )
                        persona["es_pep"] = st.checkbox(
                            "Es PEP",
                            key=f"pep_ext_{i}"
                        )
                    
                    # Datos comunes
                    persona["porcentaje"] = st.text_input(
                        "Porcentaje",
                        value="100",
                        key=f"porcentaje_{i}"
                    )
                    
                    persona["pais"] = st.selectbox(
                        "País",
                        ["Argentina", "Otro"],
                        key=f"pais_{i}"
                    )
                    
                    if persona["pais"] == "Argentina":
                        col1, col2 = st.columns(2)
                        with col1:
                            persona["provincia"] = st.selectbox(
                                "Provincia",
                                ["CABA", "Buenos Aires", "Catamarca", "Córdoba", "Corrientes"],
                                key=f"provincia_{i}"
                            )
                        with col2:
                            persona["localidad"] = st.text_input(
                                "Localidad",
                                key=f"localidad_{i}"
                            )
                    else:
                        persona["otro_pais"] = st.text_input(
                            "Otro país",
                            key=f"otro_pais_{i}"
                        )
                        persona["provincia_extranjera"] = st.text_input(
                            "Provincia/Estado",
                            key=f"provincia_ext_{i}"
                        )
                        persona["localidad_extranjera"] = st.text_input(
                            "Localidad/Ciudad",
                            key=f"localidad_ext_{i}"
                        )
                    
                    # Dirección
                    st.subheader("Dirección")
                    col1, col2 = st.columns(2)
                    with col1:
                        persona["calle"] = st.text_input(
                            "Calle",
                            key=f"calle_dir_{i}"
                        )
                    with col2:
                        persona["numero"] = st.text_input(
                            "Número",
                            key=f"numero_dir_{i}"
                        )
                    
                    persona["piso"] = st.text_input(
                        "Piso (opcional)",
                        key=f"piso_{i}"
                    )
                    persona["departamento"] = st.text_input(
                        "Departamento (opcional)",
                        key=f"depto_{i}"
                    )
                    persona["codigo_postal"] = st.text_input(
                        "Código postal (opcional)",
                        key=f"cp_{i}"
                    )
                    
                    # Contacto
                    st.subheader("Contacto")
                    col1, col2 = st.columns(2)
                    with col1:
                        persona["codigo_area"] = st.text_input(
                            "Código de área (opcional)",
                            key=f"cod_area_{i}"
                        )
                    with col2:
                        persona["telefono"] = st.text_input(
                            "Teléfono (opcional)",
                            key=f"telefono_{i}"
                        )
                    
                    persona["email"] = st.text_input(
                        "Email (opcional)",
                        key=f"email_{i}"
                    )
            
            # Rectificación
            st.header("Rectificación (opcional)")
            rectificacion_numero = st.number_input(
                "Número de control de operación original",
                min_value=0,
                value=0
            )
            
            submitted = st.form_submit_button("Generar XML")
            
            if submitted:
                data = {
                    "fecha_operacion": fecha_operacion,
                    "tipo_moneda_origen": tipo_moneda_origen,
                    "tipo_moneda_extranjera": tipo_moneda_extranjera,
                    "monto_pesos": monto_pesos,
                    "monto_total_moneda_origen": monto_total_moneda_origen,
                    "nomenclatura": nomenclatura,
                    "provincia": provincia,
                    "localidad": localidad,
                    "calle": calle,
                    "numero": numero,
                    "piso": piso,
                    "departamento": departamento,
                    "codigo_postal": codigo_postal,
                    "formas_pago": formas_pago,
                    "personas": personas
                }
                
                if rectificacion_numero > 0:
                    data["rectificacion_numero"] = rectificacion_numero
                
                xml_output = create_xml_operacion_inmuebles(data)
                
                st.success("XML generado correctamente!")
                st.download_button(
                    label="Descargar XML",
                    data=xml_output.encode('utf-8'),
                    file_name="operacion_inmueble.xml",
                    mime="application/xml"
                )
                
                st.code(xml_output, language="xml")

if __name__ == "__main__":
    main()
