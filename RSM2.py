import streamlit as st
from lxml import etree
from datetime import datetime

def create_xml(data):
    root = etree.Element("Operacion")
    
    # Reporte de Registración y Cumplimiento
    reporte = etree.SubElement(root, "Reporte_de_Registraci93n_y_Cumplimiento")
    reporte.set("Version", "1.2")
    
    # Datos básicos
    etree.SubElement(reporte, "Nombre_o_Raz93n_Social").text = data["nombre_razon_social"]
    etree.SubElement(reporte, "Tipo_Persona").text = data["tipo_persona"]
    
    # Campos condicionales para Persona Física
    if data["tipo_persona"] == "Persona Física":
        etree.SubElement(reporte, "Apellido").text = data["apellido"]
    
    etree.SubElement(reporte, "Nro_de_CUIT_CUIL").text = data["cuit"]
    
    # Datos de dirección
    etree.SubElement(reporte, "Calle").text = data["calle"]
    etree.SubElement(reporte, "Nro").text = str(data["numero"])
    
    if data.get("piso"):
        etree.SubElement(reporte, "Piso").text = data["piso"]
    if data.get("departamento"):
        etree.SubElement(reporte, "Departamento").text = data["departamento"]
    
    etree.SubElement(reporte, "Localidad").text = data["localidad"]
    
    if data.get("codigo_postal"):
        etree.SubElement(reporte, "C93digo_Postal").text = data["codigo_postal"]
    
    etree.SubElement(reporte, "Provincia").text = data["provincia"]
    etree.SubElement(reporte, "Pa92s").text = data["pais"]
    
    # Tipo de Sujeto
    etree.SubElement(reporte, "Tipo_de_Sujeto").text = data["tipo_sujeto"]
    
    # Sujeto no cumplió
    etree.SubElement(reporte, "Sujeto_no_cumplio_con_la_presentaci93n_de").text = data["incumplimiento"]
    
    # Rectificación (si aplica)
    if data.get("rectificacion_numero"):
        rectificacion = etree.SubElement(root, "Rectificaci93n_Operaci93n_Original")
        etree.SubElement(rectificacion, "Numero_Control_Operaci93n_Original").text = str(data["rectificacion_numero"])
    
    return etree.tostring(root, pretty_print=True, encoding="utf-8", xml_declaration=True).decode("utf-8")

def main():
    st.title("Generador de XML para Reporte de Registración y Cumplimiento")
    
    with st.form("datos_form"):
        st.header("Datos Básicos")
        nombre_razon_social = st.text_input("Nombre o Razón Social*")
        tipo_persona = st.selectbox("Tipo de Persona*", ["Persona Jurídica", "Persona Física"])
        
        apellido = ""
        if tipo_persona == "Persona Física":
            apellido = st.text_input("Apellido*")
        
        cuit = st.text_input("Número de CUIT/CUIL* (Formato: 99-99999999-9)", value="99-99999999-9")
        
        st.header("Datos de Dirección")
        calle = st.text_input("Calle*")
        numero = st.number_input("Número*", min_value=1, value=1)
        piso = st.text_input("Piso (opcional)")
        departamento = st.text_input("Departamento (opcional)")
        localidad = st.text_input("Localidad*")
        codigo_postal = st.text_input("Código Postal (opcional)")
        
        provincia = st.selectbox("Provincia*", [
            "CABA", "Buenos Aires", "Catamarca", "Córdoba", "Corrientes", "Chaco", 
            "Chubut", "Entre Ríos", "Formosa", "Jujuy", "La Pampa", "La Rioja", 
            "Mendoza", "Misiones", "Neuquén", "Río Negro", "Salta", "San Juan", 
            "San Luis", "Santa Cruz", "Santa Fé", "Santiago Del Estero", "Tucumán", 
            "Tierra del Fuego"
        ])
        
        pais = st.selectbox("País*", ["Argentina", "Estados Unidos", "Brasil", "Chile", "Uruguay", "Otro"])
        
        st.header("Datos Específicos")
        tipo_sujeto = st.selectbox("Tipo de Sujeto*", [
            "AFIP - Administración Federal de Ingresos Públicos",
            "BCRA - Banco Central de la Rep. Argentina",
            "CNV - Comisión Nacional de Valores",
            "Entidades Financieras, cambiarias y otros - Casas de cambio (Ley 18.924)",
            "Entidades Financieras, cambiarias y otros - Entidades Financieras",
            "Profesionales matriculados cuyas actividades estén reguladas por los cjos. profesionales de C. Económicas - Contadores"
        ])
        
        incumplimiento = st.selectbox("Sujeto no cumplió con la presentación de*", [
            "Declaración Jurada de Cumplimiento de la Normativa",
            "Constancia de Inscripción ante la UIF"
        ])
        
        st.header("Rectificación (opcional)")
        rectificacion_numero = st.number_input("Número de Control de Operación Original (si aplica)", min_value=0, value=0)
        
        submitted = st.form_submit_button("Generar XML")
        
        if submitted:
            if not nombre_razon_social or not cuit or not calle or not localidad:
                st.error("Por favor complete todos los campos obligatorios (*)")
            else:
                data = {
                    "nombre_razon_social": nombre_razon_social,
                    "tipo_persona": tipo_persona,
                    "apellido": apellido,
                    "cuit": cuit,
                    "calle": calle,
                    "numero": numero,
                    "piso": piso,
                    "departamento": departamento,
                    "localidad": localidad,
                    "codigo_postal": codigo_postal,
                    "provincia": provincia,
                    "pais": pais,
                    "tipo_sujeto": tipo_sujeto,
                    "incumplimiento": incumplimiento,
                }
                
                if rectificacion_numero > 0:
                    data["rectificacion_numero"] = rectificacion_numero
                
                xml_output = create_xml(data)
                
                st.success("XML generado correctamente!")
                st.download_button(
                    label="Descargar XML",
                    data=xml_output.encode('utf-8'),
                    file_name="reporte_registracion.xml",
                    mime="application/xml"
                )
                
                st.code(xml_output, language="xml")

if __name__ == "__main__":
    main()
