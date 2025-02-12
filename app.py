import streamlit as st
import requests

st.set_page_config(page_title="Chatbot SAEL", page_icon="💬", layout="centered")

RASA_URL = "http://localhost:5005/webhooks/rest/webhook"

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "buttons" not in st.session_state:
    st.session_state["buttons"] = []

st.title("💬 Chatbot SAEL")

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"], avatar=msg["avatar"]):
        st.markdown(msg["content"])

with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Digite sua mensagem:", key="user_input", placeholder="Escreva algo...")
    enviar = st.form_submit_button("Enviar")

if enviar and user_input.strip():
    st.session_state["messages"].append({"role": "user", "avatar": "👤", "content": user_input})

    response = requests.post(RASA_URL, json={"sender": "user", "message": user_input})

    if response.status_code == 200:
        bot_responses = response.json()
        
        buttons = []
        for bot_response in bot_responses:
            bot_message = bot_response.get("text", "Sem resposta")
            st.session_state["messages"].append({"role": "assistant", "avatar": "🤖", "content": bot_message})

            if "buttons" in bot_response:
                buttons = bot_response["buttons"]

        st.session_state["buttons"] = buttons

    st.rerun()

if st.session_state["buttons"]:
    st.write("Escolha uma opção:")
    cols = st.columns(3)

    for idx, button in enumerate(st.session_state["buttons"]):
        if cols[idx % 3].button(button["title"]):
            selected_payload = button["payload"]
            
            st.session_state["messages"].append({"role": "user", "avatar": "👤", "content": button["title"]})
            response = requests.post(RASA_URL, json={"sender": "user", "message": selected_payload})

            if response.status_code == 200:
                bot_responses = response.json()
                for bot_response in bot_responses:
                    bot_message = bot_response.get("text", "Sem resposta")
                    st.session_state["messages"].append({"role": "assistant", "avatar": "🤖", "content": bot_message})

            st.session_state["buttons"] = []
            st.rerun()

if st.button("Limpar Conversa"):
    st.session_state["messages"] = []
    st.session_state["buttons"] = []
    st.rerun()
