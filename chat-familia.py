import streamlit as st
from supabase import create_client, Client
import datetime

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
SUPABASE_URL = "https://kicbsagvmnjrpfkimawh.supabase.co"
SUPABASE_KEY = "sb_publishable_0wEQVnYIGxLuudVaXyPQiQ_znm8Qut2"

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = init_connection()

# --- INTERFACE DO CHAT ---
st.set_page_config(page_title="Chat da Família", page_icon="💬", layout="centered")
st.title("💬 Nosso Chat de Família")

# ATUALIZAÇÃO AUTOMÁTICA: O chat vai recarregar sozinho a cada 4 segundos para buscar novas mensagens
st.fragment(run_every=4)

if "usuario" not in st.session_state:
    st.subheader("Quem está acessando?")
    nome = st.selectbox("Selecione seu nome:", ["Selecione...", "Mãe", "Bibia", "Thiaguinho"])
    if nome != "Selecione...":
        st.session_state.usuario = nome
        st.rerun()
else:
    usuario_atual = st.session_state.usuario
    st.write(f"Conectado como: **{usuario_atual}**")
    
    if st.button("Trocar de Usuário"):
        del st.session_state.usuario
        st.rerun()

    st.write("---")

    def buscar_mensagens():
        try:
            resposta = supabase.table("mensagens").select("*").order("criado_em", desc=False).execute()
            return resposta.data
        except Exception as e:
            st.error(f"Erro ao buscar mensagens: {e}")
            return []

    def enviar_mensagem(texto):
        if texto.strip() != "":
            agora = datetime.datetime.now()
            dados = {
                "usuario": usuario_atual,
                "texto": texto,
                "hora": agora.strftime("%H:%M"),
                "criado_em": agora.isoformat()
            }
            try:
                supabase.table("mensagens").insert(dados).execute()
                # Mostra o aviso e solta os balões na hora do envio
                st.toast(f"Mensagem enviada! ❤️", icon="❤️")
                st.balloons()
                st.rerun()
            except Exception as e:
                st.error(f"Erro detalhado do Supabase: {e}")

    # Guarda quantas mensagens tínhamos antes de atualizar
    if "total_mensagens" not in st.session_state:
        st.session_state.total_mensagens = 0

    mensagens = buscar_mensagens()
    
    # Se chegou mensagem nova de outra pessoa, solta uma notificação na tela!
    if len(mensagens) > st.session_state.total_mensagens and st.session_state.total_mensagens > 0:
        st.toast("Nova mensagem recebida no chat! 💬", icon="💬")
    
    # Atualiza o contador na memória
    st.session_state.total_mensagens = len(mensagens)

    area_mensagens = st.container()
    with area_mensagens:
        if not mensagens:
            st.info("Nenhuma mensagem ainda. Envie a primeira!")
        for msg in mensagens:
            hora_msg = f" [{msg['hora']}]" if "hora" in msg and msg["hora"] else ""
            if msg["usuario"] == usuario_atual:
                st.markdown(f"**Você**{hora_msg}: {msg['texto']}")
            else:
                st.markdown(f"**{msg['usuario']}**{hora_msg}: {msg['texto']}")

    with st.form("form_mensagem", clear_on_submit=True):
        nova_msg = st.text_input("Digite sua mensagem:")
        botao_enviar = st.form_submit_button("Enviar")
        
        if botao_enviar and nova_msg:
            enviar_mensagem(nova_msg)
