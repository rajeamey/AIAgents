# AIAgents
This repo contains ai agents for various use cases.

Each agent is independent — its own folder, dependencies, and virtualenv.
Agents are built with [LangChain](https://python.langchain.com/) /
[LangGraph](https://langchain-ai.github.io/langgraph/).

## Layout

```
agents/
  _template/   # copy this to start a new agent
  <agent-1>/
  <agent-2>/
  ...
```

## Adding a new agent

See [agents/_template/README.md](agents/_template/README.md).
