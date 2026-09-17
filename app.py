import os
import datetime
import pandas as pd
import streamlit as st
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Renascer Locação",
    page_icon="🏰",
    layout="wide"
)

# --- DIRETÓRIO PARA SALVAR PDFS LOCALMENTE (SE EXECUTADO NO SEU COMPUTADOR) ---
PASTA_PDF = r"C:\Users\netho\OneDrive\Desktop\Modelo 02 - Copia\PDF"
if os.path.exists(r"C:\Users\netho"):
    os.makedirs(PASTA_PDF, exist_ok=True)

# --- EXIBIÇÃO DA LOGO E CABEÇALHO ---
URL_LOGO = "https://raw.githubusercontent.com/streamlit/app-archetype/main/static/logo.png"

# Determina qual imagem de logo utilizar
logo_para_exibir = "logo.png" if os.path.exists("logo.png") else URL_LOGO

col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    st.image(logo_para_exibir, width=120)

with col_titulo:
    st.title("🏰 Renascer Locação")
    st.caption("Soluções completas em locação para seu evento!")

# --- MENU LATERAL DE NAVEGAÇÃO SECRETO ---
query_params = st.query_params
eh_admin = str(query_params.get("admin", "")).lower() == "true"

st.sidebar.image(logo_para_exibir, use_container_width=True)
st.sidebar.title("📌 Navegação")

if eh_admin:
    opcoes_menu = ["Área do Cliente", "Meu Perfil", "Painel Administrativo"]
else:
    opcoes_menu = ["Área do Cliente", "Meu Perfil"]

modo = st.sidebar.radio("Ir para:", opcoes_menu)

# --- BASE DE DADOS SIMULADA ---
if "pedidos" not in st.session_state:
    st.session_state.pedidos = pd.DataFrame([
        {"ID": 101, "Cliente": "João Silva", "Data": datetime.date(2026, 9, 20), "Valor": 450.0, "Status": "Confirmado", "Imprimir": False},
        {"ID": 102, "Cliente": "Maria Santos", "Data": datetime.date(2026, 9, 25), "Valor": 1200.0, "Status": "Pendente", "Imprimir": False},
        {"ID": 103, "Cliente": "Carlos Oliveira", "Data": datetime.date(2026, 10, 5), "Valor": 800.0, "Status": "Confirmado", "Imprimir": False},
    ])

# --- FUNÇÃO DE GERAÇÃO DE CONTRATO PDF (EM MEMÓRIA E ARQUIVO LOCAL) ---
def gerar_contrato_pdf_bytes(id_pedido, cliente, valor, data_evento):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "CONTRATO DE PRESTAÇÃO DE SERVIÇOS E LOCAÇÃO")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, 730, "RENASCER LOCAÇÕES")
    
    c.setFont("Helvetica", 10)
    text = c.beginText(100, 690)
    text.setLeading(14)
    
    linhas_texto = [
        f"Contratante: {cliente}",
        f"Pedido N: {id_pedido} | Data do Evento: {data_evento.strftime('%d/%m/%Y')}",
        f"Valor Total: R$ {valor:.2f}",
        "",
        "CLÁUSULAS E CONDIÇÕES CONTRATUAIS:",
        "",
        "1. DO OBJETO E CONSERVAÇÃO:",
        "   O Locatário responsabiliza-se pela guarda e conservação dos materiais locados.",
        "",
        "2. DAS CONDIÇÕES DE ENTREGA E RECOLHIMENTO:",
        "   O Locador se prontifica a entregar os materiais em condições de uso e sem avarias,",
        "   dentro do prazo combinado e local preestabelecido, e a recolher dentro do prazo ora combinado.",
        "",
        "3. DOS DANOS E PERDAS:",
        "   O Locatário compromete-se a ressarcir o Locador em caso de danos e perdas.",
        "",
        "4. DO CANCELAMENTO E MULTA RESCISÓRIA:",
        "   O cancelamento do pedido deve ser realizado em pelo menos uma semana (7 dias) antes do evento.",
        "   Em caso de cancelamento fora do prazo ou descumprimento contratual, haverá multa de 30% do valor total do contrato.",
    ]
    
    for linha in linhas_texto:
        text.textLine(linha)
        
    c.drawText(text)
    c.save()
    
    pdf_bytes = buffer.getvalue()
    buffer.close()

    # Salva também na pasta local caso o sistema esteja rodando na máquina
    if os.path.exists(PASTA_PDF):
        caminho_local = os.path.join(PASTA_PDF, f"Contrato_Pedido_{id_pedido}.pdf")
        with open(caminho_local, "wb") as f:
            f.write(pdf_bytes)

    return pdf_bytes

# --- ÁREA DO CLIENTE ---
if modo == "Área do Cliente":
    st.header("📋 Solicitado / Agendamento de Reserva")
    
    with st.form("form_reserva"):
        nome = st.text_input("Nome Completo")
        telefone = st.text_input("Telefone / WhatsApp")
        data_evento = st.date_input("Data do Evento", min_value=datetime.date.today())
        tipo_evento = st.selectbox("Tipo de Evento", ["Aniversário", "Casamento", "Churrasco", "Corporativo", "Outro"])
        observacoes = st.text_area("Observações adicionais (opcional)")
        
        btn_enviar = st.form_submit_button("Enviar Solicitação")
        
        if btn_enviar:
            if nome and telefone:
                st.success("🎉 Solicitação enviada com sucesso! Entraremos em contato para confirmar sua reserva.")
            else:
                st.error("Por favor, preencha todos os campos obrigatórios.")

# --- MEU PERFIL ---
elif modo == "Meu Perfil":
    st.header("👤 Meu Perfil")
    st.info("Consulte o status das suas reservas ou atualize seus dados de contato.")
    
    cpf_busca = st.text_input("Informe seu CPF para localizar suas reservas:")
    if st.button("Buscar"):
        if cpf_busca:
            st.warning("Nenhuma reserva ativa encontrada para o CPF informado.")
        else:
            st.error("Por favor, informe o CPF.")

# --- PAINEL ADMINISTRATIVO (PROTEGIDO) ---
elif modo == "Painel Administrativo":
    st.header("🔒 Acesso Restrito - Administração")
    
    senha_correta = "renascer123"
    senha_digitada = st.text_input("Digite a senha de administrador:", type="password")
    
    if senha_digitada == senha_correta:
        st.success("Acesso liberado!")
        
        aba_impressao, aba_entrega, aba_financeiro = st.tabs([
            "🖨️ Impressão Rápida", 
            "🚚 Relatório de Entrega", 
            "💰 Relatório Financeiro"
        ])
        
        # ABA 1: IMPRESSÃO RÁPIDA COM SELEÇÃO
        with aba_impressao:
            st.subheader("Impressão de Pedidos em Lote")
            st.write("Marque as Caixas de Seleção dos pedidos que deseja gerar/imprimir:")
            
            # Tabela editável com caixas de marcação
            pedidos_editados = st.data_editor(
                st.session_state.pedidos,
                column_config={
                    "Imprimir": st.column_config.CheckboxColumn("Selecionar", default=False)
                },
                disabled=["ID", "Cliente", "Data", "Valor", "Status"],
                hide_index=True
            )
            
            selecionados = pedidos_editados[pedidos_editados["Imprimir"] == True]
            
            if not selecionados.empty:
                st.markdown("---")
                st.write("📄 **PDFs dos Pedidos Selecionados:**")
                for _, row in selecionados.iterrows():
                    pdf_bytes = gerar_contrato_pdf_bytes(row["ID"], row["Cliente"], row["Valor"], row["Data"])
                    
                    st.download_button(
                        label=f"⬇️ Baixar Contrato - Pedido #{row['ID']} ({row['Cliente']})",
                        data=pdf_bytes,
                        file_name=f"Contrato_Pedido_{row['ID']}.pdf",
                        mime="application/pdf",
                        key=f"dl_{row['ID']}"
                    )
            else:
                st.info("Nenhum pedido marcado no momento. Marque a caixa na coluna 'Selecionar' acima.")

        # ABA 2: RELATÓRIO DE ENTREGA COM FILTRO LIVRE DE DATAS
        with aba_entrega:
            st.subheader("Filtrar Entregas por Período Customizado")
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                dt_inicio_ent = st.date_input("Data Inicial (Entrega)", value=datetime.date(2025, 1, 1), key="ent_ini")
            with col_d2:
                dt_fim_ent = st.date_input("Data Final (Entrega)", value=datetime.date(2026, 12, 31), key="ent_fim")
                
            df_entregas = st.session_state.pedidos[
                (st.session_state.pedidos["Data"] >= dt_inicio_ent) & 
                (st.session_state.pedidos["Data"] <= dt_fim_ent)
            ]
            st.dataframe(df_entregas, use_container_width=True)

        # ABA 3: RELATÓRIO FINANCEIRO COM FILTRO LIVRE DE DATAS (MESES/ANOS DIFERENTES)
        with aba_financeiro:
            st.subheader("Relatório Financeiro Customizado")
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                dt_inicio_fin = st.date_input("Data Inicial", value=datetime.date(2025, 1, 1), key="fin_ini")
            with col_f2:
                dt_fim_fin = st.date_input("Data Final", value=datetime.date(2026, 12, 31), key="fin_fim")
                
            df_financeiro = st.session_state.pedidos[
                (st.session_state.pedidos["Data"] >= dt_inicio_fin) & 
                (st.session_state.pedidos["Data"] <= dt_fim_fin)
            ]
            
            faturamento_total = df_financeiro["Valor"].sum()
            st.metric(label="Faturamento Total no Período", value=f"R$ {faturamento_total:,.2f}")
            st.dataframe(df_financeiro, use_container_width=True)
            
    elif senha_digitada:
        st.error("Senha incorreta! Tente novamente.")
