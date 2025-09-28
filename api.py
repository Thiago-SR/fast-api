from typing import Union
from fastapi import FastAPI, Request
from main import get_chat
from financial_bot import bot

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/chat/{user_id}")
async def chat_endpoint(user_id: str, request: Request):
    """Endpoint que usa nosso bot LangGraph"""
    try:
        data = await request.json()
        mensagem = data.get("mensagem", "")
        
        # Cria o estado inicial
        initial_state = {
            "user_id": user_id,
            "user_input": mensagem,
            "response": ""
        }
        
        # Executa o bot
        result = bot.invoke(initial_state)
        
        return {"resposta": result["response"]}
    
    except Exception as e:
        return {"error": f"Erro: {str(e)}"}