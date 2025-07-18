import streamlit as st
import requests

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Smart Task Assistant", layout="wide")

# ------------------ CUSTOM CSS ------------------
st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-family: 'Helvetica', sans-serif;
        }
        .stApp {
            background-color: #0a1a2f;
            color: white;
        }
        .block-container {
            padding-top: 1rem !important;
        }
        .header-container {
            display: flex;
            flex-direction: row;
            justify-content: space-between;
            gap: 30px;
            margin-bottom: 20px;
        }
        .text-form-content {
            width: 60%;
        }
        .side-image {
            width: 35%;
            max-width: 300px;
            max-height: 300px;
            display: flex;
            justify-content: flex-end;
        }
        .stTextInput > div > div > input,
        .stSelectbox > div > div {
            background-color: white !important;
            color: black !important;
        }
        .stButton button {
            background-color: white;
            color: black;
            font-size: 16px;
            border-radius: 6px;
        }
        .chat-box {
            background-color: rgba(255,255,255,0.1);
            padding: 12px;
            border-radius: 12px;
            margin-bottom: 10px;
            border-left: 5px solid #4b8ef2;
        }
        .user-msg { color: #8ecfff; }
        .bot-msg { color: #ffffff; }
        h1, h3 { color: #ffffff; }
        input[type="text"] {
            caret-color: black !important;
        }
    </style>
""", unsafe_allow_html=True)

# ------------------ SESSION STATE ------------------
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# ------------------ PROMPT TEMPLATES ------------------
def get_prompt(task, user_input, role=None):
    if task == "Q&A":
        return f"""Answer the following question concisely.\nQuestion: {user_input}\nAnswer:"""
    elif task == "Summarization":
        return f"""Summarize the following article in bullet points.\nArticle: {user_input}\n\nSummary:"""
    elif task == "Roleplay":
        role_play_prompts = {
            "Doctor": """You are an experienced medical doctor specialized in general medicine.\nThe user asks: '{}' \nDoctor:""",
            "Lawyer": """You are a professional legal advisor with expertise in family law.\nThe user asks: '{}' \nLawyer:""",
            "Customer Support Agent": """You are a polite and helpful customer support agent for an online electronics store.\nThe user asks: '{}' \nCustomer Support Agent:"""
        }
        return role_play_prompts.get(role, "").format(user_input)

# ------------------ UI SECTION ------------------
st.markdown("## Smart AI Task Assistant")
st.markdown("Choose your task and interact with the AI below.")
st.markdown("---")

left_col, right_col = st.columns([2, 1])

with left_col:
    task = st.selectbox("Select Task", ["Q&A", "Summarization", "Roleplay"], key="task")

    selected_role = None
    if task == "Roleplay":
        selected_role = st.selectbox("Select Role", ["Doctor", "Lawyer", "Customer Support Agent"], key="role")

    # --- At the top ---
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'clear_input' not in st.session_state:
        st.session_state.clear_input = False
    if st.session_state.clear_input:
        st.session_state.clear_input = False

    # --- Input with dynamic key ---
    input_key = "input_cleared" if st.session_state.clear_input else "user_input"
    user_input = st.text_input("Enter your input", key=input_key)

    if st.button("Send") and user_input.strip():
        prompt = get_prompt(task, user_input, selected_role)

        with st.spinner("Generating response..."):
            try:
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={"model": "phi", "prompt": prompt, "stream": False}
                )
                bot_reply = response.json().get("response", "⚠️ No valid response from model.")
            except Exception as e:
                bot_reply = f"⚠️ Error: {str(e)}"

        st.session_state.chat_history.append(("user", user_input))
        st.session_state.chat_history.append(("bot", bot_reply))

        # Clear input on next render
        st.session_state.clear_input = True
        st.rerun()


    # Chat History Rendering
    st.markdown("### Chat")
    for role, msg in st.session_state.chat_history:
        msg_class = "user-msg" if role == "user" else "bot-msg"
        name = "You" if role == "user" else "AI Assistant"
        st.markdown(f"<div class='chat-box {msg_class}'><strong>{name}:</strong> {msg}</div>", unsafe_allow_html=True)


with right_col:
    st.image("image1.png", use_container_width=True)

# ------------------ RESET ------------------
if st.button("Reset Chat"):
    st.session_state.chat_history = []
    st.rerun()
