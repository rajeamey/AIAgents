# Agent template

Starting point for a new agent. To create a new agent, copy this whole folder:

```bash
cp -r agents/_template agents/<your-agent-name>
cd agents/<your-agent-name>
mv src/agent_template src/<your_agent_name>   # rename the package
```

Then update `pyproject.toml` (`name`, `dependencies`) and the import in
`tests/test_agent.py` to match the new package name.

## Setup

```bash
cd agents/<your-agent-name>
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # fill in ANTHROPIC_API_KEY
```

## Run

```bash
python -m <your_agent_name>.agent
```

## Test

```bash
pytest
```

## What's here

- `src/agent_template/agent.py` — a minimal LangGraph ReAct agent (one tool,
  one model call loop) using `langchain-anthropic`. Swap the model class
  (e.g. `langchain-openai`, `langchain-google-genai`) if this agent needs a
  different provider — LangChain's model interface is uniform.
- `tests/` — pytest example.
- Each agent owns its own `pyproject.toml` and virtualenv, since agents in
  this repo are independent and may need different dependency versions.
