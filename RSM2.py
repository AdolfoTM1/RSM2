import streamlit as st
from lxml import etree
from datetime import datetime

def create_xml(data):
    root = etree.Element("Operacion")
    operaciones = etree.SubElement(root, "Operaciones_de_compra_yX85Xo_venta_de_bienes_inmuebles", Version="1.0")

    # Datos de la operación
    fecha_operacion = etree.SubElement(operaciones, "Fecha_de_la_operaci93n")
    fecha_formateada = data["fecha_operacion"].strftime("%d/%m/%Y")
    fecha_operacion.text = fecha_formateada

    tipo_moneda_origen = etree.SubElement(operaciones, "Tipo_de_moneda_de_origen")
    tipo_moneda_origen.text = data["tipo_moneda_origen"]



    if data["tipo_moneda_origen"] == "Otro":
        tipo_moneda_extranjera = etree.SubElement(operaciones, "Tipo_de_moneda_extranjera")
        tipo_moneda_extranjera.text = data["tipo_moneda_extranjera"]
        monto_pesos = etree.SubElement(operaciones, "Monto_total_de_la_operaci93n_equivalente_en_Pesos")
        monto_pesos.text = str(data["monto_pesos"])

    monto_total_moneda_origen = etree.SubElement(operaciones, "Monto_total_de_la_operaci93n_en_moneda_de_origen")
    monto_total_moneda_origen.text = str(data["monto_total_moneda_origen"])

    nomenclatura = etree.SubElement(operaciones, "Nomenclatura_catastral_o_matr92cula_del_inmueble_transferido")
    nomenclatura.text = data["nomenclatura"]

    provincia = etree.SubElement(operaciones, "Provincia_del_inmueble")
    provincia.text = data["provincia"]

    localidad = etree.SubElement(operaciones, "Localidad_del_inmueble")
    localidad.text = data["localidad"]

    calle = etree.SubElement(operaciones, "Calle_del_inmueble")
    calle.text = data["calle"]

    numero = etree.SubElement(operaciones, "N94mero_del_inmueble")
    numero.text = data["numero"]

    if data["piso"]:
        piso = etree.SubElement(operaciones, "Piso_del_inmueble")
        piso.text = data["piso"]
    if data["departamento"]:
        departamento = etree.SubElement(operaciones, "Departamento_del_inmueble")
        departamento.text = data["departamento"]
    if data["codigo_postal"]:
        codigo_postal = etree.SubElement(operaciones, "C93digo_postal_del_inmueble")
        codigo_postal.text = data["codigo_postal"]

    # Continuará en la Parte 2...
  # Formas de pago
    for forma_pago_data in data["formas_pago"]:
        formas_pago_element = etree.SubElement(operaciones, "FORMAS_DE_PAGO")
        forma_de_pago = etree.SubElement(formas_pago_element, "Forma_de_pago")
        forma_de_pago.text = forma_pago_data["forma_de_pago"]

        if forma_pago_data["forma_de_pago"] == "Activo Virtual":
            tipo_activo_virtual = etree.SubElement(formas_pago_element, "Tipo_de_activo_virtual")
            tipo_activo_virtual.text = forma_pago_data["tipo_activo_virtual"]
        if forma_pago_data["forma_de_pago"] == "Otra":
            otra = etree.SubElement(formas_pago_element, "Otra")
            otra.text = forma_pago_data["otra"]

        tipo_moneda_pago = etree.SubElement(formas_pago_element, "Tipo_de_moneda_de_origen_del_pago")
        tipo_moneda_pago.text = forma_pago_data["tipo_moneda_pago"]
        if forma_pago_data["tipo_moneda_pago"] == "Otro":
            tipo_moneda_extranjera_pago = etree.SubElement(formas_pago_element, "Tipo_de_moneda_extranjera_de_origen_del_pago")
            tipo_moneda_extranjera_pago.text = forma_pago_data["tipo_moneda_extranjera_pago"]
            monto_pesos_pago = etree.SubElement(formas_pago_element, "Monto_Pagado_de_la_operaci93n_equivalente_en_Pesos")
            monto_pesos_pago.text = str(forma_pago_data["monto_pesos_pago"])

        monto_moneda_pago = etree.SubElement(formas_pago_element, "Monto_Pagado_de_la_operaci93n_en_moneda_de_origen")
        monto_moneda_pago.text = str(forma_pago_data["monto_moneda_pago"])

    # Continuará en la Parte 3...

# Compradores y vendedores
    for persona in data["personas"]:
        persona_element = etree.SubElement(operaciones, "IDENTIFICACI98N_DEL_COMPRADOR_Y_VENDEDOR")
        etree.SubElement(persona_element, "Rol_en_la_Operaci93n88CompradorVendedor").text = persona["rol"]
        etree.SubElement(persona_element, "Tipo_de_Persona88CompradorVendedor").text = persona["tipo"]
        # Aquí se deben agregar el resto de los campos de la persona
        if persona["tipo"] == "Persona Humana":
          etree.SubElement(persona_element, "N94mero_de_CUITX85XCUIL88Persona_Humana").text = persona["cuit"]
          etree.SubElement(persona_element, "Apellidos88PersonaHumana").text = persona["apellido"]
          etree.SubElement(persona_element, "Nombres88PersonaHumana").text = persona["nombre"]
          etree.SubElement(persona_element, "Tipo_de_Documento88PersonaHumana").text = persona["tipo_doc"]
          etree.SubElement(persona_element, "N94mero_de_Documento88PersonaHumana").text = persona["nro_doc"]
          etree.SubElement(persona_element, "Nacionalidad88PersonaHumana").text = persona["nacionalidad"]
          etree.SubElement(persona_element, "Fecha_de_nacimiento88PersonaHumana").text = persona["fecha_nacimiento"].isoformat()
          etree.SubElement(persona_element, "Es_PEP88PersonaHumana").text = str(persona["es_pep"])
          etree.SubElement(persona_element, "Porcentaje88CompradorVendedor").text = persona["porcentaje"]
          etree.SubElement(persona_element, "Pa92s88CompradorVendedor").text = persona["pais"]
          if persona["pais"] == "Argentina":
              etree.SubElement(persona_element, "Provincia88CompradorVendedor").text = persona["provincia"]
              etree.SubElement(persona_element, "Localidad88CompradorVendedor").text = persona["localidad"]
          else:
              etree.SubElement(persona_element, "Otro_pa92s88CompradorVendedor").text = persona["otro_pais"]
              etree.SubElement(persona_element, "ProvinciaX85XEstado88CompradorVendedor").text = persona["provincia_extranjera"]
              etree.SubElement(persona_element, "LocalidadX85XCiudad88CompradorVendedor").text = persona["localidad_extranjera"]

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
        elif persona["tipo"] == "Persona Jurídica":
          etree.SubElement(persona_element, "Denominaci93n88Persona_Juridica").text = persona["denominacion"]
          etree.SubElement(persona_element, "N94mero_de_CUITX85XCUIL88Persona_Juridica").text = persona["cuit"]
          etree.SubElement(persona_element, "Porcentaje88CompradorVendedor").text = persona["porcentaje"]
          etree.SubElement(persona_element, "Pa92s88CompradorVendedor").text = persona["pais"]

          if persona["pais"] == "Argentina":
              etree.SubElement(persona_element, "Provincia88CompradorVendedor").text = persona["provincia"]
              etree.SubElement(persona_element, "Localidad88CompradorVendedor").text = persona["localidad"]
          else:
              etree.SubElement(persona_element, "Otro_pa92s88CompradorVendedor").text = persona["otro_pais"]
              etree.SubElement(persona_element, "ProvinciaX85XEstado88CompradorVendedor").text = persona["provincia_extranjera"]
              etree.SubElement(persona_element, "LocalidadX85XCiudad88CompradorVendedor").text = persona["localidad_extranjera"]

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
        elif persona["tipo"] == "Persona Humana Extranjera":
          etree.SubElement(persona_element, "N94mero_de_CDI88Persona_Humana").text = persona["cdi"]
          etree.SubElement(persona_element, "Apellidos88PersonaHumanaExtranjera").text = persona["apellido"]
          etree.SubElement(persona_element, "Nombres88PersonaHumanaExtranjera").text = persona["nombre"]
          etree.SubElement(persona_element, "Tipo_de_Documento88PersonaHumanaExtranjera").text = persona["tipo_doc"]
          etree.SubElement(persona_element, "N94mero_de_Documento88PersonaHumanaExtranjera").text = persona["nro_doc"]
          etree.SubElement(persona_element, "Nacionalidad88PersonaHumanaExtranjera").text = persona["nacionalidad"]
          etree.SubElement(persona_element, "Fecha_de_nacimiento88PersonaHumanaExtranjera").text = persona["fecha_nacimiento"].isoformat()
          etree.SubElement(persona_element, "Es_PEP88PersonaHumanaExtranjera").text = str(persona["es_pep"])
          etree.SubElement(persona_element, "Porcentaje88CompradorVendedor").text = persona["porcentaje"]
          etree.SubElement(persona_element, "Pa92s88CompradorVendedor").text = persona["pais"]
          if persona["pais"] == "Argentina":
              etree.SubElement(persona_element, "Provincia88CompradorVendedor").text = persona["provincia"]
              etree.SubElement(persona_element, "Localidad88CompradorVendedor").text = persona["localidad"]
          else:
              etree.SubElement(persona_element, "Otro_pa92s88CompradorVendedor").text = persona["otro_pais"]
              etree.SubElement(persona_element, "ProvinciaX85XEstado88CompradorVendedor").text = persona["provincia_extranjera"]
              etree.SubElement(persona_element, "LocalidadX85XCiudad88CompradorVendedor").text = persona["localidad_extranjera"]
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

    return etree.tostring(root, pretty_print=True, encoding="utf-8").decode("utf-8")

def main():
    st.title("Generador de XML de Operaciones Inmobiliarias")

    # Datos de la operación
    st.header("Datos de la Operación")
    fecha_operacion = st.date_input("Fecha de la operación", datetime.today())
    tipo_moneda_origen = st.selectbox("Tipo de moneda de origen", ["Elegir...", "Peso Argentino", "Otro"])
    tipo_moneda_extranjera = st.text_input("Tipo de moneda extranjera (si aplica)")
    monto_pesos = st.number_input("Monto total en pesos (si aplica)", value=0)
    monto_total_moneda_origen = st.number_input("Monto total en moneda de origen", value=0)
    nomenclatura = st.text_input("Nomenclatura catastral o matrícula")
    provincia = st.selectbox("Provincia del inmueble", ["CABA", "Buenos Aires", "Córdoba", "..."])  # Agrega todas las provincias
    localidad = st.text_input("Localidad del inmueble")
    calle = st.text_input("Calle del inmueble")
    numero = st.text_input("Número del inmueble")
    piso = st.text_input("Piso del inmueble (opcional)")
    departamento = st.text_input("Departamento del inmueble (opcional)")
    codigo_postal = st.text_input("Código postal del inmueble (opcional)")

    # Formas de pago
    st.header("Formas de Pago")
    formas_pago = []
    if st.button("Agregar Forma de Pago"):
        formas_pago.append({})

    for i, forma_pago in enumerate(formas_pago):
        st.subheader(f"Forma de Pago {i + 1}")
        forma_pago["forma_de_pago"] = st.selectbox("Forma de Pago", ["Efectivo", "Cheque", "Transferencia Bancaria", "Activo Virtual", "Otra"], key=f"forma_pago_{i}")

        if forma_pago["forma_de_pago"] == "Activo Virtual":
            forma_pago["tipo_activo_virtual"] = st.text_input("Tipo de Activo Virtual", key=f"tipo_activo_virtual_{i}")
        if forma_pago["forma_de_pago"] == "Otra":
            forma_pago["otra"] = st.text_input("Otra Forma de Pago", key=f"otra_{i}")

        forma_pago["tipo_moneda_pago"] = st.selectbox("Tipo de Moneda de Pago", ["Peso Argentino", "Otro"], key=f"tipo_moneda_pago_{i}")
        if forma_pago["tipo_moneda_pago"] == "Otro":
            forma_pago["tipo_moneda_extranjera_pago"] = st.text_input("Tipo de Moneda Extranjera de Pago", key=f"tipo_moneda_extranjera_pago_{i}")
            forma_pago["monto_pesos_pago"] = st.number_input("Monto Pagado en Pesos", value=0, key=f"monto_pesos_pago_{i}")

        forma_pago["monto_moneda_pago"] = st.number_input("Monto Pagado en Moneda de Origen", value=0, key=f"monto_moneda_pago_{i}")

    # Compradores y vendedores
    st.header("Compradores y Vendedores")
    personas = []
    if st.button("Agregar Comprador/Vendedor"):
        personas.append({})

    for i, persona in enumerate(personas):
        st.subheader(f"Persona {i + 1}")
        persona["rol"] = st.selectbox("Rol", ["Comprador", "Vendedor"], key=f"rol_{i}")
        persona["tipo"] = st.selectbox("Tipo de Persona", ["Persona Humana", "Persona Jurídica", "Persona Humana Extranjera"], key=f"tipo_{i}")

        if persona["tipo"] == "Persona Humana":
            persona["cuit"] = st.text_input("CUIT", key=f"cuit_{i}")
            persona["apellido"] = st.text_input("Apellido", key=f"apellido_{i}")
            persona["nombre"] = st.text_input("Nombre", key=f"nombre_{i}")
            persona["tipo_doc"] = st.text_input("Tipo de Documento", key=f"tipo_doc_{i}")
            persona["nro_doc"] = st.text_input("Número de Documento", key=f"nro_doc_{i}")
            persona["nacionalidad"] = st.text_input("Nacionalidad", key=f"nacionalidad_{i}")
            persona["fecha_nacimiento"] = st.date_input("Fecha de Nacimiento", key=f"fecha_nacimiento_{i}")
            persona["es_pep"] = st.checkbox("Es PEP", key=f"es_pep_{i}")
            persona["porcentaje"] = st.number_input("Porcentaje", value=0, key=f"porcentaje_{i}")
            persona["pais"] = st.text_input("País", key=f"pais_{i}")
            if persona["pais"] == "Argentina":
                persona["provincia"] = st.text_input("Provincia", key=f"provincia_{i}")
                persona["localidad"] = st.text_input("Localidad", key=f"localidad_{i}")
            else:
                persona["otro_pais"] = st.text_input("Otro País", key=f"otro_pais_{i}")
                persona["provincia_extranjera"] = st.text_input("Provincia/Estado", key=f"provincia_extranjera_{i}")
                persona["localidad_extranjera"] = st.text_input("Localidad/Ciudad", key=f"localidad_extranjera_{i}")
            persona["calle"] = st.text_input("Calle", key=f"calle_{i}")
            persona["numero"] = st.text_input("Número", key=f"numero_{i}")
            persona["piso"] = st.text_input("Piso (opcional)", key=f"piso_{i}")

          # Continuación de la Parte 3...

            persona["departamento"] = st.text_input("Departamento (opcional)", key=f"departamento_{i}")
            persona["codigo_postal"] = st.text_input("Código Postal (opcional)", key=f"codigo_postal_{i}")
            persona["codigo_area"] = st.text_input("Código de Área Telefónico (opcional)", key=f"codigo_area_{i}")
            persona["telefono"] = st.text_input("Teléfono (opcional)", key=f"telefono_{i}")
            persona["email"] = st.text_input("Correo Electrónico (opcional)", key=f"email_{i}")

        elif persona["tipo"] == "Persona Jurídica":
            persona["denominacion"] = st.text_input("Denominación", key=f"denominacion_{i}")
            persona["cuit"] = st.text_input("CUIT", key=f"cuit_{i}")
            persona["porcentaje"] = st.number_input("Porcentaje", value=0, key=f"porcentaje_{i}")
            persona["pais"] = st.text_input("País", key=f"pais_{i}")
            if persona["pais"] == "Argentina":
                persona["provincia"] = st.text_input("Provincia", key=f"provincia_{i}")
                persona["localidad"] = st.text_input("Localidad", key=f"localidad_{i}")
            else:
                persona["otro_pais"] = st.text_input("Otro País", key=f"otro_pais_{i}")
                persona["provincia_extranjera"] = st.text_input("Provincia/Estado", key=f"provincia_extranjera_{i}")
                persona["localidad_extranjera"] = st.text_input("Localidad/Ciudad", key=f"localidad_extranjera_{i}")
            persona["calle"] = st.text_input("Calle", key=f"calle_{i}")
            persona["numero"] = st.text_input("Número", key=f"numero_{i}")
            persona["piso"] = st.text_input("Piso (opcional)", key=f"piso_{i}")
            persona["departamento"] = st.text_input("Departamento (opcional)", key=f"departamento_{i}")
            persona["codigo_postal"] = st.text_input("Código Postal (opcional)", key=f"codigo_postal_{i}")
            persona["codigo_area"] = st.text_input("Código de Área Telefónico (opcional)", key=f"codigo_area_{i}")
            persona["telefono"] = st.text_input("Teléfono (opcional)", key=f"telefono_{i}")
            persona["email"] = st.text_input("Correo Electrónico (opcional)", key=f"email_{i}")

        elif persona["tipo"] == "Persona Humana Extranjera":
            persona["cdi"] = st.text_input("CDI", key=f"cdi_{i}")
            persona["apellido"] = st.text_input("Apellido", key=f"apellido_{i}")
            persona["nombre"] = st.text_input("Nombre", key=f"nombre_{i}")
            persona["tipo_doc"] = st.text_input("Tipo de Documento", key=f"tipo_doc_{i}")
            persona["nro_doc"] = st.text_input("Número de Documento", key=f"nro_doc_{i}")
            persona["nacionalidad"] = st.text_input("Nacionalidad", key=f"nacionalidad_{i}")
            persona["fecha_nacimiento"] = st.date_input("Fecha de Nacimiento", key=f"fecha_nacimiento_{i}")
            persona["es_pep"] = st.checkbox("Es PEP", key=f"es_pep_{i}")
            persona["porcentaje"] = st.number_input("Porcentaje", value=0, key=f"porcentaje_{i}")
            persona["pais"] = st.text_input("País", key=f"pais_{i}")
            if persona["pais"] == "Argentina":
                persona["provincia"] = st.text_input("Provincia", key=f"provincia_{i}")
                persona["localidad"] = st.text_input("Localidad", key=f"localidad_{i}")
            else:
                persona["otro_pais"] = st.text_input("Otro País", key=f"otro_pais_{i}")
                persona["provincia_extranjera"] = st.text_input("Provincia/Estado", key=f"provincia_extranjera_{i}")
                persona["localidad_extranjera"] = st.text_input("Localidad/Ciudad", key=f"localidad_extranjera_{i}")
            persona["calle"] = st.text_input("Calle", key=f"calle_{i}")
            persona["numero"] = st.text_input("Número", key=f"numero_{i}")
            persona["piso"] = st.text_input("Piso (opcional)", key=f"piso_{i}")
            persona["departamento"] = st.text_input("Departamento (opcional)", key=f"departamento_{i}")
            persona["codigo_postal"] = st.text_input("Código Postal (opcional)", key=f"codigo_postal_{i}")
            persona["codigo_area"] = st.text_input("Código de Área Telefónico (opcional)", key=f"codigo_area_{i}")
            persona["telefono"] = st.text_input("Teléfono (opcional)", key=f"telefono_{i}")
            persona["email"] = st.text_input("Correo Electrónico (opcional)", key=f"email_{i}")

    # Generar y descargar XML
    if st.button("Generar XML"):
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
            "personas": personas,
        }
        xml_output = create_xml(data)
        st.download_button(
            label="Descargar XML",
            data=xml_output.encode("utf-8"),
            file_name="operacion.xml",
            mime="application/xml",
        )

if __name__ == "__main__":
    main()
