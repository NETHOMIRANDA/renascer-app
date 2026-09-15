import streamlit as st
import pandas as pd
import urllib.parse

# Configuração da página
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
        {"id": 1, "categoria": "Mobiliário & Mesas", "nome": "Jogo de Mesa com 4 Cadeiras de Plástico (Branca)", "preco": 14.00, "estoque": 50, "foto": "https://via.placeholder.com/300?text=Jogo+Mesa+Plastico", "tags": ["rustico", "piscina", "infantil"]},
        {"id": 2, "categoria": "Mobiliário & Mesas", "nome": "Mesa Redonda de 6 Lugares (com tampão de madeira)", "preco": 18.00, "estoque": 20, "foto": "https://via.placeholder.com/300?text=Mesa+Redonda+6L", "tags": ["rustico", "elegante"]},
        {"id": 3, "categoria": "Mobiliário & Mesas", "nome": "Mesa Redonda de 7 Lugares (com tampão de madeira)", "preco": 20.00, "estoque": 20, "foto": "https://via.placeholder.com/300?text=Mesa+Redonda+7L", "tags": ["rustico", "elegante"]},
        {"id": 4, "categoria": "Mobiliário & Mesas", "nome": "Aparador de Madeira (2,50m x 0,80m)", "preco": 25.00, "estoque": 5, "foto": "https://via.placeholder.com/300?text=Aparador+Madeira", "tags": ["rustico", "elegante"]},
        {"id": 36, "categoria": "Mobiliário & Mesas", "nome": "Tampão de Madeira C/ Cavalete", "preco": 10.00, "estoque": 50, "foto": "https://via.placeholder.com/300?text=Tampao+Cavalete", "tags": ["rustico"]},
        {"id": 34, "categoria": "Mobiliário & Mesas", "nome": "Cadeira de plástico branca", "preco": 3.00, "estoque": 20000, "foto": "https://via.placeholder.com/300?text=Cadeira+Plastico", "tags": ["piscina", "infantil", "rustico"]},
        {"id": 43, "categoria": "Mobiliário & Mesas", "nome": "Somente Mesa / Sem Cadeiras", "preco": 8.00, "estoque": 600, "foto": "https://via.placeholder.com/300?text=Somente+Mesa", "tags": ["piscina", "rustico"]},

        # LOUÇAS, TALHERES & COPOS
        {"id": 8, "categoria": "Louças & Copos", "nome": "Prato de jantar raso branco liso", "preco": 0.80, "estoque": 300, "foto": "https://via.placeholder.com/300?text=Prato+Branco+Liso", "tags": ["elegante", "rustico"]},
        {"id": 22, "categoria": "Louças & Copos", "nome": "Prato de jantar raso Branco Detalhado", "preco": 0.80, "estoque": 300, "foto": "https://via.placeholder.com/300?text=Prato+Branco+Detalhado", "tags": ["elegante"]},
        {"id": 28, "categoria": "Louças & Copos", "nome": "Prato de Sobremesa Branco", "preco": 0.80, "estoque": 300, "foto": "https://via.placeholder.com/300?text=Prato+Sobremesa", "tags": ["elegante", "infantil"]},
        {"id": 9, "categoria": "Louças & Copos", "nome": "Copo Tradicional", "preco": 0.80, "estoque": 300, "foto": "https://via.placeholder.com/300?text=Copo+Tradicional", "tags": ["piscina", "rustico"]},
        {"id": 10, "categoria": "Louças & Copos", "nome": "Taça para Água", "preco": 1.00, "estoque": 200, "foto": "https://via.placeholder.com/300?text=Taca+Agua", "tags": ["elegante", "rustico"]},
        {"id": 11, "categoria": "Louças & Copos", "nome": "Taça Colorida", "preco": 1.50, "estoque": 150, "foto": "https://via.placeholder.com/300?text=Taca+Colorida", "tags": ["piscina", "infantil"]},
        {"id": 25, "categoria": "Louças & Copos", "nome": "Taça Colorida Azul", "preco": 1.50, "estoque": 170, "foto": "https://via.placeholder.com/300?text=Taca+Azul", "tags": ["piscina", "infantil"]},
        {"id": 26, "categoria": "Louças & Copos", "nome": "Taça Colorida Dourada", "preco": 1.50, "estoque": 170, "foto": "https://via.placeholder.com/300?text=Taca+Dourada", "tags": ["elegante"]},
        {"id": 23, "categoria": "Louças & Copos", "nome": "Taça Colorida Rosé", "preco": 1.50, "estoque": 170, "foto": "https://via.placeholder.com/300?text=Taca+Rose", "tags": ["elegante"]},
        {"id": 27, "categoria": "Louças & Copos", "nome": "Taça Colorida Transparente", "preco": 1.50, "estoque": 170, "foto": "https://via.placeholder.com/300?text=Taca+Transparente", "tags": ["elegante", "rustico"]},
        {"id": 24, "categoria": "Louças & Copos", "nome": "Taça Colorida Verde", "preco": 1.50, "estoque": 170, "foto": "https://via.placeholder.com/300?text=Taca+Verde", "tags": ["rustico", "piscina"]},

        # PRATARIA
        {"id": 29, "categoria": "Prataria & Talheres", "nome": "Garfo de jantar", "preco": 0.80, "estoque": 300, "foto": "https://via.placeholder.com/300?text=Garfo+Jantar", "tags": ["elegante", "rustico"]},
        {"id": 30, "categoria": "Prataria & Talheres", "nome": "Faca de jantar", "preco": 0.80, "estoque": 300, "foto": "https://via.placeholder.com/300?text=Faca+Jantar", "tags": ["elegante", "rustico"]},
        {"id": 32, "categoria": "Prataria & Talheres", "nome": "Garfo de Sobremesa", "preco": 0.80, "estoque": 300, "foto": "https://via.placeholder.com/300?text=Garfo+Sobremesa", "tags": ["elegante"]},
        {"id": 35, "categoria": "Prataria & Talheres", "nome": "Faca de sobremesa", "preco": 0.80, "estoque": 200, "foto": "https://via.placeholder.com/300?text=Faca+Sobremesa", "tags": ["elegante"]},
        {"id": 31, "categoria": "Prataria & Talheres", "nome": "Colher de sobremesa", "preco": 0.80, "estoque": 300, "foto": "https://via.placeholder.com/300?text=Colher+Sobremesa", "tags": ["elegante"]},

        # SERVIÇO & RICHAUDS
        {"id": 12, "categoria": "Serviço & Rechauds", "nome": "Richaud Redondo", "preco": 25.00, "estoque": 10, "foto": "https://via.placeholder.com/300?text=Rechaud+Redondo", "tags": ["elegante", "rustico"]},
        {"id": 13, "categoria": "Serviço & Rechauds", "nome": "Richaud Quadrado 9 Litros", "preco": 40.00, "estoque": 10, "foto": "https://via.placeholder.com/300?text=Rechaud+Quadrado", "tags": ["elegante"]},
        {"id": 14, "categoria": "Serviço & Rechauds", "nome": "Bandeja Oval Média", "preco": 10.00, "estoque": 15, "foto": "https://via.placeholder.com/300?text=Bandeja+Media", "tags": ["elegante"]},
        {"id": 15, "categoria": "Serviço & Rechauds", "nome": "Bandeja Oval Grande", "preco": 15.00, "estoque": 15, "foto": "https://via.placeholder.com/300?text=Bandeja+Grande", "tags": ["elegante"]},
        {"id": 16, "categoria": "Serviço & Rechauds", "nome": "Bandeja para Garçom", "preco": 10.00, "estoque": 10, "foto": "https://via.placeholder.com/300?text=Bandeja+Garcom", "tags": ["elegante"]},
        {"id": 17, "categoria": "Serviço & Rechauds", "nome": "Pegador / Colher para Arroz ou Feijão Tropeiro", "preco": 7.00, "estoque": 20, "foto": "https://via.placeholder.com/300?text=Pegador+Servico", "tags": ["rustico", "elegante"]},
        {"id": 18, "categoria": "Serviço & Rechauds", "nome": "Jarra em Inox", "preco": 10.00, "estoque": 15, "foto": "https://via.placeholder.com/300?text=Jarra+Inox", "tags": ["elegante", "rustico"]},
        {"id": 19, "categoria": "Serviço & Rechauds", "nome": "Lixeira Redonda 7 Litros", "preco": 25.00, "estoque": 10, "foto": "https://via.placeholder.com/300?text=Lixeira+Inox", "tags": ["piscina", "rustico"]},

        # TOALHAS & ENXOVAL
        {"id": 5, "categoria": "Toalhas & Linha de Mesa", "nome": "Toalha Quadrada para 4 Lugares (1,50m x 1,50m)", "preco": 6.00, "estoque": 100, "foto": "https://via.placeholder.com/300?text=Toalha+4+Lugares", "tags": ["rustico", "piscina"]},
        {"id": 6, "categoria": "Toalhas & Linha de Mesa", "nome": "Toalha Redonda para 6 e 7 Lugares (Cor Lisa)", "preco": 12.00, "estoque": 80, "foto": "https://via.placeholder.com/300?text=Toalha+Redonda+Lisa", "tags": ["elegante"]},
        {"id": 7, "categoria": "Toalhas & Linha de Mesa", "nome": "Toalha para Aparador", "preco": 25.00, "estoque": 10, "foto": "https://via.placeholder.com/300?text=Toalha+Aparador", "tags": ["elegante", "rustico"]},
        {"id": 37, "categoria": "Toalhas & Linha de Mesa", "nome": "Toalha redonda Vermelho Adamascado", "preco": 14.00, "estoque": 20, "foto": "https://via.placeholder.com/300?text=Toalha+Vermelha", "tags": ["elegante"]},
        {"id": 39, "categoria": "Toalhas & Linha de Mesa", "nome": "Toalha Palha Adamascado Redondo", "preco": 14.00, "estoque": 40, "foto": "https://via.placeholder.com/300?text=Toalha+Palha", "tags": ["elegante", "rustico"]},
        {"id": 42, "categoria": "Toalhas & Linha de Mesa", "nome": "Toalha Quadrada Verde Escuro", "preco": 6.00, "estoque": 50, "foto": "https://via.placeholder.com/300?text=Toalha+Verde", "tags": ["piscina", "rustico"]},
        {"id": 33, "categoria": "Toalhas & Linha de Mesa", "nome": "Guardanapos", "preco": 1.00, "estoque": 1000, "foto": "https://via.placeholder.com/300?text=Guardanapos", "tags": ["elegante"]},

        # EQUIPAMENTOS & FREEZERS
        {"id": 20, "categoria": "Equipamentos & Freezers", "nome": "Freezer Horizontal Branca 2 Tampas (400 Litros)", "preco": 200.00, "estoque": 1, "foto": "https://via.placeholder.com/300?text=Freezer+400L", "tags": ["piscina", "rustico"]},
        {"id": 21, "categoria": "Equipamentos & Freezers", "nome": "Freezer Horizontal Branca 2 Tampas (500 Litros)", "preco": 250.00, "estoque": 2, "foto": "https://via.placeholder.com/300?text=Freezer+500L", "tags": ["piscina", "rustico"]},
        {"id": 40, "categoria": "Equipamentos & Freezers", "nome": "Baldinho de Acrílico", "preco": 15.00, "estoque": 4, "foto": "https://via.placeholder.com/300?text=Baldinho+Acrilico", "tags": ["piscina"]},
        {"id": 41, "categoria": "Equipamentos & Freezers", "nome": "Champanheira", "preco": 30.00, "estoque": 3, "foto": "https://via.placeholder.com/300?text=Champanheira", "tags": ["elegante", "piscina"]}
    ]

if 'clientes' not in st.session_state:
    st.session_state.clientes = []

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = {}

if 'promocao' not in st.session_state:
    st.session_state.promocao = "⚡ Garanta 10% OFF fechando e confirmando o seu pedido hoje!"

# --- MUDANÇA DINÂMICA DE APARÊNCIA E PLANO DE FUNDO VIA CSS ---
def aplicar_tema_dinamico(ambiente):
    temas = {
        "Rústico": {
            "bg_url": "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?auto=format&fit=crop&w=1200&q=80",
            "primary": "#8B4513",
            "card_bg": "rgba(255, 248, 239, 0.94)",
            "text": "#3E2723"
        },
        "Casa com Piscina": {
            "bg_url": "https://images.unsplash.com/photo-1576013551627-0cc20b96c2a7?auto=format&fit=crop&w=1200&q=80",
            "primary": "#008080",
            "card_bg": "rgba(240, 253, 255, 0.94)",
            "text": "#004D40"
        },
        "Casamento / Elegante": {
            "bg_url": "https://images.unsplash.com/photo-1519225421980-715cb0215aed?auto=format&fit=crop&w=1200&q=80",
            "primary": "#D4AF37",
            "card_bg": "rgba(255, 255, 255, 0.95)",
            "text": "#2C2C2C"
        },
        "Festa Infantil": {
            "bg_url": "https://images.unsplash.com/photo-1530103862676-de8c9debad1d?auto=format&fit=crop&w=1200&q=80",
            "primary": "#FF69B4",
            "card_bg": "rgba(255, 240, 245, 0.95)",
            "text": "#4A148C"
        }
    }
    
    t = temas.get(ambiente, {
        "bg_url": "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?auto=format&fit=crop&w=1200&q=80",
        "primary": "#1E3A8A",
        "card_bg": "rgba(255, 255, 255, 0.94)",
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
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
st.title("🎉 Renascer Locações")
modo = st.sidebar.radio("Modo de Acesso", ["Área do Cliente", "Painel Administrativo"])

# ==========================================
# 📱 ÁREA DO CLIENTE
# ==========================================
if modo == "Área do Cliente":
    
    ambiente_salvo = st.session_state.get('cliente_atual', {}).get('ambiente', 'Outro')
    aplicar_tema_dinamico(ambiente_salvo)

    if st.session_state.promocao:
        st.info(f"📢 {st.session_state.promocao}")

    # 1. DADOS E TEMA DO EVENTO
    st.header("1. Seus Dados & Tema do Evento")
    with st.form("form_cliente"):
        nome = st.text_input("Seu Nome Completo*")
        telefone = st.text_input("WhatsApp / Telefone*")
        endereco = st.text_input("Endereço do Evento*")
        data_evento = st.date_input("Data do Evento")
        
        ambiente = st.selectbox(
            "Escolha o Tema do seu Evento (Muda o visual!):",
            ["Selecione...", "Rústico", "Casa com Piscina", "Casamento / Elegante", "Festa Infantil", "Outro"]
        )
        
        btn_passo1 = st.form_submit_button("Confirmar Dados e Escolher Materiais ➔")
        
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
                st.success("Dados Salvos com Sucesso!")
                st.rerun()
            else:
                st.error("Por favor, preencha nome, WhatsApp e endereço.")

    # 2. SELEÇÃO DE MATERIAIS
    st.header("2. Escolha os Materiais")
    
    # Campo de busca direta
    busca = st.text_input("🔍 Digite o nome do item que procura (ex: Mesa, Taça, Rechaud, Freezer):")
    
    # Filtro simplificado por categoria
    categorias = ["Todos os Materiais"] + list(dict.fromkeys([item['categoria'] for item in st.session_state.catalogo]))
    cat_selecionada = st.selectbox("Ou filtre por Categoria:", categorias)

    # Filtragem do Catálogo
    produtos_exibidos = st.session_state.catalogo

    if cat_selecionada != "Todos os Materiais":
        produtos_exibidos = [i for i in produtos_exibidos if i['categoria'] == cat_selecionada]

    if busca:
        produtos_exibidos = [i for i in produtos_exibidos if busca.lower() in i['nome'].lower()]

    # Exibição dos itens
    for item in produtos_exibidos:
        with st.container():
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(item['foto'], use_container_width=True)
            with col2:
                st.subheader(item['nome'])
                st.write(f"**Valor de locação:** R$ {item['preco']:.2f}")
                qtd = st.number_input(
                    f"Quantidade desejada:",
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

    # 3. RESUMO E FECHAMENTO DO PEDIDO
    st.header("3. Resumo & Fechamento")
    
    if st.session_state.carrinho:
        subtotal_geral = 0
        
        st.subheader("Itens Selecionados:")
        for item_id, qtd in st.session_state.carrinho.items():
            produto = next(i for i in st.session_state.catalogo if i['id'] == item_id)
            sub = produto['preco'] * qtd
            subtotal_geral += sub
            st.write(f"• **{qtd}x {produto['nome']}** — R$ {sub:.2f}")

        st.markdown(f"### Valor Subtotal: **R$ {subtotal_geral:.2f}**")

        # Oferta de Fechamento Imediato (10% OFF)
        st.markdown("---")
        st.subheader("⚡ Condição de Fechamento:")
        opcao_fechamento = st.radio(
            "Selecione como prefere dar andamento:",
            ["Apenas Guardar Orçamento (Valor Normal)", "Reservar e Confirmar Agora (Com 10% DE DESCONTO + PIX)"]
        )

        total_final = subtotal_geral
        desconto_aplicado = False

        if "10% DE DESCONTO" in opcao_fechamento:
            desconto_aplicado = True
            desconto = subtotal_geral * 0.10
            total_final = subtotal_geral - desconto
            
            st.success(f"🎉 **Desconto de 10% Aplicado!** Valor Final: R$ {total_final:.2f} (Economia de R$ {desconto:.2f})")
            
            # QR Code PIX e Dados de Pagamento
            st.markdown("### 📲 Dados para Pagamento via PIX:")
            st.write("**Chave PIX (Telefone / WhatsApp):** `6298224034`")
            st.write("**Favorecido:** Renascer Locações")
            st.write(f"**Valor a Pagar:** R$ {total_final:.2f}")
            
            # Imagem QR Code Estática formatada
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=Chave+PIX+6298224034+Valor+R$+{total_final:.2f}"
            st.image(qr_url, caption="Escaneie o QR Code no app do seu banco para pagar com 10% OFF", width=220)

        # Montagem do Texto de Envio para WhatsApp
        resumo_texto = "📋 *PEDIDO DE LOCAÇÃO - RENASCER LOCAÇÕES*\n\n"
        
        if 'cliente_atual' in st.session_state:
            cli = st.session_state.cliente_atual
            resumo_texto += f"*Cliente:* {cli['nome']}\n"
            resumo_texto += f"*WhatsApp:* {cli['telefone']}\n"
            resumo_texto += f"*Endereço:* {cli['endereco']}\n"
            resumo_texto += f"*Data do Evento:* {cli['data']}\n"
            resumo_texto += f"*Estilo:* {cli['ambiente']}\n\n"
        
        resumo_texto += "*Itens Escolhidos:*\n"
        for item_id, qtd in st.session_state.carrinho.items():
            produto = next(i for i in st.session_state.catalogo if i['id'] == item_id)
            sub = produto['preco'] * qtd
            resumo_texto += f"- {qtd}x {produto['nome']} (R$ {sub:.2f})\n"

        resumo_texto += f"\n*Subtotal:* R$ {subtotal_geral:.2f}\n"
        
        if desconto_aplicado:
            resumo_texto += f"*Desconto de Fechamento (10%):* -R$ {(subtotal_geral * 0.10):.2f}\n"
            resumo_texto += f"*VALOR TOTAL FINAL:* R$ {total_final:.2f}\n"
            resumo_texto += "*Status:* RESERVADO COM DESCONTO (Aguardando/Comprovante PIX)\n"
        else:
            resumo_texto += f"*VALOR TOTAL:* R$ {total_final:.2f}\n"
            resumo_texto += "*Status:* Apenas Orçamento Guardado\n"

        # WhatsApp Link direto
        numero_whatsapp = "556298224034"
        mensagem_encoded = urllib.parse.quote(resumo_texto)
        link_whatsapp = f"https://api.whatsapp.com/send?phone={numero_whatsapp}&text={mensagem_encoded}"

        st.markdown(f"""
            <a href="{link_whatsapp}" target="_blank">
                <button style="background-color:#25D366; color:white; border:none; padding:16px; font-size:18px; border-radius:10px; width:100%; font-weight:bold; cursor:pointer; margin-top:15px;">
                    📲 Enviar Pedido para o WhatsApp Business
                </button>
            </a>
        """, unsafe_allow_html=True)
    else:
        st.info("Nenhum item selecionado. Escolha os materiais no catálogo acima.")

# ==========================================
# ⚙️ PAINEL ADMINISTRATIVO
# ==========================================
else:
    st.header("⚙️ Painel do Proprietário - Renascer Locações")
    
    senha = st.text_input("Senha de Acesso ao Painel", type="password")
    if senha == "1234":
        
        st.subheader("🖼️ Atualizar Fotos e Dados dos Produtos")
        st.caption("Insira o link da foto real do seu material para substituir nos itens do catálogo.")
        
        df_cat = pd.DataFrame(st.session_state.catalogo)
        item_editar_id = st.selectbox("Selecione o produto para alterar a foto:", df_cat['id'].tolist(), format_func=lambda x: next(i['nome'] for i in st.session_state.catalogo if i['id'] == x))
        
        item_obj = next(i for i in st.session_state.catalogo if i['id'] == item_editar_id)
        
        col_img1, col_img2 = st.columns([1, 2])
        with col_img1:
            st.image(item_obj['foto'], width=150, caption="Foto Atual")
        with col_img2:
            nova_url_foto = st.text_input("URL / Link da Nova Foto:", value=item_obj['foto'])
            novo_preco_edit = st.number_input("Preço de Locação (R$):", value=float(item_obj['preco']), step=0.50)
            novo_estoque_edit = st.number_input("Estoque Total:", value=int(item_obj['estoque']), step=1)
            
            if st.button("Salvar Alterações do Produto"):
                item_obj['foto'] = nova_url_foto
                item_obj['preco'] = novo_preco_edit
                item_obj['estoque'] = novo_estoque_edit
                st.success(f"Produto '{item_obj['nome']}' atualizado com sucesso!")
                st.rerun()

        st.divider()

        # Adicionar Novo Produto
        st.subheader("➕ Cadastrar Novo Produto")
        with st.form("form_add_novo"):
            nome_n = st.text_input("Nome do Material")
            cat_n = st.selectbox("Categoria", ["Mobiliário & Mesas", "Louças & Copos", "Prataria & Talheres", "Serviço & Rechauds", "Toalhas & Linha de Mesa", "Equipamentos & Freezers"])
            preco_n = st.number_input("Preço de Locação (R$)", min_value=0.0, step=0.50)
            estoque_n = st.number_input("Estoque Inicial", min_value=1, step=1)
            foto_n = st.text_input("Link da Foto (URL)", value="https://via.placeholder.com/300")
            
            if st.form_submit_button("Cadastrar Material"):
                novo_id = max([i['id'] for i in st.session_state.catalogo]) + 1 if st.session_state.catalogo else 1
                st.session_state.catalogo.append({
                    "id": novo_id, "categoria": cat_n, "nome": nome_n, "preco": preco_n, "estoque": estoque_n, "foto": foto_n, "tags": ["rustico"]
                })
                st.success("Novo material adicionado ao catálogo!")
                st.rerun()

        st.divider()
        st.subheader("📢 Mensagem Promocional")
        nova_p = st.text_area("Texto do Comunicado (Topo da Página):", value=st.session_state.promocao)
        if st.button("Salvar Mensagem"):
            st.session_state.promocao = nova_p
            st.success("Mensagem atualizada!")
