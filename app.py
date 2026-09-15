import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime
from difflib import SequenceMatcher
import io
import requests
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Configuração da página
st.set_page_config(
    page_title="Renascer Locações - Excelência em Eventos",
    page_icon="🎉",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilização CSS para fixar e destacar o cabeçalho de navegação (Tabs)
st.markdown("""
    <style>
    div[data-baseweb="tab-list"] {
        position: sticky;
        top: 0;
        background-color: #1E3A8A;
        padding: 10px 15px;
        border-radius: 8px;
        z-index: 999;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
        margin-bottom: 25px;
    }
    div[data-baseweb="tab"] {
        color: #FFFFFF !important;
        font-weight: bold !important;
        font-size: 16px !important;
        padding: 10px 20px !important;
    }
    div[aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #1E3A8A !important;
        border-radius: 6px !important;
    }
    </style>
""", unsafe_allow_html=True)

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
    st.components.v1.html(f'<audio autoplay style="display:none;"><source src="{audio_url}" type="audio/mpeg"></audio>', height=0, width=0)

# --- GERADOR DE PDF FORMAL ---
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
    story.append(Paragraph("Rua Presidente Rodrigues Alves, Q. 30, Lt. 06, nº 01 — Jardim Presidente, Goiânia/GO<br/>Contato: (62) 3290-5515 | WhatsApp: (62) 98224-0340", sub_style))
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

    story.append(Paragraph("<b>TERMOS E CUIDADOS DE LOCAÇÃO</b>", ParagraphStyle('SubHeader', parent=styles['Heading3'], fontSize=10, textColor=colors.HexColor('#1E3A8A'))))
    story.append(Paragraph("1. <b>Conferência Amigável:</b> Verifique os itens na entrega para garantirmos juntos o sucesso do seu evento.", legal_style))
    story.append(Paragraph("2. <b>Devolução Prática:</b> Guarde pratos, copos e talheres nas embalagens originais enviadas.", legal_style))
    story.append(Paragraph("3. <b>Compromisso com o Cliente:</b> Havendo eventuais perdas ou avarias, a reposição será cobrada a preço de custo praticado no mercado.", legal_style))
    
    doc.build(story)
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
        nome = item['nome'].lower()
        categoria = item['categoria'].lower()
        
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

# --- BASE DE DADOS DA SESSÃO ---
if 'catalogo' not in st.session_state:
    st.session_state.catalogo = [
        # Mobiliário & Mesas
        {"id": 1, "categoria": "Mobiliário & Mesas", "nome": "Jogo de Mesa com 4 Cadeiras de Plástico (Branca)", "preco": 14.00, "estoque": 50, "foto": "", "tipo_mesa": "quadrada"},
        {"id": 2, "categoria": "Mobiliário & Mesas", "nome": "Mesa Redonda de 6 Lugares (Tampão de Madeira)", "preco": 18.00, "estoque": 20, "foto": "", "tipo_mesa": "redonda"},
        {"id": 3, "categoria": "Mobiliário & Mesas", "nome": "Aparador Rústico de Madeira (2,50m)", "preco": 25.00, "estoque": 5, "foto": "", "tipo_mesa": "outro"},
        {"id": 4, "categoria": "Mobiliário & Mesas", "nome": "Cadeira de Plástico Branca Avulsa", "preco": 2.50, "estoque": 200, "foto": ""},
        {"id": 5, "categoria": "Mobiliário & Mesas", "nome": "Mesa Bistrô Alta de Madeira", "preco": 20.00, "estoque": 15, "foto": ""},
        {"id": 6, "categoria": "Mobiliário & Mesas", "nome": "Banqueta Alta para Bistrô", "preco": 5.00, "estoque": 40, "foto": ""},
        
        # Toalhas & Enxoval
        {"id": 7, "categoria": "Toalhas & Enxoval", "nome": "Toalha Quadrada para Mesa (1,50m x 1,50m)", "preco": 6.00, "estoque": 100, "foto": "", "tipo_toalha": "quadrada"},
        {"id": 8, "categoria": "Toalhas & Enxoval", "nome": "Toalha Redonda para Mesa 6 e 7 Lugares", "preco": 12.00, "estoque": 80, "foto": "", "tipo_toalha": "redonda"},
        {"id": 9, "categoria": "Toalhas & Enxoval", "nome": "Cobre-Munch / Cobre-Mesa Colorido", "preco": 3.50, "estoque": 120, "foto": ""},
        {"id": 10, "categoria": "Toalhas & Enxoval", "nome": "Guardanapo de Tecido (Diversas Cores)", "preco": 1.50, "estoque": 300, "foto": ""},
        
        # Louças & Copos
        {"id": 11, "categoria": "Louças & Copos", "nome": "Prato de Jantar Raso Branco Liso", "preco": 0.80, "estoque": 300, "foto": ""},
        {"id": 12, "categoria": "Louças & Copos", "nome": "Prato de Sobremesa Branco Liso", "preco": 0.70, "estoque": 250, "foto": ""},
        {"id": 13, "categoria": "Louças & Copos", "nome": "Taça para Água / Vinho Transparente", "preco": 1.00, "estoque": 200, "foto": ""},
        {"id": 14, "categoria": "Louças & Copos", "nome": "Taça de Cerveja / Chope (300ml)", "preco": 1.00, "estoque": 200, "foto": ""},
        {"id": 15, "categoria": "Louças & Copos", "nome": "Copo Americano / Multiuso", "preco": 0.60, "estoque": 300, "foto": ""},
        {"id": 16, "categoria": "Louças & Copos", "nome": "Garfo de Jantar Inox", "preco": 0.50, "estoque": 400, "foto": ""},
        {"id": 17, "categoria": "Louças & Copos", "nome": "Faca de Jantar Inox", "preco": 0.50, "estoque": 400, "foto": ""},
        {"id": 18, "categoria": "Louças & Copos", "nome": "Colher de Sobremesa Inox", "preco": 0.50, "estoque": 300, "foto": ""},
        
        # Serviço & Rechauds
        {"id": 19, "categoria": "Serviço & Rechauds", "nome": "Rechaud Inox Redondo Banho-Maria", "preco": 25.00, "estoque": 10, "foto": ""},
        {"id": 20, "categoria": "Serviço & Rechauds", "nome": "Rechaud Inox Retangular Duplo", "preco": 35.00, "estoque": 8, "foto": ""},
        {"id": 21, "categoria": "Serviço & Rechauds", "nome": "Suqueira de Vidro com Torneira (5 Litros)", "preco": 15.00, "estoque": 12, "foto": ""},
        {"id": 22, "categoria": "Serviço & Rechauds", "nome": "Saladeira / Travesa de Inox", "preco": 5.00, "estoque": 20, "foto": ""},
        {"id": 23, "categoria": "Serviço & Rechauds", "nome": "Pegador de Salada / Carne Inox", "preco": 2.00, "estoque": 30, "foto": ""},
        {"id": 24, "categoria": "Serviço & Rechauds", "nome": "Concha para Molho / Sopa Inox", "preco": 2.00, "estoque": 25, "foto": ""},
        
        # Equipamentos & Freezers
        {"id": 25, "categoria": "Equipamentos & Freezers", "nome": "Freezer Horizontal 2 Tampas (400 Litros)", "preco": 200.00, "estoque": 3, "foto": ""},
        {"id": 26, "categoria": "Equipamentos & Freezers", "nome": "Freezer Vertical Expositor", "preco": 220.00, "estoque": 2, "foto": ""},
        {"id": 27, "categoria": "Equipamentos & Freezers", "nome": "Caixa Térmica Grande (100 Litros)", "preco": 30.00, "estoque": 10, "foto": ""},
        {"id": 28, "categoria": "Equipamentos & Freezers", "nome": "Tina Térmica para Bebidas (Madeira/Plástico)", "preco": 25.00, "estoque": 8, "foto": ""}
    ]

if 'cliente_perfil' not in st.session_state:
    st.session_state.cliente_perfil = None

if 'enderecos_cadastrados' not in st.session_state:
    st.session_state.enderecos_cadastrados = []

if 'carrinho_atual' not in st.session_state:
    st.session_state.carrinho_atual = {}

if 'toalhas_vinculadas' not in st.session_state:
    st.session_state.toalhas_vinculadas = {}

if 'pedidos_standby' not in st.session_state:
    st.session_state.pedidos_standby = []

if 'pedido_edicao_id' not in st.session_state:
    st.session_state.pedido_edicao_id = None

if 'termo_busca' not in st.session_state:
    st.session_state.termo_busca = ""

# --- BOTÃO FLUTUANTE DE AJUDA WHATSAPP ---
st.markdown("""
    <a href="https://api.whatsapp.com/send?phone=5562982240340&text=Olá!%20Estou%20no%20aplicativo%20da%20Renascer%20Locações%20e%20gostaria%20de%20tirar%20uma%20dúvida." target="_blank" style="position:fixed;bottom:20px;right:20px;background-color:#25d366;color:white;border-radius:50px;text-align:center;font-size:15px;padding:12px 20px;box-shadow: 2px 2px 8px #888888;z-index:999999;text-decoration:none;font-weight:bold;">
        💬 Falar com um Atendente
    </a>
""", unsafe_allow_html=True)

# --- MODAL DO CARDÁPIO RESUMIDO DE MATERIAIS ---
@st.dialog("📋 Lista Rápida de Materiais", width="large")
def abrir_cardapio_resumido():
    st.write("Clique em qualquer item para localizá-lo rapidamente no catálogo:")
    st.markdown("---")
    
    catalogo_ordenado = sorted(st.session_state.catalogo, key=lambda x: x['nome'])
    
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

# --- MENU LATERAL DE NAVEGAÇÃO ---
st.sidebar.title("📌 Navegação")
modo = st.sidebar.radio("Ir para:", ["Área do Cliente", "Meu Perfil", "Painel Administrativo"])

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
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 6px solid #1E3A8A; margin-bottom: 20px;">
            <h2 style="color: #1E3A8A; margin-bottom: 4px; font-weight: bold; font-size: 22px;">Renascer Locações e Eventos</h2>
            <p style="font-size: 14px; color: #1E293B; margin: 0px; font-weight: 500; line-height: 1.4;">
                🏆 <i>Há anos realizando celebrações inesquecíveis com pontualidade, qualidade e o melhor atendimento de Goiânia.</i>
            </p>
            <div style="font-size: 13px; color: #475569; margin-top: 12px; line-height: 1.6;">
                📍 Rua Presidente Rodrigues Alves, Q. 30, Lt. 06, nº 01 — Jardim Presidente, Goiânia/GO
                <div style="margin-top: 8px; margin-bottom: 8px;">
                    <a href="https://maps.app.goo.gl/KRxqyapDwF3QVFtW8" target="_blank" style="text-decoration: none; background-color: #1E3A8A; color: white; padding: 6px 12px; border-radius: 5px; font-size: 12px; font-weight: bold; display: inline-block; white-space: nowrap;">
                        🗺️ Como Chegar (Google Maps)
                    </a>
                </div>
                📞 (62) 3290-5515 | WhatsApp: (62) 98224-0340
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("👋 Seja bem-vindo! Faça seu cadastro inicial para acessar o catálogo:")
        
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

    # TELA PRINCIPAL DO CLIENTE (Navegação Direta)
    else:
        cli = st.session_state.cliente_perfil
        
        q_total_itens = sum(st.session_state.carrinho_atual.values())
        tot_carrinho_temp = 0.0
        for item_id, q in st.session_state.carrinho_atual.items():
            prod = next((i for i in st.session_state.catalogo if i['id'] == item_id), None)
            if prod:
                tot_carrinho_temp += prod['preco'] * q
                if item_id in st.session_state.toalhas_vinculadas:
                    tot_carrinho_temp += st.session_state.toalhas_vinculadas[item_id]['preco'] * q

        st.markdown(f"""
        <div style="background-color: #1E3A8A; color: white; padding: 12px 20px; border-radius: 8px; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0px 3px 8px rgba(0,0,0,0.12);">
            <div>
                <span style="font-size: 16px; font-weight: bold;">👋 Olá, {cli['nome']}!</span>
            </div>
            <div>
                <span style="font-size: 15px; background-color: #FFFFFF; color: #1E3A8A; padding: 6px 14px; border-radius: 20px; font-weight: bold;">
                    🛒 {q_total_itens} item(ns) | Total: R$ {tot_carrinho_temp:.2f}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        pedidos_homologados_recentes = [p for p in st.session_state.pedidos_standby if p.get('status') == 'Homologado (Disponibilidade Confirmada)' and p.get('alerta_tocado') != True]
        if pedidos_homologados_recentes:
            for p_h in pedidos_homologados_recentes:
                st.success(f"🎉 Boas notícias! Seu pedido para **'{p_h['evento']}'** foi aprovado e o estoque está reservado para você!")
                tocar_som("homologado")
                p_h['alerta_tocado'] = True

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
                input_busca = st.text_input("🔍 O que você procura? (ex: mesa, freezer, prato, taça...)", value=st.session_state.termo_busca, key="input_busca_campo")
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
                            
                            if item.get("foto"):
                                st.image(item['foto'], width=150)
                            else:
                                st.caption("🖼️ *Foto pendente de inclusão*")
                            
                            if item.get("tipo_mesa") in ["quadrada", "redonda"]:
                                st.markdown("---")
                                tipo_m = item.get("tipo_mesa")
                                quer_toalha = st.checkbox(f"Adicionar Toalha {tipo_m.capitalize()} para esta mesa?", key=f"chk_toalha_{item['id']}")
                                
                                if quer_toalha:
                                    cor_toalha = st.selectbox(
                                        "Selecione a cor:",
                                        ["Branca Clássica", "Vermelho Adamascado", "Palha Adamascado", "Verde Escuro", "Preta", "Azul"],
                                        key=f"cor_toalha_{item['id']}"
                                    )
                                    st.session_state.toalhas_vinculadas[item['id']] = {
                                        "tipo": tipo_m,
                                        "cor": cor_toalha,
                                        "preco": 6.00 if tipo_m == "quadrada" else 12.00
                                    }
                                else:
                                    st.session_state.toalhas_vinculadas.pop(item['id'], None)

                        with col_qtd:
                            qtd_atual = st.session_state.carrinho_atual.get(item['id'], 0)
                            nova_qtd = st.number_input(
                                "Quantidade:", min_value=0, max_value=item['estoque'], 
                                value=qtd_atual, key=f"item_qtd_{item['id']}"
                            )
                            if nova_qtd != qtd_atual:
                                if nova_qtd > 0:
                                    st.session_state.carrinho_atual[item['id']] = nova_qtd
                                else:
                                    st.session_state.carrinho_atual.pop(item['id'], None)
                                tocar_som("click")
                    st.divider()

        # TAB 2: FINALIZAR ORÇAMENTO
        with tab_carrinho:
            st.subheader("📋 Resumo do Seu Orçamento e Local de Entrega")
            
            if not st.session_state.carrinho_atual:
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
                    <div style="background-color: #FFFFFF; border: 1px solid #CBD5E1; padding: 20px; border-radius: 8px; box-shadow: 0px 2px 5px rgba(0,0,0,0.05);">
                        <h3 style="color:#1E3A8A; margin-top:0px; border-bottom: 2px solid #1E3A8A; padding-bottom: 5px;">
                            📄 RESUMO DO PEDIDO — RENASCER LOCAÇÕES
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
                
                for item_id, q in st.session_state.carrinho_atual.items():
                    prod = next((i for i in st.session_state.catalogo if i['id'] == item_id), None)
                    if prod:
                        tot_prod = prod['preco'] * q
                        subtotal_materiais += tot_prod
                        lista_pdf_itens.append({"nome": prod['nome'], "qtd": q, "preco": prod['preco'], "total": tot_prod})
                        
                        tabela_itens_html += f"<tr style='border-bottom: 1px solid #E2E8F0;'><td style='padding:8px;'>{prod['nome']}</td><td style='text-align:center;'>{q}</td><td style='text-align:right;'>R$ {prod['preco']:.2f}</td><td style='text-align:right;'>R$ {tot_prod:.2f}</td></tr>"
                        
                        if item_id in st.session_state.toalhas_vinculadas:
                            t_info = st.session_state.toalhas_vinculadas[item_id]
                            tot_toalha = t_info['preco'] * q
                            subtotal_materiais += tot_toalha
                            nome_t = f"Toalha {t_info['tipo'].capitalize()} ({t_info['cor']})"
                            lista_pdf_itens.append({"nome": nome_t, "qtd": q, "preco": t_info['preco'], "total": tot_toalha})
                            tabela_itens_html += f"<tr style='border-bottom: 1px solid #E2E8F0; color:#475569;'><td style='padding:8px; padding-left:25px;'>└ ➕ {nome_t}</td><td style='text-align:center;'>{q}</td><td style='text-align:right;'>R$ {t_info['preco']:.2f}</td><td style='text-align:right;'>R$ {tot_toalha:.2f}</td></tr>"

                tabela_itens_html += "</table>"
                st.markdown(tabela_itens_html, unsafe_allow_html=True)
                
                # CÁLCULO DA TAXA ADICIONAL DE DIFICULDADE (Base 30,00 + Grau % sobre os Materiais)
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
                
                # --- TERMOS DE DEVOLUÇÃO ---
                st.markdown("---")
                st.markdown("#### 📜 Termos Simples de Recebimento e Devolução")
                st.caption("Por favor, leia e aceite as condições de uso para habilitar a finalização:")
                
                with st.container(height=160):
                    st.markdown("""
                    **Bem-vindo à Renascer Locações! Preparamos tudo para que seu evento seja perfeito.**
                    
                    * **1. Conferência na Entrega:** Ao receber os materiais, confira os itens junto com a nossa equipe.
                    * **2. Cuidados e Devolução:** Devolva louças, copos e talheres organizados nas embalagens originais enviadas.
                    * **3. Eventuais Danos:** Caso ocorra alguma quebra ou perda, será cobrado o valor de custo praticado no mercado.
                    * **4. Confirmação de Reserva:** A finalização realiza a solicitação de reserva. A confirmação definitiva ocorre após homologação do estoque.
                    """)

                concordou_termos = st.checkbox("✅ Li e concordo com os Termos de Locação e Devolução", key="chk_termos_aceite")

                pdf_bytes = gerar_pdf_orcamento(
                    cli, "Orçamento Formal", str(data_festa), end_rua_festa,
                    lista_pdf_itens, subtotal_materiais, val_frete, taxa_dificuldade, valor_total_bruto, "Rascunho de Orçamento", obs_dificuldade
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
                        status_final = "Aguardando Homologação da Renascer"
                        
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
                                    p['itens_detalhe'] = lista_pdf_itens
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
                                "itens_detalhe": lista_pdf_itens,
                                "alerta_tocado": False
                            }
                            st.session_state.pedidos_standby.append(novo_stb)
                        
                        # Limpeza do carrinho temporário
                        st.session_state.carrinho_atual = {}
                        st.session_state.toalhas_vinculadas = {}
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
                    with st.expander(f"🎉 {ped['evento']} — Data: {ped['data']} (Status: {ped['status']})"):
                        st.write(f"**Endereço:** {ped['endereco']}")
                        st.write(f"**Valor Total:** R$ {ped['total']:.2f} (Materiais: R$ {ped['subtotal']:.2f} | Frete: R$ {ped['frete']:.2f} | Dificuldade: R$ {ped.get('taxa_dificuldade', 0.0):.2f})")
                        if ped.get('obs_dificuldade'):
                            st.write(f"**Obs. Acesso:** {ped['obs_dificuldade']}")
                        
                        st.write("**Itens do Pedido:**")
                        for item_det in ped['itens_detalhe']:
                            st.write(f"- {item_det['qtd']}x {item_det['nome']} (R$ {item_det['total']:.2f})")
                        
                        col_actions1, col_actions2, col_actions3 = st.columns(3)
                        
                        with col_actions1:
                            if st.button("✏️ Editar Pedido", key=f"btn_edit_{ped['id']}"):
                                st.session_state.carrinho_atual = dict(ped['itens'])
                                st.session_state.toalhas_vinculadas = dict(ped['toalhas'])
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
                            
                        with col_actions3:
                            texto_wpp = f"Olá! Gostaria de confirmar meu pedido *{ped['evento']}* (ID: #{ped['id']}) para a data {ped['data']}. Valor Total: R$ {ped['total']:.2f}."
                            wpp_url = f"https://api.whatsapp.com/send?phone=5562982240340&text={urllib.parse.quote(texto_wpp)}"
                            st.markdown(f'<a href="{wpp_url}" target="_blank" style="text-decoration:none; background-color:#25d366; color:white; padding:8px 12px; border-radius:5px; font-weight:bold; display:inline-block; text-align:center;">📲 Enviar via WhatsApp</a>', unsafe_allow_html=True)

# ==========================================
# 🛠️ PAINEL ADMINISTRATIVO (GESTAO RENASCER)
# ==========================================
elif modo == "Painel Administrativo":
    st.title("🛠️ Painel Administrativo — Renascer Locações")
    
    tab_admin_pedidos, tab_admin_catalogo = st.tabs(["📥 Gerenciar Pedidos / Homologação", "📦 Gerenciar Catálogo e Estoque"])
    
    with tab_admin_pedidos:
        st.subheader("Pedidos Recebidos")
        
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
                        if st.button("✅ Homologar Pedido (Confirmar Estoque)", key=f"btn_homologar_{p['id']}"):
                            p['status'] = 'Homologado (Disponibilidade Confirmada)'
                            tocar_som("homologado")
                            st.success(f"Pedido #{p['id']} Homologado com Sucesso!")
                            st.rerun()

    with tab_admin_catalogo:
        st.subheader("📦 Catálogo de Produtos e Gestão de Estoque")
        st.caption("Edite os valores diretamente na tabela ou selecione uma linha e pressione 'Delete' para excluir o item do catálogo.")
        
        df_cat = pd.DataFrame(st.session_state.catalogo)
        
        # Tabela editável interativa com exclusão/adição nativa
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
                st.session_state.catalogo = df_editado.to_dict(orient="records")
                tocar_som("sucesso")
                st.success("Catálogo e estoque atualizados com sucesso!")
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
                    novo_id = max([i['id'] for i in st.session_state.catalogo], default=0) + 1
                    st.session_state.catalogo.append({
                        "id": novo_id, "categoria": nova_cat, "nome": novo_nome,
                        "preco": novo_preco, "estoque": novo_estq, "foto": nova_foto
                    })
                    tocar_som("sucesso")
                    st.success(f"Item '{novo_nome}' adicionado com sucesso!")
                    st.rerun()
