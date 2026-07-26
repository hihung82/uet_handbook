import requests

URL = "https://dripping-spoils-untapped.ngrok-free.dev/generate"

def generate_answer(question, retrieved_docs, history=None):

    if history is None:
        history = []

    response = requests.post(
        URL,
        json={
            "question": question,
            "docs": retrieved_docs,
            "history": history
        },
        timeout=120
    )

    response.raise_for_status()

    return response.json()