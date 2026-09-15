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

# --- BASE DE DADOS EM MEMÓRIA ---
if 'catalogo' not in st.session_state:
    st.session_state.catalogo = [
        {"id": 1, "nome": "Cadeira Bistrô Branca", "categoria": "Móveis", "preco": 3.50, "foto": "https://images.unsplash.com/photo-1503602642458-232111445657?w=300", "tags": ["rustico", "piscina"]},
        {"id": 2, "nome": "Mesa Rústica de Madeira", "categoria": "Móveis", "preco": 45.00, "foto": "https://images.unsplash.com/photo-1530018607912-eff2daa1bac4?w=300", "tags": ["rustico"]},
        {"id": 3, "nome": "Freezer Vertical 500L", "categoria": "Equipamentos", "preco": 120.00, "foto": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=300", "tags": ["piscina", "rustico"]},
        {"id": 4, "nome": "Caixa de Som Amplificada", "categoria": "Som", "preco": 80.00, "foto": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=300", "tags": ["piscina"]}
    ]

if 'clientes' not in st.session_state:
    st.session_state.clientes = []

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = {}

if 'promocao' not in st.session_state:
    st.session_state.promocao = "🔥 Promoção de Mês: Desconto especial para eventos acima de R$ 300,00!"

# --- MÓDULO DE RECOMENDAÇÃO INTELIGENTE ---
def recomendar_combinacao(ambiente_selecionado, carrinho_atual):
    recomendacoes = []
    tag_busca = "rustico" if ambiente_selecionado == "Rústico" else "piscina"
    for item in st.session_state.catalogo:
        if tag_busca in item['tags'] and item['id'] not in carrinho_atual:
            recomendacoes.append(item)
    return recomendacoes

# --- TÍTULO E NAVEGAÇÃO ---
st.title("🎉 Renascer Locações")

modo = st.sidebar.radio("Modo de Acesso", ["Área do Cliente", "Painel Administrativo"])

# ==========================================
# 📱 ÁREA DO CLIENTE
# ==========================================
if modo == "Área do Cliente":
    
    if st.session_state.promocao:
        st.info(f"📢 **AVISO / PROMOÇÃO:** {st.session_state.promocao}")

    # ETAPA 1: Cadastro dos Dados Pessoais e Evento
    st.header("1. Seus Dados Pessoais")
    with st.form("form_cliente"):
        nome = st.text_input("Nome Completo*")
        telefone = st.text_input("Telefone / WhatsApp*")
        endereco = st.text_input("Endereço / Localização do Evento*")
        data_evento = st.date_input("Sugestão de Data do Evento")
        
        ambiente = st.selectbox(
            "Selecione o Estilo/Ambiente do Evento:",
            ["Selecione...", "Rústico", "Casa com Piscina", "Outro"]
        )
        
        foto_ambiente = st.file_uploader("Tirar foto ou enviar imagem do local (Opcional)", type=["jpg", "png", "jpeg"])
        
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
                st.success("Dados salvos! Escolha os materiais abaixo.")
            else:
                st.error("Preencha os campos obrigatórios (*).")

    # ETAPA 2: Escolha dos Produtos no Catálogo
    st.header("2. Seleção de Materiais")
    
    # Recomendações da IA de acordo com o Ambiente
    if 'cliente_atual' in st.session_state and st.session_state.cliente_atual.get('ambiente') in ["Rústico", "Casa com Piscina"]:
        env = st.session_state.cliente_atual['ambiente']
        sugestoes = recomendar_combinacao(env, st.session_state.carrinho)
        if sugestoes:
            st.markdown(f"💡 **Recomendações da IA para o ambiente ({env}):**")
            cols_sug = st.columns(len(sugestoes[:3]))
            for idx, item in enumerate(sugestoes[:3]):
                with cols_sug[idx]:
                    st.caption(item['nome'])
                    st.write(f"R$ {item['preco']:.2f}")

    # Lista de Produtos com Fotos
    for item in st.session_state.catalogo:
        with st.container():
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(item['foto'], use_container_width=True)
            with col2:
                st.subheader(item['nome'])
                st.write(f"**Valor un.:** R$ {item['preco']:.2f}")
                qtd = st.number_input(
                    f"Quantidade",
                    min_value=0,
                    value=st.session_state.carrinho.get(item['id'], 0),
                    key=f"item_{item['id']}"
                )
                if qtd > 0:
                    st.session_state.carrinho[item['id']] = qtd
                elif item['id'] in st.session_state.carrinho and qtd == 0:
                    del st.session_state.carrinho[item['id']]
            st.divider()

    # ETAPA 3: Fechamento e Envio para WhatsApp
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
            resumo_texto += f"*Ambiente:* {cli['ambiente']}\n\n"
        
        resumo_texto += "*Materiais Selecionados:*\n"
        
        for item_id, qtd in st.session_state.carrinho.items():
            produto = next(i for i in st.session_state.catalogo if i['id'] == item_id)
            subtotal = produto['preco'] * qtd
            total_geral += subtotal
            resumo_texto += f"- {qtd}x {produto['nome']} (R$ {subtotal:.2f})\n"
            st.write(f"• **{qtd}x {produto['nome']}** — R$ {subtotal:.2f}")

        resumo_texto += f"\n*VALOR TOTAL ESTIMADO:* R$ {total_geral:.2f}"
        st.markdown(f"### **Total: R$ {total_geral:.2f}**")

        opcao_reserva = st.radio("Deseja reservar agora ou apenas guardar?", ["Reservar para o evento", "Apenas guardar para mais próximo"])
        resumo_texto += f"\n*Status:* {opcao_reserva}"

        # SEU NÚMERO DE WHATSAPP CONFIGURADO:
        numero_whatsapp = "556298224034"
        
        mensagem_encoded = urllib.parse.quote(resumo_texto)
        link_whatsapp = f"https://wa.me/{numero_whatsapp}?text={mensagem_encoded}"

        st.markdown(f"""
            <a href="{link_whatsapp}" target="_blank">
                <button style="background-color:#25D366; color:white; border:none; padding:15px; font-size:16px; border-radius:8px; width:100%; font-weight:bold; cursor:pointer;">
                    📲 Enviar Orçamento para o WhatsApp
                </button>
            </a>
        """, unsafe_allow_html=True)
    else:
        st.info("Nenhum material selecionado ainda.")

# ==========================================
# ⚙️ PAINEL ADMINISTRATIVO (SEU CONTROLE)
# ==========================================
else:
    st.header("⚙️ Painel de Controle - Renascer Locações")
    
    senha = st.text_input("Senha de Acesso", type="password")
    if senha == "1234":
        
        # 1. Cadastro de novos materiais
        st.subheader("📦 Cadastrar Novo Material")
        with st.form("add_material"):
            novo_nome = st.text_input("Nome do Material")
            novo_preco = st.number_input("Valor de Locação (R$)", min_value=0.0, step=0.50)
            nova_foto = st.text_input("URL da Foto do Produto", value="https://via.placeholder.com/150")
            tags = st.multiselect("Estilo do Ambiente", ["rustico", "piscina"])
            
            if st.form_submit_button("Lançar Material"):
                novo_id = len(st.session_state.catalogo) + 1
                st.session_state.catalogo.append({
                    "id": novo_id, "nome": novo_nome, "preco": novo_preco, "foto": nova_foto, "tags": tags
                })
                st.success(f"'{novo_nome}' adicionado com sucesso ao catálogo!")

        # 2. Lançamento de Promoções
        st.subheader("📢 Atualizar Promoção / Comunicado")
        nova_promo = st.text_area("Texto da Promoção", value=st.session_state.promocao)
        if st.button("Enviar Promoção aos Clientes"):
            st.session_state.promocao = nova_promo
            st.success("Promoção atualizada!")

        # 3. Lista de Clientes Cadastrados
        st.subheader("👥 Clientes que se Cadastraram")
        if st.session_state.clientes:
            st.dataframe(pd.DataFrame(st.session_state.clientes))
        else:
            st.info("Nenhum cadastro de cliente nesta sessão.")
