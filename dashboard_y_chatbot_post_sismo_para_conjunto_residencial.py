from datetime import datetime
import io
import json
import os
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Prados del Refugio | PMU",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estética institucional sobria y minimalista inspirada en ProPacífico
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,600;1,400&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
    }
    
    section[data-testid="stSidebar"] [data-testid="stFileUploadDropzone"] {
        background-color: #ffffff !important;
        border: 2px dashed #cbd5e1 !important;
    }
    section[data-testid="stSidebar"] [data-testid="stFileUploadDropzone"] span,
    section[data-testid="stSidebar"] [data-testid="stFileUploadDropzone"] small,
    section[data-testid="stSidebar"] [data-testid="stFileUploadDropzone"] div,
    section[data-testid="stSidebar"] [data-testid="stFileUploadDropzone"] p {
        color: #495057 !important;
        font-weight: 500 !important;
    }
    section[data-testid="stSidebar"] [data-testid="stFileUploadDropzone"] button {
        background-color: #2f3e46 !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 600 !important;
    }
    /* Correccion de visibilidad para la caja de subir archivos */
    section[data-testid="stSidebar"] [data-testid="stFileUploadDropzone"] {
        background-color: #ffffff !important;
        border: 2px dashed #cbd5e1 !important;
    }
    section[data-testid="stSidebar"] [data-testid="stFileUploadDropzone"] span,
    section[data-testid="stSidebar"] [data-testid="stFileUploadDropzone"] small,
    section[data-testid="stSidebar"] [data-testid="stFileUploadDropzone"] div,
    section[data-testid="stSidebar"] [data-testid="stFileUploadDropzone"] p {
        color: #495057 !important;
        font-weight: 500 !important;
    }
    section[data-testid="stSidebar"] [data-testid="stFileUploadDropzone"] button {
        background-color: #2f3e46 !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 600 !important;
    }
    .hero-banner {
        background: linear-gradient(135deg, #1f2421 0%, #2f3e46 60%, #e05a2b 100%);
        padding: 36px 44px;
        border-radius: 2px;
        color: white;
        margin-bottom: 28px;
    }
    .hero-title {
        font-family: 'Playfair Display', serif;
        font-size: 30px;
        font-weight: 600;
        letter-spacing: -0.5px;
        margin: 0;
        color: #ffffff !important;
    }
    .hero-subtitle {
        font-size: 12px;
        font-weight: 400;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #f4a261;
        margin-top: 6px;
    }

    .kpi-container {
        background-color: #ffffff;
        border-top: 3px solid #e05a2b;
        border-left: 1px solid #e9ecef;
        border-right: 1px solid #e9ecef;
        border-bottom: 1px solid #e9ecef;
        padding: 20px 22px;
        border-radius: 2px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .kpi-label {
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        color: #6c757d !important;
    }
    .kpi-value {
        font-size: 26px;
        font-weight: 700;
        color: #1f2421 !important;
        margin-top: 4px;
    }
    .kpi-sub {
        font-size: 12px;
        color: #e05a2b !important;
        font-weight: 500;
        margin-top: 4px;
    }
    
    .traffic-card {
        background: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 2px;
        padding: 20px 22px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .traffic-header {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
    }
    .dot-urg { width: 8px; height: 8px; background-color: #c92a2a; border-radius: 50%; display: inline-block; margin-right: 8px; }
    .dot-proc { width: 8px; height: 8px; background-color: #f59f00; border-radius: 50%; display: inline-block; margin-right: 8px; }
    .dot-don { width: 8px; height: 8px; background-color: #2b8a3e; border-radius: 50%; display: inline-block; margin-right: 8px; }
    .text-urg { color: #c92a2a !important; }
    .text-proc { color: #d97706 !important; }
    .text-don { color: #2b8a3e !important; }
    
    .traffic-list {
        font-size: 13px;
        color: #495057 !important;
        line-height: 1.8;
        margin: 0;
        padding-left: 18px;
    }

    .legal-card {
        background-color: #fdfbf7;
        border-left: 3px solid #868e96;
        border-top: 1px solid #e9ecef;
        border-right: 1px solid #e9ecef;
        border-bottom: 1px solid #e9ecef;
        padding: 16px 20px;
        margin-top: 30px;
        border-radius: 2px;
    }
    .legal-title {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        color: #495057 !important;
        margin-bottom: 4px;
    }
    .legal-text {
        font-size: 12px;
        color: #6c757d !important;
        line-height: 1.5;
        margin: 0;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# Funcion global para mostrar el banner de Habeas Data legal en cada pagina
def mostrar_banner_habeas_data():
  st.markdown(
      """
        <div class="legal-card">
            <div class="legal-title">Marco de Protección de Datos Personales (Ley 1581 de 2012 / Decreto 1377 de 2013)</div>
            <p class="legal-text">
                El **Conjunto Residencial Prados del Refugio**, en calidad de Responsable del Tratamiento de Datos, garantiza que la información recolectada mediante los censos de diagnóstico post-sismo se encuentra amparada bajo el principio de finalidad estricta. Los datos personales de contacto, identificación y fotografías serán utilizados única y exclusivamente para la atención de la emergencia, la radicación del expediente formal ante la compañía aseguradora y la coordinación de los comités de trabajo, resguardando la confidencialidad y el derecho fundamental al **Habeas Data** de todos los copropietarios y residentes.
            </p>
        </div>
    """,
      unsafe_allow_html=True,
  )


# -------------------------------------------------------------
# 1. PERSISTENCIA DE FASES Y EXPORTACION EN EXCEL
# -------------------------------------------------------------
ARCHIVO_FASES = "estructura_fases_comites.json"


def cargar_datos_fases():
  fases_base = {
      "fase_1": {
          "titulo": "1. Evaluación de Daños y Seguridad",
          "descripcion": (
              "Inspección técnica visual de afectaciones estructurales en"
              " Torres A, B, C y zonas comunes (porteria, gradas, parqueadero, piscina y salón social)."
              " Verificacion de habitabilidad y redes."
          ),
          "Tareas": (
              "• Recorrido tecnico por niveles.\n• Marcacion de fisuras no"
              " estructurales a 45° vs. fisuras de estuco.\n• Verificacion de"
              " acometidas e instalaciones principales de gas."
          ),
          "Personas": (
              "EJ: Arq. Roberto Gomez (Apto 302A), Ing. Carlos Mina (Apto 501B)"
          ),
      },
      "fase_2": {
          "titulo": "2. Censo y Caracterización",
          "descripcion": (
              "Consolidación de la base de datos de los 28 apartamentos y áreas"
              " comunes, reporte de afectaciones y autorizaciones formales de"
              " Habeas Data."
          ),
          "Tareas": (
              "• Cierre del censo de unidades privadas en Torres A, B y C.\n•"
              " Consolidación de autorizaciones firmadas para el ajustador.\n•"
              " Acompanamiento y orientación a propietarios."
          ),
          "personas": "Ejemplo: Melisa Espinosa (Apto 202B), etc",
      },
      "fase_3": {
          "titulo": "3. Seguros y Reclamaciones",
          "descripcion": (
              "Tramite formal del siniestro ante la compañia de seguros,"
              " integración de expedientes por unidad e interlocucion con el"
              " perito ajustador."
          ),
          "tareas": (
              "• Notificación formal del siniestro bajo amparo de terremoto.\n•"
              " Radicación de poderes de representación de copropietarios.\n•"
              " Acompañamiento en sitio durante la inspeccion técnica del"
              " ajustador."
          ),
          "personas": " Ejemplo: Pedro Pérez (Apto xxx)",
      },
      "fase_4": {
          "titulo": "4. Reconstrucción e Infraestructura",
          "descripción": (
              "Recepción y evaluación de propuestas técnicas para obras de"
              " mamposteria, reparación de zonas comunes y adecuaciones"
              " prioritarias."
          ),
          "tareas": (
              "• Cuadro comparativo de mínimo 3 cotizaciones por concepto.\n•"
              " Supervisión de obras menores en zonas comunes.\n• Cronograma de"
              " intervención en fachadas y cerramientos."
          ),
          "personas": " Ejemplo : Ing. Fernando Castro (Apto 402C)",
      },
      "fase_5": {
          "titulo": "5. Comunicaciones y Atención a Residentes",
          "descripcion": (
              "Gestión de canales oficiales de información, atención de"
              " inquietudes y emisión períodica de boletines sobre el estado de"
              " la copropiedad."
          ),
          "tareas": (
              "• Emisión de boletines oficiales del PMU.\n• Moderación de"
              " canales de consulta y atención comunitaria.\n• Actualización"
              " permanente del panel informativo."
          ),
          "personas": "Comite de Comunicaciones, Ejemplo: Laura Benitez (Apto 201B)",
      },
      "fase_6": {
          "titulo": "6. Administración, Finanzas y Proveedores",
          "descripción": (
              "Control y ejecución del fondo de imprevistos, cotización"
              " transparente con proveedores de obra y rendicion de cuentas en"
              " tiempo real."
          ),
          "tareas": (
              "• Balance del fondo de imprevistos y flujo de caja.\n•"
              " Comparativo de mínimo 3 cotizaciones por servicio técnico.\n•"
              " Publicación de soportes contables del siniestro."
          ),
          "personas": (
              "Ejemplo: Administración Prados del Refugio, Revisor Fiscal, Tesorería"
          ),
      },
  }
  if os.path.exists(ARCHIVO_FASES):
    try:
      with open(ARCHIVO_FASES, "r", encoding="utf-8") as f:
        return json.load(f)
    except Exception:
      return fases_base
  return fases_base


def guardar_datos_fases(datos):
  with open(ARCHIVO_FASES, "w", encoding="utf-8") as f:
    json.dump(datos, f, ensure_ascii=False, indent=2)


def exportar_fases_a_excel(datos_fases):
  lista_filas = []
  for k, v in datos_fases.items():
    lista_filas.append({
        "Fase": v.get("titulo", ""),
        "Descripcion General": v.get("descripcion", ""),
        "Tareas Detalladas": v.get("tareas", ""),
        "Personas Asignadas / Voluntarios": v.get("personas", ""),
        "Fecha Actualizacioón": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
  df_f = pd.DataFrame(lista_filas)
  buffer = io.BytesIO()
  with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    df_f.to_excel(writer, index=False, sheet_name="Estructura_Operativa")
  return buffer.getvalue()


# -------------------------------------------------------------
# 2. PERSISTENCIA DE INSCRIPCIONES INDIVIDUALES (ARCHIVO CSV)
# -------------------------------------------------------------
ARCHIVO_INSCRIPCIONES = "inscripciones_voluntarios.csv"


def guardar_inscripcion(
    nombre, torre, apto, telefono, profesion, mesa, disponibilidad
):
  registro = {
      "Fecha_Registro": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
      "Nombre_Completo": [nombre],
      "Torre": [torre],
      "Apartamento": [apto],
      "Telefono": [telefono],
      "Profesion_Habilidad": [profesion],
      "Mesa_Asignada": [mesa],
      "Disponibilidad": [disponibilidad],
  }
  df_nuevo = pd.DataFrame(registro)
  if os.path.exists(ARCHIVO_INSCRIPCIONES):
    df_existente = pd.read_csv(ARCHIVO_INSCRIPCIONES)
    df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
  else:
    df_final = df_nuevo
  df_final.to_csv(ARCHIVO_INSCRIPCIONES, index=False)
  return df_final


def cargar_inscripciones():
  if os.path.exists(ARCHIVO_INSCRIPCIONES):
    return pd.read_csv(ARCHIVO_INSCRIPCIONES)
  else:
    return pd.DataFrame(columns=[
        "Fecha_Registro",
        "Nombre_Completo",
        "Torre",
        "Apartamento",
        "Telefono",
        "Profesion_Habilidad",
        "Mesa_Asignada",
        "Disponibilidad",
    ])


# -------------------------------------------------------------
# 3. ESTRUCTURA BASE DE DATOS (29 APTOS + 6 AREAS COMUNES)
# -------------------------------------------------------------
def generar_estructura_exacta():
  np.random.seed(42)
  aptos_a = [
      f"{piso}0{num}A" for piso in range(1, 5) for num in [1, 2]
  ] + ["501A"]
  aptos_b = [
      f"{piso}0{num}B" for piso in range(1, 5) for num in [1, 2]
  ] + ["501B"]
  aptos_c = [
      f"{piso}0{num}C" for piso in range(1, 6) for num in [1, 2]
  ] + ["601C"]

  registros = []
  for a in aptos_a:
    registros.append({"torre": "Torre A", "unidad": a, "tipo": "Privado"})
  for b in aptos_b:
    registros.append({"torre": "Torre B", "unidad": b, "tipo": "Privado"})
  for c in aptos_c:
    registros.append({"torre": "Torre C", "unidad": c, "tipo": "Privado"})

  df_p = pd.DataFrame(registros)
  n = len(df_p)

  df_p["propietario"] = [f"Residente {i}" for i in range(1, n + 1)]
  df_p["cedula"] = [
      f"{np.random.randint(10000000, 99999999)}" for _ in range(n)
  ]
  df_p["telefono"] = [
      f"3{np.random.randint(100000000, 999999999)}" for _ in range(n)
  ]
  df_p["correo"] = [f"contacto{i}@prados.com" for i in range(1, n + 1)]
  df_p["inmueble_afectado"] = np.random.choice(["Si", "No"], n, p=[0.55, 0.45])
  df_p["autoriza_datos"] = np.random.choice(["Si", "No"], n, p=[0.93, 0.07])

  comunes = [
      "Pasillos",
      "Porteria",
      "Gradas",
      "Parqueadero",
      "Salón Social",
      "Piscina",
  ]
  registros_c = []
  for com in comunes:
    registros_c.append({
        "torre": "Áreas Comunes",
        "unidad": com,
        "tipo": "Comun",
        "propietario": "Administración General",
        "cedula": "NIT Copropiedad",
        "telefono": "PBX Principal",
        "correo": "admin@pradosdelrefugio.com",
        "inmueble_afectado": np.random.choice(["Si", "No"], p=[0.5, 0.5]),
        "autoriza_datos": "Si",
    })
  df_c = pd.DataFrame(registros_c)
  return pd.concat([df_p, df_c], ignore_index=True)


def normalizar_columnas_censo(df_raw):
  df_res = df_raw.copy()
  col_map = {}
  for col in df_res.columns:
    c_low = str(col).lower()
    if "torre" in c_low or "bloque" in c_low:
      col_map[col] = "torre"
    elif "apto" in c_low or "apartamento" in c_low or "unidad" in c_low:
      col_map[col] = "unidad"
    elif "afecta" in c_low or "dano" in c_low or "averia" in c_low:
      col_map[col] = "inmueble_afectado"
    elif "autoriza" in c_low or "habeas" in c_low or "datos" in c_low:
      col_map[col] = "autoriza_datos"
    elif "nombre" in c_low or "propietario" in c_low or "residente" in c_low:
      col_map[col] = "propietario"
    elif "cedula" in c_low or "documento" in c_low or "nit" in c_low:
      col_map[col] = "cedula"
    elif "telefono" in c_low or "celular" in c_low or "whatsapp" in c_low:
      col_map[col] = "telefono"
    elif "correo" in c_low or "email" in c_low:
      col_map[col] = "correo"

  df_res = df_res.rename(columns=col_map)

  if "tipo" not in df_res.columns:
    df_res["tipo"] = df_res["torre"].apply(
        lambda x: "Comun" if "comun" in str(x).lower() else "Privado"
    )
  if "inmueble_afectado" not in df_res.columns:
    df_res["inmueble_afectado"] = "No"
  else:
    df_res["inmueble_afectado"] = df_res["inmueble_afectado"].apply(
        lambda x: (
            "Si" if str(x).lower().strip() in ["si", "true", "1", "yes"] else "No"
        )
    )

  if "autoriza_datos" not in df_res.columns:
    df_res["autoriza_datos"] = "Si"
  else:
    df_res["autoriza_datos"] = df_res["autoriza_datos"].apply(
        lambda x: (
            "Si"
            if str(x).lower().strip()
            in ["si", "true", "1", "yes", "autorizo"]
            else "No"
        )
    )

  return df_res


# -------------------------------------------------------------
# MENU LATERAL
# -------------------------------------------------------------
st.sidebar.markdown(
    """
    <div style="padding: 5px 0 15px 0;">
        <span style="font-family: 'Playfair Display', serif; font-size: 20px; font-weight: 700; color: #1f2421;">Prados del Refugio</span><br>
        <span style="font-size: 11px; color: #e05a2b; letter-spacing: 1.5px; text-transform: uppercase;">Puesto de Mando Unificado</span>
    </div>
""",
    unsafe_allow_html=True,
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<span style='font-size: 11px; font-weight: 700; color: #1f2421;"
    " letter-spacing: 1px; text-transform: uppercase;'>Cargar Censo (Excel /"
    " Forms)</span>",
    unsafe_allow_html=True,
)
archivo_subido = st.sidebar.file_uploader(
    "Seleccionar archivo de datos:",
    type=["xlsx", "xls", "csv"],
    help="Sube el archivo Excel o CSV para sincronizar el panel.",
)

if archivo_subido is not None:
  try:
    if archivo_subido.name.endswith(".csv"):
      df_cargado = pd.read_csv(archivo_subido)
    else:
      df_cargado = pd.read_excel(archivo_subido)
    df = normalizar_columnas_censo(df_cargado)
    st.sidebar.success("Base de datos sincronizada.")
  except Exception as e:
    st.sidebar.error(f"Error en lectura: {e}")
    df = generar_estructura_exacta()
elif os.path.exists("censo_administracion.xlsx"):
  df = normalizar_columnas_censo(pd.read_excel("censo_administracion.xlsx"))
elif os.path.exists("resultados.csv"):
  df = normalizar_columnas_censo(pd.read_csv("resultados.csv"))
else:
  df = generar_estructura_exacta()

df_priv = df[df["tipo"] == "Privado"]
df_com = df[df["tipo"] == "Comun"]
if len(df_com) == 0:
  df_base_temp = generar_estructura_exacta()
  df_com = df_base_temp[df_base_temp["tipo"] == "Comun"]

st.sidebar.markdown("---")
pagina = st.sidebar.radio(
    "Navegacion Principal:",
    [
        "Panel de Control y Diagnostico",
        "Participa en la Recuperacion",
        "Poliza y Reclamacion de Seguros",
        "Planos Estructurales e Inspeccion",
        "Asistente Virtual",
    ],
)

# Header Global
st.markdown(
    """
    <div class="hero-banner">
        <div class="hero-title">Conjunto Residencial Prados del Refugio</div>
        <div class="hero-subtitle">Sistema Integrado de Informacion Post-Sismo · Cali</div>
    </div>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# MODULO 1: PANEL DE CONTROL Y DIAGNOSTICO
# -------------------------------------------------------------
if pagina == "Panel de Control y Diagnostico":
  c1, c2, c3 = st.columns(3)
  total_censados = len(df_priv)
  afectados_aptos = (df_priv["inmueble_afectado"] == "Si").sum()
  afectados_comunes = (df_com["inmueble_afectado"] == "Si").sum()

  with c1:
    st.markdown(
        f"""
            <div class="kpi-container">
                <div class="kpi-label">Censo Unidades Privadas</div>
                <div class="kpi-value">{total_censados}</div>
                <div class="kpi-sub">Torres A (9), B (9), C (11)</div>
            </div>
        """,
        unsafe_allow_html=True,
    )
  with c2:
    porcentaje_afect = (
        round((afectados_aptos / total_censados * 100))
        if total_censados > 0
        else 0
    )
    st.markdown(
        f"""
            <div class="kpi-container">
                <div class="kpi-label">Inmuebles con Afectacion</div>
                <div class="kpi-value">{afectados_aptos}</div>
                <div class="kpi-sub">{porcentaje_afect}% del total censado</div>
            </div>
        """,
        unsafe_allow_html=True,
    )
  with c3:
    st.markdown(
        f"""
            <div class="kpi-container">
                <div class="kpi-label">Zonas Comunes Afectadas</div>
                <div class="kpi-value">{afectados_comunes} / {len(df_com)}</div>
                <div class="kpi-sub">Evaluacion locativa</div>
            </div>
        """,
        unsafe_allow_html=True,
    )

  st.write("")
  st.write("")

  g1, g2 = st.columns(2)
  with g1:
    df_torres = (
        df_priv.groupby(["torre", "inmueble_afectado"])
        .size()
        .reset_index(name="conteo")
    )
    fig1 = px.bar(
        df_torres,
        x="torre",
        y="conteo",
        color="inmueble_afectado",
        title="Consolidado de Afectaciones por Torre",
        barmode="stack",
        color_discrete_map={"Si": "#e05a2b", "No": "#2f3e46"},
        category_orders={"torre": ["Torre A", "Torre B", "Torre C"]},
    )
    fig1.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Montserrat", size=12),
        legend_title_text="Reporte Dano",
    )
    st.plotly_chart(fig1, use_container_width=True)

  with g2:
    fig2 = px.bar(
        df_com,
        x="unidad",
        y="inmueble_afectado",
        title="Diagnostico Tecnico en Areas Comunes",
        color="inmueble_afectado",
        color_discrete_map={"Si": "#e05a2b", "No": "#2f3e46"},
    )
    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Montserrat", size=12),
        xaxis_title="",
        yaxis_title="",
        legend_title_text="Afectacion",
    )
    st.plotly_chart(fig2, use_container_width=True)

  st.write("---")
  st.subheader("Inventario Nominal de Apartamentos")
  st.caption("Filtro por bloque con resguardo estricto de Habeas Data.")
  torres_disponibles = list(df_priv["torre"].unique())
  torre_sel = st.selectbox(
      "Seleccionar Bloque:",
      torres_disponibles if len(torres_disponibles) > 0 else ["Torre A"],
  )

  cols_mostrar = ["unidad", "inmueble_afectado", "autoriza_datos"]
  cols_exist = [c for c in cols_mostrar if c in df_priv.columns]

  df_vista = df_priv[df_priv["torre"] == torre_sel][cols_exist].rename(
      columns={
          "unidad": "Apartamento",
          "inmueble_afectado": "Afectacion Reportada",
          "autoriza_datos": "Autorizacion Poliza",
      }
  )
  st.dataframe(df_vista, use_container_width=True, hide_index=True)
  mostrar_banner_habeas_data()

# -------------------------------------------------------------
# MODULO 2: PARTICIPA EN LA RECUPERACION (FASES, JSON Y EXCEL)
# -------------------------------------------------------------
elif pagina == "Participa en la Recuperación":
  st.subheader("Estructura Operativa y Cómites por Fases")
  st.markdown(
      """
        <p style="font-size: 14px; color: #495057; line-height: 1.6; margin-bottom: 20px;">
            Organizacion modular del conjunto en 6 grandes fases de trabajo. Puede modificar las tareas detalladas y las personas encargadas de cada frente; los cambios se guardan permanentemente en el sistema y pueden descargarse en formato Excel.
        </p>
    """,
      unsafe_allow_html=True,
  )

  datos_fases = cargar_datos_fases()

  with st.form("form_fases_completo"):
    # FASE 1
    st.markdown(
        "<span style='color: #e05a2b; font-weight: 700; font-size: 11px;"
        " letter-spacing: 1.5px; text-transform: uppercase;'>FASE 1 —"
        " RESPUESTA Y DIAGNOSTICO</span>",
        unsafe_allow_html=True,
    )
    col_f1_a, col_f1_b = st.columns(2)

    with col_f1_a:
      f1 = datos_fases.get("fase_1", {})
      st.markdown(
          f"""
                <div style="background: white; border-left: 3px solid #e05a2b; padding: 16px 18px; border-radius: 2px; border-top: 1px solid #e9ecef; border-right: 1px solid #e9ecef; border-bottom: 1px solid #e9ecef; margin-bottom: 8px;">
                    <b style="color: #1f2421; font-size: 15px;">{f1.get('titulo')}</b>
                    <p style="font-size: 12px; color: #6c757d; margin: 4px 0 0 0; line-height: 1.4;">{f1.get('descripcion')}</p>
                </div>
            """,
          unsafe_allow_html=True,
      )
      with st.expander("Modificar tareas detalladas"):
        t_f1 = st.text_area(
            "Tareas detalladas:",
            value=f1.get("tareas", ""),
            key="t_f1",
            height=90,
        )
      p_f1 = st.text_area(
          "Personas que pueden colaborar:",
          value=f1.get("personas", ""),
          key="p_f1",
          height=70,
      )

    with col_f1_b:
      f2 = datos_fases.get("fase_2", {})
      st.markdown(
          f"""
                <div style="background: white; border-left: 3px solid #e05a2b; padding: 16px 18px; border-radius: 2px; border-top: 1px solid #e9ecef; border-right: 1px solid #e9ecef; border-bottom: 1px solid #e9ecef; margin-bottom: 8px;">
                    <b style="color: #1f2421; font-size: 15px;">{f2.get('titulo')}</b>
                    <p style="font-size: 12px; color: #6c757d; margin: 4px 0 0 0; line-height: 1.4;">{f2.get('descripcion')}</p>
                </div>
            """,
          unsafe_allow_html=True,
      )
      with st.expander("Modificar tareas detalladas"):
        t_f2 = st.text_area(
            "Tareas detalladas:",
            value=f2.get("tareas", ""),
            key="t_f2",
            height=90,
        )
      p_f2 = st.text_area(
          "Personas que pueden colaborar:",
          value=f2.get("personas", ""),
          key="p_f2",
          height=70,
      )

    st.write("")
    # FASE 2
    st.markdown(
        "<span style='color: #e05a2b; font-weight: 700; font-size: 11px;"
        " letter-spacing: 1.5px; text-transform: uppercase;'>FASE 2 — GESTION"
        " TECNICA, SEGUROS Y RECURSOS</span>",
        unsafe_allow_html=True,
    )
    col_f2_a, col_f2_b = st.columns(2)

    with col_f2_a:
      f3 = datos_fases.get("fase_3", {})
      st.markdown(
          f"""
                <div style="background: white; border-left: 3px solid #2f3e46; padding: 16px 18px; border-radius: 2px; border-top: 1px solid #e9ecef; border-right: 1px solid #e9ecef; border-bottom: 1px solid #e9ecef; margin-bottom: 8px;">
                    <b style="color: #1f2421; font-size: 15px;">{f3.get('titulo')}</b>
                    <p style="font-size: 12px; color: #6c757d; margin: 4px 0 0 0; line-height: 1.4;">{f3.get('descripcion')}</p>
                </div>
            """,
          unsafe_allow_html=True,
      )
      with st.expander("Modificar tareas detalladas"):
        t_f3 = st.text_area(
            "Tareas detalladas:",
            value=f3.get("tareas", ""),
            key="t_f3",
            height=90,
        )
      p_f3 = st.text_area(
          "Personas que pueden colaborar:",
          value=f3.get("personas", ""),
          key="p_f3",
          height=70,
      )

    with col_f2_b:
      f4 = datos_fases.get("fase_4", {})
      st.markdown(
          f"""
                <div style="background: white; border-left: 3px solid #2f3e46; padding: 16px 18px; border-radius: 2px; border-top: 1px solid #e9ecef; border-right: 1px solid #e9ecef; border-bottom: 1px solid #e9ecef; margin-bottom: 8px;">
                    <b style="color: #1f2421; font-size: 15px;">{f4.get('titulo')}</b>
                    <p style="font-size: 12px; color: #6c757d; margin: 4px 0 0 0; line-height: 1.4;">{f4.get('descripcion')}</p>
                </div>
            """,
          unsafe_allow_html=True,
      )
      with st.expander("Modificar tareas detalladas"):
        t_f4 = st.text_area(
            "Tareas detalladas:",
            value=f4.get("tareas", ""),
            key="t_f4",
            height=90,
        )
      p_f4 = st.text_area(
          "Personas que pueden colaborar:",
          value=f4.get("personas", ""),
          key="p_f4",
          height=70,
      )

    st.write("")
    # FASE 3 Y 4
    st.markdown(
        "<span style='color: #e05a2b; font-weight: 700; font-size: 11px;"
        " letter-spacing: 1.5px; text-transform: uppercase;'>FASE 3 Y 4 —"
        " GOBERNANZA, COMUNICACION Y FINANZAS</span>",
        unsafe_allow_html=True,
    )
    col_f3_a, col_f3_b = st.columns(2)

    with col_f3_a:
      f5 = datos_fases.get("fase_5", {})
      st.markdown(
          f"""
                <div style="background: white; border-left: 3px solid #1f2421; padding: 16px 18px; border-radius: 2px; border-top: 1px solid #e9ecef; border-right: 1px solid #e9ecef; border-bottom: 1px solid #e9ecef; margin-bottom: 8px;">
                    <b style="color: #1f2421; font-size: 15px;">{f5.get('titulo')}</b>
                    <p style="font-size: 12px; color: #6c757d; margin: 4px 0 0 0; line-height: 1.4;">{f5.get('descripcion')}</p>
                </div>
            """,
          unsafe_allow_html=True,
      )
      with st.expander("Modificar tareas detalladas"):
        t_f5 = st.text_area(
            "Tareas detalladas:",
            value=f5.get("tareas", ""),
            key="t_f5",
            height=90,
        )
      p_f5 = st.text_area(
          "Personas que pueden colaborar:",
          value=f5.get("personas", ""),
          key="p_f5",
          height=70,
      )

    with col_f3_b:
      f6 = datos_fases.get("fase_6", {})
      st.markdown(
          f"""
                <div style="background: white; border-left: 3px solid #1f2421; padding: 16px 18px; border-radius: 2px; border-top: 1px solid #e9ecef; border-right: 1px solid #e9ecef; border-bottom: 1px solid #e9ecef; margin-bottom: 8px;">
                    <b style="color: #1f2421; font-size: 15px;">{f6.get('titulo')}</b>
                    <p style="font-size: 12px; color: #6c757d; margin: 4px 0 0 0; line-height: 1.4;">{f6.get('descripcion')}</p>
                </div>
            """,
          unsafe_allow_html=True,
      )
      with st.expander("Modificar tareas detalladas"):
        t_f6 = st.text_area(
            "Tareas detalladas:",
            value=f6.get("tareas", ""),
            key="t_f6",
            height=90,
        )
      p_f6 = st.text_area(
          "Personas que pueden colaborar:",
          value=f6.get("personas", ""),
          key="p_f6",
          height=70,
      )

    st.write("")
    btn_salvar_fases = st.form_submit_button(
        "Guardar Cambios en Tareas y Comites"
    )
    if btn_salvar_fases:
      nuevos = {
          "fase_1": {
              "titulo": f1.get("titulo"),
              "descripcion": f1.get("descripcion"),
              "tareas": t_f1,
              "personas": p_f1,
          },
          "fase_2": {
              "titulo": f2.get("titulo"),
              "descripcion": f2.get("descripcion"),
              "tareas": t_f2,
              "personas": p_f2,
          },
          "fase_3": {
              "titulo": f3.get("titulo"),
              "descripcion": f3.get("descripcion"),
              "tareas": t_f3,
              "personas": p_f3,
          },
          "fase_4": {
              "titulo": f4.get("titulo"),
              "descripcion": f4.get("descripcion"),
              "tareas": t_f4,
              "personas": p_f4,
          },
          "fase_5": {
              "titulo": f5.get("titulo"),
              "descripcion": f5.get("descripcion"),
              "tareas": t_f5,
              "personas": p_f5,
          },
          "fase_6": {
              "titulo": f6.get("titulo"),
              "descripcion": f6.get("descripcion"),
              "tareas": t_f6,
              "personas": p_f6,
          },
      }
      guardar_datos_fases(nuevos)
      st.success(
          "Estructura operativa actualizada y guardada correctamente."
      )

  # Boton para descargar la configuracion actual de fases en Excel
  datos_actuales_fases = cargar_datos_fases()
  excel_fases = exportar_fases_a_excel(datos_actuales_fases)
  st.download_button(
      label="Descargar Fases y Comites Actualizados (Excel)",
      data=excel_fases,
      file_name="Estructura_Operativa_Prados_del_Refugio.xlsx",
      mime=(
          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
      ),
  )

  st.write("---")

  col_urg, col_proc, col_comp = st.columns(3)
  with col_urg:
    st.markdown(
        """
            <div class="traffic-card" style="border-top: 3px solid #c92a2a;">
                <div class="traffic-header text-urg"><span class="dot-urg"></span>Urgente / Critico</div>
                <ul class="traffic-list">
                    <li>Validar censo de los 29 apartamentos reales.</li>
                    <li>Radicacion de poderes para tramite de seguro.</li>
                    <li>Inspeccion visual tecnica en Torres B y C.</li>
                </ul>
            </div>
        """,
        unsafe_allow_html=True,
    )

  with col_proc:
    st.markdown(
        """
            <div class="traffic-card" style="border-top: 3px solid #f59f00;">
                <div class="traffic-header text-proc"><span class="dot-proc"></span>En Proceso</div>
                <ul class="traffic-list">
                    <li>Evaluacion tecnica de piscina y gradas.</li>
                    <li>Cotizacion de reparaciones locativas no estructurales.</li>
                    <li>Consolidacion del expediente digital de ajuste.</li>
                    <li>Revision de acometidas e instalaciones de gas.</li>
                </ul>
            </div>
        """,
        unsafe_allow_html=True,
    )

  with col_comp:
    st.markdown(
        """
            <div class="traffic-card" style="border-top: 3px solid #2b8a3e;">
                <div class="traffic-header text-don"><span class="dot-don"></span>Completado</div>
                <ul class="traffic-list">
                    <li>Aviso formal de siniestro a la aseguradora.</li>
                    <li>Habilitación del panel PMU en linea.</li>
                    <li>Registro fotográfico preliminar de zonas comunes.</li>
                    <li>Instalación de mesas comunitarias por fases.</li>
                </ul>
            </div>
        """,
        unsafe_allow_html=True,
    )

  st.write("---")
  st.markdown("#### Formulario de Postulación de Nuevos Voluntarios")
  st.caption(
      "Diligencie sus datos para sumarse a alguna de las mesas de trabajo."
  )

  with st.form("form_inscripcion_individual", clear_on_submit=True):
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
      nombre_input = st.text_input(
          "Nombre y Apellidos *", placeholder="Ej: Melisa Espinosa"
      )
      torre_input = st.selectbox("Torre *", ["Torre A", "Torre B", "Torre C"])
      apto_input = st.text_input(
          "Apartamento *", placeholder="Ej: 301A / 402B / 601C"
      )
    with f_col2:
      tel_input = st.text_input(
          "WhatsApp de Contacto *", placeholder="Ej: 3151234567"
      )
      profesion_input = st.text_input(
          "Profesión / Habilidad",
          placeholder="Ej: Ingeniería / Datos / Contabilidad / Logistica",
      )
    with f_col3:
      mesa_input = st.selectbox(
          "Mesa en la que desea participar *",
          [
              "1. Evaluación de Daños y Seguridad",
              "2. Censo y Caracterización",
              "3. Seguros y Reclamaciones",
              "4. Reconstrucción e Infraestructura",
              "5. Comunicaciones y Atención",
              "6. Administracion y Finanzas",
          ],
      )
      disp_input = st.selectbox(
          "Disponibilidad *",
          [
              "Tiempo Parcial (Tardes / Fines de Semana)",
              "Tiempo Completo (Presencial en PMU)",
              "Apoyo Remoto / Digital",
          ],
      )

    acepta_datos = st.checkbox(
        "Autorizo el tratamiento de mis datos de contacto para la atención de"
        " la emergencia (Política de Protección de Datos Personales, Ley 1581/2012) *"
    )
    btn_enviar_vol = st.form_submit_button("Confirmar Inscripción en Mesa")

    if btn_enviar_vol:
      if not nombre_input or not apto_input or not tel_input:
        st.error("Por favor complete los campos obligatorios (*).")
      elif not acepta_datos:
        st.warning("Debe autorizar el tratamiento de datos para registrarse.")
      else:
        guardar_inscripcion(
            nombre_input,
            torre_input,
            apto_input,
            tel_input,
            profesion_input,
            mesa_input,
            disp_input,
        )
        st.success(
            f"Gracias, {nombre_input}. Su postulación para '{mesa_input}' ha"
            " sido guardada."
        )

  st.write("---")
  st.markdown("#### Registro Consolidado de Voluntarios Inscritos")
  df_vol = cargar_inscripciones()
  if len(df_vol) > 0:
    st.caption(f"Total registrados en tiempo real: {len(df_vol)}")
    st.dataframe(
        df_vol[[
            "Fecha_Registro",
            "Nombre_Completo",
            "Torre",
            "Apartamento",
            "Mesa_Asignada",
            "Disponibilidad",
        ]],
        use_container_width=True,
        hide_index=True,
    )

    # Exportacion a Excel de los voluntarios
    buffer_vol = io.BytesIO()
    with pd.ExcelWriter(buffer_vol, engine="openpyxl") as writer:
      df_vol.to_excel(writer, index=False, sheet_name="Voluntarios_PMU")
    st.download_button(
        label="Descargar Base de Voluntarios (Excel)",
        data=buffer_vol.getvalue(),
        file_name="Voluntarios_PMU_Prados_del_Refugio.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
    )
  else:
    st.info(
        "Aun no hay voluntarios registrados. Diligencie el formulario superior."
    )

  mostrar_banner_habeas_data()

# -------------------------------------------------------------
# MODULO 3: POLIZA Y RECLAMACION DE SEGUROS
# -------------------------------------------------------------
elif pagina == "Poliza y Reclamacion de Seguros":
  st.subheader("Gestion y Tramite de Poliza Colectiva")
  c_p1, c_p2 = st.columns([1, 1])
  with c_p1:
    st.markdown("""
            ### Ficha Técnica de la Póliza
            * **Aseguradora:** Seguros del Estado / Copropiedades
            * **Régimen:** Póliza de Zonas Comunes y Privadas con Amparo de Terremoto
            * **Vigencia:** 2026 - 2027
            * **Deducible Sismo:** Ejemplo: 10% del valor de la perdida con minimo legal
            * **Estado:** Aviso de siniestro emitido formalmente
        """)
  with c_p2:
    st.markdown("""
            ### Protocolo de Radicación
            1. **Consolidación del Censo:** Cierre de afectaciones en los 29 apartamentos.
            2. **Filtro de Habeas Data:** Inclusión estricta de copropietarios con poder firmado.
            3. **Inspeccion de Ajuste:** Visita del perito designado para dictamen tecnico.
            4. **Acta de Liquidación:** Emision de calendario de resarcimiento.
        """)

  st.write("---")
  st.subheader("Expediente para Radicación al Ajustador")
  cols_exp = ["torre", "unidad", "propietario", "cedula", "teléfono", "correo"]
  cols_validas = [c for c in cols_exp if c in df.columns]

  df_seguro = df[
      (df["inmueble_afectado"] == "Si") & (df["autoriza_datos"] == "Si")
  ][cols_validas]
  st.caption(f"Total registros listos: {len(df_seguro)} inmuebles.")
  st.dataframe(df_seguro, use_container_width=True, hide_index=True)

  buffer_seg = io.BytesIO()
  with pd.ExcelWriter(buffer_seg, engine="openpyxl") as writer:
    df_seguro.to_excel(writer, index=False, sheet_name="Expediente_Seguros")
  st.download_button(
      label="Descargar Expediente Consolidado (Excel)",
      data=buffer_seg.getvalue(),
      file_name="Expediente_Seguros_Prados_del_Refugio.xlsx",
      mime=(
          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
      ),
  )
  mostrar_banner_habeas_data()

# -------------------------------------------------------------
# MODULO 4: PLANOS ESTRUCTURALES E INSPECCION (CON CARGA DE IMAGEN)
# -------------------------------------------------------------
elif pagina == "Planos Estructurales ":
  st.subheader("Planos Estructurales y Puntos Criticos de Inspeccion")
  st.write(
      "Consulte la distribucion arquitectonica y visualice las fotos o esquemas"
      " técnicos de los planos estructurales de cada bloque."
  )

  torre_plano = st.selectbox(
      "Seleccionar Bloque:",
      [
          "Torre A (5 Niveles · 9 Apartamentos)",
          "Torre B (5 Niveles · 9 Apartamentos)",
          "Torre C (6 Niveles · 11 Apartamentos)",
      ],
  )

  col_plano, col_crit = st.columns([1.4, 1])

  with col_plano:
    opcion_vista = st.radio(
        "Modo de Visualización:",
        ["Foto del Plano Estructural", "Elevación Esquemática por Niveles"],
        horizontal=True,
    )

    if opcion_vista == "Foto del Plano Estructural":
      nombre_foto_base = (
          "plano_torre_a.png"
          if "Torre A" in torre_plano
          else (
              "plano_torre_b.png"
              if "Torre B" in torre_plano
              else "plano_torre_c.png"
          )
      )

      foto_subida = st.file_uploader(
          f"Cargar imagen del plano para {torre_plano.split(' (')[0]}:",
          type=["png", "jpg", "jpeg", "webp"],
          key=f"uploader_{torre_plano}",
      )

      if foto_subida is not None:
        st.image(
            foto_subida,
            caption=f"Plano cargado: {torre_plano.split(' (')[0]}",
            use_container_width=True,
        )
      elif os.path.exists(nombre_foto_base):
        st.image(
            nombre_foto_base,
            caption=(
                f"Plano Estructural Oficial: {torre_plano.split(' (')[0]}"
            ),
            use_container_width=True,
        )
      elif os.path.exists("plano_general.png") or os.path.exists(
          "plano_general.jpg"
      ):
        img_gen = (
            "plano_general.png"
            if os.path.exists("plano_general.png")
            else "plano_general.jpg"
        )
        st.image(
            img_gen,
            caption=(
                f"Plano General del Conjunto - {torre_plano.split(' (')[0]}"
            ),
            use_container_width=True,
        )
      else:
        st.info(
            "Suba la foto del plano con el boton superior o incluyala en el"
            f" repositorio como '{nombre_foto_base}'."
        )

    else:
      if "Torre A" in torre_plano or "Torre B" in torre_plano:
        pisos = [
            "Piso 5 (1 Apto)",
            "Piso 4 (2 Aptos)",
            "Piso 3 (2 Aptos)",
            "Piso 2 (2 Aptos)",
            "Piso 1 (2 Aptos)",
        ]
        unidades_piso = [1, 2, 2, 2, 2]
      else:
        pisos = [
            "Piso 6 (1 Apto)",
            "Piso 5 (2 Aptos)",
            "Piso 4 (2 Aptos)",
            "Piso 3 (2 Aptos)",
            "Piso 2 (2 Aptos)",
            "Piso 1 (2 Aptos)",
        ]
        unidades_piso = [1, 2, 2, 2, 2, 2]

      fig_ele = px.bar(
          x=unidades_piso,
          y=pisos,
          orientation="h",
          title=f"Elevacion Esquematica - {torre_plano.split(' (')[0]}",
          labels={"x": "Apartamentos por Nivel", "y": "Piso"},
          color_discrete_sequence=["#2f3e46"],
          text=unidades_piso,
      )
      fig_ele.update_traces(textposition="inside")
      fig_ele.update_layout(
          paper_bgcolor="rgba(0,0,0,0)",
          plot_bgcolor="rgba(0,0,0,0)",
          font=dict(family="Montserrat", size=12),
      )
      st.plotly_chart(fig_ele, use_container_width=True)

  with col_crit:
    st.markdown("""
            ### Puntos de Control Técnico
            * **Pisos Superiores:** Cubiertas y remates en Piso 5 (Torres A/B) y Piso 6 (Torre C).
            * **Juntas Sismicas:** Verificación de dilatacion entre bloques.
            * **Mamposteria:** Revision de fisuras a 45° vs. fisuras de acabado superficial.
            * **Redes:** Comprobación de integridad en bajantes y gas.
        """)
  mostrar_banner_habeas_data()

# -------------------------------------------------------------
# MODULO 5: ASISTENTE VIRTUAL (CHATBOT)
# -------------------------------------------------------------
elif pagina == "Asistente Virtual":
  st.subheader("💬 Asistente Comunitario")
  st.caption(
      "Consulte sobre las 3 torres (29 aptos), zonas comunes, seguro o comités"
      " de trabajo."
  )

  if "mensajes" not in st.session_state:
    st.session_state.mensajes = [{
        "role": "assistant",
        "content": (
            "Buenas tardes. Soy el asistente oficial del PMU Prados del"
            " Refugio. ¿En qué información sobre las 3 torres (29"
            " apartamentos), comités de trabajo o reclamación de seguros puedo"
            " orientarle?"
        ),
    }]

  for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
      st.write(msg["content"])

  if prompt := st.chat_input(
      "Escriba su consulta (ej: ¿Cuántos aptos tiene la Torre C? ¿Cómo me"
      " inscribo?)"
  ):
    st.session_state.mensajes.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.write(prompt)

    p_low = prompt.lower()
    if (
        "inscrib" in p_low
        or "postular" in p_low
        or "participar" in p_low
        or "comité" in p_low
        or "voluntario" in p_low
    ):
      resp = (
          "Puedes ver los integrantes y postularte en la pestaña 'Participa en"
          " la Recuperación'. Allí puedes editar los comités o llenar el"
          " formulario individual."
      )
    elif "urgente" in p_low or "semaforo" in p_low or "pendiente" in p_low:
      resp = (
          "Las prioridades urgentes son: consolidar el censo de los 28"
          " apartamentos reales, radicar poderes para la aseguradora e"
          " inspeccionar Torres B y C."
      )
    elif "torre a" in p_low:
      d = len(
          df[(df["torre"] == "Torre A") & (df["inmueble_afectado"] == "Si")]
      )
      resp = (
          "La Torre A cuenta con 9 apartamentos (Pisos 1-4 con 2 aptos y Piso"
          f" 5 con 1 apto). Registra {d} inmuebles con novedad."
      )
    elif "torre b" in p_low:
      d = len(
          df[(df["torre"] == "Torre B") & (df["inmueble_afectado"] == "Si")]
      )
      resp = (
          "La Torre B cuenta con 9 apartamentos (Pisos 1-4 con 2 aptos y Piso"
          f" 5 con 1 apto). Registra {d} inmuebles con novedad."
      )
    elif "torre c" in p_low:
      d = len(
          df[(df["torre"] == "Torre C") & (df["inmueble_afectado"] == "Si")]
      )
      resp = (
          "La Torre C cuenta con 11 apartamentos (Pisos 1-5 con 2 aptos y Piso"
          f" 6 con 1 apto). Registra {d} inmuebles con novedad."
      )
    elif "poliza" in p_low or "seguro" in p_low:
      resp = (
          "El expediente de póliza se encuentra consolidando poderes de los"
          " propietarios afectados para radicar ante la aseguradora."
      )
    else:
      resp = (
          "Su inquietud ha sido registrada en el sistema del PMU. Consulte los"
          " módulos laterales para más detalles."
      )

    st.session_state.mensajes.append({"role": "assistant", "content": resp})
    with st.chat_message("assistant"):
      st.write(resp)

  mostrar_banner_habeas_data()
