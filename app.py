import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime
from difflib import SequenceMatcher
import io
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
def gerar_pdf_orcamento(cliente, evento, data_evento, endereco, itens, subtotal, frete, total, status):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#1E3A8A'), spaceAfter=4)
    sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#475569'), spaceAfter=10)
    normal_style = styles['Normal']
    legal_style = ParagraphStyle('LegalStyle', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#334155'), spaceAfter=4)
    
    story.append(Paragraph("<b>RENASCER LOCAÇÕES E EVENTOS</b>", title_style))
    story.append(Paragraph("Rua Presidente Rodrigues Alves, Q. 30, Lt. 06, nº 01 — Jardim Presidente, Goiânia/GO<br/>Contato: (62) 3290-5515 | WhatsApp: (62) 98224-034", sub_style))
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
        ["Taxa de Frete / Logística:", f"R$ {frete:.2f}"],
        ["VALOR TOTAL DO ORÇAMENTO:", f"R$ {total:.2f}"]
    ]
    t_totais = Table(totais_data, colWidths=[380, 160])
    t_totais.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,-1), (-1,-1), colors.HexColor('#1E3A8A')),
        ('PADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_totais)
    story.append(Spacer(1, 12))

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
            
        sim_nome = max([calcular_similaridade(termo_processado, palavra) for palavra in nome.split()])
        sim_cat = max([calcular_similaridade(termo_processado, palavra) for palavra in categoria.split()])
        maior_sim = max(sim_nome, sim_cat)
        
        if maior_sim >= 0.55:
            resultados.append((item, maior_sim))
            
    resultados.sort(key=lambda x: x[1], reverse=True)
    return [r[0] for r in resultados]

# --- BASE DE DADOS DA SESSÃO ---
if 'catalogo' not in st.session_state:
    st.session_state.catalogo = [
        {"id": 1, "categoria": "Mobiliário & Mesas", "nome": "Jogo de Mesa com 4 Cadeiras de Plástico (Branca)", "preco": 14.00, "estoque": 50, "foto": "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?auto=format&fit=crop&w=400&q=80", "tipo_mesa": "quadrada"},
        {"id": 2, "categoria": "Mobiliário & Mesas", "nome": "Mesa Redonda de 6 Lugares (Tampão de Madeira)", "preco": 18.00, "estoque": 20, "foto": "https://images.unsplash.com/photo-1530103862676-de8c9debad1d?auto=format&fit=crop&w=400&q=80", "tipo_mesa": "redonda"},
        {"id": 3, "categoria": "Mobiliário & Mesas", "nome": "Aparador Rústico de Madeira (2,50m)", "preco": 25.00, "estoque": 5, "foto": "https://images.unsplash.com/photo-1519225421980-715cb0215aed?auto=format&fit=crop&w=400&q=80", "tipo_mesa": "outro"},
        {"id": 5, "categoria": "Toalhas & Enxoval", "nome": "Toalha Quadrada para Mesa (1,50m x 1,50m)", "preco": 6.00, "estoque": 100, "foto": "https://images.unsplash.com/photo-1584100936595-c0654b55a2e2?auto=format&fit=crop&w=400&q=80", "tipo_toalha": "quadrada"},
        {"id": 6, "categoria": "Toalhas & Enxoval", "nome": "Toalha Redonda para Mesa 6 e 7 Lugares", "preco": 12.00, "estoque": 80, "foto": "https://images.unsplash.com/photo-1584100936595-c0654b55a2e2?auto=format&fit=crop&w=400&q=80", "tipo_toalha": "redonda"},
        {"id": 8, "categoria": "Louças & Copos", "nome": "Prato de Jantar Raso Branco Liso", "preco": 0.80, "estoque": 300, "foto": "https://images.unsplash.com/photo-1578749556568-bc2c40e68b61?auto=format&fit=crop&w=400&q=80"},
        {"id": 9, "categoria": "Louças & Copos", "nome": "Taça para Água / Vinho Transparente", "preco": 1.00, "estoque": 200, "foto": "https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?auto=format&fit=crop&w=400&q=80"},
        {"id": 12, "categoria": "Serviço & Rechauds", "nome": "Rechaud Inox Redondo Banho-Maria", "preco": 25.00, "estoque": 10, "foto": "https://images.unsplash.com/photo-1555244162-803834f70033?auto=format&fit=crop&w=400&q=80"},
        {"id": 20, "categoria": "Equipamentos & Freezers", "nome": "Freezer Horizontal 2 Tampas (400 Litros)", "preco": 200.00, "estoque": 3, "foto": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=400&q=80"},
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
    <a href="https://api.whatsapp.com/send?phone=556298224034&text=Olá!%20Estou%20no%20aplicativo%20da%20Renascer%20Locações%20e%20gostaria%20de%20tirar%20uma%20dúvida." target="_blank" style="position:fixed;bottom:20px;right:20px;background-color:#25d366;color:white;border-radius:50px;text-align:center;font-size:15px;padding:12px 20px;box-shadow: 2px 2px 8px #888888;z-index:999999;text-decoration:none;font-weight:bold;">
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
            
        with st.form("form_novo_endereco"):
            st.write("**Cadastrar Novo Endereço:**")
            rotulo = st.text_input("Identificação (ex: Minha Chácara, Salão de Festas)")
            logradouro = st.text_input("Endereço Completo (Rua, Número, Bairro, Cidade)")
            cep = st.text_input("CEP")
            
            if st.form_submit_button("Salvar Endereço"):
                if rotulo and logradouro and cep:
                    st.session_state.enderecos_cadastrados.append({
                        "rotulo": rotulo, "logradouro": logradouro, "cep": cep
                    })
                    tocar_som("sucesso")
                    st.success("Novo endereço salvo com sucesso.")
                    st.rerun()

# ==========================================
# 📱 ÁREA DO CLIENTE & CATÁLOGO
# ==========================================
elif modo == "Área do Cliente":
    
    # CHAMADA INSTITUCIONAL NO TOPO
    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 22px; border-radius: 10px; border-left: 6px solid #1E3A8A; margin-bottom: 20px;">
        <h2 style="color: #1E3A8A; margin-bottom: 4px; font-weight: bold;">Renascer Locações e Eventos</h2>
        <p style="font-size: 15px; color: #1E293B; margin: 0px; font-weight: 500;">
            🏆 <i>Há anos realizando celebrações inesquecíveis com pontualidade, qualidade e o melhor atendimento de Goiânia.</i>
        </p>
        <p style="font-size: 13px; color: #475569; margin-top: 10px; margin-bottom: 0px;">
            📍 Rua Presidente Rodrigues Alves, Q. 30, Lt. 06, nº 01 — Jardim Presidente, Goiânia/GO 
            <a href="https://maps.app.goo.gl/KRxqyapDwF3QVFtW8" target="_blank" style="text-decoration:none; background-color:#1E3A8A; color:white; padding:4px 10px; border-radius:4px; font-size:12px; font-weight:bold; margin-left:6px;">
                🗺️ Como Chegar (Google Maps)
            </a>
            <br/>📞 (62) 3290-5515 | WhatsApp: (62) 98224-034
        </p>
    </div>
    """, unsafe_allow_html=True)

    # TELA DE CADASTRO INICIAL
    if not st.session_state.cliente_perfil:
        st.subheader("👋 Seja bem-vindo! Preencha abaixo para montar seu orçamento:")
        
        with st.form("form_cad_inicial"):
            c_nome = st.text_input("Seu Nome Completo*")
            c_tel = st.text_input("WhatsApp para Contato*")
            c_email = st.text_input("E-mail (Opcional)")
            st.markdown("---")
            c_end_rua = st.text_input("Endereço de Entrega do Evento*")
            c_end_cep = st.text_input("CEP do Local*")
            
            if st.form_submit_button("Escolher Materiais ➔"):
                if c_nome and c_tel and c_end_rua and c_end_cep:
                    st.session_state.cliente_perfil = {
                        "nome": c_nome, "telefone": c_tel, "email": c_email
                    }
                    st.session_state.enderecos_cadastrados.append({
                        "rotulo": "Endereço Principal",
                        "logradouro": c_end_rua,
                        "cep": c_end_cep
                    })
                    tocar_som("sucesso")
                    st.rerun()
                else:
                    st.error("Por favor, preencha os campos obrigatórios (*) para continuar.")

    # SEGUNDA TELA: NAVEGAÇÃO SUPERIOR
    else:
        cli = st.session_state.cliente_perfil
        tem_orcamento_em_andamento = bool(st.session_state.carrinho_atual)
        
        col_saudacao, col_status_carrinho = st.columns([3, 1])
        with col_saudacao:
            st.markdown(f"<p style='font-size:14px; color:#475569; margin:0px;'>Olá, <b>{cli['nome']}</b>! Seja bem-vindo(a).</p>", unsafe_allow_html=True)
        with col_status_carrinho:
            q_total_itens = sum(st.session_state.carrinho_atual.values())
            st.markdown(f"<p style='font-size:14px; color:#1E3A8A; font-weight:bold; text-align:right; margin:0px;'>🛒 {q_total_itens} item(ns) no orçamento</p>", unsafe_allow_html=True)

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
                        col_img, col_det, col_qtd = st.columns([1, 2, 1])
                        with col_img:
                            st.image(item['foto'], width=120)
                        with col_det:
                            st.markdown(f"#### {item['nome']}")
                            st.caption(f"Categoria: {item['categoria']}")
                            st.write(f"Valor unitário: **R$ {item['preco']:.2f}**")
                            
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
            st.subheader("📋 Resumo do Seu Orçamento")
            
            if not st.session_state.carrinho_atual:
                st.info("Seu carrinho está vazio. Acesse a aba 'Catálogo de Materiais' para escolher os itens do seu evento.")
            else:
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    opcoes_end = [f"{e['rotulo']} ({e['logradouro']} - CEP: {e['cep']})" for e in st.session_state.enderecos_cadastrados] + ["Outro Endereço"]
                    sel_end = st.selectbox("Local do Evento:", opcoes_end)
                    
                    if sel_end == "Outro Endereço":
                        end_rua_festa = st.text_input("Endereço Completo da Festa")
                        end_cep_festa = st.text_input("CEP da Festa")
                    else:
                        idx_end = opcoes_end.index(sel_end)
                        end_rua_festa = st.session_state.enderecos_cadastrados[idx_end]['logradouro']
                        end_cep_festa = st.session_state.enderecos_cadastrados[idx_end]['cep']
                        
                with col_e2:
                    data_festa = st.date_input("Data da Festa:")
                
                dados_frete = calcular_distancia_cep(end_cep_festa)
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
                    st.write(f"**Data do Evento:** {data_festa}")
                    st.write(f"**Endereço de Entrega:** {end_rua_festa}")
                
                st.markdown("##### Itens Selecionados:")
                
                subtotal_materiais = 0.0
                lista_pdf_itens = []
                
                tabela_itens_html = "<table style='width:100%; border-collapse: collapse; margin-top:10px; font-size:14px;'>"
                tabela_itens_html += "<tr style='background-color:#F1F5F9; border-bottom: 2px solid #CBD5E1;'><th style='text-align:left; padding:8px;'>Item</th><th style='text-align:center;'>Qtd</th><th style='text-align:right;'>Unitário</th><th style='text-align:right;'>Total</th></tr>"
                
                for item_id, q in st.session_state.carrinho_atual.items():
                    prod = next(i for i in st.session_state.catalogo if i['id'] == item_id)
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
                
                valor_total_bruto = subtotal_materiais + val_frete
                
                st.markdown("---")
                col_t1, col_t2 = st.columns([2, 2])
                with col_t2:
                    st.write(f"Subtotal dos Materiais: **R$ {subtotal_materiais:.2f}**")
                    st.write(f"Taxa de Entrega / Frete: **R$ {val_frete:.2f}**")
                    st.markdown(f"<h3 style='color:#1E3A8A; margin:0px;'>Total Geral: R$ {valor_total_bruto:.2f}</h3>", unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)
                
                # --- CAIXA DE TEXTO COM ROLAGEM OBRIGATÓRIA E TERMOS DE DEVOLUÇÃO ---
                st.markdown("---")
                st.markdown("#### 📜 Termos Simples de Recebimento e Devolução")
                st.caption("Por favor, role a caixa abaixo até o fim para ler e aceitar as condições de uso:")
                
                with st.container(height=180):
                    st.markdown("""
                    **Bem-vindo à Renascer Locações! Preparamos tudo para que seu evento seja perfeito.**
                    
                    * **1. Conferência na Entrega:** Ao receber os materiais, confira os itens junto com a nossa equipe. Caso perceba qualquer detalhe, avise-nos imediatamente.
                    * **2. Cuidados e Devolução:** Pedimos o carinho de devolver louças, copos e talheres organizados nas caixas e embalagens plásticas enviadas.
                    * **3. Eventuais Danos:** Sabemos que imprevistos acontecem! Caso ocorra alguma quebra ou perda, será cobrado apenas o valor de custo do item para reposição.
                    * **4. Confirmação de Reserva:** A finalizing do orçamento realiza a pré-reserva. A confirmação definitiva ocorre após validação da nossa equipe para a data do evento.
                    
                    *Agradecemos a confiança em nosso trabalho!*
                    """)

                concordou_termos = st.checkbox("✅ Li e concordo com os Termos de Locação e Devolução")

                pdf_bytes = gerar_pdf_orcamento(
                    cli, "Orçamento Formal", str(data_festa), end_rua_festa,
                    lista_pdf_itens, subtotal_materiais, val_frete, valor_total_bruto, "Rascunho de Orçamento"
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
                
                opcao_fechar = st.radio(
                    "O que você deseja fazer agora?",
                    ["Salvar Orçamento para Analisar Depois", "Confirmar Pedido e Solicitar Reserva de Estoque"]
                )
                
                nome_identificador = st.text_input("Dê um nome para o seu evento (ex: Aniversário da Maria, Churrasco de Domingo):")

                btn_desabilitado = not concordou_termos

                if st.button("💾 Gravar e Finalizar Orçamento", use_container_width=True, disabled=btn_desabilitado):
                    if not nome_identificador:
                        st.error("Digite um nome para identificar o seu evento.")
                    else:
                        status_final = "Em Análise" if opcao_fechar == "Salvar Orçamento para Analisar Depois" else "Aguardando Homologação da Renascer"
                        
                        if st.session_state.pedido_edicao_id:
                            for p in st.session_state.pedidos_standby:
                                if p['id'] == st.session_state.pedido_edicao_id:
                                    p['evento'] = nome_identificador
                                    p['data'] = str(data_festa)
                                    p['endereco'] = end_rua_festa
                                    p['frete'] = val_frete
                                    p['total'] = valor_total_bruto
                                    p['subtotal'] = subtotal_materiais
                                    p['status'] = status_final
                                    p['itens'] = dict(st.session_state.carrinho_atual)
                                    p['toalhas'] = dict(st.session_state.toalhas_vinculadas)
                                    p['itens_detalhe'] = lista_pdf_itens
                            st.session_state.pedido_edicao_id = None
                        else:
                            novo_stb = {
                                "id": len(st.session_state.pedidos_standby) + 1,
                                "cliente": cli,
                                "evento": nome_identificador,
                                "data": str(data_festa),
                                "endereco": end_rua_festa,
                                "frete": val_frete,
                                "subtotal": subtotal_materiais,
                                "total": valor_total_bruto,
                                "status": status_final,
                                "itens": dict(st.session_state.carrinho_atual),
                                "toalhas": dict(st.session_state.toalhas_vinculadas),
                                "itens_detalhe": lista_pdf_itens,
                                "alerta_tocado": False
                            }
                            st.session_state.pedidos_standby.append(novo_stb)

                        st.session_state.carrinho_atual = {}
                        st.session_state.toalhas_vinculadas = {}
                        st.session_state.termo_busca = ""
                        tocar_som("sucesso")
                        st.success("Seu orçamento foi salvo com sucesso!")
                        st.rerun()

                if not concordou_termos:
                    st.info("💡 Marque a caixa de seleção dos termos acima para liberar a gravação do pedido.")

                if opcao_fechar == "Confirmar Pedido e Solicitar Reserva de Estoque":
                    st.markdown("---")
                    st.subheader("💳 Dados para Pagamento via PIX")
                    
                    col_pix1, col_pix2 = st.columns([1, 2])
                    with col_pix1:
                        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=PIX+Renascer+Locacoes+Chave+6298224034+Valor+{valor_total_bruto:.2f}"
                        st.image(qr_url, caption="QR Code PIX", width=180)
                    with col_pix2:
                        st.write("**Chave PIX (Telefone):** `6298224034`")
                        st.write("**Favorecido:** Valdir Ferreira Miranda / Renascer Locações")
                        st.write(f"**Valor do Pedido:** R$ {valor_total_bruto:.2f}")
                        
                        txt_whatsapp = f"📋 *NOVO PEDIDO - RENASCER LOCAÇÕES*\n"
                        txt_whatsapp += f"*Cliente:* {cli['nome']}\n"
                        txt_whatsapp += f"*Evento:* {nome_identificador}\n"
                        txt_whatsapp += f"*Data:* {data_festa}\n"
                        txt_whatsapp += f"*VALOR TOTAL:* R$ {valor_total_bruto:.2f}\n"
                        txt_whatsapp += f"Olá! Acabei de enviar o pedido pelo aplicativo e gostaria de confirmar a reserva."
                        
                        link_wa_fechar = f"https://api.whatsapp.com/send?phone=556298224034&text={urllib.parse.quote(txt_whatsapp)}"
                        
                        st.markdown(f"""
                            <a href="{link_wa_fechar}" target="_blank">
                                <button style="background-color:#25D366; color:white; border:none; padding:12px; font-size:15px; border-radius:6px; font-weight:bold; cursor:pointer;">
                                    📲 Enviar Pedido via WhatsApp
                                </button>
                            </a>
                        """, unsafe_allow_html=True)

        # TAB 3: STANDBY & HISTÓRICO
        with tab_standby:
            st.subheader("📅 Meus Eventos e Orçamentos")
            
            if tem_orcamento_em_andamento:
                st.warning("⚠️ Você possui itens no carrinho. Finalize ou limpe o orçamento atual para reabrir pedidos anteriores.")
            else:
                if st.button("➕ Iniciar Novo Orçamento Zerado", use_container_width=True):
                    st.session_state.carrinho_atual = {}
                    st.session_state.toalhas_vinculadas = {}
                    st.session_state.pedido_edicao_id = None
                    tocar_som("click")
                    st.success("Novo orçamento iniciado!")
                    st.rerun()

            st.divider()

            if not st.session_state.pedidos_standby:
                st.info("Você ainda não possui orçamentos salvos.")
            else:
                for p in st.session_state.pedidos_standby:
                    with st.expander(f"🎉 {p['evento']} — Data: {p['data']} | Status: {p['status']}"):
                        st.write(f"**Endereço:** {p['endereco']}")
                        st.write(f"**Subtotal Materiais:** R$ {p['subtotal']:.2f}")
                        st.write(f"**Taxa de Entrega:** R$ {p['frete']:.2f}")
                        st.write(f"**Valor Total:** R$ {p['total']:.2f}")
                        
                        pdf_p = gerar_pdf_orcamento(
                            p['cliente'], p['evento'], p['data'], p['endereco'],
                            p['itens_detalhe'], p['subtotal'], p['frete'], p['total'], p['status']
                        )
                        st.download_button(
                            label="📄 Baixar PDF do Orçamento",
                            data=pdf_p,
                            file_name=f"Orcamento_{p['id']}_{p['evento'].replace(' ', '_')}.pdf",
                            mime="application/pdf",
                            key=f"dl_pdf_{p['id']}"
                        )
                        
                        if not tem_orcamento_em_andamento:
                            if st.button(f"✏️ Editar este Pedido (ID #{p['id']})", key=f"reabrir_{p['id']}"):
                                st.session_state.carrinho_atual = dict(p['itens'])
                                st.session_state.toalhas_vinculadas = dict(p.get('toalhas', {}))
                                st.session_state.pedido_edicao_id = p['id']
                                tocar_som("click")
                                st.success("Pedido reaberto para edição.")
                                st.rerun()

# ==========================================
# ⚙️ PAINEL ADMINISTRATIVO
# ==========================================
else:
    st.header("⚙️ Painel Interno — Renascer Locações")
    senha = st.text_input("Senha de Acesso", type="password")
    
    if senha == "1234":
        st.subheader("📊 Pedidos para Validação de Estoque")
        if not st.session_state.pedidos_standby:
            st.info("Nenhum pedido pendente para validação.")
        else:
            for p in st.session_state.pedidos_standby:
                with st.container():
                    st.markdown(f"### Pedido #{p['id']} — {p['evento']} ({p['cliente']['nome']})")
                    st.write(f"**Data da Festa:** {p['data']} | **Contato:** {p['cliente']['telefone']}")
                    st.write(f"**Endereço:** {p['endereco']}")
                    st.write(f"**Valor Total:** R$ {p['total']:.2f} (Frete: R$ {p['frete']:.2f})")
                    st.write(f"**Status:** `{p['status']}`")
                    
                    col_h1, col_h2 = st.columns(2)
                    with col_h1:
                        if st.button(f"✅ Homologar e Confirmar Estoque (ID #{p['id']})", key=f"btn_homo_{p['id']}"):
                            p['status'] = "Homologado (Disponibilidade Confirmada)"
                            p['alerta_tocado'] = False
                            tocar_som("sucesso")
                            st.success("Pedido Homologado.")
                            st.rerun()
                    with col_h2:
                        if st.button(f"❌ Indisponível para a Data (ID #{p['id']})", key=f"btn_rec_{p['id']}"):
                            p['status'] = "Indisponível (Sem Estoque para a Data)"
                            st.error("Status alterado para indisponível.")
                            st.rerun()
                    st.divider()
