import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime

# Configuração inicial da página
st.set_page_config(
    page_title="Renascer Locações - Móveis e Utensílios",
    page_icon="🎉",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- REPRODUTOR DE ÁUDIO PARA NAVEGAÇÃO ---
def tocar_som(tipo="click"):
    if tipo == "click":
        # Som de clique suave
        audio_html = """
            <audio autoplay style="display:none;">
                <source src="https://assets.mixkit.co/active_storage/sfx/2568/2568-preview.mp3" type="audio/mpeg">
            </audio>
        """
    elif tipo == "sucesso":
        # Som de confirmação/sucesso
        audio_html = """
            <audio autoplay style="display:none;">
                <source src="https://assets.mixkit.co/active_storage/sfx/1435/1435-preview.mp3" type="audio/mpeg">
            </audio>
        """
    st.components.v1.html(audio_html, height=0, width=0)

# --- BASE DE DADOS E ESTADOS NA SESSÃO ---
if 'catalogo' not in st.session_state:
    st.session_state.catalogo = [
        {"id": 1, "categoria": "Mobiliário & Mesas", "nome": "Jogo de Mesa com 4 Cadeiras de Plástico (Branca)", "preco": 14.00, "estoque": 50, "foto": "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?auto=format&fit=crop&w=400&q=80"},
        {"id": 2, "categoria": "Mobiliário & Mesas", "nome": "Mesa Redonda de 6 Lugares (Tampão de Madeira)", "preco": 18.00, "estoque": 20, "foto": "https://images.unsplash.com/photo-1530103862676-de8c9debad1d?auto=format&fit=crop&w=400&q=80"},
        {"id": 3, "categoria": "Mobiliário & Mesas", "nome": "Aparador Rústico de Madeira (2,50m)", "preco": 25.00, "estoque": 5, "foto": "https://images.unsplash.com/photo-1519225421980-715cb0215aed?auto=format&fit=crop&w=400&q=80"},
        {"id": 8, "categoria": "Louças & Copos", "nome": "Prato de Jantar Raso Branco Liso", "preco": 0.80, "estoque": 300, "foto": "https://images.unsplash.com/photo-1578749556568-bc2c40e68b61?auto=format&fit=crop&w=400&q=80"},
        {"id": 9, "categoria": "Louças & Copos", "nome": "Taça para Água / Vinho Transparente", "preco": 1.00, "estoque": 200, "foto": "https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?auto=format&fit=crop&w=400&q=80"},
        {"id": 12, "categoria": "Serviço & Rechauds", "nome": "Rechaud Inox Redondo Banho-Maria", "preco": 25.00, "estoque": 10, "foto": "https://images.unsplash.com/photo-1555244162-803834f70033?auto=format&fit=crop&w=400&q=80"},
        {"id": 20, "categoria": "Equipamentos & Freezers", "nome": "Freezer Horizontal 2 Tampas (400 Litros)", "preco": 200.00, "estoque": 3, "foto": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=400&q=80"},
    ]

if 'cliente_cadastrado' not in st.session_state:
    st.session_state.cliente_cadastrado = None

if 'pedidos_standby' not in st.session_state:
    st.session_state.pedidos_standby = []

if 'carrinho_atual' not in st.session_state:
    st.session_state.carrinho_atual = {}

# --- MENU LATERAL DE NAVEGAÇÃO ---
st.sidebar.title("📌 Menu Principal")
modo = st.sidebar.radio("Navegação", ["Área do Cliente", "Painel Administrativo"])

# ==========================================
# 📱 ÁREA DO CLIENTE
# ==========================================
if modo == "Área do Cliente":
    
    # TELA 1: PORTFÓLIO E CADASTRO
    if not st.session_state.cliente_cadastrado:
        st.markdown("""
        <div style="text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 10px; margin-bottom: 20px;">
            <h1 style="color: #1E3A8A;">🎉 Renascer Locações</h1>
            <h3>Transformando seu evento em uma experiência inesquecível!</h3>
            <p>Há mais de 14 anos oferecendo as melhores soluções em aluguel de móveis, pratos, rechauds, toalhas e equipamentos para festas.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_sobre1, col_sobre2 = st.columns(2)
        
        with col_sobre1:
            st.markdown("### 🏢 Sobre Nós & Portfólio")
            st.write("""
            A **Renascer Locações** atua no mercado oferecendo infraestrutura completa para casamentos, aniversários, reuniões familiares e grandes celebrações. 
            Contamos com materiais higienizados, conservados e de alta qualidade.
            """)
            st.info("""
            📍 **Localização Oficial:**
            Rua Presidente Rodrigues Alves, Q. 30, Lt. 06, nº 01
            Bairro Jardim Presidente — Goiânia/GO
            📞 **Contato:** (62) 3290-5515 / (62) 98224-034
            """)
            
        with col_sobre2:
            st.markdown("### 📸 Galeria de Eventos")
            st.image("https://images.unsplash.com/photo-1519167758481-83f550bb49b3?auto=format&fit=crop&w=600&q=80", caption="Estrutura e Móveis Rústicos")

        st.divider()
        st.markdown("---")
        st.subheader("👋 Seja Bem-Vindo(a)! Faça seu cadastro rápido para acessar o catálogo completo:")
        
        with st.form("form_cadastro_inicial"):
            c_nome = st.text_input("Nome Completo*")
            c_cpf = st.text_input("CPF ou CNPJ*")
            c_tel = st.text_input("WhatsApp / Telefone*")
            c_email = st.text_input("E-mail")
            c_end = st.text_input("Endereço Residencial Completo (Rua, Nº, Bairro, Cidade)*")
            
            btn_cadastrar = st.form_submit_button("Acessar Catálogo & Agendar Eventos ➔")
            
            if btn_cadastrar:
                if c_nome and c_tel and c_end:
                    st.session_state.cliente_cadastrado = {
                        "nome": c_nome,
                        "cpf": c_cpf,
                        "telefone": c_tel,
                        "email": c_email,
                        "endereco": c_end
                    }
                    tocar_som("sucesso")
                    st.success("Cadastro realizado com sucesso!")
                    st.rerun()
                else:
                    st.error("Por favor, preencha todos os campos obrigatórios (*).")

    # TELA 2: CATÁLOGO, AGENDAMENTO E STANDBY
    else:
        cli = st.session_state.cliente_cadastrado
        st.title(f"Bem-vindo(a), {cli['nome']}!")
        st.caption(f"Endereço cadastrado: {cli['endereco']} | Tel: {cli['telefone']}")
        
        # Menu do cliente
        aba_catalogo, aba_standby = st.tabs(["🛒 Catálogo & Seleção de Itens", "📅 Meus Eventos em Standby / Rascunhos"])
        
        # ABA 1: CATÁLOGO E SELEÇÃO SIMULTÂNEA
        with aba_catalogo:
            st.subheader("Selecione os materiais para o seu evento")
            
            # Busca em Tempo Real
            termo_busca = st.text_input("🔍 Digite o nome do item para filtrar instantaneamente:", key="busca_instantanea")
            
            # Filtro simultâneo
            itens_filtrados = [
                i for i in st.session_state.catalogo 
                if termo_busca.lower() in i['nome'].lower() or termo_busca.lower() in i['categoria'].lower()
            ]
            
            st.caption(f"Exibindo {len(itens_filtrados)} item(ns)")
            
            # Exibição dos itens
            for item in itens_filtrados:
                with st.container():
                    col_img, col_det, col_qtd = st.columns([1, 2, 1])
                    with col_img:
                        st.image(item['foto'], width=120)
                    with col_det:
                        st.markdown(f"**{item['nome']}**")
                        st.caption(f"Categoria: {item['categoria']}")
                        st.write(f"Preço Unitário: **R$ {item['preco']:.2f}**")
                    with col_qtd:
                        qtd_atual = st.session_state.carrinho_atual.get(item['id'], 0)
                        nova_qtd = st.number_input(
                            "Qtd:", min_value=0, max_value=item['estoque'], 
                            value=qtd_atual, key=f"q_{item['id']}"
                        )
                        if nova_qtd != qtd_atual:
                            if nova_qtd > 0:
                                st.session_state.carrinho_atual[item['id']] = nova_qtd
                            else:
                                st.session_state.carrinho_atual.pop(item['id'], None)
                            tocar_som("click")
                st.divider()

            # PAINEL DE GUARDAR OU FECHAR PEDIDO
            if st.session_state.carrinho_atual:
                st.markdown("### 📋 Resumo da Seleção Atual")
                subtotal = 0
                for item_id, q in st.session_state.carrinho_atual.items():
                    prod = next(i for i in st.session_state.catalogo if i['id'] == item_id)
                    tot_item = prod['preco'] * q
                    subtotal += tot_item
                    st.write(f"• **{q}x {prod['nome']}** = R$ {tot_item:.2f}")
                
                st.markdown(f"#### Subtotal: **R$ {subtotal:.2f}**")
                
                st.subheader("🗓️ Agendar este evento")
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    nome_evento = st.text_input("Nome/Tipo do Evento (ex: Aniversário João, Casamento, Churrasco):")
                with col_e2:
                    data_evento = st.date_input("Data Prevista do Evento:")
                
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.button("💾 Guardar Pedido em Standby (Rascunho)"):
                        if nome_evento:
                            novo_standby = {
                                "id_pedido": len(st.session_state.pedidos_standby) + 1,
                                "cliente": cli,
                                "nome_evento": nome_evento,
                                "data_evento": str(data_evento),
                                "itens": dict(st.session_state.carrinho_atual),
                                "valor_total": subtotal,
                                "status": "Standby (Rascunho)",
                                "data_criacao": datetime.now().strftime("%d/%m/%Y %H:%M")
                            }
                            st.session_state.pedidos_standby.append(novo_standby)
                            st.session_state.carrinho_atual = {}
                            tocar_som("sucesso")
                            st.success("Evento salvo em Standby! Você pode fechar a efetivação a qualquer momento.")
                            st.rerun()
                        else:
                            st.error("Identifique o nome do evento para salvar.")
                            
                with col_btn2:
                    if st.button("⚡ Efetivar com 10% OFF + Gerar PIX"):
                        if nome_evento:
                            total_com_desconto = subtotal * 0.90
                            novo_standby = {
                                "id_pedido": len(st.session_state.pedidos_standby) + 1,
                                "cliente": cli,
                                "nome_evento": nome_evento,
                                "data_evento": str(data_evento),
                                "itens": dict(st.session_state.carrinho_atual),
                                "valor_total": total_com_desconto,
                                "status": "Efetivado (Aguardando PIX)",
                                "data_criacao": datetime.now().strftime("%d/%m/%Y %H:%M")
                            }
                            st.session_state.pedidos_standby.append(novo_standby)
                            st.session_state.carrinho_atual = {}
                            tocar_som("sucesso")
                            st.success("Pedido efetivado com desconto!")
                            st.rerun()
                        else:
                            st.error("Identifique o nome do evento para efetivar.")

        # ABA 2: EVENTOS EM STANDBY
        with aba_standby:
            st.subheader("📅 Seus Eventos e Orçamentos Salvos")
            meus_pedidos = [p for p in st.session_state.pedidos_standby if p['cliente']['cpf'] == cli['cpf']]
            
            if not meus_pedidos:
                st.info("Você ainda não possui eventos salvos em standby.")
            else:
                for ped in meus_pedidos:
                    with st.expander(f"🎉 {ped['nome_evento']} — Data: {ped['data_evento']} ({ped['status']})"):
                        st.write(f"**Data de Criação:** {ped['data_criacao']}")
                        st.write(f"**Valor Estimado:** R$ {ped['valor_total']:.2f}")
                        st.write("**Itens Selecionados:**")
                        for i_id, q in ped['itens'].items():
                            p_obj = next((x for x in st.session_state.catalogo if x['id'] == i_id), None)
                            if p_obj:
                                st.write(f"- {q}x {p_obj['nome']}")
                        
                        # Montar envio para WhatsApp
                        txt_wa = f"Olá! Quero efetivar meu pedido em Standby:\n*Evento:* {ped['nome_evento']}\n*Data:* {ped['data_evento']}\n*Valor:* R$ {ped['valor_total']:.2f}"
                        link_w = f"https://api.whatsapp.com/send?phone=556298224034&text={urllib.parse.quote(txt_wa)}"
                        
                        st.markdown(f"[📲 Enviar Comprovante / Efetivar pelo WhatsApp]({link_w})")

# ==========================================
# ⚙️ PAINEL ADMINISTRATIVO
# ==========================================
else:
    st.header("⚙️ Painel do Proprietário — Expectativas & Gestão")
    senha = st.text_input("Senha de Acesso", type="password")
    
    if senha == "1234":
        tocar_som("click")
        
        st.subheader("📊 Planejamento de Estoque & Expectativas dos Clientes (Standby)")
        st.caption("Acompanhe as festas agendadas pelos clientes para ajustar seu estoque com antecedência.")
        
        if st.session_state.pedidos_standby:
            df_standby = []
            for p in st.session_state.pedidos_standby:
                df_standby.append({
                    "ID": p['id_pedido'],
                    "Cliente": p['cliente']['nome'],
                    "Telefone": p['cliente']['telefone'],
                    "Evento": p['nome_evento'],
                    "Data do Evento": p['data_evento'],
                    "Valor Total": f"R$ {p['valor_total']:.2f}",
                    "Status": p['status']
                })
            st.dataframe(pd.DataFrame(df_standby), use_container_width=True)
        else:
            st.info("Nenhum cliente salvou orçamentos em standby até o momento.")
            
        st.divider()
        
        # Gestão de Produtos
        st.subheader("📦 Gerenciar Catálogo de Materiais")
        for prod in st.session_state.catalogo:
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                st.write(f"**{prod['nome']}** ({prod['categoria']})")
            with c2:
                prod['preco'] = st.number_input(f"Preço ID {prod['id']}", value=float(prod['preco']), key=f"p_{prod['id']}")
            with c3:
                prod['estoque'] = st.number_input(f"Estoque ID {prod['id']}", value=int(prod['estoque']), key=f"e_{prod['id']}")
        
        if st.button("Salvar Alterações de Estoque/Preços"):
            tocar_som("sucesso")
            st.success("Dados do catálogo atualizados!")
