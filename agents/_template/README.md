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
pip install -e ".[dev,anthropic]"   # swap "anthropic" for "openai" / "google-genai", or add several
cp .env.example .env                # set LLM_MODEL and the matching provider API key
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

- `src/agent_template/agent.py` — a minimal tool-calling agent built with
  LangChain's `create_agent(os.environ["LLM_MODEL"], tools=[...])` (the
  `langgraph.prebuilt.create_react_agent` this replaces is now deprecated).
  No vendor SDK is imported in code — switching providers is just changing
  `LLM_MODEL` in `.env` and installing the matching extra (see
  `pyproject.toml`).
- `tests/` — pytest example.
- Each agent owns its own `pyproject.toml` and virtualenv, since agents in
  this repo are independent and may need different dependency versions.
