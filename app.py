import streamlit as st
import pandas as pd
import urllib.parse

# Configuração da página para navegação em celulares
st.set_page_config(
    page_title="Renascer Locações",
    page_icon="🎉",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- BASE DE DADOS COMPLETA DO SISTEMA ---
if 'catalogo' not in st.session_state:
    st.session_state.catalogo = [
        # MOBILIÁRIO & MESAS
        {"id": 1, "categoria": "Mobiliário & Mesas", "nome": "Jogo de Mesa com 4 Cadeiras de Plástico (Branca)", "preco": 14.00, "estoque": 50, "foto": "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=300", "tags": ["rustico", "piscina", "infantil"]},
        {"id": 2, "categoria": "Mobiliário & Mesas", "nome": "Mesa Redonda de 6 Lugares (com tampão de madeira)", "preco": 18.00, "estoque": 20, "foto": "https://images.unsplash.com/photo-1530018607912-eff2daa1bac4?w=300", "tags": ["rustico", "elegante"]},
        {"id": 3, "categoria": "Mobiliário & Mesas", "nome": "Mesa Redonda de 7 Lugares (com tampão de madeira)", "preco": 20.00, "estoque": 20, "foto": "https://images.unsplash.com/photo-1530018607912-eff2daa1bac4?w=300", "tags": ["rustico", "elegante"]},
        {"id": 4, "categoria": "Mobiliário & Mesas", "nome": "Aparador de Madeira (2,50m x 0,80m)", "preco": 25.00, "estoque": 5, "foto": "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=300", "tags": ["rustico", "elegante"]},
        {"id": 36, "categoria": "Mobiliário & Mesas", "nome": "Tampão de Madeira C/ Cavalete", "preco": 10.00, "estoque": 50, "foto": "https://images.unsplash.com/photo-1530018607912-eff2daa1bac4?w=300", "tags": ["rustico"]},
        {"id": 34, "categoria": "Mobiliário & Mesas", "nome": "Cadeira de plástico branca", "preco": 3.00, "estoque": 20000, "foto": "https://images.unsplash.com/photo-1503602642458-232111445657?w=300", "tags": ["piscina", "infantil", "rustico"]},
        {"id": 43, "categoria": "Mobiliário & Mesas", "nome": "Somente Mesa / Sem Cadeiras", "preco": 8.00, "estoque": 600, "foto": "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=300", "tags": ["piscina", "rustico"]},

        # LOUÇAS, TALHERES & COPOS
        {"id": 8, "categoria": "Louças, Talheres & Copos", "nome": "Prato de jantar raso branco liso", "preco": 0.80, "estoque": 300, "foto": "https://images.unsplash.com/photo-1610701596007-11502861dcfa?w=300", "tags": ["elegante", "rustico"]},
        {"id": 22, "categoria": "Louças, Talheres & Copos", "nome": "Prato de jantar raso Branco Detalhado", "preco": 0.80, "estoque": 300, "foto": "https://images.unsplash.com/photo-1610701596007-11502861dcfa?w=300", "tags": ["elegante"]},
        {"id": 28, "categoria": "Louças, Talheres & Copos", "nome": "Prato de Sobremesa Branco", "preco": 0.80, "estoque": 300, "foto": "https://images.unsplash.com/photo-1610701596007-11502861dcfa?w=300", "tags": ["elegante", "infantil"]},
        {"id": 9, "categoria": "Louças, Talheres & Copos", "nome": "Copo Tradicional", "preco": 0.80, "estoque": 300, "foto": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=300", "tags": ["piscina", "rustico"]},
        {"id": 10, "categoria": "Louças, Talheres & Copos", "nome": "Taça para Água", "preco": 1.00, "estoque": 200, "foto": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=300", "tags": ["elegante", "rustico"]},
        {"id": 11, "categoria": "Louças, Talheres & Copos", "nome": "Taça Colorida", "preco": 1.50, "estoque": 150, "foto": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=300", "tags": ["piscina", "infantil"]},
        {"id": 25, "categoria": "Louças, Talheres & Copos", "nome": "Taça Colorida Azul", "preco": 1.50, "estoque": 170, "foto": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=300", "tags": ["piscina", "infantil"]},
        {"id": 26, "categoria": "Louças, Talheres & Copos", "nome": "Taça Colorida Dourada", "preco": 1.50, "estoque": 170, "foto": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=300", "tags": ["elegante"]},
        {"id": 23, "categoria": "Louças, Talheres & Copos", "nome": "Taça Colorida Rosé", "preco": 1.50, "estoque": 170, "foto": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=300", "tags": ["elegante"]},
        {"id": 27, "categoria": "Louças, Talheres & Copos", "nome": "Taça Colorida Transparente", "preco": 1.50, "estoque": 170, "foto": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=300", "tags": ["elegante", "rustico"]},
        {"id": 24, "categoria": "Louças, Talheres & Copos", "nome": "Taça Colorida Verde", "preco": 1.50, "estoque": 170, "foto": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=300", "tags": ["rustico", "piscina"]},

        # PRATARIA
        {"id": 29, "categoria": "Prataria", "nome": "Garfo de jantar", "preco": 0.80, "estoque": 300, "foto": "https://images.unsplash.com/photo-1584345604476-8ec5e12e42dd?w=300", "tags": ["elegante", "rustico"]},
        {"id": 30, "categoria": "Prataria", "nome": "Faca de jantar", "preco": 0.80, "estoque": 300, "foto": "https://images.unsplash.com/photo-1584345604476-8ec5e12e42dd?w=300", "tags": ["elegante", "rustico"]},
        {"id": 32, "categoria": "Prataria", "nome": "Garfo de Sobremesa", "preco": 0.80, "estoque": 300, "foto": "https://images.unsplash.com/photo-1584345604476-8ec5e12e42dd?w=300", "tags": ["elegante"]},
        {"id": 35, "categoria": "Prataria", "nome": "Faca de sobremesa", "preco": 0.80, "estoque": 200, "foto": "https://images.unsplash.com/photo-1584345604476-8ec5e12e42dd?w=300", "tags": ["elegante"]},
        {"id": 31, "categoria": "Prataria", "nome": "Colher de sobremesa", "preco": 0.80, "estoque": 300, "foto": "https://images.unsplash.com/photo-1584345604476-8ec5e12e42dd?w=300", "tags": ["elegante"]},

        # SERVIÇO & RICHAUDS
        {"id": 12, "categoria": "Serviço & Richauds", "nome": "Richaud Redondo", "preco": 25.00, "estoque": 10, "foto": "https://images.unsplash.com/photo-1555244162-803834f70033?w=300", "tags": ["elegante", "rustico"]},
        {"id": 13, "categoria": "Serviço & Richauds", "nome": "Richaud Quadrado 9 Litros", "preco": 40.00, "estoque": 10, "foto": "https://images.unsplash.com/photo-1555244162-803834f70033?w=300", "tags": ["elegante"]},
        {"id": 14, "categoria": "Serviço & Richauds", "nome": "Bandeja Oval Média", "preco": 10.00, "estoque": 15, "foto": "https://images.unsplash.com/photo-1555244162-803834f70033?w=300", "tags": ["elegante"]},
        {"id": 15, "categoria": "Serviço & Richauds", "nome": "Bandeja Oval Grande", "preco": 15.00, "estoque": 15, "foto": "https://images.unsplash.com/photo-1555244162-803834f70033?w=300", "tags": ["elegante"]},
        {"id": 16, "categoria": "Serviço & Richauds", "nome": "Bandeja para Garçom", "preco": 10.00, "estoque": 10, "foto": "https://images.unsplash.com/photo-1555244162-803834f70033?w=300", "tags": ["elegante"]},
        {"id": 17, "categoria": "Serviço & Richauds", "nome": "Pegador / Colher para Arroz ou Feijão Tropeiro", "preco": 7.00, "estoque": 20, "foto": "https://images.unsplash.com/photo-1584345604476-8ec5e12e42dd?w=300", "tags": ["rustico", "elegante"]},
        {"id": 18, "categoria": "Serviço & Richauds", "nome": "Jarra em Inox", "preco": 10.00, "estoque": 15, "foto": "https://images.unsplash.com/photo-1555244162-803834f70033?w=300", "tags": ["elegante", "rustico"]},
        {"id": 19, "categoria": "Serviço & Richauds", "nome": "Lixeira Redonda 7 Litros", "preco": 25.00, "estoque": 10, "foto": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=300", "tags": ["piscina", "rustico"]},
        {"id": 38, "categoria": "Serviço & Richauds", "nome": "Rishalds", "preco": 25.00, "estoque": 9, "foto": "https://images.unsplash.com/photo-1555244162-803834f70033?w=300", "tags": ["elegante"]},

        # TOALHAS & ENXOVAL
        {"id": 5, "categoria": "Toalhas & Enxoval", "nome": "Toalha Quadrada para 4 Lugares (1,50m x 1,50m)", "preco": 6.00, "estoque": 100, "foto": "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=300", "tags": ["rustico", "piscina"]},
        {"id": 6, "categoria": "Toalhas & Enxoval", "nome": "Toalha Redonda para 6 e 7 Lugares (Cor Lisa)", "preco": 12.00, "estoque": 80, "foto": "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=300", "tags": ["elegante"]},
        {"id": 7, "categoria": "Toalhas & Enxoval", "nome": "Toalha para Aparador", "preco": 25.00, "estoque": 10, "foto": "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=300", "tags": ["elegante", "rustico"]},
        {"id": 37, "categoria": "Toalhas & Enxoval", "nome": "Toalha redonda Vermelho Adasmascado", "preco": 14.00, "estoque": 20, "foto": "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=300", "tags": ["elegante"]},
        {"id": 39, "categoria": "Toalhas & Enxoval", "nome": "Toalha Palha Adamascado Redondo", "preco": 14.00, "estoque": 40, "foto": "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=300", "tags": ["elegante", "rustico"]},
        {"id": 42, "categoria": "Toalhas & Enxoval", "nome": "Toalha Quadrada Verde Escuro", "preco": 6.00, "estoque": 50, "foto": "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=300", "tags": ["piscina", "rustico"]},
        {"id": 33, "categoria": "Toalhas & Enxoval", "nome": "Guardanapos", "preco": 1.00, "estoque": 1000, "foto": "https://images.unsplash.com/photo-1584345604476-8ec5e12e42dd?w=300", "tags": ["elegante"]},

        # EQUIPAMENTOS
        {"id": 20, "categoria": "Equipamento", "nome": "Freezer Horizontal Branca 2 Tampas (400 Litros)", "preco": 200.00, "estoque": 1, "foto": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=300", "tags": ["piscina", "rustico"]},
        {"id": 21, "categoria": "Equipamento", "nome": "Freezer Horizontal Branca 2 Tampas (500 Litros)", "preco": 250.00, "estoque": 2, "foto": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=300", "tags": ["piscina", "rustico"]},
        {"id": 40, "categoria": "Equipamento", "nome": "Baldinho de Acrílico", "preco": 15.00, "estoque": 4, "foto": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=300", "tags": ["piscina"]},
        {"id": 41, "categoria": "Equipamento", "nome": "Champanheira", "preco": 30.00, "estoque": 3, "foto": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=300", "tags": ["elegante", "piscina"]}
    ]

if 'clientes' not in st.session_state:
    st.session_state.clientes = []

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = {}

if 'promocao' not in st.session_state:
    st.session_state.promocao = "🔥 Promoção do Mês: Desconto especial para eventos completos com louças e mesas!"

# --- MUDANÇA DINÂMICA DE APARÊNCIA E PLANO DE FUNDO VIA CSS ---
def aplicar_tema_dinamico(ambiente):
    temas = {
        "Rústico": {
            "bg_url": "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?auto=format&fit=crop&w=1200&q=80",
            "primary": "#8B4513",
            "card_bg": "rgba(255, 248, 239, 0.92)",
            "text": "#3E2723"
        },
        "Casa com Piscina": {
            "bg_url": "https://images.unsplash.com/photo-1576013551627-0cc20b96c2a7?auto=format&fit=crop&w=1200&q=80",
            "primary": "#008080",
            "card_bg": "rgba(240, 253, 255, 0.92)",
            "text": "#004D40"
        },
        "Casamento / Elegante": {
            "bg_url": "https://images.unsplash.com/photo-1519225421980-715cb0215aed?auto=format&fit=crop&w=1200&q=80",
            "primary": "#D4AF37",
            "card_bg": "rgba(255, 255, 255, 0.94)",
            "text": "#2C2C2C"
        },
        "Festa Infantil": {
            "bg_url": "https://images.unsplash.com/photo-1530103862676-de8c9debad1d?auto=format&fit=crop&w=1200&q=80",
            "primary": "#FF69B4",
            "card_bg": "rgba(255, 240, 245, 0.94)",
            "text": "#4A148C"
        }
    }
    
    t = temas.get(ambiente, {
        "bg_url": "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?auto=format&fit=crop&w=1200&q=80",
        "primary": "#1E3A8A",
        "card_bg": "rgba(255, 255, 255, 0.92)",
        "text": "#1E293B"
    })

    css = f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(0,0,0,0.35), rgba(0,0,0,0.35)), url("{t['bg_url']}");
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
        color: {t['text']};
    }}
    .stMarkdown, .stText, h1, h2, h3, h4, label {{
        color: {t['text']} !important;
    }}
    div[data-testid="stVerticalBlock"] > div {{
        background-color: {t['card_bg']};
        border-radius: 12px;
        padding: 8px 14px;
        margin-bottom: 8px;
    }}
    button[kind="primary"] {{
        background-color: {t['primary']} !important;
        border: none !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# --- MÓDULO DE RECOMENDAÇÃO DE ACORDO COM O TEMA ---
def recomendar_combinacao(ambiente_selecionado, carrinho_atual):
    mapa_tags = {
        "Rústico": "rustico",
        "Casa com Piscina": "piscina",
        "Casamento / Elegante": "elegante",
        "Festa Infantil": "infantil"
    }
    tag_busca = mapa_tags.get(ambiente_selecionado, "rustico")
    recomendacoes = [item for item in st.session_state.catalogo if tag_busca in item['tags'] and item['id'] not in carrinho_atual]
    return recomendacoes

# --- TÍTULO E NAVEGAÇÃO ---
st.title("🎉 Renascer Locações")

modo = st.sidebar.radio("Modo de Acesso", ["Área do Cliente", "Painel Administrativo"])

# ==========================================
# 📱 ÁREA DO CLIENTE
# ==========================================
if modo == "Área do Cliente":
    
    # Aplica o tema visual conforme seleção anterior
    ambiente_salvo = st.session_state.get('cliente_atual', {}).get('ambiente', 'Outro')
    aplicar_tema_dinamico(ambiente_salvo)

    if st.session_state.promocao:
        st.info(f"📢 **COMUNICADO:** {st.session_state.promocao}")

    # ETAPA 1: Cadastro dos Dados Pessoais e Escolha do Estilo
    st.header("1. Seus Dados & Estilo do Evento")
    with st.form("form_cliente"):
        nome = st.text_input("Nome Completo*")
        telefone = st.text_input("Telefone / WhatsApp*")
        endereco = st.text_input("Endereço / Localização do Evento*")
        data_evento = st.date_input("Data do Evento")
        
        ambiente = st.selectbox(
            "Selecione o Estilo do Evento (Muda a aparência do App!):",
            ["Selecione...", "Rústico", "Casa com Piscina", "Casamento / Elegante", "Festa Infantil", "Outro"]
        )
        
        btn_passo1 = st.form_submit_button("Avançar para Catálogo ➔")
        
        if btn_passo1:
            if nome and telefone and endereco:
                st.session_state.cliente_atual = {
                    "nome": nome,
                    "telefone": telefone,
                    "endereco": endereco,
                    "data": str(data_evento),
                    "ambiente": ambiente
                }
                st.session_state.clientes.append(st.session_state.cliente_atual)
                st.success("Dados salvos e visual personalizado! Escolha os materiais abaixo.")
                st.rerun()
            else:
                st.error("Preencha todos os campos obrigatórios (*).")

    # ETAPA 2: Escolha dos Produtos no Catálogo
    st.header("2. Seleção de Materiais")
    
    # Recomendações da IA de acordo com o Ambiente
    if 'cliente_atual' in st.session_state and st.session_state.cliente_atual.get('ambiente') != "Selecione...":
        env = st.session_state.cliente_atual['ambiente']
        sugestoes = recomendar_combinacao(env, st.session_state.carrinho)
        if sugestoes:
            st.markdown(f"💡 **Sugestões Especiais para o Estilo ({env}):**")
            cols_sug = st.columns(min(len(sugestoes), 3))
            for idx, item in enumerate(sugestoes[:3]):
                with cols_sug[idx]:
                    st.caption(f"**{item['nome']}**")
                    st.write(f"R$ {item['preco']:.2f}")

    # Filtro de Categoria
    categorias = ["Todas"] + list(set([item['categoria'] for item in st.session_state.catalogo]))
    cat_selecionada = st.selectbox("Filtrar Categoria de Materiais:", categorias)

    # Lista de Produtos
    produtos_exibidos = st.session_state.catalogo if cat_selecionada == "Todas" else [i for i in st.session_state.catalogo if i['categoria'] == cat_selecionada]

    for item in produtos_exibidos:
        with st.container():
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(item['foto'], use_container_width=True)
            with col2:
                st.subheader(item['nome'])
                st.caption(f"Categoria: {item['categoria']} | Disponível: {item['estoque']}")
                st.write(f"**Valor un.:** R$ {item['preco']:.2f}")
                qtd = st.number_input(
                    f"Quantidade",
                    min_value=0,
                    max_value=item['estoque'],
                    value=st.session_state.carrinho.get(item['id'], 0),
                    key=f"item_{item['id']}"
                )
                if qtd > 0:
                    st.session_state.carrinho[item['id']] = qtd
                elif item['id'] in st.session_state.carrinho and qtd == 0:
                    del st.session_state.carrinho[item['id']]
            st.divider()

    # ETAPA 3: Fechamento e Envio para WhatsApp Business
    st.header("3. Orçamento Completo")
    
    if st.session_state.carrinho:
        total_geral = 0
        resumo_texto = "📋 *NOVO PEDIDO DE ORÇAMENTO - RENASCER LOCAÇÕES*\n\n"
        
        if 'cliente_atual' in st.session_state:
            cli = st.session_state.cliente_atual
            resumo_texto += f"*Cliente:* {cli['nome']}\n"
            resumo_texto += f"*Telefone:* {cli['telefone']}\n"
            resumo_texto += f"*Endereço:* {cli['endereco']}\n"
            resumo_texto += f"*Data:* {cli['data']}\n"
            resumo_texto += f"*Estilo do Evento:* {cli['ambiente']}\n\n"
        
        resumo_texto += "*Materiais Selecionados:*\n"
        
        for item_id, qtd in st.session_state.carrinho.items():
            produto = next(i for i in st.session_state.catalogo if i['id'] == item_id)
            subtotal = produto['preco'] * qtd
            total_geral += subtotal
            resumo_texto += f"- {qtd}x {produto['nome']} (R$ {subtotal:.2f})\n"
            st.write(f"• **{qtd}x {produto['nome']}** — R$ {subtotal:.2f}")

        resumo_texto += f"\n*VALOR TOTAL ESTIMADO:* R$ {total_geral:.2f}"
        st.markdown(f"### **Total Geral: R$ {total_geral:.2f}**")

        opcao_reserva = st.radio("Status do Pedido:", ["Reservar materiais para o evento", "Apenas guardar orçamento"])
        resumo_texto += f"\n*Status:* {opcao_reserva}"

        # NÚMERO DO SEU WHATSAPP BUSINESS:
        numero_whatsapp = "556298224034"
        
        mensagem_encoded = urllib.parse.quote(resumo_texto)
        link_whatsapp = f"https://wa.me/{numero_whatsapp}?text={mensagem_encoded}"

        st.markdown(f"""
            <a href="{link_whatsapp}" target="_blank">
                <button style="background-color:#25D366; color:white; border:none; padding:16px; font-size:18px; border-radius:10px; width:100%; font-weight:bold; cursor:pointer;">
                    📲 Enviar Orçamento para o WhatsApp Business
                </button>
            </a>
        """, unsafe_allow_html=True)
    else:
        st.info("Nenhum material selecionado no carrinho.")

# ==========================================
# ⚙️ PAINEL ADMINISTRATIVO (SEU CONTROLE)
# ==========================================
else:
    st.header("⚙️ Painel de Controle - Renascer Locações")
    
    senha = st.text_input("Senha de Acesso", type="password")
    if senha == "1234":
        
        # 1. Gerenciador de Catálogo
        st.subheader("📦 Materiais Cadastrados no Catálogo")
        st.dataframe(pd.DataFrame(st.session_state.catalogo)[['id', 'categoria', 'nome', 'preco', 'estoque']])

        # 2. Cadastro de Novos Itens
        st.subheader("➕ Adicionar Novo Item")
        with st.form("add_material"):
            novo_nome = st.text_input("Nome do Material")
            nova_cat = st.selectbox("Categoria", ["Mobiliário & Mesas", "Louças, Talheres & Copos", "Prataria", "Serviço & Richauds", "Toalhas & Enxoval", "Equipamento"])
            novo_preco = st.number_input("Preço de Locação (R$)", min_value=0.0, step=0.50)
            novo_estoque = st.number_input("Quantidade em Estoque", min_value=1, step=1)
            nova_foto = st.text_input("URL da Foto", value="https://via.placeholder.com/150")
            tags = st.multiselect("Tags de Estilo", ["rustico", "piscina", "elegante", "infantil"])
            
            if st.form_submit_button("Salvar Item"):
                novo_id = max([i['id'] for i in st.session_state.catalogo]) + 1 if st.session_state.catalogo else 1
                st.session_state.catalogo.append({
                    "id": novo_id, "categoria": nova_cat, "nome": novo_nome, "preco": novo_preco, "estoque": novo_estoque, "foto": nova_foto, "tags": tags
                })
                st.success(f"Item '{novo_nome}' adicionado com sucesso!")
                st.rerun()

        # 3. Comunicado / Promoção
        st.subheader("📢 Atualizar Mensagem Promocional")
        nova_promo = st.text_area("Texto do Comunicado", value=st.session_state.promocao)
        if st.button("Atualizar Comunicado"):
            st.session_state.promocao = nova_promo
            st.success("Mensagem atualizada com sucesso!")

        # 4. Cadastro de Clientes
        st.subheader("👥 Clientes Cadastrados nesta Sessão")
        if st.session_state.clientes:
            st.dataframe(pd.DataFrame(st.session_state.clientes))
        else:
            st.info("Nenhum cliente cadastrado ainda.")
