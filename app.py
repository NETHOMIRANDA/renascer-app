import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime
from difflib import SequenceMatcher
import io
import os
import requests
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Configuração da página
st.set_page_config(
    page_title="Renascer Locações & Eventos",
    page_icon="🎉",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilização CSS para Interface Moderna, Tela Cheia Total e Sem Elementos da Plataforma
st.markdown("""
    <style>
    /* Ocultar elementos padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display:none !important;}
    
    /* Layout em Tela Cheia */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 1.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }

    /* Banner / Slogan Centralizado da Empresa */
    .hero-container {
        background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%);
        color: #FFFFFF;
        padding: 30px 20px;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0px 8px 20px rgba(15, 23, 42, 0.15);
        margin-bottom: 25px;
    }
    .hero-title {
        font-size: 32px;
        font-weight: 800;
        letter-spacing: 1px;
        color: #F8FAFC;
        margin: 0;
    }
    .hero-slogan {
        font-size: 16px;
        color: #F59E0B;
        font-weight: 600;
        margin-top: 6px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .hero-description {
        font-size: 14px;
        color: #94A3B8;
        max-width: 800px;
        margin: 12px auto 0 auto;
        line-height: 1.5;
    }

    /* Estilização dos Tabs */
    div[data-baseweb="tab-list"] {
        background-color: #F1F5F9;
        padding: 6px;
        border-radius: 12px;
        z-index: 999;
        margin-bottom: 25px;
    }
    div[data-baseweb="tab"] {
        color: #475569 !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
    }
    div[aria-selected="true"] {
        background-color: #1E3A8A !important;
        color: #FFFFFF !important;
        box-shadow: 0px 4px 10px rgba(30, 58, 138, 0.2);
    }

    /* Botão Discreto no Rodapé */
    .btn-sair-container {
        display: flex;
        justify-content: center;
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid #E2E8F0;
    }
    </style>
""", unsafe_allow_html=True)

# --- GERENCIAMENTO DO ARQUIVO CSV DE CATÁLOGO ---
CSV_CATALOGO = "catalogo.csv"
PASTA_PDF = r"C:\Users\netho\OneDrive\Desktop\Modelo 02 - Copia\PDF"

CATALOGO_PADRAO = [
    # Mobiliário & Mesas
    {"id": 1, "categoria": "Mobiliário & Mesas", "nome": "Jogo de Mesa com 4 Cadeiras de Plástico (Branca)", "preco": 14.00, "estoque": 50, "foto": "", "tipo_mesa": "quadrada", "tipo_toalha": "None"},
    {"id": 2, "categoria": "Mobiliário & Mesas", "nome": "Mesa Redonda de 6 Lugares (Tampão de Madeira)", "preco": 18.00, "estoque": 20, "foto": "", "tipo_mesa": "redonda", "tipo_toalha": "None"},
    {"id": 3, "categoria": "Mobiliário & Mesas", "nome": "Aparador Rústico de Madeira (2,50m)", "preco": 25.00, "estoque": 5, "foto": "", "tipo_mesa": "aparador", "tipo_toalha": "None"},
    {"id": 4, "categoria": "Mobiliário & Mesas", "nome": "Cadeira de Plástico Branca Avulsa", "preco": 3.00, "estoque": 200, "foto": "", "tipo_mesa": "None", "tipo_toalha": "None"},
         
    # Toalhas & Enxoval
    {"id": 7, "categoria": "Toalhas & Enxoval", "nome": "Toalha Quadrada para Mesa (1,50m x 1,50m)", "preco": 6.00, "estoque": 100, "foto": "", "tipo_mesa": "None", "tipo_toalha": "quadrada"},
    {"id": 8, "categoria": "Toalhas & Enxoval", "nome": "Toalha Redonda para Mesa 6 e 7 Lugares", "preco": 12.00, "estoque": 80, "foto": "", "tipo_mesa": "None", "tipo_toalha": "redonda"},
    {"id": 9, "categoria": "Toalhas & Enxoval", "nome": "Cobre-Mancha / Cobre-Mesa Colorido", "preco": 6.00, "estoque": 120, "foto": "", "tipo_mesa": "None", "tipo_toalha": "None"},
    {"id": 10, "categoria": "Toalhas & Enxoval", "nome": "Guardanapo de Tecido (Diversas Cores)", "preco": 1.00, "estoque": 300, "foto": "", "tipo_mesa": "None", "tipo_toalha": "None"},
    
    # Louças & Copos
    {"id": 11, "categoria": "Louças & Copos", "nome": "Prato de Jantar Raso Branco Liso", "preco": 0.80, "estoque": 300, "foto": "", "tipo_mesa": "None", "tipo_toalha": "None"},
    {"id": 12, "categoria": "Louças & Copos", "nome": "Prato de Sobremesa Branco Liso", "preco": 0.80, "estoque": 250, "foto": "", "tipo_mesa": "None", "tipo_toalha": "None"},
    {"id": 13, "categoria": "Louças & Copos", "nome": "Taça para Água / Vinho Transparente", "preco": 1.00, "estoque": 200, "foto": "", "tipo_mesa": "None", "tipo_toalha": "None"},
    {"id": 14, "categoria": "Louças & Copos", "nome": "Taça de Cerveja / Chope (300ml)", "preco": 1.00, "estoque": 200, "foto": "", "tipo_mesa": "None", "tipo_toalha": "None"},
    {"id": 15, "categoria": "Louças & Copos", "nome": "Copo Americano / Multiuso", "preco": 0.80, "estoque": 300, "foto": "", "tipo_mesa": "None", "tipo_toalha": "None"},
    {"id": 16, "categoria": "Louças & Copos", "nome": "Garfo de Jantar Inox", "preco": 0.80, "estoque": 400, "foto": "", "tipo_mesa": "None", "tipo_toalha": "None"},
    {"id": 17, "categoria": "Louças & Copos", "nome": "Faca de Jantar Inox", "preco": 0.80, "estoque": 400, "foto": "", "tipo_mesa": "None", "tipo_toalha": "None"},
    {"id": 18, "categoria": "Louças & Copos", "nome": "Colher de Sobremesa Inox", "preco": 0.80, "estoque": 300, "foto": "", "tipo_mesa": "None", "tipo_toalha": "None"},
    
    # Serviço & Rechauds
    {"id": 19, "categoria": "Serviço & Rechauds", "nome": "Rechaud Inox Redondo Banho-Maria", "preco": 25.00, "estoque": 10, "foto": "", "tipo_mesa": "None", "tipo_toalha": "None"},
    {"id": 20, "categoria": "Serviço & Rechauds", "nome": "Rechaud Inox Retangular Duplo", "preco": 40.00, "estoque": 8, "foto": "", "tipo_mesa": "None", "tipo_toalha": "None"},
    {"id": 21, "categoria": "Serviço & Rechauds", "nome": "Suqueira de Vidro com Torneira (5 Litros)", "preco": 25.00, "estoque": 12, "foto": "", "tipo_mesa": "None", "tipo_toalha": "None"},
    {"id": 22, "categoria": "Serviço & Rechauds", "nome": "Saladeira / Travesa de Inox", "preco": 15.00, "estoque": 20, "foto": "", "tipo_mesa": "None", "tipo_toalha": "None"},
    {"id": 23, "categoria": "Serviço & Rechauds", "nome": "Pegador de Salada / Carne Inox", "preco": 3.00, "estoque": 30, "foto": "", "tipo_mesa": "None", "tipo_toalha": "None"},
    {"id": 24, "categoria": "Serviço & Rechauds", "nome": "Concha para Molho / Sopa Inox", "preco": 5.00, "estoque": 25, "foto": "", "tipo_mesa": "None", "tipo_toalha": "None"},
    
    # Equipamentos & Freezers
    {"id": 25, "categoria": "Equipamentos & Freezers", "nome": "Freezer Horizontal 2 Tampas (400 Litros)", "preco": 200.00, "estoque": 3, "foto": "", "tipo_mesa": "None", "tipo_toalha": "None"},
    {"id": 26, "categoria": "Equipamentos & Freezers", "nome": "Freezer Horizontal 2 Tampas (500 Litros)", "preco": 250.00, "estoque": 2, "foto": "", "tipo_mesa": "None", "tipo_toalha": "None"},
    {"id": 28, "categoria": "Equipamentos & Freezers", "nome": "Tina Térmica para Bebidas (Madeira/Plástico)", "preco": 10.00, "estoque": 8, "foto": "", "tipo_mesa": "None", "tipo_toalha": "None"}
]

def carregar_catalogo_csv():
    if not os.path.exists(CSV_CATALOGO):
        df_init = pd.DataFrame(CATALOGO_PADRAO)
        df_init.to_csv(CSV_CATALOGO, index=False)
        return CATALOGO_PADRAO
    try:
        df = pd.read_csv(CSV_CATALOGO)
        df['foto'] = df['foto'].fillna('')
        return df.to_dict(orient="records")
    except Exception:
        return CATALOGO_PADRAO

def salvar_catalogo_csv(lista_itens):
    df = pd.DataFrame(lista_itens)
    df.to_csv(CSV_CATALOGO, index=False)

def salvar_pdf_localmente(buffer_pdf, nome_arquivo):
    try:
        if not os.path.exists(PASTA_PDF):
            os.makedirs(PASTA_PDF)
        caminho_completo = os.path.join(PASTA_PDF, nome_arquivo)
        with open(caminho_completo, "wb") as f:
            f.write(buffer_pdf.getvalue())
    except Exception as e:
        st.warning(f"Não foi possível salvar a cópia local do PDF em '{PASTA_PDF}': {e}")

# --- CONSULTA E VALIDAÇÃO DE CEP VIA VIACEP ---
def consultar_cep(cep):
    clean_cep = str(cep).replace("-", "").replace(".", "").strip()
    if len(clean_cep) != 8 or not clean_cep.isdigit():
        return None
    try:
        response = requests.get(f"https://viacep.com.br/ws/{clean_cep}/json/", timeout=5)
        if response.status_code == 200:
            dados = response.json()
            if "erro" not in dados:
                return dados
    except Exception:
        pass
    return None

def buscar_cep_por_rua(uf, cidade, logradouro):
    if len(logradouro.strip()) < 3:
        return []
    try:
        url = f"https://viacep.com.br/ws/{uf}/{urllib.parse.quote(cidade)}/{urllib.parse.quote(logradouro)}/json/"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            dados = response.json()
            if isinstance(dados, list):
                return dados
    except Exception:
        pass
    return []

# --- REPRODUTOR DE ÁUDIO E NOTIFICAÇÃO ---
def tocar_som(tipo="click"):
    if tipo == "click":
        audio_url = "https://assets.mixkit.co/active_storage/sfx/2568/2568-preview.mp3"
    elif tipo == "sucesso":
        audio_url = "https://assets.mixkit.co/active_storage/sfx/1435/1435-preview.mp3"
    elif tipo == "homologado":
        audio_url = "https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3"
    elif tipo == "novo_pedido":
        audio_url = "https://assets.mixkit.co/active_storage/sfx/1000/1000-preview.mp3"
    st.components.v1.html(f'<audio autoplay style="display:none;"><source src="{audio_url}" type="audio/mpeg"></audio>', height=0, width=0)

# --- GERADOR DE PDF FORMAL E CONTRATO DE LOCAÇÃO ---
def gerar_pdf_orcamento(cliente, evento, data_evento, endereco, itens, subtotal, frete, taxa_dificuldade, total, status, obs_dificuldade=""):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#1E3A8A'), spaceAfter=4)
    sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#475569'), spaceAfter=10)
    normal_style = styles['Normal']
    legal_style = ParagraphStyle('LegalStyle', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#334155'), spaceAfter=4)
    
    story.append(Paragraph("<b>RENASCER LOCAÇÕES E EVENTOS</b>", title_style))
    story.append(Paragraph("Rua Presidente Rodrigues Alves, Q. 30, Lt. 06, nº 01 — Jardim Presidente, Goiânia/GO<br/>Contato: (62) 3290-5515 | WhatsApp: (62) 98224-0434", sub_style))
    story.append(Spacer(1, 8))
    
    dados_cli = [
        [Paragraph(f"<b>Cliente:</b> {cliente['nome']}", normal_style), Paragraph(f"<b>Evento:</b> {evento}", normal_style)],
        [Paragraph(f"<b>Telefone:</b> {cliente['telefone']}", normal_style), Paragraph(f"<b>Data da Festa:</b> {data_evento}", normal_style)],
        [Paragraph(f"<b>Endereço de Entrega:</b> {endereco}", normal_style), Paragraph(f"<b>Status:</b> {status}", normal_style)]
    ]
    t_cli = Table(dados_cli, colWidths=[270, 270])
    t_cli.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    story.append(t_cli)
    story.append(Spacer(1, 10))
    
    tabela_data = [["Item / Descrição", "Qtd", "Unitário (R$)", "Total (R$)"]]
    for item in itens:
        tabela_data.append([item['nome'], str(item['qtd']), f"{item['preco']:.2f}", f"{item['total']:.2f}"])
        
    t_itens = Table(tabela_data, colWidths=[280, 50, 100, 110])
    t_itens.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_itens)
    story.append(Spacer(1, 10))
    
    totais_data = [
        ["Subtotal Materiais:", f"R$ {subtotal:.2f}"],
        ["Taxa de Frete / Logística:", f"R$ {frete:.2f}"]
    ]
    if taxa_dificuldade > 0:
        totais_data.append(["Taxa Adicional de Dificuldade de Acesso:", f"R$ {taxa_dificuldade:.2f}"])
    totais_data.append(["VALOR TOTAL DO ORÇAMENTO:", f"R$ {total:.2f}"])

    t_totais = Table(totais_data, colWidths=[380, 160])
    t_totais.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,-1), (-1,-1), colors.HexColor('#1E3A8A')),
        ('PADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_totais)
    story.append(Spacer(1, 12))

    if obs_dificuldade:
        story.append(Paragraph(f"<b>Obs. Acesso / Descarregamento:</b> {obs_dificuldade}", legal_style))
        story.append(Spacer(1, 6))

    story.append(Paragraph("<b>CONTRATO E TERMOS DE LOCAÇÃO</b>", ParagraphStyle('SubHeader', parent=styles['Heading3'], fontSize=10, textColor=colors.HexColor('#1E3A8A'))))
    story.append(Paragraph("1. <b>Guarda e Conservação:</b> O locatário responsabiliza-se pela guarda e perfeita conservação dos materiais contratados durante todo o período do evento.", legal_style))
    story.append(Paragraph("2. <b>Cancelamento:</b> O cancelamento do pedido deve ser solicitado com pelo menos 1 (uma) semana de antecedência da data do evento. Caso ocorra após este prazo, incidirá multa de 30% sobre o valor total do contrato.", legal_style))
    story.append(Paragraph("3. <b>Danos e Perdas:</b> O locatário compromete-se a ressarcir integralmente o locador em caso de danos, avarias ou perdas das peças, a preço de custo praticado no mercado.", legal_style))
    story.append(Paragraph("4. <b>Entrega e Logística:</b> O locador prontifica-se a entregar os materiais em perfeitas condições de uso e sem avarias, dentro do prazo combinado e local preestabelecido.", legal_style))
    story.append(Paragraph("5. <b>Recolhimento e Descumprimento:</b> Os bens serão recolhidos pelo locador dentro do prazo combinado. Em caso de descumprimento injustificado das condições contratuais, incidirá multa de 30%.", legal_style))
    
    doc.build(story)
    buffer.seek(0)
    
    nome_pdf = f"Orcamento_Renascer_{cliente['nome'].replace(' ', '_')}_{evento.replace(' ', '_')}.pdf"
    salvar_pdf_localmente(buffer, nome_pdf)
    buffer.seek(0)
    
    return buffer

# --- CÁLCULO DE FRETE E DISTÂNCIA POR CEP ---
def calcular_distancia_cep(cep_destino):
    try:
        clean_cep = str(cep_destino).replace("-", "").replace(".", "").strip()
        if len(clean_cep) != 8 or not clean_cep.isdigit():
            return None
        base_num = int(clean_cep[:5])
        renascer_num = 74353
        
        diff_abs = abs(base_num - renascer_num)
        km_estimado = round(3.5 + (diff_abs / 18.0), 1)
        
        valor_base = km_estimado * 4.0
        valor_frete = valor_base * 1.10
        
        return {
            "km": km_estimado,
            "valor_frete": round(valor_frete, 2)
        }
    except Exception:
        return None

# --- ALGORITMO DE BUSCA INTELIGENTE ---
SINONIMOS = {
    "pano": "toalha", "panos": "toalha", "friser": "freezer", "frizzer": "freezer",
    "geladeira": "freezer", "copo": "taça", "copos": "taça", "prato": "louça", "talher": "garfo"
}

def calcular_similaridade(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def buscar_materiais_inteligente(termo, catalogo):
    if not termo:
        return catalogo
    termo_limpo = termo.lower().strip()
    termo_processado = SINONIMOS.get(termo_limpo, termo_limpo)
    
    resultados = []
    for item in catalogo:
        nome = str(item['nome']).lower()
        categoria = str(item['categoria']).lower()
        
        if termo_processado in nome or termo_processado in categoria:
            resultados.append((item, 1.0))
            continue
            
        sim_nome = max([calcular_similaridade(termo_processado, palavra) for palavra in nome.split()]) if nome.split() else 0
        sim_cat = max([calcular_similaridade(termo_processado, palavra) for palavra in categoria.split()]) if categoria.split() else 0
        maior_sim = max(sim_nome, sim_cat)
        
        if maior_sim >= 0.55:
            resultados.append((item, maior_sim))
            
    resultados.sort(key=lambda x: x[1], reverse=True)
    return [r[0] for r in resultados]

def obter_preco_toalha_estoque(tipo_mesa, catalogo):
    """Busca o preço padrão de toalha no estoque baseado no tipo de mesa/aparador"""
    tipo = str(tipo_mesa).lower()
    if tipo == "redonda":
        toalha_item = next((i for i in catalogo if "redonda" in str(i['nome']).lower() and i['categoria'] == "Toalhas & Enxoval"), None)
        return toalha_item['preco'] if toalha_item else 12.00
    else:
        toalha_item = next((i for i in catalogo if "quadrada" in str(i['nome']).lower() and i['categoria'] == "Toalhas & Enxoval"), None)
        return toalha_item['preco'] if toalha_item else 6.00

# --- BASE DE DADOS DA SESSÃO ---
if 'catalogo' not in st.session_state:
    st.session_state.catalogo = carregar_catalogo_csv()

if 'cliente_perfil' not in st.session_state:
    st.session_state.cliente_perfil = None

if 'enderecos_cadastrados' not in st.session_state:
    st.session_state.enderecos_cadastrados = []

if 'carrinho_atual' not in st.session_state:
    st.session_state.carrinho_atual = {}

if 'toalhas_vinculadas' not in st.session_state:
    st.session_state.toalhas_vinculadas = {}

if 'guardanapos_vinculados' not in st.session_state:
    st.session_state.guardanapos_vinculados = {}

if 'pedidos_standby' not in st.session_state:
    st.session_state.pedidos_standby = []

if 'pedido_edicao_id' not in st.session_state:
    st.session_state.pedido_edicao_id = None

if 'termo_busca' not in st.session_state:
    st.session_state.termo_busca = ""

if 'eh_admin' not in st.session_state:
    st.session_state.eh_admin = False

# --- CABEÇALHO / HERO BANNER DA EMPRESA (CENTRALIZADO & ESTENDIDO) ---
st.markdown("""
<div class="hero-container">
    <div class="hero-title">RENASCER LOCAÇÕES & EVENTOS</div>
    <div class="hero-slogan">EXCELÊNCIA E QUALIDADE EM CADA DETALHE</div>
    <div class="hero-description">
        Há anos oferecendo a melhor estrutura em mesas, cadeiras, toalhas, louças e equipamentos para festas e eventos corporativos em Goiânia e Região. Agilidade na entrega, higiene impecável e atendimento de primeira para tornar sua celebração inesquecível.
    </div>
</div>
""", unsafe_allow_html=True)

# --- MODAL DO CARDÁPIO RESUMIDO DE MATERIAIS ---
@st.dialog("📋 Lista Rápida de Materiais", width="large")
def abrir_cardapio_resumido():
    st.write("Clique em qualquer item para localizá-lo rapidamente no catálogo:")
    st.markdown("---")
    
    catalogo_ordenado = sorted(st.session_state.catalogo, key=lambda x: str(x['nome']))
    
    with st.container(height=420):
        for item in catalogo_ordenado:
            col_txt, col_btn = st.columns([3, 1])
            with col_txt:
                st.markdown(f"**{item['nome']}**  \n<small style='color:gray;'>{item['categoria']} — R$ {item['preco']:.2f}</small>", unsafe_allow_html=True)
            with col_btn:
                if st.button("Ver Item ➔", key=f"btn_sel_cardapio_{item['id']}"):
                    st.session_state.termo_busca = item['nome']
                    tocar_som("click")
                    st.rerun()
            st.divider()

# --- CONTROLE DE ROTAS E NAVEGAÇÃO ---
if st.session_state.eh_admin:
    st.sidebar.title("📌 Navegação Admin")
    modo = st.sidebar.radio("Ir para:", ["Área do Cliente", "Meu Perfil", "Painel Administrativo"])
else:
    modo = "Área do Cliente"

# ==========================================
# 📱 TELA DE PERFIL DO CLIENTE
# ==========================================
if modo == "Meu Perfil":
    st.title("👤 Seus Dados & Endereços")
    
    if not st.session_state.cliente_perfil:
        st.info("Insira suas informações na página inicial para sincronizar seu perfil.")
    else:
        perf = st.session_state.cliente_perfil
        with st.form("form_edita_perfil"):
            st.subheader("Dados Cadastrais")
            e_nome = st.text_input("Nome Completo", value=perf['nome'])
            e_tel = st.text_input("WhatsApp / Telefone", value=perf['telefone'])
            e_email = st.text_input("E-mail", value=perf['email'])
            
            if st.form_submit_button("Atualizar Meus Dados"):
                st.session_state.cliente_perfil['nome'] = e_nome
                st.session_state.cliente_perfil['telefone'] = e_tel
                st.session_state.cliente_perfil['email'] = e_email
                tocar_som("sucesso")
                st.success("Seus dados foram atualizados com sucesso!")
                
        st.divider()
        st.subheader("Locais de Eventos Cadastrados")
        for idx, end in enumerate(st.session_state.enderecos_cadastrados):
            st.info(f"📍 **{end['rotulo']}**: {end['logradouro']} — CEP: {end['cep']}")

# ==========================================
# 📱 ÁREA DO CLIENTE & CATÁLOGO
# ==========================================
elif modo == "Área do Cliente":
    
    # TELA DE CADASTRO INICIAL
    if not st.session_state.cliente_perfil:
        st.markdown("""
        <div style='background-color:#F8FAFC; border: 1px solid #E2E8F0; padding:25px; border-radius:12px; margin-bottom:20px;'>
            <h3 style='color:#1E3A8A; margin-top:0;'>👋 Seja bem-vindo!</h3>
            <p style='color:#64748B;'>Faça seu cadastro rápido para calcular o frete exato e acessar todo nosso catálogo de produtos:</p>
        </div>
        """, unsafe_allow_html=True)
        
        c_nome = st.text_input("Seu Nome Completo*", key="cad_nome")
        c_tel = st.text_input("WhatsApp para Contato*", key="cad_tel")
        c_email = st.text_input("E-mail (Opcional)", key="cad_email")
        
        st.markdown("---")
        st.write("### 🏠 Endereço Residencial Principal")
        
        c_cep = st.text_input("Digite o CEP da sua Residência*", key="cad_cep")
        
        dados_cep_val = None
        if c_cep:
            dados_cep_val = consultar_cep(c_cep)
            if dados_cep_val:
                st.success(f"📍 **Endereço Localizado:** {dados_cep_val.get('logradouro')}, {dados_cep_val.get('bairro')} - {dados_cep_val.get('localidade')}/{dados_cep_val.get('uf')}")
            else:
                st.error("⚠️ CEP não encontrado ou inválido. Digite um CEP válido com 8 dígitos.")
                with st.expander("🔍 Não sabe o CEP? Busque pelo nome da rua"):
                    col_uf, col_cid = st.columns([1, 2])
                    uf_busca = col_uf.selectbox("UF", ["GO", "DF", "SP", "RJ", "MG"], key="cad_uf_b")
                    cid_busca = col_cid.text_input("Cidade", value="Goiânia", key="cad_cid_b")
                    rua_busca = st.text_input("Nome da Rua / Logradouro (mín. 3 letras)", key="cad_rua_b")
                    if st.button("Buscar CEP", key="btn_b_cep_cad"):
                        res_ceps = buscar_cep_por_rua(uf_busca, cid_busca, rua_busca)
                        if res_ceps:
                            for c_item in res_ceps[:5]:
                                st.write(f"👉 **CEP:** `{c_item.get('cep')}` — {c_item.get('logradouro')}, {c_item.get('bairro')}")
                        else:
                            st.warning("Nenhum CEP localizado para este nome de rua.")
        
        c_num = st.text_input("Número e Complemento (ex: Qd. 10 Lt. 05 / Ap. 302)*", key="cad_num")

        st.markdown("---")
        st.write("### 🏢 Tipo do Imóvel Residencial e Acesso")
        tipo_imovel_cad = st.selectbox(
            "Selecione o tipo do imóvel residencial:",
            ["Residência (Casa)", "Edifício (Prédio / Apartamento)", "Condomínio Fechado / Chácara"],
            key="cad_tipo_imovel"
        )

        cad_tem_dificuldade = False
        cad_grau_dificuldade = 1
        cad_obs_dificuldade = ""

        if tipo_imovel_cad in ["Edifício (Prédio / Apartamento)", "Condomínio Fechado / Chácara"]:
            st.write("**Atenção:** Locais com escadas, elevadores demorados ou longas distâncias a pé exigem equipe adicional.")
            resp_dif_cad = st.radio(
                "Existe dificuldade ou longa distância a pé para o descarregamento dos materiais nesta residência?",
                ["Não", "Sim"],
                key="cad_radio_dificuldade"
            )
            
            if resp_dif_cad == "Sim":
                cad_tem_dificuldade = True
                cad_grau_dificuldade = st.slider("De 1 a 10, qual o grau de dificuldade do descarregamento?", min_value=1, max_value=10, value=3, key="cad_sld_grau_dif")
                cad_obs_dificuldade = st.text_area("Descreva o motivo da dificuldade (ex: 3º andar de escada, caminhada longa do estacionamento):", key="cad_txt_obs_dificuldade")

        if st.button("Concluir Cadastro e Ir para o Catálogo ➔", use_container_width=True):
            if not c_nome or not c_tel or not c_cep or not c_num:
                st.error("Por favor, preencha todos os campos obrigatórios (*).")
            elif not dados_cep_val:
                st.error("Digite um CEP válido para concluir o cadastro residencial.")
            else:
                end_completo = f"{dados_cep_val.get('logradouro')}, {c_num} - {dados_cep_val.get('bairro')}, {dados_cep_val.get('localidade')}/{dados_cep_val.get('uf')}"
                st.session_state.cliente_perfil = {
                    "nome": c_nome, "telefone": c_tel, "email": c_email
                }
                st.session_state.enderecos_cadastrados.append({
                    "rotulo": "Minha Residência",
                    "logradouro": end_completo,
                    "cep": str(c_cep).replace("-", "").replace(".", "").strip(),
                    "tipo_imovel": tipo_imovel_cad,
                    "tem_dificuldade": cad_tem_dificuldade,
                    "grau_dificuldade": cad_grau_dificuldade,
                    "obs_dificuldade": cad_obs_dificuldade
                })
                tocar_som("sucesso")
                st.rerun()

    # TELA PRINCIPAL DO CLIENTE
    else:
        cli = st.session_state.cliente_perfil
        
        q_total_itens = sum(st.session_state.carrinho_atual.values())
        tot_carrinho_temp = 0.0
        for item_id, q in st.session_state.carrinho_atual.items():
            prod = next((i for i in st.session_state.catalogo if i['id'] == item_id), None)
            if prod:
                tot_carrinho_temp += prod['preco'] * q
                if item_id in st.session_state.toalhas_vinculadas:
                    t_vinc = st.session_state.toalhas_vinculadas[item_id]
                    tot_carrinho_temp += t_vinc['preco'] * t_vinc['qtd']

        # Adiciona total de guardanapos personalizados na soma
        for g_id, g_vinc in st.session_state.guardanapos_vinculados.items():
            tot_carrinho_temp += g_vinc['preco'] * g_vinc['qtd']

        st.markdown(f"""
        <div style="background-color: #1E3A8A; color: white; padding: 14px 24px; border-radius: 12px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0px 4px 12px rgba(30, 58, 138, 0.15);">
            <div>
                <span style="font-size: 16px; font-weight: bold;">👋 Cliente: {cli['nome']}</span>
            </div>
            <div>
                <span style="font-size: 15px; background-color: #FFFFFF; color: #1E3A8A; padding: 8px 18px; border-radius: 20px; font-weight: bold;">
                    🛒 {q_total_itens} item(ns) | Total: R$ {tot_carrinho_temp:.2f}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ALERTAS SONOROS AUTOMÁTICOS
        pedidos_homologados_recentes = [p for p in st.session_state.pedidos_standby if p['cliente']['telefone'] == cli['telefone'] and p.get('status') == 'Homologado (Disponibilidade Confirmada)' and p.get('alerta_cliente_tocado') != True]
        if pedidos_homologados_recentes:
            for p_h in pedidos_homologados_recentes:
                st.balloons()
                st.success(f"🎉 Boas notícias! Seu pedido para **'{p_h['evento']}'** foi HOMOLOGADO! O pagamento via Pix já está liberado.")
                tocar_som("homologado")
                p_h['alerta_cliente_tocado'] = True

        if st.session_state.pedido_edicao_id:
            st.warning(f"📝 Você está editando o Pedido ID #{st.session_state.pedido_edicao_id}. As alterações serão salvas ao finalizar.")

        tab_catalogo, tab_carrinho, tab_standby = st.tabs([
            "🛒 CATÁLOGO DE MATERIAIS", 
            "📋 FINALIZAR ORÇAMENTO & FRETE", 
            "📅 MEUS EVENTOS"
        ])
        
        # TAB 1: CATÁLOGO DE MATERIAIS
        with tab_catalogo:
            st.subheader("Escolha os itens para o seu evento")
            
            col_busca, col_cardapio = st.columns([3, 1])
            with col_busca:
                input_busca = st.text_input("🔍 O que você procura? (ex: mesa, aparador, guardanapo, freezer, prato, taça...)", value=st.session_state.termo_busca, key="input_busca_campo")
                st.session_state.termo_busca = input_busca
            with col_cardapio:
                st.write("&#160;")
                if st.button("📋 Ver Lista Completa", use_container_width=True):
                    abrir_cardapio_resumido()

            itens_exibidos = buscar_materiais_inteligente(st.session_state.termo_busca, st.session_state.catalogo)
            
            if not itens_exibidos:
                st.warning("Não encontramos este item na busca. Clique em '📋 Ver Lista Completa' para navegar por todos os produtos.")
            else:
                for item in itens_exibidos:
                    with st.container():
                        col_det, col_qtd = st.columns([3, 1])
                        with col_det:
                            st.markdown(f"#### {item['nome']}")
                            st.caption(f"Categoria: {item['categoria']}")
                            st.write(f"Valor unitário: **R$ {item['preco']:.2f}**")
                            
                            if item.get("foto") and str(item['foto']).strip() != "":
                                st.image(item['foto'], width=150)
                            
                            nome_item_lower = str(item['nome']).lower()
                            tipo_mesa_val = str(item.get("tipo_mesa", "None")).lower()
                            
                            # --- CAMPO DINÂMICO PARA INCLUSÃO DE TOALHA EM MESAS E APARADORES ---
                            is_mesa_ou_aparador = (
                                "mesa" in nome_item_lower or 
                                "aparador" in nome_item_lower or 
                                tipo_mesa_val in ["quadrada", "redonda", "aparador", "outro"]
                            )
                            
                            if is_mesa_ou_aparador:
                                st.markdown("---")
                                quer_toalha = st.checkbox(
                                    f"Deseja incluir toalha para este móvel?", 
                                    value=(item['id'] in st.session_state.toalhas_vinculadas),
                                    key=f"chk_toalha_{item['id']}"
                                )
                                
                                if quer_toalha:
                                    col_cor, col_qtd_toalha = st.columns([2, 1])
                                    with col_cor:
                                        cor_manual = st.text_input(
                                            "Digite a cor pretendida para a toalha:",
                                            value=st.session_state.toalhas_vinculadas.get(item['id'], {}).get('cor', 'Branca'),
                                            placeholder="Ex: Vermelho, Branca, Azul, Rústica...",
                                            key=f"cor_manual_{item['id']}"
                                        )
                                    with col_qtd_toalha:
                                        qtd_atual_m = st.session_state.carrinho_atual.get(item['id'], 1)
                                        qtd_toalha = st.number_input(
                                            "Qtd de toalhas:",
                                            min_value=1,
                                            value=int(st.session_state.toalhas_vinculadas.get(item['id'], {}).get('qtd', qtd_atual_m)),
                                            key=f"qtd_toalha_{item['id']}"
                                        )
                                    
                                    preco_unit_toalha = obter_preco_toalha_estoque(tipo_mesa_val, st.session_state.catalogo)
                                    st.caption(f"💡 Valor unitário da toalha (conforme estoque): **R$ {preco_unit_toalha:.2f}**")
                                    
                                    st.session_state.toalhas_vinculadas[item['id']] = {
                                        "tipo": tipo_mesa_val if tipo_mesa_val != "None" else "Móvel",
                                        "cor": cor_manual if cor_manual.strip() else "Não especificada",
                                        "qtd": qtd_toalha,
                                        "preco": preco_unit_toalha
                                    }
                                else:
                                    st.session_state.toalhas_vinculadas.pop(item['id'], None)

                            # --- CAMPO DINÂMICO PARA INCLUSÃO DE COR NOS GUARDANAPOS ---
                            is_guardanapo = "guardanapo" in nome_item_lower

                            if is_guardanapo:
                                st.markdown("---")
                                quer_guardanapo_cor = st.checkbox(
                                    f"Deseja especificar a cor e quantidade para este guardanapo?",
                                    value=(item['id'] in st.session_state.guardanapos_vinculados),
                                    key=f"chk_guardanapo_{item['id']}"
                                )
                                
                                if quer_guardanapo_cor:
                                    col_g_cor, col_g_qtd = st.columns([2, 1])
                                    with col_g_cor:
                                        cor_guardanapo = st.text_input(
                                            "Digite a cor pretendida para os guardanapos:",
                                            value=st.session_state.guardanapos_vinculados.get(item['id'], {}).get('cor', 'Branca'),
                                            placeholder="Ex: Vermelho, Marsala, Dourado, Branco...",
                                            key=f"cor_guardanapo_{item['id']}"
                                        )
                                    with col_g_qtd:
                                        qtd_g_escolhida = st.number_input(
                                            "Qtd de guardanapos:",
                                            min_value=1,
                                            max_value=int(item['estoque']),
                                            value=int(st.session_state.guardanapos_vinculados.get(item['id'], {}).get('qtd', 10)),
                                            key=f"qtd_guardanapo_{item['id']}"
                                        )
                                    
                                    st.caption(f"💡 Valor unitário do guardanapo (conforme estoque): **R$ {item['preco']:.2f}**")
                                    
                                    st.session_state.guardanapos_vinculados[item['id']] = {
                                        "cor": cor_guardanapo if cor_guardanapo.strip() else "Não especificada",
                                        "qtd": qtd_g_escolhida,
                                        "preco": item['preco']
                                    }
                                else:
                                    st.session_state.guardanapos_vinculados.pop(item['id'], None)

                        with col_qtd:
                            # Para guardanapos com cor customizada, gerenciamos pela caixa de inclusão dedicada
                            if not "guardanapo" in str(item['nome']).lower():
                                qtd_atual = st.session_state.carrinho_atual.get(item['id'], 0)
                                nova_qtd = st.number_input(
                                    "Quantidade:", min_value=0, max_value=int(item['estoque']), 
                                    value=int(qtd_atual), key=f"item_qtd_{item['id']}"
                                )
                                if nova_qtd != qtd_atual:
                                    if nova_qtd > 0:
                                        st.session_state.carrinho_atual[item['id']] = nova_qtd
                                    else:
                                        st.session_state.carrinho_atual.pop(item['id'], None)
                                    tocar_som("click")
                            else:
                                st.write("✏️ *Configure a cor e quantidade nas opções ao lado.*")

                    st.divider()

        # TAB 2: FINALIZAR ORÇAMENTO
        with tab_carrinho:
            st.subheader("📋 Resumo do Seu Orçamento e Local de Entrega")
            
            if not st.session_state.carrinho_atual and not st.session_state.guardanapos_vinculados:
                st.info("Seu carrinho está vazio. Acesse a aba 'Catálogo de Materiais' para escolher os itens do seu evento.")
            else:
                st.write("### 🚚 Local do Evento & Entrega")
                
                tipo_local = st.radio(
                    "Onde será realizada a entrega dos materiais?",
                    ["Sera na Minha Casa (Endereço do Cadastro)", "Em Outro Endereço / Salão de Festas / Chácara"],
                    key="radio_tipo_local"
                )
                
                end_rua_festa = ""
                end_cep_festa = ""
                cep_validado_ok = False
                tem_dificuldade = False
                grau_dificuldade = 1
                obs_dificuldade = ""

                if tipo_local == "Sera na Minha Casa (Endereço do Cadastro)":
                    if st.session_state.enderecos_cadastrados:
                        end_cad = st.session_state.enderecos_cadastrados[0]
                        end_rua_festa = end_cad['logradouro']
                        end_cep_festa = end_cad['cep']
                        cep_validado_ok = True
                        tem_dificuldade = end_cad.get('tem_dificuldade', False)
                        grau_dificuldade = end_cad.get('grau_dificuldade', 1)
                        obs_dificuldade = end_cad.get('obs_dificuldade', "")
                        st.info(f"📍 **Endereço Selecionado:** {end_rua_festa} (CEP: {end_cep_festa})")
                else:
                    st.write("**Informe o CEP do novo local de entrega:**")
                    end_cep_festa = st.text_input("CEP do Local do Evento*", key="input_cep_novo_local")
                    
                    if end_cep_festa:
                        dados_c_novo = consultar_cep(end_cep_festa)
                        if dados_c_novo:
                            cep_validado_ok = True
                            rua_previa = f"{dados_c_novo.get('logradouro')}, {dados_c_novo.get('bairro')} - {dados_c_novo.get('localidade')}/{dados_c_novo.get('uf')}"
                            st.success(f"📍 **Prévia do Endereço:** {rua_previa}")
                            num_compl_novo = st.text_input("Número / Complemento / Nome do Salão ou Chácara*", key="input_num_novo_local")
                            end_rua_festa = f"{rua_previa} ({num_compl_novo})" if num_compl_novo else rua_previa
                        else:
                            st.error("⚠️ CEP não encontrado. Digite um CEP válido de 8 dígitos para o cálculo exato do frete.")
                            with st.expander("🔍 Não sabe o CEP do local? Encontre pelo nome da rua"):
                                col_uf2, col_cid2 = st.columns([1, 2])
                                uf_b2 = col_uf2.selectbox("UF", ["GO", "DF", "SP", "RJ", "MG"], key="uf_b2")
                                cid_b2 = col_cid2.text_input("Cidade", value="Goiânia", key="cid_b2")
                                rua_b2 = st.text_input("Nome da Rua / Logradouro (mín. 3 letras)", key="rua_b2")
                                if st.button("Buscar CEP do Local", key="btn_b_cep_loc"):
                                    res2 = buscar_cep_por_rua(uf_b2, cid_b2, rua_b2)
                                    if res2:
                                        for c2 in res2[:5]:
                                            st.write(f"👉 **CEP:** `{c2.get('cep')}` — {c2.get('logradouro')}, {c2.get('bairro')}")
                                    else:
                                        st.warning("Nenhum CEP encontrado.")
                    
                    st.markdown("---")
                    st.write("### 🏢 Tipo de Imóvel e Acesso para o Novo Local")
                    tipo_imovel_op = st.selectbox(
                        "Selecione o tipo do local de entrega:",
                        ["Residência (Casa)", "Edifício (Prédio / Apartamento)", "Condomínio Fechado / Chácara"],
                        key="sel_tipo_imovel_op"
                    )
                    
                    if tipo_imovel_op in ["Edifício (Prédio / Apartamento)", "Condomínio Fechado / Chácara"]:
                        st.write("**Atenção:** Locais com escadas, elevadores demorados ou longas distâncias a pé exigem equipe adicional.")
                        resp_dif_novo = st.radio(
                            "Existe dificuldade ou longa distância a pé para o descarregamento dos materiais?",
                            ["Não", "Sim"],
                            key="radio_dificuldade_novo"
                        )
                        if resp_dif_novo == "Sim":
                            tem_dificuldade = True
                            grau_dificuldade = st.slider("De 1 a 10, qual o grau de dificuldade do descarregamento?", min_value=1, max_value=10, value=3, key="sld_grau_dif_novo")
                            obs_dificuldade = st.text_area("Descreva o motivo da dificuldade (ex: 3º andar de escada, caminhada longa do estacionamento):", key="txt_obs_dificuldade_novo")

                col_dt1, col_dt2 = st.columns(2)
                with col_dt1:
                    data_festa = st.date_input("Data da Festa / Evento:", key="dt_evento_festa")

                dados_frete = calcular_distancia_cep(end_cep_festa) if cep_validado_ok else None
                val_frete = dados_frete['valor_frete'] if dados_frete else 0.0

                st.markdown("---")
                
                st.markdown("""
                    <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; padding: 22px; border-radius: 12px; box-shadow: 0px 4px 12px rgba(0,0,0,0.05);">
                        <h3 style="color:#1E3A8A; margin-top:0px; border-bottom: 2px solid #1E3A8A; padding-bottom: 6px;">
                            📄 RESUMO DO PEDIDO
                        </h3>
                """, unsafe_allow_html=True)
                
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.write(f"**Cliente:** {cli['nome']}")
                    st.write(f"**Contato:** {cli['telefone']}")
                with col_d2:
                    st.write(f"**Data do Evento:** {data_festa.strftime('%d/%m/%Y') if hasattr(data_festa, 'strftime') else data_festa}")
                    st.write(f"**Endereço de Entrega:** {end_rua_festa if end_rua_festa else 'A preencher'}")
                
                st.markdown("##### Itens Selecionados:")
                
                subtotal_materiais = 0.0
                lista_pdf_itens = []
                
                tabela_itens_html = "<table style='width:100%; border-collapse: collapse; margin-top:10px; font-size:14px;'>"
                tabela_itens_html += "<tr style='background-color:#F1F5F9; border-bottom: 2px solid #CBD5E1;'><th style='text-align:left; padding:8px;'>Item</th><th style='text-align:center;'>Qtd</th><th style='text-align:right;'>Unitário</th><th style='text-align:right;'>Total</th></tr>"
                
                # Exibição de itens normais do carrinho
                for item_id, q in st.session_state.carrinho_atual.items():
                    prod = next((i for i in st.session_state.catalogo if i['id'] == item_id), None)
                    if prod:
                        tot_prod = prod['preco'] * q
                        subtotal_materiais += tot_prod
                        lista_pdf_itens.append({"nome": prod['nome'], "qtd": q, "preco": prod['preco'], "total": tot_prod})
                        
                        tabela_itens_html += f"<tr style='border-bottom: 1px solid #E2E8F0;'><td style='padding:8px;'>{prod['nome']}</td><td style='text-align:center;'>{q}</td><td style='text-align:right;'>R$ {prod['preco']:.2f}</td><td style='text-align:right;'>R$ {tot_prod:.2f}</td></tr>"
                        
                        if item_id in st.session_state.toalhas_vinculadas:
                            t_info = st.session_state.toalhas_vinculadas[item_id]
                            qtd_t = t_info['qtd']
                            tot_toalha = t_info['preco'] * qtd_t
                            subtotal_materiais += tot_toalha
                            nome_t = f"Toalha para {prod['nome']} (Cor: {t_info['cor']})"
                            lista_pdf_itens.append({"nome": nome_t, "qtd": qtd_t, "preco": t_info['preco'], "total": tot_toalha})
                            tabela_itens_html += f"<tr style='border-bottom: 1px solid #E2E8F0; color:#475569;'><td style='padding:8px; padding-left:25px;'>└ ➕ {nome_t}</td><td style='text-align:center;'>{qtd_t}</td><td style='text-align:right;'>R$ {t_info['preco']:.2f}</td><td style='text-align:right;'>R$ {tot_toalha:.2f}</td></tr>"

                # Exibição de guardanapos com cor customizada
                for g_id, g_info in st.session_state.guardanapos_vinculados.items():
                    g_prod = next((i for i in st.session_state.catalogo if i['id'] == g_id), None)
                    if g_prod:
                        qtd_g = g_info['qtd']
                        tot_g = g_info['preco'] * qtd_g
                        subtotal_materiais += tot_g
                        nome_g_desc = f"{g_prod['nome']} (Cor: {g_info['cor']})"
                        lista_pdf_itens.append({"nome": nome_g_desc, "qtd": qtd_g, "preco": g_info['preco'], "total": tot_g})
                        tabela_itens_html += f"<tr style='border-bottom: 1px solid #E2E8F0;'><td style='padding:8px;'>{nome_g_desc}</td><td style='text-align:center;'>{qtd_g}</td><td style='text-align:right;'>R$ {g_info['preco']:.2f}</td><td style='text-align:right;'>R$ {tot_g:.2f}</td></tr>"

                tabela_itens_html += "</table>"
                st.markdown(tabela_itens_html, unsafe_allow_html=True)
                
                # CÁLCULO DA TAXA ADICIONAL DE DIFICULDADE
                taxa_dificuldade = 0.0
                if tem_dificuldade:
                    taxa_dificuldade = 30.00 + (subtotal_materiais * (grau_dificuldade / 100.0))

                valor_total_bruto = subtotal_materiais + val_frete + taxa_dificuldade
                
                st.markdown("---")
                col_t1, col_t2 = st.columns([2, 2])
                with col_t2:
                    st.write(f"Subtotal dos Materiais: **R$ {subtotal_materiais:.2f}**")
                    st.write(f"Taxa de Entrega / Frete Base: **R$ {val_frete:.2f}**")
                    if tem_dificuldade:
                        st.write(f"Taxa Adicional Acesso/Dificuldade (Grau {grau_dificuldade}): **R$ {taxa_dificuldade:.2f}**")
                    st.markdown(f"<h3 style='color:#1E3A8A; margin:0px;'>Total Geral: R$ {valor_total_bruto:.2f}</h3>", unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)
                
                # --- TERMOS E CONTRATO DE LOCAÇÃO ---
                st.markdown("---")
                st.markdown("#### 📜 Termos de Locação e Devolução")
                st.caption("Por favor, leia e aceite as condições para habilitar a finalização:")
                
                with st.container(height=170):
                    st.markdown("""
                    * **1. Guarda e Conservação:** O locatário responsabiliza-se pela guarda e conservação dos materiais contratados durante o evento.
                    * **2. Cancelamento:** O pedido pode ser cancelado sem custo até 1 semana antes do evento. Após esse prazo, haverá multa de 30% do valor total do contrato.
                    * **3. Danos e Perdas:** O locatário compromete-se a ressarcir o locador em caso de danos, avarias ou perdas das peças.
                    * **4. Compromisso do Locador:** O locador prontifica-se a entregar os materiais em condições de uso e sem avarias, no prazo combinado e local preestabelecido.
                    * **5. Recolhimento:** O locador recolherá os itens dentro do prazo combinado. Em caso de descumprimento contratual, incidirá multa de 30%.
                    """)

                concordou_termos = st.checkbox("✅ Li e concordo com os Termos e Cláusulas de Locação", key="chk_termos_aceite")

                pdf_bytes = gerar_pdf_orcamento(
                    cli, "Orçamento Formal", str(data_festa), end_rua_festa,
                    lista_pdf_itens, subtotal_materiais, val_frete, taxa_dificuldade, valor_total_bruto, "Aguardando Homologação", obs_dificuldade
                )
                st.download_button(
                    label="📄 Baixar Cópia Formal em PDF",
                    data=pdf_bytes,
                    file_name=f"Orcamento_Renascer_{cli['nome'].replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

                st.markdown("---")
                st.markdown("#### Finalização do Pedido")
                
                nome_identificador = st.text_input(
                    "Dê um nome para o seu evento (ex: Aniversário da Maria, Churrasco de Domingo):",
                    key="input_nome_evento"
                )

                btn_desabilitado = not concordou_termos or not cep_validado_ok

                if st.button("💾 Gravar Pedido e Enviar para Homologação ➔", use_container_width=True, disabled=btn_desabilitado):
                    if not nome_identificador:
                        st.error("Por favor, digite um nome para identificar o seu evento antes de finalizar.")
                    elif not cep_validado_ok:
                        st.error("Insira um CEP válido para calcular o frete e liberar a gravação.")
                    else:
                        status_final = "Aguardando Homologação"
                        
                        if st.session_state.pedido_edicao_id:
                            for p in st.session_state.pedidos_standby:
                                if p['id'] == st.session_state.pedido_edicao_id:
                                    p['evento'] = nome_identificador
                                    p['data'] = str(data_festa)
                                    p['endereco'] = end_rua_festa
                                    p['frete'] = val_frete
                                    p['taxa_dificuldade'] = taxa_dificuldade
                                    p['total'] = valor_total_bruto
                                    p['subtotal'] = subtotal_materiais
                                    p['status'] = status_final
                                    p['obs_dificuldade'] = obs_dificuldade
                                    p['itens'] = dict(st.session_state.carrinho_atual)
                                    p['toalhas'] = dict(st.session_state.toalhas_vinculadas)
                                    p['guardanapos'] = dict(st.session_state.guardanapos_vinculados)
                                    p['itens_detalhe'] = lista_pdf_itens
                                    p['alerta_admin_tocado'] = False
                            st.session_state.pedido_edicao_id = None
                        else:
                            novo_id = len(st.session_state.pedidos_standby) + 1
                            novo_stb = {
                                "id": novo_id,
                                "cliente": cli,
                                "evento": nome_identificador,
                                "data": str(data_festa),
                                "endereco": end_rua_festa,
                                "frete": val_frete,
                                "taxa_dificuldade": taxa_dificuldade,
                                "subtotal": subtotal_materiais,
                                "total": valor_total_bruto,
                                "status": status_final,
                                "obs_dificuldade": obs_dificuldade,
                                "itens": dict(st.session_state.carrinho_atual),
                                "toalhas": dict(st.session_state.toalhas_vinculadas),
                                "guardanapos": dict(st.session_state.guardanapos_vinculados),
                                "itens_detalhe": lista_pdf_itens,
                                "alerta_cliente_tocado": False,
                                "alerta_admin_tocado": False
                            }
                            st.session_state.pedidos_standby.append(novo_stb)
                        
                        st.session_state.carrinho_atual = {}
                        st.session_state.toalhas_vinculadas = {}
                        st.session_state.guardanapos_vinculados = {}
                        tocar_som("sucesso")
                        st.success("🎉 Seu pedido foi enviado com sucesso e está aguardando homologação! Consulte a aba 'MEUS EVENTOS'.")
                        st.rerun()

        # TAB 3: MEUS EVENTOS / STANDBY
        with tab_standby:
            st.subheader("📅 Seus Eventos Salvos e Solicitados")
            
            meus_pedidos = [p for p in st.session_state.pedidos_standby if p['cliente']['telefone'] == cli['telefone']]
            
            if not meus_pedidos:
                st.info("Você ainda não possui eventos gravados em seu histórico.")
            else:
                for ped in meus_pedidos:
                    eh_homologado = ped['status'] == 'Homologado (Disponibilidade Confirmada)'
                    cor_status = "green" if eh_homologado else "orange"
                    
                    with st.expander(f"🎉 {ped['evento']} — Data: {ped['data']} (Status: :{cor_status}[{ped['status']}])"):
                        st.write(f"**Endereço:** {ped['endereco']}")
                        st.write(f"**Valor Total:** R$ {ped['total']:.2f} (Materiais: R$ {ped['subtotal']:.2f} | Frete: R$ {ped['frete']:.2f} | Dificuldade: R$ {ped.get('taxa_dificuldade', 0.0):.2f})")
                        if ped.get('obs_dificuldade'):
                            st.write(f"**Obs. Acesso:** {ped['obs_dificuldade']}")
                        
                        st.write("**Itens do Pedido:**")
                        for item_det in ped['itens_detalhe']:
                            st.write(f"- {item_det['qtd']}x {item_det['nome']} (R$ {item_det['total']:.2f})")
                        
                        st.divider()

                        # --- ÁREA DE PAGAMENTO PIX ---
                        if eh_homologado:
                            st.markdown("### 💳 Pagamento Liberado via PIX")
                            st.success("Estoque reservado com sucesso! Realize o pagamento para confirmar seu pedido.")
                            
                            col_qr, col_pix = st.columns([1, 2])
                            with col_qr:
                                st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=00020126580014BR.GOV.BCB.PIX0136629822404345204000053039865405{ped['total']:.2f}5802BR5923RENASCER%20LOCACOES6007GOIANIA62070503***6304", width=180)
                            with col_pix:
                                st.markdown("**Chave PIX (Telefone):** `62982240434`")
                                st.markdown("**Favorecido:** Renascer Locações & Eventos")
                                st.markdown(f"**Valor a Pagar:** `R$ {ped['total']:.2f}`")
                                st.info("Após efetuar o pagamento, envie o comprovante para o nosso WhatsApp: (62) 98224-0434")
                        else:
                            st.warning("⏳ **Pagamento Bloqueado:** Aguardando homologação e conferência de estoque por nossa equipe. Assim que homologado, o QR Code e chave PIX serão disponibilizados nesta aba.")

                        st.divider()
                        col_actions1, col_actions2 = st.columns(2)
                        
                        with col_actions1:
                            if st.button("✏️ Editar Pedido", key=f"btn_edit_{ped['id']}"):
                                st.session_state.carrinho_atual = dict(ped['itens'])
                                st.session_state.toalhas_vinculadas = dict(ped.get('toalhas', {}))
                                st.session_state.guardanapos_vinculados = dict(ped.get('guardanapos', {}))
                                st.session_state.pedido_edicao_id = ped['id']
                                tocar_som("click")
                                st.rerun()
                                
                        with col_actions2:
                            pdf_p = gerar_pdf_orcamento(
                                ped['cliente'], ped['evento'], ped['data'], ped['endereco'],
                                ped['itens_detalhe'], ped['subtotal'], ped['frete'], ped.get('taxa_dificuldade', 0.0), ped['total'], ped['status'], ped.get('obs_dificuldade', "")
                            )
                            st.download_button(
                                label="📄 Baixar PDF",
                                data=pdf_p,
                                file_name=f"Orcamento_{ped['evento'].replace(' ', '_')}.pdf",
                                mime="application/pdf",
                                key=f"btn_pdf_stb_{ped['id']}"
                            )

# ==========================================
# 🛠️ PAINEL ADMINISTRATIVO (GESTAO RENASCER)
# ==========================================
elif modo == "Painel Administrativo" and st.session_state.eh_admin:
    st.title("🛠️ Painel Administrativo de Homologação")

    novos_pedidos_pendentes = [p for p in st.session_state.pedidos_standby if p['status'] == 'Aguardando Homologação' and p.get('alerta_admin_tocado') != True]
    if novos_pedidos_pendentes:
        tocar_som("novo_pedido")
        st.toast("🚨 Novo pedido aguardando homologação!", icon="🔔")
        for p_p in novos_pedidos_pendentes:
            p_p['alerta_admin_tocado'] = True
    
    tab_admin_pedidos, tab_impressao_rapida, tab_relatorio_entrega, tab_relatorio_financeiro, tab_admin_catalogo = st.tabs([
        "📥 Gerenciar Pedidos / Homologação",
        "🖨️ Impressão Rápida em Lote",
        "🚚 Relatório de Entregas por Período",
        "📊 Relatório Financeiro por Período",
        "📦 Gerenciar Catálogo e Estoque"
    ])
    
    # TAB ADMINISTRATIVA 1: GERENCIAR PEDIDOS
    with tab_admin_pedidos:
        st.subheader("Pedidos Recebidos para Homologação")
        
        if not st.session_state.pedidos_standby:
            st.info("Nenhum pedido registrado no momento.")
        else:
            for p in st.session_state.pedidos_standby:
                with st.expander(f"ID #{p['id']} - {p['cliente']['nome']} - Evento: {p['evento']} ({p['status']})"):
                    st.write(f"**Contato:** {p['cliente']['telefone']} | **Data:** {p['data']}")
                    st.write(f"**Endereço:** {p['endereco']}")
                    st.write(f"**Total:** R$ {p['total']:.2f} (Frete: R$ {p['frete']:.2f} | Adic. Acesso: R$ {p.get('taxa_dificuldade', 0.0):.2f})")
                    if p.get('obs_dificuldade'):
                        st.write(f"**Obs. Dificuldade de Acesso:** {p['obs_dificuldade']}")
                    
                    st.markdown("**Itens:**")
                    for it in p['itens_detalhe']:
                        st.write(f"- {it['qtd']}x {it['nome']}")
                        
                    if p['status'] != 'Homologado (Disponibilidade Confirmada)':
                        if st.button("✅ Homologar Pedido (Liberar Pagamento/Pix)", key=f"btn_homologar_{p['id']}"):
                            p['status'] = 'Homologado (Disponibilidade Confirmada)'
                            tocar_som("homologado")
                            st.success(f"Pedido #{p['id']} Homologado com Sucesso! Pagamento PIX Liberado para o Cliente.")
                            st.rerun()

    # TAB ADMINISTRATIVA 2: IMPRESSÃO RÁPIDA EM LOTE
    with tab_impressao_rapida:
        st.subheader("🖨️ Seleção e Impressão Rápida de Pedidos")
        st.caption("Marque as caixas dos pedidos que deseja gerar em PDF:")
        
        if not st.session_state.pedidos_standby:
            st.info("Não existem pedidos no sistema para seleção.")
        else:
            pedidos_selecionados = []
            for p in st.session_state.pedidos_standby:
                col_chk, col_info = st.columns([1, 10])
                with col_chk:
                    marcado = st.checkbox("", key=f"chk_imp_lote_{p['id']}")
                    if marcado:
                        pedidos_selecionados.append(p)
                with col_info:
                    st.write(f"**ID #{p['id']}** — Cliente: {p['cliente']['nome']} | Evento: {p['evento']} | Data: {p['data']} | Status: {p['status']}")
                st.divider()

            if st.button("📄 Gerar e Baixar PDFs Selecionados em Lote", use_container_width=True):
                if not pedidos_selecionados:
                    st.warning("Por favor, selecione ao menos um pedido para gerar o PDF.")
                else:
                    for p_sel in pedidos_selecionados:
                        pdf_gen = gerar_pdf_orcamento(
                            p_sel['cliente'], p_sel['evento'], p_sel['data'], p_sel['endereco'],
                            p_sel['itens_detalhe'], p_sel['subtotal'], p_sel['frete'], p_sel.get('taxa_dificuldade', 0.0),
                            p_sel['total'], p_sel['status'], p_sel.get('obs_dificuldade', "")
                        )
                    st.success(f"🎉 {len(pedidos_selecionados)} PDF(s) gerado(s) e gravado(s) na pasta: `{PASTA_PDF}`")

    # TAB ADMINISTRATIVA 3: RELATÓRIO DE ENTREGAS
    with tab_relatorio_entrega:
        st.subheader("🚚 Relatório de Entregas por Período Personalizado")
        
        col_dt_e1, col_dt_e2 = st.columns(2)
        with col_dt_e1:
            dt_inicio_e = st.date_input("Data de Início das Entregas:", value=datetime.today(), key="dt_ini_entregas")
        with col_dt_e2:
            dt_fim_e = st.date_input("Data de Fim das Entregas:", value=datetime.today(), key="dt_fim_entregas")

        pedidos_no_periodo = []
        for p in st.session_state.pedidos_standby:
            try:
                dt_p = datetime.strptime(p['data'], "%Y-%m-%d").date()
                if dt_inicio_e <= dt_p <= dt_fim_e:
                    pedidos_no_periodo.append(p)
            except Exception:
                pass

        st.markdown(f"### Entregas Agendadas ({dt_inicio_e.strftime('%d/%m/%Y')} até {dt_fim_e.strftime('%d/%m/%Y')}):")
        if not pedidos_no_periodo:
            st.info("Nenhuma entrega agendada para o período selecionado.")
        else:
            for p_e in pedidos_no_periodo:
                st.markdown(f"📍 **Data: {p_e['data']}** | Cliente: {p_e['cliente']['nome']} (Tel: {p_e['cliente']['telefone']})")
                st.write(f"Endereço: {p_e['endereco']}")
                st.write(f"Observações de Acesso: {p_e.get('obs_dificuldade', 'Sem restrições')}")
                st.divider()

    # TAB ADMINISTRATIVA 4: RELATÓRIO FINANCEIRO
    with tab_relatorio_financeiro:
        st.subheader("📊 Relatório Financeiro Personalizado (Faturamento)")
        
        col_dt_f1, col_dt_f2 = st.columns(2)
        with col_dt_f1:
            dt_inicio_f = st.date_input("Data Inicial:", value=datetime.today(), key="dt_ini_fin")
        with col_dt_f2:
            dt_fim_f = st.date_input("Data Final:", value=datetime.today(), key="dt_fim_fin")

        total_materiais = 0.0
        total_frete = 0.0
        total_dificuldade = 0.0
        total_geral = 0.0
        qtd_pedidos = 0

        for p in st.session_state.pedidos_standby:
            try:
                dt_p = datetime.strptime(p['data'], "%Y-%m-%d").date()
                if dt_inicio_f <= dt_p <= dt_fim_f:
                    total_materiais += p.get('subtotal', 0.0)
                    total_frete += p.get('frete', 0.0)
                    total_dificuldade += p.get('taxa_dificuldade', 0.0)
                    total_geral += p.get('total', 0.0)
                    qtd_pedidos += 1
            except Exception:
                pass

        st.markdown(f"### Balanço do Período ({dt_inicio_f.strftime('%d/%m/%Y')} a {dt_fim_f.strftime('%d/%m/%Y')}):")
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Pedidos Totais", f"{qtd_pedidos}")
        col_m2.metric("Subtotal Materiais", f"R$ {total_materiais:.2f}")
        col_m3.metric("Total Fretes", f"R$ {total_frete:.2f}")
        col_m4.metric("Faturamento Geral", f"R$ {total_geral:.2f}")

    # TAB ADMINISTRATIVA 5: GERENCIAR CATÁLOGO E ESTOQUE
    with tab_admin_catalogo:
        st.subheader("📦 Catálogo de Produtos e Gestão de Estoque")
        st.caption("Edite os valores diretamente na tabela ou selecione uma linha e pressione 'Delete' para excluir o item do catálogo.")
        
        df_cat = pd.DataFrame(st.session_state.catalogo)
        
        df_editado = st.data_editor(
            df_cat,
            num_rows="dynamic",
            column_config={
                "id": st.column_config.NumberColumn("ID", disabled=True),
                "nome": st.column_config.TextColumn("Nome do Item", required=True),
                "categoria": st.column_config.SelectboxColumn("Categoria", options=["Mobiliário & Mesas", "Toalhas & Enxoval", "Louças & Copos", "Serviço & Rechauds", "Equipamentos & Freezers"]),
                "preco": st.column_config.NumberColumn("Preço (R$)", format="R$ %.2f"),
                "estoque": st.column_config.NumberColumn("Estoque", min_value=0),
                "foto": st.column_config.TextColumn("URL da Foto / Caminho")
            },
            hide_index=True,
            use_container_width=True,
            key="editor_catalogo_admin"
        )
        
        col_salvar, col_espaco = st.columns([1, 3])
        with col_salvar:
            if st.button("💾 Salvar Alterações / Exclusões no Catálogo", use_container_width=True):
                novos_dados = df_editado.to_dict(orient="records")
                st.session_state.catalogo = novos_dados
                salvar_catalogo_csv(novos_dados)
                tocar_som("sucesso")
                st.success("Catálogo e estoque gravados permanentemente com sucesso!")
                st.rerun()

        st.markdown("---")
        st.subheader("➕ Adicionar Novo Item ao Catálogo")
        with st.form("form_add_catalogo"):
            novo_nome = st.text_input("Nome do Material")
            nova_cat = st.selectbox("Categoria", ["Mobiliário & Mesas", "Toalhas & Enxoval", "Louças & Copos", "Serviço & Rechauds", "Equipamentos & Freezers"])
            novo_preco = st.number_input("Preço da Diária (R$)", min_value=0.0, value=10.0, step=0.50)
            novo_estq = st.number_input("Quantidade em Estoque", min_value=1, value=50)
            nova_foto = st.text_input("URL/Caminho da Foto (deixe em branco se não houver)", value="")
            
            if st.form_submit_button("➕ Cadastrar Item no Catálogo"):
                if novo_nome:
                    novo_id = max([int(i['id']) for i in st.session_state.catalogo], default=0) + 1
                    novo_item = {
                        "id": novo_id, "categoria": nova_cat, "nome": novo_nome,
                        "preco": novo_preco, "estoque": novo_estq, "foto": nova_foto,
                        "tipo_mesa": "None", "tipo_toalha": "None"
                    }
                    st.session_state.catalogo.append(novo_item)
                    salvar_catalogo_csv(st.session_state.catalogo)
                    tocar_som("sucesso")
                    st.success(f"Item '{novo_nome}' adicionado com sucesso!")
                    st.rerun()

# --- CAMPO DISCRETO NO RODAPÉ PARA ACESSO DO ADMINISTRADOR ---
st.markdown('<div class="btn-sair-container">', unsafe_allow_html=True)
col_rod1, col_rod2, col_rod3 = st.columns([1, 2, 1])

with col_rod2:
    with st.expander("🔐 Acesso Restrito / Área Administrativa"):
        if not st.session_state.eh_admin:
            senha_admin_input = st.text_input("Senha Admin:", type="password", key="pwd_disc_admin")
            if st.button("Entrar no Modo Admin", use_container_width=True):
                if senha_admin_input == "renascer@2026":
                    st.session_state.eh_admin = True
                    tocar_som("sucesso")
                    st.success("Modo Administrador ativado!")
                    st.rerun()
                else:
                    st.error("Senha incorreta.")
        else:
            st.success("Você está logado como Administrador.")
            if st.button("Sair do Modo Admin", use_container_width=True):
                st.session_state.eh_admin = False
                st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
