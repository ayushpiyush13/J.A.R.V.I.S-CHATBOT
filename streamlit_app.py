import sys
import asyncio
import streamlit as st

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="J.A.R.V.I.S.",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── JARVIS CSS ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&display=swap');

/* Global background */
.stApp { background-color: #020b18 !important; }
section[data-testid="stSidebar"] { background-color: #041525 !important; border-right: 1px solid #0a3a55; }
section[data-testid="stSidebar"] * { color: #cceeff !important; font-family: 'Share Tech Mono', monospace !important; }

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem !important; }

/* Title */
h1, h2, h3 { font-family: 'Orbitron', monospace !important; color: #00d4ff !important; letter-spacing: 3px; }

/* Chat messages */
.user-msg {
    background: #041525;
    border-left: 3px solid #00ffcc;
    padding: 12px 16px;
    margin: 8px 0;
    border-radius: 0 6px 6px 0;
    font-family: 'Share Tech Mono', monospace;
    color: #00ffcc;
}
.ai-msg {
    background: #010d18;
    border-left: 3px solid #00d4ff;
    padding: 12px 16px;
    margin: 8px 0;
    border-radius: 0 6px 6px 0;
    font-family: 'Share Tech Mono', monospace;
    color: #00cfff;
}
.msg-label {
    font-size: 10px;
    letter-spacing: 3px;
    margin-bottom: 4px;
    font-family: 'Orbitron', monospace !important;
    opacity: 0.7;
}
.sys-msg {
    color: #336688;
    font-family: 'Share Tech Mono', monospace;
    font-size: 12px;
    border-left: 2px solid #003344;
    padding-left: 10px;
    margin: 4px 0;
}

/* Input box */
.stTextInput input {
    background-color: #010d18 !important;
    border: 1px solid #0a3a55 !important;
    color: #00ffcc !important;
    font-family: 'Share Tech Mono', monospace !important;
    border-radius: 0 !important;
}
.stTextInput input:focus { border-color: #00d4ff !important; box-shadow: none !important; }

/* Buttons */
.stButton button {
    background-color: #003344 !important;
    border: 1px solid #0a3a55 !important;
    color: #00d4ff !important;
    font-family: 'Share Tech Mono', monospace !important;
    border-radius: 0 !important;
    letter-spacing: 1px;
}
.stButton button:hover { background-color: #0077aa !important; color: #000 !important; }

/* Sidebar metrics */
.stMetric { background: #041525; padding: 8px; border: 1px solid #0a3a55; }
.stMetric label { color: #336688 !important; font-size: 10px !important; letter-spacing: 2px !important; }
.stMetric [data-testid="metric-container"] div { color: #00d4ff !important; font-family: 'Orbitron', monospace !important; }

div[data-testid="stMarkdownContainer"] p { color: #cceeff; font-family: 'Share Tech Mono', monospace; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "system",
        "content": (
            "You are J.A.R.V.I.S. (Just A Rather Very Intelligent System), "
            "Tony Stark's AI assistant. Speak with calm confidence, wit, and precision. "
            "Be helpful, slightly formal but personable."
        )
    }]
if "msg_count" not in st.session_state:
    st.session_state.msg_count = 0
if "booted" not in st.session_state:
    st.session_state.booted = False

# ── AI call ───────────────────────────────────────────────────
async def ask_ai_async(messages):
    from g4f.client import AsyncClient
    client = AsyncClient()
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    return response.choices[0].message.content

def ask_ai(messages):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(ask_ai_async(messages))
    finally:
        loop.close()

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⬡ J.A.R.V.I.S.")
    st.markdown("---")
    st.markdown("**[ DIAGNOSTICS ]**")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("STATUS", "ONLINE")
        st.metric("MESSAGES", st.session_state.msg_count)
    with col2:
        st.metric("MODEL", "GPT-4o")
        st.metric("ENGINE", "G4F")
    st.markdown("---")
    st.markdown("**[ CONTROLS ]**")
    if st.button("▸ CLEAR MEMORY"):
        st.session_state.messages = [st.session_state.messages[0]]
        st.session_state.msg_count = 0
        st.session_state.booted = False
        st.rerun()
    st.markdown("---")
    st.markdown(
        "<div style='color:#336688;font-size:10px;letter-spacing:2px;'>"
        "MARK VII · POWERED BY G4F<br>NO API KEY REQUIRED"
        "</div>",
        unsafe_allow_html=True
    )

# ── Header ────────────────────────────────────────────────────
st.markdown(
    "<h1 style='text-align:center;font-size:28px;letter-spacing:6px;"
    "text-shadow:0 0 20px rgba(0,212,255,0.5);margin-bottom:4px;'>"
    "J.A.R.V.I.S.</h1>"
    "<p style='text-align:center;color:#336688;font-size:11px;"
    "letter-spacing:3px;margin-bottom:16px;font-family:Share Tech Mono,monospace;'>"
    "JUST A RATHER VERY INTELLIGENT SYSTEM · MARK VII · ONLINE</p>",
    unsafe_allow_html=True
)

# ── Boot message ─────────────────────────────────────────────
if not st.session_state.booted:
    st.markdown(
        "<div class='sys-msg'>SYSTEM CHECK ............ [ PASS ]<br>"
        "NEURAL INTERFACE ........ [ READY ]<br>"
        "G4F ENGINE .............. [ ONLINE ]<br>"
        "AI CORE ................. [ ARMED ]</div>",
        unsafe_allow_html=True
    )
    st.session_state.booted = True

# ── Chat history ─────────────────────────────────────────────
chat_messages = [m for m in st.session_state.messages if m["role"] != "system"]

for msg in chat_messages:
    if msg["role"] == "user":
        st.markdown(
            f"<div class='user-msg'>"
            f"<div class='msg-label'>YOU ▸</div>{msg['content']}"
            f"</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div class='ai-msg'>"
            f"<div class='msg-label'>J.A.R.V.I.S. ▸</div>{msg['content']}"
            f"</div>",
            unsafe_allow_html=True
        )

# ── Input ─────────────────────────────────────────────────────
st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

col_inp, col_btn = st.columns([5, 1])
with col_inp:
    user_input = st.text_input(
        label="input",
        placeholder="Enter directive...",
        label_visibility="collapsed",
        key="user_input"
    )
with col_btn:
    send = st.button("SEND ▶", use_container_width=True)

if (send or user_input) and user_input.strip():
    prompt = user_input.strip()
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.msg_count += 1

    with st.spinner("J.A.R.V.I.S. is processing..."):
        try:
            answer = ask_ai(st.session_state.messages)
        except Exception as e:
            answer = f"[SYSTEM ERROR] {e}"

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()
