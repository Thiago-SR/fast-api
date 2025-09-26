import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()  # Carrega as variáveis do .env

key_api = os.getenv("API_KEY")

genai.configure(api_key=key_api)

chats = {}

def get_chat(user_id: str):
    # Se já existe uma sessão, retorna
    if user_id in chats:
        return chats[user_id]
    
    # Se não existe, cria e salva
    model = genai.GenerativeModel("gemini-2.5-flash")
    chat = model.start_chat(history=[])
    chats[user_id] = chat
    return chat
