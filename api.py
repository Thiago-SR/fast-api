from typing import Union

from fastapi import FastAPI, Request

from main import get_chat

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/chat/{user_id}")
async def chat_endpoint(user_id: str, request: Request):
    data = await request.json()
    mensagem = data.get("mensagem")

    chat = get_chat(user_id)  # Recupera ou cria
    resposta = chat.send_message(mensagem)

    return {"resposta": resposta.text}