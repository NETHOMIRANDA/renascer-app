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
    page_title="Renascer Locações - Catálogo & Reservas",
    page_icon="🎉",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#1E3A8A'), spaceAfter=6)
    sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#475569'), spaceAfter=12)
    normal_style = styles['Normal']
    
    # Cabeçalho Timbrado
    story.append(Paragraph("<b>RENASCER LOCAÇÕES E EVENTOS</b>", title_style))
    story.append(Paragraph("Rua Presidente Rodrigues Alves, Q. 30, Lt. 06, nº 01 — Jardim Presidente, Goiânia/GO<br/>Contato: (62) 3290-5515 | WhatsApp: (62) 98224-034", sub_style))
    story.append(Spacer(1, 10))
    
    # Dados do Orçamento
    dados_cli = [
        [Paragraph(f"<b>Cliente:</b> {cliente['nome']}", normal_style), Paragraph(f"<b>Evento:</b> {evento}", normal_style)],
        [Paragraph(f"<b>Telefone:</b> {cliente['telefone']}", normal_style), Paragraph(f"<b>Data da Festa:</b> {data_evento}", normal_style)],
        [Paragraph(f"<b>Endereço de Entrega:</b> {endereco}", normal_style), Paragraph(f"<b>Status:</b> {status}", normal_style)]
    ]
    t_cli = Table(dados_cli, colWidths=[270, 270])
    t_cli.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    story.append(t_cli)
    story.append(Spacer(1, 15))
    
    # Tabela de Itens
    tabela_data = [["Item / Descrição", "Qtd", "Unitário (R$)", "Total (R$)"]]
    for item in itens:
        tabela_data.append([item['nome'], str(item['qtd']), f"{item['preco']:.2f}", f"{item['total']:.2f}"])
        
    t_itens = Table(tabela_data, colWidths=[280, 50, 100, 110])
    t_itens.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_itens)
    story.append(Spacer(1, 15))
    
    # Resumo Financeiro
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
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_totais)
    story.append(Spacer(1, 20))
    story.append(Paragraph("<i>* Orçamento sujeito a homologação de disponibilidade de estoque para a data solicitada.</i>", sub_style))
    
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
    <a href="https://api.whatsapp.com/send?phone=556298224034&text=Olá!%20Estou%20no%20aplicativo%20da%20Renascer%20Locações%20e%20preciso%20de%20ajuda%20com%20meu%20pedido." target="_blank" style="position:fixed;bottom:20px;right:20px;background-color:#25d366;color:white;border-radius:50px;text-align:center;font-size:15px;padding:12px 20px;box-shadow: 2px 2px 8px #888888;z-index:999999;text-decoration:none;font-weight:bold;">
        💬 Dúvidas? Fale Conosco
    </a>
""", unsafe_allow_html=True)

# --- MODAL DO CARDÁPIO RESUMIDO DE MATERIAIS ---
@st.dialog("📋 Cardápio Resumido de Materiais", width="large")
def abrir_cardapio_resumido():
    st.write("Clique no material desejado para ir direto para a escolha da quantidade e subitens:")
    st.markdown("---")
    
    # Ordenar catálogo por ordem alfabética de nome
    catalogo_ordenado = sorted(st.session_state.catalogo, key=lambda x: x['nome'])
    
    # Container rolável
    with st.container(height=420):
        for item in catalogo_ordenado:
            col_txt, col_btn = st.columns([3, 1])
            with col_txt:
                st.markdown(f"**{item['nome']}**  \n<small style='color:gray;'>{item['categoria']} — R$ {item['preco']:.2f}</small>", unsafe_allow_html=True)
            with col_btn:
                if st.button("Seleccionar ➔", key=f"btn_sel_cardapio_{item['id']}"):
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
    st.title("👤 Meu Perfil & Endereços de Entrega")
    
    if not st.session_state.cliente_perfil:
        st.warning("Você ainda não realizou o cadastro inicial na Área do Cliente.")
    else:
        perf = st.session_state.cliente_perfil
        with st.form("form_edita_perfil"):
            st.subheader("Editar Dados Pessoais")
            e_nome = st.text_input("Nome Completo", value=perf['nome'])
            e_tel = st.text_input("WhatsApp", value=perf['telefone'])
            e_email = st.text_input("E-mail", value=perf['email'])
            
            if st.form_submit_button("Atualizar Perfil"):
                st.session_state.cliente_perfil['nome'] = e_nome
                st.session_state.cliente_perfil['telefone'] = e_tel
                st.session_state.cliente_perfil['email'] = e_email
                tocar_som("sucesso")
                st.success("Perfil atualizado com sucesso!")
                
        st.divider()
        st.subheader("🏡 Endereços Cadastrados para Eventos")
        for idx, end in enumerate(st.session_state.enderecos_cadastrados):
            st.info(f"**{end['rotulo']}**: {end['logradouro']} - CEP: {end['cep']}")
            
        with st.form("form_novo_endereco"):
            st.write("**Adicionar Novo Endereço:**")
            rotulo = st.text_input("Identificação (ex: Minha Casa, Chácara, Salão de Festas)")
            logradouro = st.text_input("Endereço Completo (Rua, Nº, Bairro, Cidade)")
            cep = st.text_input("CEP do Local")
            
            if st.form_submit_button("Cadastrar Endereço"):
                if rotulo and logradouro and cep:
                    st.session_state.enderecos_cadastrados.append({
                        "rotulo": rotulo, "logradouro": logradouro, "cep": cep
                    })
                    tocar_som("sucesso")
                    st.success("Novo endereço cadastrado com sucesso!")
                    st.rerun()

# ==========================================
# 📱 ÁREA DO CLIENTE & CATÁLOGO
# ==========================================
elif modo == "Área do Cliente":
    
    # APRESENTAÇÃO INSTITUCIONAL COM LINK DE MAPA COMPACTO
    if not st.session_state.cliente_perfil:
        st.markdown("""
        <div style="background-color: #f8f9fa; padding: 22px; border-radius: 12px; border-left: 6px solid #1E3A8A; margin-bottom: 20px;">
            <h1 style="color: #1E3A8A; margin-bottom: 5px;">🎉 Renascer Locações</h1>
            <h4 style="color: #475569; margin-top: 0px;">Tradição, Qualidade e Pontualidade para o seu Evento</h4>
            <p style="font-size: 15px; color: #334155;">
                Com <b>mais de 20 anos de atuação no mercado</b>, a <b>Renascer Locações</b> é referência na locação de pratos, copos, talheres, toalhas, rechauds e equipamentos para festas e eventos. Nosso compromisso é entregar tudo com a agilidade que a sua celebração merece.
            </p>
            <p style="font-size: 14px; color: #64748B; margin-bottom: 0px;">
                📍 <b>Sede Própria:</b> Rua Presidente Rodrigues Alves, Q. 30, Lt. 06, nº 01 — Jardim Presidente, Goiânia/GO 
                <a href="https://maps.google.com/?q=Rua+Presidente+Rodrigues+Alves+Quadra+30+Lote+06+Jardim+Presidente+Goiania" target="_blank" style="text-decoration:none; background-color:#1E3A8A; color:white; padding:3px 8px; border-radius:4px; font-size:12px; font-weight:bold; margin-left:5px;">
                    🗺️ Ver no Mapa
                </a>
                <br/>📞 <b>Contato:</b> (62) 3290-5515 | 📱 <b>WhatsApp:</b> (62) 98224-034
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("👋 Seja Bem-Vindo(a)! Preencha seus dados para acessar o catálogo:")
        
        with st.form("form_cad_inicial"):
            c_nome = st.text_input("Nome Completo*")
            c_tel = st.text_input("WhatsApp / Telefone*")
            c_email = st.text_input("E-mail")
            st.markdown("---")
            st.markdown("**Endereço Residencial:**")
            c_end_rua = st.text_input("Endereço Completo (Rua, Nº, Bairro, Cidade)*")
            c_end_cep = st.text_input("CEP Residencial*")
            
            if st.form_submit_button("Acessar Catálogo & Fazer Orçamento ➔"):
                if c_nome and c_tel and c_end_rua and c_end_cep:
                    st.session_state.cliente_perfil = {
                        "nome": c_nome, "telefone": c_tel, "email": c_email
                    }
                    st.session_state.enderecos_cadastrados.append({
                        "rotulo": "Minha Residência",
                        "logradouro": c_end_rua,
                        "cep": c_end_cep
                    })
                    tocar_som("sucesso")
                    st.rerun()
                else:
                    st.error("Por favor, preencha todos os campos obrigatórios (*).")

    # CATÁLOGO, SELEÇÃO E ORÇAMENTO
    else:
        cli = st.session_state.cliente_perfil
        
        # CHECAGEM DE HOMOLOGAÇÃO PARA DISPARAR ÁUDIO E NOTIFICAÇÃO AO CLIENTE
        pedidos_homologados_recentes = [p for p in st.session_state.pedidos_standby if p.get('status') == 'Homologado (Disponibilidade Confirmada)' and p.get('alerta_tocado') != True]
        if pedidos_homologados_recentes:
            for p_h in pedidos_homologados_recentes:
                st.success(f"🔔 **BOAS NOTÍCIAS!** O seu pedido para o evento **'{p_h['evento']}'** foi homologado e confirmado pela equipe da Renascer Locações!")
                tocar_som("homologado")
                p_h['alerta_tocado'] = True

        col_tit, col_novo = st.columns([3, 1])
        with col_tit:
            st.title(f"Olá, {cli['nome']}!")
        with col_novo:
            if st.button("➕ Iniciar Novo Pedido"):
                st.session_state.carrinho_atual = {}
                st.session_state.toalhas_vinculadas = {}
                st.session_state.pedido_edicao_id = None
                st.session_state.termo_busca = ""
                tocar_som("click")
                st.rerun()

        if st.session_state.pedido_edicao_id:
            st.warning(f"📝 **Você está editando o Pedido ID #{st.session_state.pedido_edicao_id}**. Ao concluir, as alterações serão salvas diretamente nele.")

        tab_catalogo, tab_carrinho, tab_standby = st.tabs(["🛒 Catálogo de Materiais", "📋 Finalizar Orçamento & Frete", "📅 Eventos & Histórico"])
        
        # TAB 1: CATÁLOGO COM BUSCA INTELIGENTE E CARDÁPIO RESUMIDO
        with tab_catalogo:
            st.subheader("Qual material você procura?")
            
            col_busca, col_cardapio = st.columns([3, 1])
            with col_busca:
                input_busca = st.text_input("🔍 Digite o nome do item (ex: mesa, frizzer, pano, copo):", value=st.session_state.termo_busca, key="input_busca_campo")
                st.session_state.termo_busca = input_busca
            with col_cardapio:
                st.write("&#160;")
                if st.button("📋 Cardápio Resumido", use_container_width=True):
                    abrir_cardapio_resumido()

            itens_exibidos = buscar_materiais_inteligente(st.session_state.termo_busca, st.session_state.catalogo)
            
            if not itens_exibidos:
                st.warning("Nenhum material encontrado exatamente com este termo. Clique no botão **📋 Cardápio Resumido** ao lado para ver a lista completa de materiais.")
            else:
                for item in itens_exibidos:
                    with st.container():
                        col_img, col_det, col_qtd = st.columns([1, 2, 1])
                        with col_img:
                            st.image(item['foto'], width=130)
                        with col_det:
                            st.markdown(f"### {item['nome']}")
                            st.caption(f"Categoria: {item['categoria']}")
                            st.write(f"Preço Unitário: **R$ {item['preco']:.2f}**")
                            
                            if item.get("tipo_mesa") in ["quadrada", "redonda"]:
                                st.markdown("---")
                                tipo_m = item.get("tipo_mesa")
                                quer_toalha = st.checkbox(f"Deseja incluir Toalha {tipo_m.capitalize()} para esta mesa?", key=f"chk_toalha_{item['id']}")
                                
                                if quer_toalha:
                                    cor_toalha = st.selectbox(
                                        "Escolha a cor da toalha:",
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

        # TAB 2: DETALHES DO EVENTO, CÁLCULO DE FRETE E FLUXO DE PAGAMENTO
        with tab_carrinho:
            st.subheader("📋 Detalhes da Entrega e Cálculo de Frete")
            
            if not st.session_state.carrinho_atual:
                st.info("Seu carrinho está vazio. Adicione materiais na aba Catálogo para continuar.")
            else:
                # 1. Seleção do Local da Festa
                st.markdown("#### 1. Selecione o Local do Evento")
                opcoes_end = [f"{e['rotulo']} ({e['logradouro']} - CEP: {e['cep']})" for e in st.session_state.enderecos_cadastrados] + ["Outro Endereço (Cadastrar Agora)"]
                sel_end = st.selectbox("Escolha onde será a festa:", opcoes_end)
                
                if sel_end == "Outro Endereço (Cadastrar Agora)":
                    col_n1, col_n2 = st.columns(2)
                    with col_n1:
                        end_rua_festa = st.text_input("Endereço Completo do Evento")
                    with col_n2:
                        end_cep_festa = st.text_input("CEP do Evento")
                else:
                    idx_end = opcoes_end.index(sel_end)
                    end_rua_festa = st.session_state.enderecos_cadastrados[idx_end]['logradouro']
                    end_cep_festa = st.session_state.enderecos_cadastrados[idx_end]['cep']

                st.write(f"📍 **Endereço da Festa Confirmado:** {end_rua_festa} | CEP: {end_cep_festa}")
                
                # 2. Cálculo do Frete Integrado
                dados_frete = calcular_distancia_cep(end_cep_festa)
                val_frete = 0.0
                if dados_frete:
                    val_frete = dados_frete['valor_frete']
                    st.success(f"🚚 **Frete Calculado Integrado:** Distância da Renascer Locações: {dados_frete['km']} km ➔ **Valor do Frete: R$ {val_frete:.2f}**")
                else:
                    st.warning("Informe um CEP válido para calcular e somar o valor do frete automático ao orçamento.")

                # 3. Data do Evento
                data_festa = st.date_input("Data do Evento:")

                # 4. Resumo de Itens e Valores
                st.markdown("---")
                st.markdown("#### 2. Resumo do Orçamento")
                
                subtotal_materiais = 0.0
                lista_pdf_itens = []
                
                for item_id, q in st.session_state.carrinho_atual.items():
                    prod = next(i for i in st.session_state.catalogo if i['id'] == item_id)
                    tot_prod = prod['preco'] * q
                    subtotal_materiais += tot_prod
                    st.write(f"• **{q}x {prod['nome']}** — R$ {tot_prod:.2f}")
                    lista_pdf_itens.append({"nome": prod['nome'], "qtd": q, "preco": prod['preco'], "total": tot_prod})
                    
                    if item_id in st.session_state.toalhas_vinculadas:
                        t_info = st.session_state.toalhas_vinculadas[item_id]
                        tot_toalha = t_info['preco'] * q
                        subtotal_materiais += tot_toalha
                        nome_t = f"Toalha {t_info['tipo'].capitalize()} ({t_info['cor']})"
                        st.write(f"  └ ➕ *{q}x {nome_t}* — R$ {tot_toalha:.2f}")
                        lista_pdf_itens.append({"nome": nome_t, "qtd": q, "preco": t_info['preco'], "total": tot_toalha})

                valor_total_bruto = subtotal_materiais + val_frete
                st.markdown(f"Subtotal Materiais: **R$ {subtotal_materiais:.2f}**")
                st.markdown(f"Valor do Frete Computado: **R$ {val_frete:.2f}**")
                st.markdown(f"### Valor Total do Orçamento: **R$ {valor_total_bruto:.2f}**")

                # GERAR E BAIXAR PDF FORMAL
                pdf_bytes = gerar_pdf_orcamento(
                    cli, "Orçamento Formal", str(data_festa), end_rua_festa,
                    lista_pdf_itens, subtotal_materiais, val_frete, valor_total_bruto, "Rascunho de Orçamento"
                )
                st.download_button(
                    label="📄 Baixar Orçamento Formal em PDF",
                    data=pdf_bytes,
                    file_name=f"Orcamento_Renascer_{cli['nome'].replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )

                # RECADOS DE ESTOQUE E HOMOLOGAÇÃO
                st.warning("⚠️ **AVISO IMPORTANTE:** Caso deixe a confirmação do seu pedido para cima da hora, corre-se o risco do material desejado não ter mais disponibilidade em estoque para a data do evento.")
                st.info("ℹ️ **Processo de Confirmação:** Ao efetivar o pedido, nossa equipe fará a **homologação e validação formal de estoque** para a data informada. Você receberá uma notificação assim que o pedido for aceito.")

                # 5. Opções de Fechamento / Standby
                st.markdown("---")
                st.markdown("#### 3. Conclusão do Pedido")
                
                opcao_fechar = st.radio(
                    "Como prefere dar andamento a este pedido?",
                    ["Guardar Pedido em Standby para Data Futura", "Efetivar Pedido e Ir para Pagamento"]
                )
                
                nome_identificador = st.text_input("Identificação do Evento (ex: Aniversário da Sofia, Churrasco da Firma):")

                if st.button("💾 Finalizar e Confirmar Pedido"):
                    if not nome_identificador:
                        st.error("Por favor, digite um nome para identificar a sua festa.")
                    else:
                        status_final = "Standby (Aguardando Definição)" if opcao_fechar == "Guardar Pedido em Standby para Data Futura" else "Aguardando Homologação da Renascer"
                        
                        # Se for edição, atualiza
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
                        st.success("Pedido gravado com sucesso! Redirecionando...")
                        st.rerun()

                # SE FOR EFETIVAR, EXIBE ÁREA DE PAGAMENTO PIX
                if opcao_fechar == "Efetivar Pedido e Ir para Pagamento":
                    st.markdown("---")
                    st.subheader("💳 Dados para Pagamento via PIX")
                    
                    col_pix1, col_pix2 = st.columns([1, 2])
                    with col_pix1:
                        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=PIX+Renascer+Locacoes+Chave+6298224034+Valor+{valor_total_bruto:.2f}"
                        st.image(qr_url, caption="Escaneie para Pagar via PIX", width=200)
                    with col_pix2:
                        st.write("**Chave PIX (Telefone):** `6298224034`")
                        st.write("**Favorecido:** Valdir Ferreira Miranda / Renascer Locações")[cite: 1]
                        st.write(f"**Valor do Pedido (com frete):** R$ {valor_total_bruto:.2f}")
                        
                        txt_whatsapp = f"📋 *NOVO PEDIDO EFETIVADO - RENASCER LOCAÇÕES*\n"
                        txt_whatsapp += f"*Cliente:* {cli['nome']}\n"
                        txt_whatsapp += f"*Evento:* {nome_identificador}\n"
                        txt_whatsapp += f"*Data:* {data_festa}\n"
                        txt_whatsapp += f"*Endereço:* {end_rua_festa}\n"
                        txt_whatsapp += f"*VALOR TOTAL:* R$ {valor_total_bruto:.2f}\n"
                        txt_whatsapp += f"Solicito a homologação e confirmação de disponibilidade do material."
                        
                        link_wa_fechar = f"https://api.whatsapp.com/send?phone=556298224034&text={urllib.parse.quote(txt_whatsapp)}"
                        
                        st.markdown(f"""
                            <a href="{link_wa_fechar}" target="_blank">
                                <button style="background-color:#25D366; color:white; border:none; padding:15px; font-size:16px; border-radius:8px; font-weight:bold; cursor:pointer;">
                                    📲 Enviar Pedido para Homologação no WhatsApp
                                </button>
                            </a>
                        """, unsafe_allow_html=True)

        # TAB 3: STANDBY & REABERTURA DE PEDIDOS
        with tab_standby:
            st.subheader("📅 Seus Pedidos & Orçamentos Guardados")
            if not st.session_state.pedidos_standby:
                st.info("Nenhum pedido ou orçamento encontrado.")
            else:
                for p in st.session_state.pedidos_standby:
                    with st.expander(f"🎉 {p['evento']} — Data: {p['data']} | Status: {p['status']}"):
                        st.write(f"**Endereço de Entrega:** {p['endereco']}")
                        st.write(f"**Subtotal Materiais:** R$ {p['subtotal']:.2f}")
                        st.write(f"**Valor do Frete:** R$ {p['frete']:.2f}")
                        st.write(f"**Valor Total:** R$ {p['total']:.2f}")
                        
                        pdf_p = gerar_pdf_orcamento(
                            p['cliente'], p['evento'], p['data'], p['endereco'],
                            p['itens_detalhe'], p['subtotal'], p['frete'], p['total'], p['status']
                        )
                        st.download_button(
                            label="📄 Baixar PDF deste Pedido",
                            data=pdf_p,
                            file_name=f"Orcamento_{p['id']}_{p['evento'].replace(' ', '_')}.pdf",
                            mime="application/pdf",
                            key=f"dl_pdf_{p['id']}"
                        )
                        
                        if st.button(f"✏️ Reabrir e Alterar este Pedido (ID #{p['id']})", key=f"reabrir_{p['id']}"):
                            st.session_state.carrinho_atual = dict(p['itens'])
                            st.session_state.toalhas_vinculadas = dict(p.get('toalhas', {}))
                            st.session_state.pedido_edicao_id = p['id']
                            tocar_som("click")
                            st.success("Pedido reaberto com sucesso! Vá para a aba 'Catálogo de Materiais' ou 'Finalizar Orçamento' para ajustar o pedido.")
                            st.rerun()

# ==========================================
# ⚙️ PAINEL ADMINISTRATIVO (HOMOLOGAÇÃO)
# ==========================================
else:
    st.header("⚙️ Painel da Renascer Locações — Homologação de Estoque")
    senha = st.text_input("Senha do Painel", type="password")
    
    if senha == "1234":
        st.subheader("📊 Pedidos para Validação & Homologação de Disponibilidade")
        if not st.session_state.pedidos_standby:
            st.info("Nenhum pedido cadastrado no momento.")
        else:
            for p in st.session_state.pedidos_standby:
                with st.container():
                    st.markdown(f"### Pedido #{p['id']} — {p['evento']} ({p['cliente']['nome']})")
                    st.write(f"**Data da Festa:** {p['data']} | **Telefone:** {p['cliente']['telefone']}")
                    st.write(f"**Local:** {p['endereco']}")
                    st.write(f"**Valor Total:** R$ {p['total']:.2f} (Frete: R$ {p['frete']:.2f})")
                    st.write(f"**Status Atual:** `{p['status']}`")
                    
                    col_h1, col_h2 = st.columns(2)
                    with col_h1:
                        if st.button(f"✅ Homologar e Confirmar Estoque (ID #{p['id']})", key=f"btn_homo_{p['id']}"):
                            p['status'] = "Homologado (Disponibilidade Confirmada)"
                            p['alerta_tocado'] = False
                            tocar_som("sucesso")
                            st.success("Pedido Homologado! O cliente será notificado no aplicativo.")
                            st.rerun()
                    with col_h2:
                        if st.button(f"❌ Indisponível para esta Data (ID #{p['id']})", key=f"btn_rec_{p['id']}"):
                            p['status'] = "Indisponível (Sem Estoque para a Data)"
                            st.error("Status atualizado para indisponível.")
                            st.rerun()
                    st.divider()
