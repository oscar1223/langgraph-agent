from langchain_core.tools import tool
from datetime import datetime
from pathlib import Path
from tavily import TavilyClient 
from dotenv import load_dotenv
import os

DOCS_DIR = Path(__file__).parent / "docs"
DOCS_DIR.mkdir(exist_ok=True)

load_dotenv()

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


@tool
def get_current_time() -> str:
    """Return the actual date"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool
def read_doc(file_name:str) -> str:
    """Read .md and .txt files fron the docs directory"""
    file_path = DOCS_DIR / file_name
    if not file_path.exists():
        return f"Archivo {file_name} no encontrado"
    return file_path.read_text(encoding="utf-8")

@tool
def write_doc(file_name:str, content:str) -> str:
    """Write to .md and .txt files in the docs directory"""
    file_path = DOCS_DIR / file_name
    file_path.write_text(content, encoding="utf-8")
    return f"Archivo {file_name} actualizado"

@tool
def delete_doc(file_name:str) -> str:
    """Delete .md and .txt files from the docs directory"""
    file_path = DOCS_DIR / file_name
    if not file_path.exists():
        return f"Archivo {file_name} no encontrado"
    file_path.unlink()
    return f"Archivo {file_name} eliminado"

@tool
def edit_file(file_name: str, original_text:str, new_text:str) -> str:
    """Edit .md and .txt files in the docs directory. Replace a specific part of the document with a new one."""
    file_path = DOCS_DIR / file_name
    if not file_path.exists():
        return f"Archivo {file_name} no encontrado"
    content = file_path.read_text(encoding="utf-8")
    if original_text not in content:
        return f"Texto original {original_text} no encontrado en el archivo {file_name}"
    new_content = content.replace(original_text, new_text)
    file_path.write_text(new_content, encoding="utf-8")
    return f"Archivo {file_name} editado"

@tool
def list_docs() -> list[str]:
    """List all .md and .txt files in the docs directory"""
    return [file.name for file in DOCS_DIR.glob("*.md")] + [file.name for file in DOCS_DIR.glob("*.txt")]

@tool
def web_search(query:str) -> str:
    """Search the internet for researchment purposes"""
    results = tavily_client.search(query=query, max_results=5)

    output = []
    for r in results["results"]:
        output.append(f"**{r['title']}**\n{r['url']}\n{r['content']}\n")

    return "\n---\n".join(output)

ALL_TOOLS = [
    get_current_time,
    read_doc,
    write_doc,
    delete_doc,
    edit_file,
    list_docs,
    web_search,
]
