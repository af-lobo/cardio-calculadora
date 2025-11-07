import streamlit as st
import math
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

st.set_page_config(page_title="Calculadora Cardio", page_icon="❤️", layout="centered")

st.title("🫀 Calculadora de Indicadores Cardíacos")
st.write(
    "Aplicação simples para cálculo rápido de alguns indicadores "
    "cardiológicos (BSA, duplo produto, FCTMP e % da FCM atingida)."
)
st.markdown("— desenvolvida pelo filho para uso do pai cardiologista 🙂")

# =========================
# Campos opcionais do paciente
# =========================
st.header("👤 Identificação (opcional)")

col_id1, col_id2 = st.columns(2)
with col_id1:
    nome_paciente = st.text_input("Nome do paciente (opcional)", value="")
with col_id2:
    numero_paciente = st.text_input("Número de paciente / Processo (opcional)", value="")

st.divider()

# =========================
# Inputs clínicos
# =========================
st.header("1️⃣ Dados do doente")

col1, col2 = st.columns(2)
with col1:
    idade = st.number_input("Idade (anos)", min_value=1, max_value=120, value=60, step=1)
    peso = st.number_input("Peso (kg)", min_value=20.0, max_value=250.0, value=70.0, step=0.5)
with col2:
    altura = st.number_input("Altura (cm)", min_value=100.0, max_value=220.0, value=170.0, step=0.5)
    fc_max = st.number_input("FC máxima atingida (bpm)", min_value=30, max_value=250, value=140, step=1)

tas_max = st.number_input(
    "Tensão arterial sistólica máxima (mmHg)",
    min_value=50,
    max_value=300,
    value=180,
    step=1,
)

st.divider()

# =========================
# Cálculos
# =========================

# 1. BSA (Du Bois)
bsa = 0.007184 * (peso ** 0.425) * (altura ** 0.725)

# 2. FCTMP (220 - idade)
fctmp = 220 - idade

# 3. % FCM atingida
percent_fcm = (fc_max / fctmp) * 100 if fctmp > 0 else None

# 4. Duplo produto
duplo_produto = tas_max * fc_max   # se quiseres indexado, podes dividir por 100


st.header("2️⃣ Resultados")

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("📏 BSA – Área de superfície corporal")
    st.metric("BSA (m²)", f"{bsa:.2f}")
    with st.expander("ℹ Ver fórmula e notas"):
        st.markdown(
            r"""
            **Fórmula de Du Bois:**

            \[
            BSA = 0{,}007184 \times Peso^{0{,}425} \times Altura^{0{,}725}
            \]

            - Peso em **kg**  
            - Altura em **cm**  
            - Resultado em **m²**

            Uso típico: indexar variáveis (ex.: indexação de débito cardíaco).
            """
        )

    st.subheader("🧮 FCTMP – FC Teórica Máxima Prevista")
    st.metric("FCTMP (bpm)", f"{fctmp}")
    with st.expander("ℹ Ver fórmula e notas"):
        st.markdown(
            r"""
            **Fórmula clássica:**

            \[
            FCTMP = 220 - idade
            \]

            Utilizada como aproximação simples, sobretudo em contexto de 
            prescrição/exploração de esforço.  
            Existem fórmulas alternativas (Tanaka, etc.), mas esta é a mais usada.
            """
        )

with col_b:
    st.subheader("❤️ % da FCM atingida")
    if percent_fcm is not None:
        st.metric("% da FCTMP atingida", f"{percent_fcm:.1f} %")
    else:
        st.metric("% da FCTMP atingida", "—")

    with st.expander("ℹ Ver fórmula e notas"):
        st.markdown(
            r"""
            **Definição:**

            \[
            \% FCM = \frac{FC_{\text{máx atingida}}}{FCTMP} \times 100
            \]

            Onde:

            - \( FCTMP = 220 - idade \)  
            - Útil para avaliar em que fração da FC teórica máxima 
              o doente foi testado.
            """
        )

    st.subheader("📊 Duplo produto máximo")
    st.metric("Duplo produto (TAS × FC)", f"{duplo_produto:,}".replace(",", " "))
    with st.expander("ℹ Ver fórmula e notas"):
        st.markdown(
            r"""
            **Definição clássica:**

            \[
            DP_{\text{máx}} = TAS_{\text{máx}} \times FC_{\text{máx}}
            \]

            - TAS em **mmHg**  
            - FC em **bpm**

            Algumas fontes expressam o DP dividindo por 100 para facilitar a leitura:  
            \( DP_{\text{indexado}} = TAS_{\text{máx}} \times FC_{\text{máx}} / 100 \).
            """
        )

st.divider()

# =========================
# Função para gerar PDF
# =========================

def gerar_pdf(
    nome_paciente,
    numero_paciente,
    idade,
    peso,
    altura,
    fc_max,
    tas_max,
    bsa,
    fctmp,
    percent_fcm,
    duplo_produto,
):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Título
    titulo = "Relatório Sumário de Avaliação Cardíaca"
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 60, titulo)

    c.setFont("Helvetica", 9)
    c.drawString(50, height - 80, f"Data/Hora: {datetime.now().strftime('%d-%m-%Y %H:%M')}")

    # Identificação
    y = height - 120
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Identificação do paciente")
    c.setFont("Helvetica", 10)
    y -= 16
    c.drawString(60, y, f"Nome: {nome_paciente if nome_paciente else '—'}")
    y -= 14
    c.drawString(60, y, f"Nº de paciente / Processo: {numero_paciente if numero_paciente else '—'}")

    # Dados clínicos
    y -= 30
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Dados clínicos de base")
    c.setFont("Helvetica", 10)
    y -= 16
    c.drawString(60, y, f"Idade: {idade} anos")
    y -= 14
    c.drawString(60, y, f"Peso: {peso:.1f} kg")
    y -= 14
    c.drawString(60, y, f"Altura: {altura:.1f} cm")
    y -= 14
    c.drawString(60, y, f"FC máxima atingida: {fc_max} bpm")
    y -= 14
    c.drawString(60, y, f"TAS máxima: {tas_max} mmHg")

    # Resultados
    y -= 30
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Resultados dos cálculos")
    c.setFont("Helvetica", 10)
    y -= 16
    c.drawString(60, y, f"BSA (Du Bois): {bsa:.2f} m²")
    y -= 14
    c.drawString(60, y, f"FCTMP (220 - idade): {fctmp} bpm")
    y -= 14
    if percent_fcm is not None:
        c.drawString(60, y, f"% da FCTMP atingida: {percent_fcm:.1f} %")
    else:
        c.drawString(60, y, f"% da FCTMP atingida: —")
    y -= 14
    c.drawString(60, y, f"Duplo produto (TAS × FC): {duplo_produto}")

    # Rodapé
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(50, 40, "Nota: relatório gerado automaticamente. Não substitui o juízo clínico.")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# =========================
# Botão para exportar PDF
# =========================

st.header("3️⃣ Exportar relatório")

pdf_buffer = gerar_pdf(
    nome_paciente,
    numero_paciente,
    idade,
    peso,
    altura,
    fc_max,
    tas_max,
    bsa,
    fctmp,
    percent_fcm,
    duplo_produto,
)

st.download_button(
    label="📄 Descarregar relatório em PDF",
    data=pdf_buffer,
    file_name="relatorio_avaliacao_cardiaca.pdf",
    mime="application/pdf",
)

st.divider()
st.caption(
    "Nota: esta calculadora é meramente auxiliar e não substitui o juízo clínico."
)
