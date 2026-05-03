from tools import ALL_TOOLS

from typing import Annotated
from typing_extensions import TypedDict
from pathlib import Path
import os

from datetime import datetime
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

mistral_api_key = os.getenv("MISTRAL_API_KEY")

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

def load_system_prompt() -> str:
    prompts_dir = Path(__file__).parent / "prompts"
    files = sorted(prompts_dir.glob("*.md"))
    return "\n\n".join(
        f.read_text(encoding="utf-8").strip()
        for f in files
    )

def build_dynamco_prompt(base_prompt:str, ctx: dict) -> str:
    return f""" 
{base_prompt}
# Sesión actual
Usuario: {ctx.get('user_name', 'desconocido')}
Grupo: {ctx.get('user_group', 'desconocido')}
Fecha actual: {ctx.get('current_date', 'desconocida')}
    """



def create_agent():
    llm = ChatMistralAI(model="mistral-medium-3.5", api_key=mistral_api_key, temperature=0)
    llm_with_tools = llm.bind_tools(ALL_TOOLS)
    system_prompt = load_system_prompt()

    print(f"\nSistema de instrucciones cargado: {system_prompt[:100]}...")
    def chatbot(state: AgentState, config):
        ctx = config["configurable"]
        dynamco_prompt = build_dynamco_prompt(system_prompt, ctx)
        messages = [SystemMessage(content=dynamco_prompt)] + state["messages"]
        return {"messages": [llm_with_tools.invoke(messages)]}

    graph_builder = StateGraph(AgentState)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", ToolNode(tools=ALL_TOOLS))

    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_conditional_edges("chatbot", tools_condition)
    graph_builder.add_edge("tools", "chatbot")

    memory = MemorySaver()
    return graph_builder.compile(checkpointer=memory)
    
def build_session_config(thread_id: str, user_name: str, user_group: str) -> dict:
    return {
        "configurable": {
            "thread_id": thread_id,
            "user_name": user_name,
            "user_group": user_group,
            "current_date": datetime.now().strftime("%Y-%m-%d"),
        }
    }

def main():
    print("=" * 50)
    print("  Agente Conversacional (Mistral + LangGraph)")
    print("=" * 50)

    agent = create_agent()
    session_count = 1
    config = build_session_config(f"session-{session_count}", "Dr. García", "Neurociencia")
    print(f"\nConversación {session_count} iniciada con usuario: {config['configurable']['user_name']} y grupo: {config['configurable']['user_group']}")

    
    print("\n✓ Agente iniciado con Mistral")
    print("  Escribe 'salir' para terminar.")
    print("  Escribe 'nuevo' para iniciar nueva conversación.")
    print("-" * 50)
    while True:
        user_input = input("\nTu: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ("salir", "quit", "exit"):
            print("\nHasta luego!")
            break
        
        if user_input.lower() == "nuevo":
            session_count += 1
            prev_ctx = config["configurable"]
            config = build_session_config(
                thread_id=f"session-{session_count}",
                user_name=prev_ctx["user_name"],
                user_group=prev_ctx["user_group"],
            )
            print(f"\nNueva conversación {session_count} iniciada")
            continue

        
        response = agent.invoke(
            {"messages": [HumanMessage(content=user_input)]}, 
            config=config
        )
        
        print(f"\nAgente: {response['messages'][-1].content}")

        if len(response["messages"]) > 1:
            print(f"\nHistorial de la conversación {session_count}:")
            for msg in response["messages"][:-1]:
                print(f"{msg.type.capitalize()}: {msg.content}")

        if os.getenv("DEBUG"):
            state = agent.get_state(config)
            print(f"\n[DEBUG] Mensajes en memoria: {len(state.values['messages'])}")
            print(f"[DEBUG] Thread: {state.config['configurable']['thread_id']}")


if __name__ == "__main__":
    main()