from pathlib import Path

import streamlit as st
from backend import ask

BASE_DIR = Path(__file__).parent

st.set_page_config(
    page_title="UET Chatbot",
    page_icon=BASE_DIR / "static" / "logo.png",
    layout="wide"
)

# load css
with open(BASE_DIR / "style.css", encoding="utf-8") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )


col1, col2 = st.columns([1, 8])

with col1:
    st.image(BASE_DIR / "static" / "logo.png", width=70)

with col2:
    st.markdown(
        """
# UET Chatbot
Trợ lý hỏi đáp Handbook Trường Đại học Công nghệ - ĐHQGHN
"""
    )

st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []


for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.markdown(msg["content"])

        if (
            msg["role"] == "assistant"
            and msg.get("sources")
        ):

            with st.expander("Nguồn tham khảo"):

                for source in msg["sources"]:
                    st.markdown(f"- {source}")


if prompt := st.chat_input("Nhập câu hỏi..."):

    # Hiển thị câu hỏi
    with st.chat_message("user"):
        st.markdown(prompt)

    history = [
        {
            "role": m["role"],
            "content": m["content"]
        }
        for m in st.session_state.messages[-6:] # chỉ lấy 6 cái cuối nếu không prompt sẽ rất dài
    ]

    # chờ backend
    with st.spinner("Đang tìm câu trả lời..."):

        answer, sources = ask(
            question=prompt,
            history=history
        )

    with st.chat_message("assistant"):

        st.markdown(answer)

        if sources:

            with st.expander("📚 Nguồn tham khảo", expanded=False):

                for source in sources:

                    st.markdown(f"**{source['title']}**")

                    if source.get("chapter"):
                        st.markdown(f"- {source['chapter']}")

                    if source.get("article"):
                        st.markdown(f"- {source['article']}")

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources
        }
    )