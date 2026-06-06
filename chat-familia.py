import streamlit as st
from supabase import create_client, Client
import datetime
import streamlit.components.v1 as components

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

# O chat verifica o banco de dados sozinho a cada 3 segundos
st.fragment(run_every=3)

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
                st.rerun()
            except Exception as e:
                st.error(f"Erro detalhado do Supabase: {e}")

    # Inicializa o guardador do histórico na memória
    if "ultima_quantidade_msg" not in st.session_state:
        st.session_state.ultima_quantidade_msg = None

    mensagens = buscar_mensagens()
    total_atual = len(mensagens)

    # LÓGICA DA NOTIFICAÇÃO EM TEXTO E SOM:
    if st.session_state.ultima_quantidade_msg is not None:
        if total_atual > st.session_state.ultima_quantidade_msg:
            ultima_msg = mensagens[-1]
            # Se a mensagem veio de outra pessoa, avisa e toca o som!
            if ultima_msg["usuario"] != usuario_atual:
                st.toast(f"Nova mensagem de {ultima_msg['usuario']}! 💬", icon="💬")
                
                # Injeta um player invisível de áudio para tocar o barulho de notificação
                components.html(
                    """
                    <audio autoplay style="display:none;">
                        <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-84.wav" type="audio/wav">
                    </audio>
                    """,
                    height=0
                )

    # Atualiza o guardador com o total atual de mensagens
    st.session_state.ultima_quantidade_msg = total_atual

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
