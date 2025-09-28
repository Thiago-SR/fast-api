from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json

load_dotenv()
genai.configure(api_key=os.getenv("API_KEY"))

class FinancialState(TypedDict):
    user_id: str
    user_input: str
    intent: Optional[str]
    transaction_data: Optional[dict]
    response: str

def simple_response_node(state: FinancialState) -> FinancialState:
    """Responde baseado na intenção e dados extraídos"""
    
    intent = state.get("intent", "chat")
    user_id = state["user_id"]
    user_input = state["user_input"]
    transaction_data = state.get("transaction_data", {})
    
    if intent == "add_expense":
        if transaction_data:
            amount = transaction_data.get("amount", 0)
            category = transaction_data.get("category", "outros")
            description = transaction_data.get("description", "")
            
            state["response"] = f"💰 {user_id}, entendi!\n" \
                            f"📝 Descrição: {description}\n" \
                            f"💵 Valor: R$ {amount:.2f}\n" \
                            f"🏷️ Categoria: {category}\n" \
                            f"✅ Vou registrar essa despesa!"
        else:
            state["response"] = f"💰 {user_id}, entendi que você gastou algo. Vou registrar essa despesa!"
            
    elif intent == "check_balance":
        state["response"] = f"💳 {user_id}, vou consultar seu saldo atual..."
        
    elif intent == "get_report":
        state["response"] = f"📊 {user_id}, vou gerar seu relatório financeiro..."
        
    else:
        state["response"] = f"Olá {user_id}! Você disse: '{user_input}'"
    
    return state

def create_simple_workflow():
    """Cria um fluxo que analisa intenção, extrai dados e responde"""
    
    # Cria o grafo
    workflow = StateGraph(FinancialState)
    
    # Adiciona as funções como "nós"
    workflow.add_node("analisar_intencao", analyze_intent_node)
    workflow.add_node("extrair_dados", extract_transaction_data_node)
    workflow.add_node("responder", simple_response_node)
    
    # Define o fluxo: START → analisar_intenção → extrair_dados → responder → END
    workflow.add_edge(START, "analisar_intencao")
    workflow.add_edge("analisar_intencao", "extrair_dados")
    workflow.add_edge("extrair_dados", "responder")
    workflow.add_edge("responder", END)
    
    # Compila o fluxo
    return workflow.compile() 

def analyze_intent_node(state: FinancialState) -> FinancialState:
    """Analisa o que o usuário quer fazer usando IA"""
    
    mensagem = state["user_input"]
    
    # Prompt para o Gemini
    prompt = f"""
    Analise esta mensagem e determine a intenção do usuário.
    Responda APENAS com uma dessas opções: add_expense, check_balance, get_report, chat
    
    Mensagem: "{mensagem}"
    
    Regras de análise:
    
    add_expense: Quando o usuário menciona gastos, compras, pagamentos, despesas
    - "gastei X reais", "comprei algo", "paguei conta", "despesa de"
    
    check_balance: Quando o usuário quer saber saldo, quanto tem, situação financeira atual
    - "qual meu saldo", "quanto tenho", "situação financeira", "estou gastando muito"
    
    get_report: Quando o usuário quer relatórios, resumos, análises, histórico
    - "relatório", "resumo", "análise", "histórico", "como estão minhas finanças"
    
    chat: Conversas casuais, cumprimentos, dúvidas gerais
    - "oi", "como está", "obrigado", "tchau"
    
    Exemplos:
    - "gastei 50 reais no almoço" → add_expense
    - "qual meu saldo atual?" → check_balance
    - "preciso saber sobre minhas finanças" → get_report
    - "estou gastando muito?" → check_balance
    - "meu relatório do mês" → get_report
    - "oi, como você está?" → chat
    """
    
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        state["intent"] = response.text.strip()
    except Exception as e:
        # Fallback para análise simples se IA falhar
        mensagem_lower = mensagem.lower()
        if "gastei" in mensagem_lower or "gasto" in mensagem_lower:
            state["intent"] = "add_expense"
        elif "saldo" in mensagem_lower or "quanto tenho" in mensagem_lower:
            state["intent"] = "check_balance"
        elif "relatório" in mensagem_lower or "resumo" in mensagem_lower:
            state["intent"] = "get_report"
        else:
            state["intent"] = "chat"
    
    return state

def extract_transaction_data_node(state: FinancialState) -> FinancialState:
    """Extrai dados específicos de transações usando IA"""
    
    mensagem = state["user_input"]
    
    # Prompt para extrair dados da transação
    prompt = f"""
    Extraia informações desta mensagem sobre uma transação financeira.
    Responda APENAS com um JSON válido contendo: amount, category, description
    
    Mensagem: "{mensagem}"
    
    Exemplos de resposta:
    - "gastei 50 reais no almoço" → {{"amount": 50.0, "category": "alimentação", "description": "almoço"}}
    - "comprei um livro por 30 reais" → {{"amount": 30.0, "category": "educação", "description": "livro"}}
    - "paguei 120 de conta de luz" → {{"amount": 120.0, "category": "utilidades", "description": "conta de luz"}}
    
    Categorias possíveis: alimentação, transporte, saúde, educação, lazer, utilidades, vestuário, outros
    
    Se não conseguir extrair alguma informação, use valores padrão apropriados.
    """
    
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        
        # Limpa a resposta (remove markdown se presente)
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        
        # Converte para dicionário
        extracted_data = json.loads(response_text)
        
        # Adiciona os dados extraídos ao estado
        state["transaction_data"] = extracted_data
        
    except Exception as e:
        # Fallback se a extração falhar
        state["transaction_data"] = {
            "amount": 0.0,
            "category": "outros", 
            "description": mensagem
        }
    
    return state

def test_bot():
    """Função para testar nosso bot"""
    
    # Cria um estado inicial (como uma mensagem de entrada)
    initial_state = {
        "user_id": "usuario_teste",
        "user_input": "Olá, bot!",
        "response": ""
    }
    
    # Executa o fluxo
    result = bot.invoke(initial_state)
    
    # Mostra o resultado
    print(f"Resposta do bot: {result['response']}")

# Cria uma instância do fluxo
bot = create_simple_workflow()  

# Executa o teste se este arquivo for rodado diretamente
if __name__ == "__main__":
    test_bot()