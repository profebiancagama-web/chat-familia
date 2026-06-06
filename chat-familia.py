import streamlit as st
from supabase import create_client, Client
import datetime

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
SUPABASE_URL = "https://kicbsagvmnjrpfkimawh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtpY2JzYWd2bW5qcnBma2ltYXdoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTU4NzUzNzIsImV4cCI6MjAzMTQ1MTM3Mn0.bndfU3YyNmswMG54X0RSc1FzMms4X2h0Yk9pZnMwX2t4bjl2MXM0"

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = init_connection()

# --- INTERFACE DO CHAT ---
st.set_page_config(page_title="Chat da Família", page_icon="💬", layout="centered")
st.title("💬 Nosso Chat de Família")

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
            resposta = supabase.table("mensagens").select("*").order("criado_em", ascending=True).execute()
            return resposta.data
        except Exception:
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
            supabase.table("mensagens").insert(dados).execute()

    mensagens = buscar_mensagens()
    
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
            st.rerun()
