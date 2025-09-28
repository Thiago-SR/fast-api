from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END

class FinancialState(TypedDict):
    user_id: str
    user_input: str
    intent: Optional[str]
    response: str

def simple_response_node(state: FinancialState) -> FinancialState:
    """Responde baseado na intenção analisada"""
    
    intent = state.get("intent", "chat")
    user_id = state["user_id"]
    user_input = state["user_input"]
    
    if intent == "add_expense":
        state["response"] = f"💰 {user_id}, entendi que você gastou algo. Vou registrar essa despesa!"
    elif intent == "check_balance":
        state["response"] = f"💳 {user_id}, vou consultar seu saldo atual..."
    elif intent == "get_report":
        state["response"] = f"📊 {user_id}, vou gerar seu relatório financeiro..."
    else:
        state["response"] = f"Olá {user_id}! Você disse: '{user_input}'"
    
    return state

def create_simple_workflow():
    """Cria um fluxo que analisa intenção e depois responde"""
    
    # Cria o grafo
    workflow = StateGraph(FinancialState)
    
    # Adiciona as funções como "nós"
    workflow.add_node("analisar_intencao", analyze_intent_node)
    workflow.add_node("responder", simple_response_node)
    
    # Define o fluxo: START → analisar_intenção → responder → END
    workflow.add_edge(START, "analisar_intencao")
    workflow.add_edge("analisar_intencao", "responder")
    workflow.add_edge("responder", END)
    
    # Compila o fluxo
    return workflow.compile() 

def analyze_intent_node(state: FinancialState) -> FinancialState:
    """Analisa o que o usuário quer fazer"""
    
    mensagem = state["user_input"].lower()
    
    if "gastei" in mensagem or "gasto" in mensagem:
        state["intent"] = "add_expense"
    elif "saldo" in mensagem or "quanto tenho" in mensagem:
        state["intent"] = "check_balance"
    elif "relatório" in mensagem or "resumo" in mensagem:
        state["intent"] = "get_report"
    else:
        state["intent"] = "chat"
    
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