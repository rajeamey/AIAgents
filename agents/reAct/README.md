# ReAct agent (Gemini)

A minimal ReAct-style tool-calling agent built with LangChain's
`create_agent`, running on the Gemini API via `LLM_MODEL`.

## Setup

```bash
cd agents/reAct
python -m venv .venv && source .venv/bin/activate

# either:
pip install -e ".[dev,google-genai]"
# or:
pip install -r requirements.txt

cp .env.example .env   # already done here; just fill in GOOGLE_API_KEY
```

Set in `.env`:

```
LLM_MODEL=google_genai:gemini-2.0-flash
GOOGLE_API_KEY=...
```

## Run

```bash
python -m react_agent.agent
```

## Test

```bash
pytest
```

## What's here

- `src/react_agent/agent.py` — a tool-calling agent built with LangChain's
  `create_agent(os.environ["LLM_MODEL"], tools=[...])`. No vendor SDK is
  imported in code — switching providers is just changing `LLM_MODEL` in
  `.env` and installing the matching extra.
- `tests/` — pytest examples for the tools.
- This agent owns its own `pyproject.toml`, `requirements.txt`, and
  `.venv`, isolated from the rest of the monorepo.
