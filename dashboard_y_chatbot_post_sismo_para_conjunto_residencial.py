import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os

st.set_page_config(
    page_title="Prados del Refugio | PMU",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo editorial institucional (Inspirado en ProPacífico)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,600;1,400&display=swap');

    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
        color: #2b2b2b;
    }

    .hero-banner {
        background: linear-gradient(135deg, #1f2421 0%, #2f3e46 60%, #e05a2b 100%);
        padding: 36px 44px;
        border-radius: 4px;
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
        font-size: 13px;
        font-weight: 300;
        letter-spacing: 1.5px;
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
        color: #6c757d;
    }
    .kpi-value {
        font-size: 26px;
        font-weight: 700;
        color: #1f2421;
        margin-top: 4px;
    }
    .kpi-sub {
        font-size: 12px;
        color: #e05a2b;
        font-weight: 500;
        margin-top: 4px;
    }

    section[data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #e9ecef;
    }

    .phase-badge {
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #e05a2b;
        margin-top: 10px;
        margin-bottom: 8px;
    }

    .team-card {
        background: #ffffff;
        border-left: 4px solid #e05a2b;
        border-top: 1px solid #e9ecef;
        border-right: 1px solid #e9ecef;
        border-bottom: 1px solid #e9ecef;
        padding: 18px 20px;
        margin-bottom: 10px;
        border-radius: 3px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .team-card-header {
        font-size: 15px;
        font-weight: 600;
        color: #1f2421;
        margin-bottom: 6px;
    }
    .team-scope {
        font-size: 13px;
        color: #495057;
        margin-bottom: 6px;
        line-height: 1.5;
    }
    </style>
""", unsafe_allow_html=True)

# Generador de datos simulados
def generar_datos_base():
    np.random.seed(42)
    aptos_a = [f"{piso}0{num}" for piso in range(1, 6) for num in range(1, 5)]
    aptos_b = [f"{piso}0{num}" for piso in range(1, 6) for num in range(1, 5)]
    aptos_c = [f"{piso}0{num}" for piso in range(1, 7) for num in range(1, 5)]

    registros = []
    for a in aptos_a: registros.append({"torre": "Torre A", "unidad": a, "tipo": "Privado"})
    for b in aptos_b: registros.append({"torre": "Torre B", "unidad": b, "tipo": "Privado"})
    for c in aptos_c: registros.append({"torre": "Torre C", "unidad": c, "tipo": "Privado"})

    df_p = pd.DataFrame(registros)
    n = len(df_p)

    df_p["propietario"] = [f"Residente {i}" for i in range(1, n + 1)]
    df_p["cedula"] = [f"{np.random.randint(10000000, 99999999)}" for _ in range(n)]
    df_p["telefono"] = [f"3{np.random.randint(100000000, 999999999)}" for _ in range(n)]
    df_p["correo"] = [f"contacto{i}@prados.com" for i in range(1, n + 1)]
    df_p["hubo_lesionados"] = np.random.choice(["Sí", "No"], n, p=[0.04, 0.96])
    df_p["tipo_lesion"] = df_p["hubo_lesionados"].apply(
        lambda x: np.random.choice(["Contusión leve", "Corte superficial", "Ansiedad aguda"]) if x == "Sí" else "Ninguna"
    )
    df_p["inmueble_afectado"] = np.random.choice(["Sí", "No"], n, p=[0.52, 0.48])
    df_p["autoriza_datos"] = np.random.choice(["Sí", "No"], n, p=[0.94, 0.06])

    comunes = ["Pasillos", "Portería", "Gradas", "Parqueadero", "Salón Social", "Piscina"]
    registros_c = []
    for com in comunes:
        registros_c.append({
            "torre": "Áreas Comunes",
            "unidad": com,
            "tipo": "Común",
            "propietario": "Administración General",
            "cedula": "NIT Copropiedad",
            "telefono": "PBX Principal",
            "correo": "admin@pradosdelrefugio.com",
            "hubo_lesionados": "No",
            "tipo_lesion": "Ninguna",
            "inmueble_afectado": np.random.choice(["Sí", "No"], p=[0.5, 0.5]),
            "autoriza_datos": "Sí"
        })
    df_c = pd.DataFrame(registros_c)
    return pd.concat([df_p, df_c], ignore_index=True)

@st.cache_data
def cargar_datos():
    if os.path.exists("resultados.csv"):
        return pd.read_csv("resultados.csv")
    else:
        return generar_datos_base()

df = cargar_datos()
df_priv = df[df["tipo"] == "Privado"]
df_com = df[df["tipo"] == "Común"]

# Menú lateral
st.sidebar.markdown("""
    <div style="padding: 10px 0 20px 0;">
        <span style="font-family: 'Playfair Display', serif; font-size: 20px; font-weight: 700; color: #1f2421;">Prados del Refugio</span><br>
        <span style="font-size: 11px; color: #e05a2b; letter-spacing: 1px; text-transform: uppercase;">Puesto de Mando Unificado</span>
    </div>
""", unsafe_allow_html=True)

pagina = st.sidebar.radio(
    "Módulos de Información",
    [
        "Panel de Control y Diagnóstico",
        "Póliza y Reclamación de Seguros",
        "Planos Estructurales e Inspección",
        "Equipos de Trabajo y Tareas",
        "Asistente Virtual"
    ]
)

# Header Global
st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">Conjunto Residencial Prados del Refugio</div>
        <div class="hero-subtitle">Sistema Integrado de Información Post-Sismo · Cali</div>
    </div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 1. PANEL DE CONTROL Y DIAGNÓSTICO
# -------------------------------------------------------------
if pagina == "Panel de Control y Diagnóstico":
    c1, c2, c3, c4 = st.columns(4)
    total_censados = len(df_priv)
    afectados_aptos = (df_priv["inmueble_afectado"] == "Sí").sum()
    afectados_comunes = (df_com["inmueble_afectado"] == "Sí").sum()
    lesionados = (df["hubo_lesionados"] == "Sí").sum()

    with c1:
        st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-label">Censo Unidades Privadas</div>
                <div class="kpi-value">{total_censados}</div>
                <div class="kpi-sub">Torres A (5p), B (5p), C (6p)</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-label">Inmuebles con Afectación</div>
                <div class="kpi-value">{afectados_aptos}</div>
                <div class="kpi-sub">{round(afectados_aptos/total_censados*100)}% del total censado</div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-label">Zonas Comunes Afectadas</div>
                <div class="kpi-value">{afectados_comunes} / {len(df_com)}</div>
                <div class="kpi-sub">Evaluación locativa</div>
            </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-label">Atención en Salud</div>
                <div class="kpi-value">{lesionados}</div>
                <div class="kpi-sub">Prioridad asistencial</div>
            </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.write("")

    g1, g2 = st.columns(2)
    with g1:
        df_torres = df_priv.groupby(["torre", "inmueble_afectado"]).size().reset_index(name="conteo")
        fig1 = px.bar(
            df_torres, x="torre", y="conteo", color="inmueble_afectado",
            title="Consolidado de Afectaciones por Torre",
            barmode="stack",
            color_discrete_map={"Sí": "#e05a2b", "No": "#2f3e46"},
            category_orders={"torre": ["Torre A", "Torre B", "Torre C"]}
        )
        fig1.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Montserrat", size=12),
            legend_title_text="Reporte Daño"
        )
        st.plotly_chart(fig1, use_container_width=True)

    with g2:
        fig2 = px.bar(
            df_com, x="unidad", y="inmueble_afectado",
            title="Diagnóstico Técnico en Áreas Comunes",
            color="inmueble_afectado",
            color_discrete_map={"Sí": "#e05a2b", "No": "#2f3e46"}
        )
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Montserrat", size=12),
            xaxis_title="", yaxis_title="",
            legend_title_text="Afectación"
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.write("---")
    st.subheader("Detalle Nominal de Inmuebles")
    st.caption("Filtro por bloque estructural con resguardo estricto de Habeas Data.")
    torre_sel = st.selectbox("Seleccionar Bloque:", ["Torre A", "Torre B", "Torre C"])
    df_vista = df_priv[df_priv["torre"] == torre_sel][
        ["unidad", "inmueble_afectado", "hubo_lesionados", "tipo_lesion", "autoriza_datos"]
    ].rename(columns={
        "unidad": "Apartamento",
        "inmueble_afectado": "Afectación Reportada",
        "hubo_lesionados": "Lesionados",
        "tipo_lesion": "Diagnóstico Inicial",
        "autoriza_datos": "Autorización Póliza"
    })
    st.dataframe(df_vista, use_container_width=True, hide_index=True)

# -------------------------------------------------------------
# 2. PÓLIZA Y RECLAMACIÓN DE SEGUROS
# -------------------------------------------------------------
elif pagina == "Póliza y Reclamación de Seguros":
    st.subheader("Gestión y Trámite de Póliza Colectiva")
    st.write("Lineamientos técnicos y normativos para la radicación del siniestro ante la compañía aseguradora.")

    c_p1, c_p2 = st.columns([1, 1])
    with c_p1:
        st.markdown("""
            ### Ficha Técnica de la Póliza
            * **Aseguradora:** Seguros del Estado / Copropiedades
            * **Régimen:** Póliza de Zonas Comunes y Privadas con Amparo de Terremoto
            * **Vigencia:** 2026 - 2027
            * **Deducible Sismo:** 10% del valor de la pérdida con mínimo legal
            * **Estado:** Aviso de siniestro emitido formalmente
        """)
    with c_p2:
        st.markdown("""
            ### Protocolo de Integración de Expedientes
            1. **Consolidación del Censo:** Cierre formal del censo de afectaciones locativas.
            2. **Filtro de Habeas Data:** Inclusión estricta de propietarios con autorización digital firmada.
            3. **Inspección de Ajuste:** Visita del perito designado para evaluación técnica en sitio.
            4. **Dictamen Estructural:** Emisión de acta de liquidación y cronograma de resarcimiento.
        """)

    st.write("---")
    st.subheader("Expediente para Radicación al Ajustador")
    df_seguro = df[(df["inmueble_afectado"] == "Sí") & (df["autoriza_datos"] == "Sí")][
        ["torre", "unidad", "propietario", "cedula", "telefono", "correo"]
    ]
    st.caption(f"Total registros listos para radicación inmediata: {len(df_seguro)} inmuebles.")
    st.dataframe(df_seguro, use_container_width=True, hide_index=True)

    csv_exp = df_seguro.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Descargar Expediente Consolidado (CSV)",
        data=csv_exp,
        file_name="Expediente_Seguros_Prados_del_Refugio.csv",
        mime="text/csv"
    )

# -------------------------------------------------------------
# 3. PLANOS ESTRUCTURALES E INSPECCIÓN
# -------------------------------------------------------------
elif pagina == "Planos Estructurales e Inspección":
    st.subheader("Planos Estructurales y Puntos Críticos de Inspección")
    st.write("Consulte la distribución por niveles de las Torres A, B y C junto a las directrices de revisión de mampostería y estructura portante.")

    torre_plano = st.selectbox("Seleccionar Plano por Bloque:", [
        "Torre A (5 Niveles - Sistema Aporticado)",
        "Torre B (5 Niveles - Sistema Aporticado)",
        "Torre C (6 Niveles - Sistema Aporticado / Muros de Corte)"
    ])

    col_plano, col_crit = st.columns([1.4, 1])

    with col_plano:
        if "Torre A" in torre_plano or "Torre B" in torre_plano:
            pisos = [f"Nivel {i}" for i in range(5, 0, -1)]
        else:
            pisos = [f"Nivel {i}" for i in range(6, 0, -1)]

        fig_ele = px.bar(
            x=[4]*len(pisos),
            y=pisos,
            orientation='h',
            title=f"Elevación Esquemática - {torre_plano.split(' (')[0]}",
            labels={'x': 'Unidades por Nivel', 'y': 'Piso'},
            color_discrete_sequence=['#2f3e46']
        )
        fig_ele.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Montserrat", size=12)
        )
        st.plotly_chart(fig_ele, use_container_width=True)

    with col_crit:
        st.markdown("""
            ### Puntos de Control Técnico
            * **Juntas de Dilatación:** Verificación de separación libre entre bloques.
            * **Caja de Gradas:** Inspección de muros divisorios no estructurales.
            * **Paredes de Mampostería:** Registro de fisuras diagonales a 45° vs. fisuras superficiales de estuco.
            * **Redes Hidrosanitarias:** Comprobación de integridad en bajantes principales de aguas servidas.
        """)

# -------------------------------------------------------------
# 4. EQUIPOS DE TRABAJO Y TAREAS (ESTRUCTURA DE 6 FASES)
# -------------------------------------------------------------
elif pagina == "Equipos de Trabajo y Tareas":
    st.subheader("Estructura Operativa y Comités por Fases")
    st.write("Organización modular del conjunto en 6 grandes fases de trabajo para garantizar agilidad, gobernanza y seguimiento de tareas.")

    if "colaboradores" not in st.session_state:
        st.session_state.colaboradores = {
            "eq1": "Arq. Roberto Gómez (Apto 302-A), Ing. Carlos Mina (Apto 504-B)",
            "eq2": "Melisa Espinosa (Apto 401-C), Diana Pérez (Apto 102-A)",
            "eq3": "Dr. Fernando Ruiz (Apto 204-B), Sandra Jaramillo (Apto 501-C)",
            "eq4": "Abg. Claudia Morales (Apto 402-A), Juan David Soto (Apto 303-C)",
            "eq5": "Comité de Comunicaciones, Laura Benítez (Apto 201-B)",
            "eq6": "Administración Prados del Refugio, Revisor Fiscal, Tesorería",
            "eq7": "Brigada de Aseo, Manuel Quintero (Apto 104-C)",
            "eq8": "Comité de Obras, Ing. Civil Residente (Apto 403-B)"
        }

    fases = [
        {
            "fase": "FASE 1 — RESPUESTA Y DIAGNÓSTICO",
            "equipos": [
                {
                    "id": "eq1",
                    "nombre": "1. Evaluación de Daños y Seguridad",
                    "alcance": "Inspección técnica visual de afectaciones estructurales en Torres A, B, C y zonas comunes (gradas, parqueadero, piscina). Verificación de habitabilidad y redes.",
                    "tareas": "• Recorrido técnico por niveles y registro fotográfico.\n• Delimitación preventiva de zonas de riesgo.\n• Emisión de informe preliminar de seguridad locativa."
                },
                {
                    "id": "eq2",
                    "nombre": "2. Censo y Caracterización",
                    "alcance": "Consolidación de la base de datos de propietarios y arrendatarios afectados, reporte de personas lesionadas y estado general de los inmuebles privados.",
                    "tareas": "• Depuración del formulario digital de afectaciones.\n• Verificación de llamadas puerta a puerta en apartamentos pendientes.\n• Actualización en tiempo real del tablero de mando."
                }
            ]
        },
        {
            "fase": "FASE 2 — PROTECCIÓN Y GESTIÓN DEL SINIESTRO",
            "equipos": [
                {
                    "id": "eq3",
                    "nombre": "3. Seguros y Siniestros",
                    "alcance": "Gestión directa con la aseguradora de la copropiedad (póliza de zonas comunes y privadas) y acompañamiento a los peritos de ajuste.",
                    "tareas": "• Consolidación del archivo digital de reclamación con Habeas Data.\n• Coordinación del cronograma de visitas del ajustador.\n• Seguimiento a la liquidación del siniestro y deducibles."
                },
                {
                    "id": "eq4",
                    "nombre": "4. Jurídico-Administrativo",
                    "alcance": "Soporte legal en contratos de emergencia, redacción de actas de asamblea, verificación de quórum y cumplimiento de la Ley 675.",
                    "tareas": "• Elaboración de poderes y actas extraordinarias.\n• Revisión de cláusulas contractuales de proveedores de auxilio.\n• Asesoría jurídica a copropietarios en trámites de siniestro."
                }
            ]
        },
        {
            "fase": "FASE 3 — INFORMACIÓN Y PARTICIPACIÓN",
            "equipos": [
                {
                    "id": "eq5",
                    "nombre": "5. Comunicaciones y Atención a Residentes",
                    "alcance": "Canal oficial y transparente de información a la comunidad, emisión de comunicados oficiales y atención de dudas en portería/asistente.",
                    "tareas": "• Emisión de boletines informativos periódicos.\n• Atención prioritaria a adultos mayores y familias con afectaciones.\n• Difusión y pedagogía sobre el uso del dashboard y chatbot."
                }
            ]
        },
        {
            "fase": "FASE 4 — RECURSOS Y FINANZAS",
            "equipos": [
                {
                    "id": "eq6",
                    "nombre": "6. Administración, Finanzas y Proveedores",
                    "alcance": "Control y ejecución del fondo de imprevistos, cotización transparente con proveedores de obra y rendición de cuentas en tiempo real.",
                    "tareas": "• Balance del fondo de imprevistos y flujo de caja.\n• Comparativo de mínimo 3 cotizaciones por servicio técnico.\n• Publicación de soportes contables del siniestro."
                }
            ]
        },
        {
            "fase": "FASE 5 — RECUPERACIÓN Y HABITABILIDAD",
            "equipos": [
                {
                    "id": "eq7",
                    "nombre": "7. Limpieza, Recuperación y Habitabilidad",
                    "alcance": "Operativos de remoción de escombros no estructurales, retiro de vidrios rotos, restablecimiento de servicios básicos y aseo general.",
                    "tareas": "• Jornadas de recolección segura de escombros en gradas y pasillos.\n• Revisión del funcionamiento de bombas de agua y piscina.\n• Habilitación y señalización de zonas comunes seguras."
                }
            ]
        },
        {
            "fase": "FASE 6 — RECONSTRUCCIÓN",
            "equipos": [
                {
                    "id": "eq8",
                    "nombre": "8. Reparación y Reconstrucción",
                    "alcance": "Supervisión de obras civiles definitivas, resane de mampostería, reposición de acabados y cierre formal de expedientes técnicos.",
                    "tareas": "• Interventoría comunitaria y seguimiento a cronogramas de obra.\n• Inspección de calidad en materiales y mano de obra.\n• Entrega de actas de satisfacción a copropietarios e interventor."
                }
            ]
        }
    ]

    for f in fases:
        st.markdown(f'<div class="phase-badge">{f["fase"]}</div>', unsafe_allow_html=True)
        cols = st.columns(len(f["equipos"]))

        for idx, eq in enumerate(f["equipos"]):
            with cols[idx]:
                st.markdown(f"""
                    <div class="team-card">
                        <div class="team-card-header">{eq["nombre"]}</div>
                        <div class="team-scope">{eq["alcance"]}</div>
                    </div>
                """, unsafe_allow_html=True)

                with st.expander("Ver tareas detalladas"):
                    st.markdown(eq["tareas"])

                nuevo_colab = st.text_area(
                    f"Personas que pueden colaborar:",
                    value=st.session_state.colaboradores.get(eq["id"], ""),
                    key=f"input_{eq['id']}",
                    height=70,
                    help="Ingresa nombres, apartamentos o profesiones de voluntarios para este equipo."
                )
                st.session_state.colaboradores[eq["id"]] = nuevo_colab

        st.write("")

# -------------------------------------------------------------
# 5. ASISTENTE VIRTUAL
# -------------------------------------------------------------
elif pagina == "Asistente Virtual":
    st.subheader("💬 Asistente Comunitario")
    st.caption("Consulte en lenguaje natural el estado de su torre, áreas comunes, póliza o equipos de trabajo.")

    if "mensajes" not in st.session_state:
        st.session_state.mensajes = [{
            "role": "assistant",
            "content": "Buenas tardes. Soy el asistente oficial de Prados del Refugio. ¿En qué información sobre las torres, póliza de seguro o equipos de trabajo puedo orientarle?"
        }]

    for msg in st.session_state.mensajes:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Escriba su consulta (ej: ¿Qué comités están en la Fase 1? ¿Cómo está la póliza?)"):
        st.session_state.mensajes.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        p_low = prompt.lower()
        if "fase" in p_low or "equipo" in p_low or "comite" in p_low or "grupo" in p_low:
            resp = "La copropiedad se organiza en 6 Fases operativas: 1) Respuesta y Diagnóstico (Evaluación y Censo), 2) Protección y Siniestro (Seguros y Jurídico), 3) Información (Comunicaciones), 4) Recursos (Finanzas y Proveedores), 5) Recuperación (Limpieza y Habitabilidad) y 6) Reconstrucción (Reparación)."
        elif "poliza" in p_low or "seguro" in p_low or "aseguradora" in p_low:
            resp = "El equipo de Seguros y Siniestros (Fase 2) está consolidando el expediente con las firmas de autorización para radicar en bloque ante la aseguradora."
        elif "torre a" in p_low:
            d = len(df[(df["torre"] == "Torre A") & (df["inmueble_afectado"] == "Sí")])
            resp = f"La Torre A (5 pisos) registra {d} inmuebles con reportes de afectaciones en proceso de verificación por el Equipo 1."
        elif "torre b" in p_low:
            d = len(df[(df["torre"] == "Torre B") & (df["inmueble_afectado"] == "Sí")])
            resp = f"La Torre B (5 pisos) registra {d} inmuebles con reportes de afectaciones en proceso de verificación por el Equipo 1."
        elif "torre c" in p_low:
            d = len(df[(df["torre"] == "Torre C") & (df["inmueble_afectado"] == "Sí")])
            resp = f"La Torre C (6 pisos) registra {d} inmuebles con reportes de afectaciones en proceso de verificación por el Equipo 1."
        elif "piscina" in p_low or "parqueadero" in p_low or "gradas" in p_low or "comunes" in p_low:
            resp = "Las zonas comunes se encuentran bajo inspección del equipo de Evaluación y el equipo de Limpieza y Recuperación para habilitar su uso seguro."
        else:
            resp = "Su inquietud ha sido registrada. Puede consultar la pestaña de Equipos de Trabajo para conocer los coordinadores y tareas asignadas."

        st.session_state.mensajes.append({"role": "assistant", "content": resp})
        with st.chat_message("assistant"):
            st.write(resp)
