import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool

load_dotenv()


@tool
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b


@tool
def current_utc_time() -> str:
    """Return the current date and time in UTC, ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def build_agent():
    # LLM_MODEL selects both provider and model, e.g. "google_genai:gemini-2.0-flash".
    # Swapping vendors only requires changing this env var and installing the
    # matching langchain-<provider> package - no code change.
    return create_agent(os.environ["LLM_MODEL"], tools=[add, current_utc_time])


def run(message: str) -> str:
    agent = build_agent()
    result = agent.invoke({"messages": [{"role": "user", "content": message}]})
    return result["messages"][-1].content


if __name__ == "__main__":
    print(run("What is 12.5 plus 30, and what's the current UTC time?"))
