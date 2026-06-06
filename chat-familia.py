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

# Cria uma caixinha na memória para saber se acabou de mandar mensagem
if "disparar_coracoes" not in st.session_state:
    st.session_state.disparar_coracoes = False

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
                # Ativa o efeito dos corações
                st.session_state.disparar_coracoes = True
                st.toast(f"Mensagem enviada por {usuario_atual}!", icon="❤️")
                st.rerun()
            except Exception as e:
                st.error(f"Erro detalhado do Supabase: {e}")

    mensagens = buscar_mensagens()
    
    if mensagens:
        st.caption(f"Status: Conectado ao banco. {len(mensagens)} mensagens carregadas.")

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

    # --- TRUQUE DOS CORAÇÕES EM JAVASCRIPT ---
    if st.session_state.disparar_coracoes:
        st.session_state.disparar_coracoes = False # Desativa para a próxima vez
        
        # Injeta o efeito visual dos corações subindo na tela
        components.html(
            """
            <div id="coracoes-container" style="position:fixed; top:0; left:0; width:100vw; height:100vh; pointer-events:none; z-index:99999;"></div>
            <script>
                const container = document.getElementById('coracoes-container');
                const emojis = ['❤️', '💖', '💝', '💕', '💗'];
                
                for (let i = 0; i < 40; i++) {
                    const herat = document.createElement('div');
                    herat.innerText = emojis[Math.floor(Math.random() * emojis.length)];
                    herat.style.position = 'absolute';
                    herat.style.bottom = '-50px';
                    herat.style.left = Math.random() * 100 + 'vw';
                    herat.style.fontSize = (Math.random() * 20 + 20) + 'px';
                    herat.style.transition = 'transform ' + (Math.random() * 2 + 2) + 's linear, opacity ' + (Math.random() * 2 + 2) + 's linear';
                    herat.style.opacity = '1';
                    
                    container.appendChild(herat);
                    
                    setTimeout(() => {
                        herat.style.transform = 'translateY(-110vh) translateX(' + (Math.random() * 100 - 50) + 'px)';
                        herat.style.opacity = '0';
                    }, 50);
                    
                    setTimeout(() => { herat.remove(); }, 4000);
                }
            </script>
            """,
            height=0
        )
