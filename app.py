import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime
from difflib import SequenceMatcher

# Configuração da página
st.set_page_config(
    page_title="Renascer Locações - Catálogo & Reservas",
    page_icon="🎉",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- REPRODUTOR DE ÁUDIO ---
def tocar_som(tipo="click"):
    audio_url = "https://assets.mixkit.co/active_storage/sfx/2568/2568-preview.mp3" if tipo == "click" else "https://assets.mixkit.co/active_storage/sfx/1435/1435-preview.mp3"
    st.components.v1.html(f'<audio autoplay style="display:none;"><source src="{audio_url}" type="audio/mpeg"></audio>', height=0, width=0)

# --- CÁLCULO DE FRETE E DISTÂNCIA POR CEP ---
def calcular_distancia_cep(cep_destino):
    try:
        clean_cep = str(cep_destino).replace("-", "").replace(".", "").strip()
        if len(clean_cep) != 8 or not clean_cep.isdigit():
            return None
        base_num = int(clean_cep[:5])
        renascer_num = 74353  # CEP Jardim Presidente
        
        diff_abs = abs(base_num - renascer_num)
        km_estimado = round(3.5 + (diff_abs / 18.0), 1)
        
        # Fórmula do frete: (Km * 4) + 10%
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
    "pano": "toalha",
    "panos": "toalha",
    "friser": "freezer",
    "frizzer": "freezer",
    "geladeira": "freezer",
    "copo": "taça",
    "copos": "taça",
    "prato": "louça",
    "talher": "garfo"
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

# --- BOTÃO FLUTUANTE DE AJUDA WHATSAPP ---
st.markdown("""
    <a href="https://api.whatsapp.com/send?phone=556298224034&text=Olá!%20Estou%20no%20aplicativo%20da%20Renascer%20Locações%20e%20preciso%20de%20ajuda%20com%20meu%20pedido." target="_blank" style="position:fixed;bottom:20px;right:20px;background-color:#25d366;color:white;border-radius:50px;text-align:center;font-size:15px;padding:12px 20px;box-shadow: 2px 2px 8px #888888;z-index:999999;text-decoration:none;font-weight:bold;">
        💬 Dúvidas? Fale Conosco
    </a>
""", unsafe_allow_html=True)

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
    
    # APRESENTAÇÃO INSTITUCIONAL E CADASTRO RÁPIDO
    if not st.session_state.cliente_perfil:
        st.markdown("""
        <div style="background-color: #f8f9fa; padding: 22px; border-radius: 12px; border-left: 6px solid #1E3A8A; margin-bottom: 20px;">
            <h1 style="color: #1E3A8A; margin-bottom: 5px;">🎉 Renascer Locações</h1>
            <h4 style="color: #475569; margin-top: 0px;">Tradição, Qualidade e Pontualidade para o seu Evento</h4>
            <p style="font-size: 15px; color: #334155;">
                Com <b>mais de 20 anos de atuação no mercado</b>, a <b>Renascer Locações</b> é referência na locação de móveis, pratos, copos, talheres, toalhas, rechauds e equipamentos para eventos. Nosso compromisso é entregar materiais higienizados, conservados e com a agilidade que a sua celebração merece.
            </p>
            <p style="font-size: 14px; color: #64748B; margin-bottom: 0px;">
                📍 <b>Sede Própria:</b> Rua Presidente Rodrigues Alves, Q. 30, Lt. 06, nº 01 — Jardim Presidente, Goiânia/GO | 📞 <b>Contato:</b> (62) 3290-5515 / (62) 98224-034
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
        st.title(f"Olá, {cli['nome']}!")
        
        tab_catalogo, tab_carrinho, tab_standby = st.tabs(["🛒 Catálogo de Materiais", "📋 Finalizar Orçamento & Frete", "📅 Eventos em Standby"])
        
        # TAB 1: CATÁLOGO COM BUSCA INTELIGENTE E TOALHAS VINCULADAS
        with tab_catalogo:
            st.subheader("Qual material você procura?")
            
            termo_busca = st.text_input("🔍 Digite o nome do item (ex: mesa, frizzer, pano para mesa, copo, taça):", key="busca_inteligente")
            
            itens_exibidos = buscar_materiais_inteligente(termo_busca, st.session_state.catalogo)
            
            if not itens_exibidos:
                st.warning("Nenhum material encontrado exatamente com este termo. Tente digitar de outra forma ou fale com nosso suporte no botão ao lado.")
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
                            
                            # VÍNCULO AUTOMÁTICO DE MESAS E TOALHAS
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
                
                # 2. Cálculo do Frete
                dados_frete = calcular_distancia_cep(end_cep_festa)
                val_frete = 0.0
                if dados_frete:
                    val_frete = dados_frete['valor_frete']
                    st.success(f"🚚 **Frete Calculado:** Distância da Renascer Locações: {dados_frete['km']} km ➔ **Valor do Frete: R$ {val_frete:.2f}**")
                else:
                    st.warning("Informe um CEP válido para calcular o valor do frete automático.")

                # 3. Data do Evento
                data_festa = st.date_input("Data do Evento:")

                # 4. Resumo de Itens e Valores
                st.markdown("---")
                st.markdown("#### 2. Resumo do Orçamento")
                
                subtotal_materiais = 0.0
                for item_id, q in st.session_state.carrinho_atual.items():
                    prod = next(i for i in st.session_state.catalogo if i['id'] == item_id)
                    tot_prod = prod['preco'] * q
                    subtotal_materiais += tot_prod
                    st.write(f"• **{q}x {prod['nome']}** — R$ {tot_prod:.2f}")
                    
                    if item_id in st.session_state.toalhas_vinculadas:
                        t_info = st.session_state.toalhas_vinculadas[item_id]
                        tot_toalha = t_info['preco'] * q
                        subtotal_materiais += tot_toalha
                        st.write(f"  └ ➕ *{q}x Toalha {t_info['tipo'].capitalize()} ({t_info['cor']})* — R$ {tot_toalha:.2f}")

                valor_total_bruto = subtotal_materiais + val_frete
                st.markdown(f"Subtotal Materiais: **R$ {subtotal_materiais:.2f}**")
                st.markdown(f"Valor do Frete: **R$ {val_frete:.2f}**")
                st.markdown(f"### Valor Total do Orçamento: **R$ {valor_total_bruto:.2f}**")

                # 5. Opções de Fechamento / Standby
                st.markdown("---")
                st.markdown("#### 3. Forma de Conclusão")
                
                opcao_fechar = st.radio(
                    "Como prefere dar andamento a este pedido?",
                    ["Guardar Pedido em Standby (Rascunho)", "Ir para Pagamento com 10% DE DESCONTO"]
                )
                
                nome_identificador = st.text_input("Identificação do Evento (ex: Aniversário da Sofia, Churrasco da Firma):")

                if opcao_fechar == "Guardar Pedido em Standby (Rascunho)":
                    if st.button("💾 Confirmar e Guardar em Standby"):
                        if nome_identificador:
                            novo_stb = {
                                "id": len(st.session_state.pedidos_standby) + 1,
                                "cliente": cli,
                                "evento": nome_identificador,
                                "data": str(data_festa),
                                "endereco": end_rua_festa,
                                "frete": val_frete,
                                "total": valor_total_bruto,
                                "status": "Standby (Aguardando Efetivação)",
                                "itens": dict(st.session_state.carrinho_atual)
                            }
                            st.session_state.pedidos_standby.append(novo_stb)
                            st.session_state.carrinho_atual = {}
                            tocar_som("sucesso")
                            st.success("Pedido salvo em Standby com sucesso!")
                            st.rerun()
                        else:
                            st.error("Por favor, digite um nome para identificar a sua festa.")

                else:
                    # ÁREA DE PAGAMENTO
                    st.markdown("---")
                    st.subheader("💳 Tela de Pagamento & Confirmação")
                    
                    desconto = valor_total_bruto * 0.10
                    valor_final_pix = valor_total_bruto - desconto
                    
                    st.success(f"🎉 **10% DE DESCONTO APLICADO!** De ~R$ {valor_total_bruto:.2f}~ por **R$ {valor_final_pix:.2f}** (Economia de R$ {desconto:.2f})")
                    
                    col_pix1, col_pix2 = st.columns([1, 2])
                    with col_pix1:
                        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=PIX+Renascer+Locacoes+Chave+6298224034+Valor+{valor_final_pix:.2f}"
                        st.image(qr_url, caption="Escaneie para Pagar via PIX", width=200)
                    with col_pix2:
                        st.write("**Chave PIX (Telefone):** `6298224034`")
                        st.write("**Favorecido:** Valdir Ferreira Miranda / Renascer Locações")[cite: 1]
                        st.write(f"**Valor Com Desconto:** R$ {valor_final_pix:.2f}")
                        
                        txt_whatsapp = f"📋 *PEDIDO CONFIRMADO COM PIX - RENASCER LOCAÇÕES*\n"
                        txt_whatsapp += f"*Cliente:* {cli['nome']}\n"
                        txt_whatsapp += f"*Evento:* {nome_identificador}\n"
                        txt_whatsapp += f"*Data:* {data_festa}\n"
                        txt_whatsapp += f"*Endereço:* {end_rua_festa}\n"
                        txt_whatsapp += f"*Valor do Frete:* R$ {val_frete:.2f}\n"
                        txt_whatsapp += f"*VALOR FINAL PAGO (com 10% OFF):* R$ {valor_final_pix:.2f}\n"
                        
                        link_wa_fechar = f"https://api.whatsapp.com/send?phone=556298224034&text={urllib.parse.quote(txt_whatsapp)}"
                        
                        st.markdown(f"""
                            <a href="{link_wa_fechar}" target="_blank">
                                <button style="background-color:#25D366; color:white; border:none; padding:15px; font-size:16px; border-radius:8px; font-weight:bold; cursor:pointer;">
                                    📲 Enviar Comprovante no WhatsApp Business
                                </button>
                            </a>
                        """, unsafe_allow_html=True)

        # TAB 3: STANDBY
        with tab_standby:
            st.subheader("📅 Seus Pedidos em Standby")
            if not st.session_state.pedidos_standby:
                st.info("Nenhum orçamento em standby encontrado.")
            else:
                for p in st.session_state.pedidos_standby:
                    with st.expander(f"🎉 {p['evento']} — Data: {p['data']} ({p['status']})"):
                        st.write(f"**Endereço de Entrega:** {p['endereco']}")
                        st.write(f"**Valor do Frete:** R$ {p['frete']:.2f}")
                        st.write(f"**Valor Total:** R$ {p['total']:.2f}")

# ==========================================
# ⚙️ PAINEL ADMINISTRATIVO
# ==========================================
else:
    st.header("⚙️ Painel do Proprietário — Gestão & Expectativas")
    senha = st.text_input("Senha do Painel", type="password")
    
    if senha == "1234":
        st.subheader("📊 Expectativa de Pedidos dos Clientes (Standby)")
        if st.session_state.pedidos_standby:
            df_p = pd.DataFrame(st.session_state.pedidos_standby)
            st.dataframe(df_p, use_container_width=True)
        else:
            st.info("Nenhum pedido guardado em standby até o momento.")
