# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A monorepo of independent AI agents for various use cases. Agents are not
linked to each other — each one lives in its own folder under `agents/`,
built with LangChain / LangGraph, and owns its own dependencies and
virtualenv.

## Commands

There is no root-level build/test — everything is per-agent. From an agent's
directory (e.g. `agents/<name>/`):

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,anthropic]"   # swap/add extras: anthropic, openai, google-genai
cp .env.example .env                # set LLM_MODEL and the matching provider API key

python -m <package_name>.agent      # run
pytest                              # run all tests
pytest tests/test_agent.py::test_add_tool   # run a single test
```

## Architecture

### Layout

```
agents/
  _template/   # copy this to start a new agent
  <agent-1>/
  <agent-2>/
  ...
```

To create a new agent: `cp -r agents/_template agents/<name>`, rename the
`src/agent_template` package, and update `pyproject.toml` (`name`,
`dependencies`) and the import in `tests/test_agent.py` accordingly. Full
instructions are in `agents/_template/README.md`.

### Per-agent isolation

Each agent has its own `pyproject.toml` and virtualenv (not a shared root
one), because agents are independent and may need different dependency
versions or even different LangChain provider integrations.

### Vendor-agnostic model selection

Agents must not import a vendor SDK (`langchain_anthropic`, `langchain_openai`,
etc.) directly in code. Instead, use LangChain's `create_agent` from
`langchain.agents`, passing the model as a provider-prefixed string read from
env, e.g.:

```python
from langchain.agents import create_agent
create_agent(os.environ["LLM_MODEL"], tools=[...])
```

`LLM_MODEL` (set in `.env`, e.g. `anthropic:claude-sonnet-5` or
`openai:gpt-4o`) selects both provider and model at runtime. Switching
vendors for an agent is done by changing this env var and installing the
matching optional extra in that agent's `pyproject.toml` (`anthropic` /
`openai` / `google-genai`) — never by editing the agent's code.

Note: `langgraph.prebuilt.create_react_agent` is deprecated as of
LangChain v1 — use `create_agent` from `langchain.agents` instead (it builds
on LangGraph internally and returns a compiled graph).
