# LangGraph agent

A conversational agent with tools and per-session memory, built on [LangGraph](https://github.com/langchain-ai/langgraph) and Mistral.

The example persona, *Vivario*, assists lab staff with managing animal colonies for biomedical research. The persona and domain live in Markdown prompts, so the same agent can be adapted to another field by editing those files.

## How it works

```
START → chatbot ──(tool calls?)──► tools
            ▲                        │
            └────────────────────────┘
```

- **Graph:** a `StateGraph` with a `chatbot` node (Mistral with tools bound) and a `ToolNode`. `tools_condition` routes between them until the model answers without calling a tool.
- **Memory:** a `MemorySaver` checkpointer keeps each conversation's history by `thread_id`. Type `nuevo` to start a new thread.
- **Modular system prompt:** every file in `prompts/` (identity, tone, tools, domain, boundaries, uncertainty, format, user context) is loaded in order and joined. Session context (user, group, date) is injected on each turn.
- **Tools** (`tools.py`):
  - `read_doc`, `write_doc`, `edit_file`, `delete_doc`, `list_docs`: manage `.md`/`.txt` notes in `docs/`.
  - `web_search`: web research through Tavily.
  - `get_current_time`.

## Run it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set MISTRAL_API_KEY and TAVILY_API_KEY
python main.py
```

Type `salir` to quit. Set `DEBUG=1` to print the memory state after each turn.
