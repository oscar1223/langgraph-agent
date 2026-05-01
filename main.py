from typing import Annotated
from typing_extensions import TypedDict
from pathlib import Path
import os

from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

mistral_api_key = os.getenv("MISTRAL_API_KEY")

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

def load_system_prompt() -> str:
    prompt_path =  Path(__file__).parent / "system_prompt.md"
    return prompt_path.read_text(encoding="utf-8").strip()



def create_agent():
    llm = ChatMistralAI(model="mistral-medium-3.5", api_key=mistral_api_key, temperature=0)
    system_prompt = load_system_prompt()

    print(f"\nSistema de instrucciones cargado: {system_prompt[:100]}...")
    def chatbot(state: AgentState):
        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        return {"messages": [llm.invoke(messages)]}


    graph_builder = StateGraph(AgentState)
    graph_builder.add_node("chatbot", chatbot)

    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_edge("chatbot", END)

    memory = MemorySaver()

    return graph_builder.compile(checkpointer=memory)


def main():
    print("=" * 50)
    print("  Agente Conversacional (Mistral + LangGraph)")
    print("=" * 50)

    agent = create_agent()
    config = {"configurable": {"thread_id": "session-1"}}

    print("\n✓ Agente iniciado con Mistral")
    print("  Escribe 'salir' para terminar.")
    print("  Escribe 'nuevo' para iniciar nueva conversación.")
    print("-" * 50)

    session_count = 1

    while True:
        user_input = input("\nTu: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ("salir", "quit", "exit"):
            print("\nHasta luego!")
            break
        if user_input.lower() == "nuevo":
            session_coint += 1
            config = {"configurable": {"thread_id": f"session-{session_count}"}}
            print(f"\nNueva conversación {session_count} iniciada")
            continue

        
        response = agent.invoke({"messages": [HumanMessage(content=user_input)]}, config=config)
        print(f"\nAgente: {response['messages'][-1].content}")

        if len(response["messages"]) > 1:
            print(f"\nHistorial de la conversación {session_count}:")
            for msg in response["messages"][:-1]:
                print(f"{msg.type.capitalize()}: {msg.content}")

if __name__ == "__main__":
    main()