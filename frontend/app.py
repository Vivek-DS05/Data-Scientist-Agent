import requests
import streamlit as st
from PIL import Image

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Data Scientist Agent", layout="wide")
st.title("📊 Chat With Your Data")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "dataset_loaded" not in st.session_state:
    st.session_state.dataset_loaded = False

with st.sidebar:
    st.header("Upload Dataset")
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    if uploaded_file and st.button("Upload"):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
        with st.spinner("Uploading and profiling dataset..."):
            resp = requests.post(f"{API_URL}/upload", files=files)
        if resp.status_code == 200:
            st.session_state.dataset_loaded = True
            st.success("Dataset loaded!")
            st.text(resp.json()["summary"])
        else:
            st.error(resp.json().get("detail", "Upload failed."))

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        for c in msg.get("code", []):
            with st.expander("View generated code"):
                st.code(c, language="python")
        for p in msg.get("plots", []):
            try:
                st.image(Image.open(p))
            except Exception:
                pass

if question := st.chat_input("Ask a question about your data..."):
    if not st.session_state.dataset_loaded:
        st.warning("Please upload a CSV first.")
    else:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                resp = requests.post(f"{API_URL}/chat", json={"question": question})
            if resp.status_code == 200:
                data = resp.json()
                st.markdown(data["answer"])
                for c in data.get("code", []):
                    with st.expander("View generated code"):
                        st.code(c, language="python")
                for p in data.get("plots", []):
                    try:
                        st.image(Image.open(p))
                    except Exception:
                        pass
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": data["answer"],
                    "code": data.get("code", []),
                    "plots": data.get("plots", []),
                })
            else:
                st.error("Something went wrong. Try rephrasing your question.")