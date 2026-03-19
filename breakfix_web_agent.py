from __future__ import annotations

import os
from typing import TypedDict, Literal, Any


class AgentState(TypedDict, total=False):
    question: str
    confidence: float
    results: list[dict]
    status: str


def evaluate_accuracy(state: AgentState) -> AgentState:
    question = state.get("question", "")
    if not question:
        return {"confidence": 0.0}

    # Opção A: sem LLM. Sempre considera baixa confiança e parte para busca.
    return {"confidence": 0.0}


def web_search(state: AgentState) -> AgentState:
    question = state.get("question", "")
    if not question:
        return {"results": [], "status": "no_question"}

    tavily_key = os.getenv("TAVILY_API_KEY", "").strip()
    if not tavily_key:
        # Sem Tavily, não busca.
        return {"results": [], "status": "missing_tavily_key"}

    def _normalize(raw: Any) -> list[dict]:
        # Normaliza para list[dict] com url/title/content quando disponível.
        results: list[dict] = []
        if isinstance(raw, list):
            for item in raw:
                if isinstance(item, dict):
                    results.append(
                        {
                            "title": item.get("title") or item.get("name") or "",
                            "url": item.get("url") or item.get("link") or "",
                            "content": item.get("content") or item.get("snippet") or item.get("raw_content") or "",
                        }
                    )
                else:
                    results.append({"title": "", "url": "", "content": str(item)})
            return results

        if isinstance(raw, dict):
            if isinstance(raw.get("results"), list):
                return _normalize(raw.get("results"))
            return [
                {
                    "title": raw.get("title") or raw.get("name") or "",
                    "url": raw.get("url") or raw.get("link") or "",
                    "content": raw.get("content") or raw.get("snippet") or raw.get("raw_content") or str(raw),
                }
            ]

        return [{"title": "", "url": "", "content": str(raw)}]

    # 1) Tenta caminho atual (langchain tool)
    try:
        from langchain_community.tools.tavily_search import TavilySearchResults

        tool = TavilySearchResults(k=4)
        raw: Any = tool.invoke({"query": question})
        results = [r for r in _normalize(raw) if r.get("url") or r.get("content")]
        if results:
            return {"results": results, "status": "ok"}
    except Exception:
        # cai para fallback oficial do tavily-python
        pass

    # 2) Fallback robusto usando tavily-python diretamente
    try:
        from tavily import TavilyClient

        client = TavilyClient(api_key=tavily_key)
        raw = client.search(query=question, search_depth="basic", max_results=5)
        results = [r for r in _normalize(raw) if r.get("url") or r.get("content")]
        if results:
            return {"results": results, "status": "ok"}
        return {"results": [], "status": "no_results"}
    except Exception:
        return {"results": [], "status": "error"}


def route_search(state: AgentState) -> Literal["web_search", "generate_answer"]:
    if float(state.get("confidence", 0.0)) < float(os.getenv("BREAKFIX_REFLECT_THRESHOLD", "0.3")):
        return "web_search"
    return "generate_answer"


def run_breakfix_agent(question: str) -> AgentState:
    """
    Executa o fluxo estilo LangGraph:
      avaliar confiança -> (se baixa) busca online -> gerar resposta
    """
    from langgraph.graph import StateGraph, END

    graph = StateGraph(AgentState)
    graph.add_node("evaluate_accuracy", evaluate_accuracy)
    graph.add_node("web_search", web_search)
    # Opção A: sem LLM, "generate_answer" só finaliza o estado.
    graph.add_node("generate_answer", lambda state: {"status": state.get("status", "ok")})

    graph.set_entry_point("evaluate_accuracy")
    graph.add_conditional_edges("evaluate_accuracy", route_search, {"web_search": "web_search", "generate_answer": "generate_answer"})
    graph.add_edge("web_search", "generate_answer")
    graph.add_edge("generate_answer", END)

    app = graph.compile()
    return app.invoke({"question": question, "results": [], "status": "init"})

