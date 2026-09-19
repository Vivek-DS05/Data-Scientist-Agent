import os
from dotenv import load_dotenv

import httpx
from langchain_mistralai import ChatMistralAI
from deepagents import create_deep_agent

from backend.tools import (
    get_dataset_summary,
    get_execution_log,
    clear_execution_log,
)
from backend.subagents import ALL_SUBAGENTS

load_dotenv()

MODEL_NAME = (
    os.getenv("LLM_MODEL")
    or os.getenv("MISTRAL_MODEL")
    or "mistral-small-latest"
)

ORCHESTRATOR_INSTRUCTIONS = """
You are the orchestrator for a data science assistant. A user has uploaded a CSV
and asks questions about it in plain English. You do NOT write or execute code
yourself — you delegate to specialized sub-agents using the `task` tool.

Available sub-agents:
- data-analyst: EDA, stats, correlations, missing values, cleaning.
- visualizer: any chart/plot/visualization request.
- insight-writer: turns raw findings into a final plain-English answer.

Workflow for EVERY user question:
1) Decide which sub-agent(s) are needed.
   - Analytical/statistical question -> data-analyst
   - Plot/show/visualize -> visualizer
   - If both are needed -> call both.
2) Delegate via the `task` tool with a clear, specific instruction.
3) If the user asks for explanation/insights, call insight-writer LAST with:
   - the original user question
   - all raw findings / chart descriptions returned by other sub-agents
4) If the user ONLY asked to plot/show/visualize and did NOT ask for explanation,
   you may return the visualizer's response directly (to save tokens and calls).
5) Never invent results. Only use what sub-agents/tool outputs provide.
"""

print(f"[agent] Using Mistral model: {MODEL_NAME}")
_llm = ChatMistralAI(
    model=MODEL_NAME,
    temperature=0,
    max_tokens=512,
)


agent = create_deep_agent(
    model=_llm,
    system_prompt=ORCHESTRATOR_INSTRUCTIONS,
    subagents=ALL_SUBAGENTS,
)


def ask_agent(question: str) -> dict:
    """
    Runs orchestrator (+ sub-agents). Always returns whatever code/plots were
    generated even if the final LLM call fails (e.g., model access / rate limit).
    """
    clear_execution_log()

    dataset_context = get_dataset_summary()
    prompt = f"Dataset info:\n{dataset_context}\n\nUser question: {question}"

    answer_text = None

    try:
        result = agent.invoke({"messages": [{"role": "user", "content": prompt}]})
        final_message = result["messages"][-1]
        answer_text = getattr(final_message, "content", str(final_message))

    except httpx.HTTPStatusError as e:
        status = e.response.status_code if e.response is not None else "unknown"
        answer_text = (
            f"Mistral API error (HTTP {status}).\n"
            f"Details: {str(e)}\n\n"
            "If this is a 403 tier error, switch LLM_MODEL to a model your account can access "
            "(check https://api.mistral.ai/v1/models) or upgrade your Mistral plan."
        )

    except Exception as e:
        answer_text = f"Agent failed with error: {str(e)}"
    execution_log = get_execution_log()
    code_blocks = [e.get("code", "") for e in execution_log if e.get("code")]
    plot_paths = [p for e in execution_log for p in e.get("plots", [])]

    return {
        "answer": answer_text or "",
        "code": code_blocks,
        "plots": plot_paths,
    }