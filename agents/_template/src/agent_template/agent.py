from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

load_dotenv()


@tool
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b


def build_agent():
    model = ChatAnthropic(model="claude-sonnet-5")
    return create_react_agent(model, tools=[add])


def run(message: str) -> str:
    agent = build_agent()
    result = agent.invoke({"messages": [{"role": "user", "content": message}]})
    return result["messages"][-1].content


if __name__ == "__main__":
    print(run("What is 12.5 plus 30?"))
