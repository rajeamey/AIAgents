# LangGraph Interview-Prep Agents

## Context

The user has a LangGraph-focused interview today/tomorrow, covering agentic AI
and general system design. The repo (`AIAgents`) is currently a skeleton: only
`agents/_template/` exists, demonstrating the single-agent `create_agent`
pattern with one tool. The goal is to build a small set of runnable example
agents — each isolated under `agents/<name>/` per the repo's copy-template
convention — that together cover the architectures most likely to come up in
the interview, plus a condensed notes doc for last-minute review. This is
study material, not production code: keep each example minimal, realistic,
and focused on making one architectural idea clear. Per the user's direction,
no verification/testing section is needed — this is a skeleton for learning,
not a deliverable to validate.

Coverage the user asked for, in priority order: (1) basic ReAct/tool-calling,
(2) multi-agent orchestration, (3) memory & persistence, (4) human-in-the-loop,
(5) streaming & observability (explicitly lowest priority — a lightweight
addition, not a full agent). RAG is explicitly excluded (user already knows it
well). The user is fairly new to LangGraph, so every agent's README carries
both "how the graph works" and "why you'd design it this way / production
tradeoffs" — the second half is what makes this useful for a system-design
interview, not just an API tour.

## Repo conventions to follow (from `agents/_template/`)

- Copy `agents/_template/` → `agents/<name>/`, rename `src/agent_template` →
  `src/<name_with_underscores>`, update `pyproject.toml` `name`/`dependencies`,
  update the import in `tests/test_agent.py`.
- **Never import a vendor SDK directly.** Simple single-agent cases use
  `create_agent(os.environ["LLM_MODEL"], tools=[...])` from `langchain.agents`.
  Anywhere a custom graph node needs a raw chat model (supervisor routing,
  custom HITL nodes), use `langchain.chat_models.init_chat_model(os.environ["LLM_MODEL"])`
  instead — same provider-agnostic string, still no vendor import.
- `LLM_MODEL` env var (`anthropic:claude-sonnet-5`, etc.) selects provider +
  model; matching extra (`anthropic`/`openai`/`google-genai`) goes in that
  agent's `pyproject.toml` optional-dependencies, mirrored from the template.
- Each agent keeps its own `pyproject.toml`, `.env.example`, `src/`, `tests/`.
- Agents 2–4 below introduce raw LangGraph primitives (`StateGraph`, `Command`,
  `interrupt`, checkpointers) that aren't used anywhere in the repo yet — add
  `langgraph>=0.2` as an explicit dependency in those agents' `pyproject.toml`
  (currently only a transitive dep via `create_agent`).

## Agents to build

### 1. `agents/react-tool-agent` — Basic ReAct / tool-calling

**Use case:** Order-support assistant with three tools: `check_order_status(order_id)`,
`calculate_refund(order_id, reason)`, `lookup_product_price(sku)` (all
in-memory/fake data, no real backend).

**Architecture:** Same as the template — `create_agent(os.environ["LLM_MODEL"], tools=[...])`
— but with 3 tools instead of 1, so the interviewer-relevant point is the
*loop* `create_agent` compiles under the hood: `agent` node calls the LLM →
conditional edge checks for tool calls → `tools` node executes them → back to
`agent` → repeats until the LLM responds with no tool calls → `END`.

**Files:** `src/react_tool_agent/agent.py` (tools + `build_agent`/`run`),
`README.md` explaining the ReAct loop diagram and talking points (why
conditional edges vs a fixed pipeline; what "ReAct" actually means —
reason+act interleaving; token/latency cost of multi-hop tool loops).

**New deps:** none beyond the template.

### 2. `agents/multi-agent-supervisor` — Multi-agent orchestration

**Use case:** Support-ticket triage system. A supervisor reads an incoming
ticket and routes it to either a **billing agent** or a **technical agent**,
each a specialized sub-agent with its own tools (billing: `lookup_invoice`,
`issue_credit`; technical: `check_system_status`, `restart_service`).

**Architecture:** Raw `StateGraph` with state `{messages, next}`. `supervisor`
node uses `init_chat_model(...).with_structured_output(Route)` (a `Literal["billing","technical","FINISH"]`
schema) to decide where to go, then returns `Command(goto=next)` — the modern
LangGraph handoff pattern (no separate conditional-edge function needed).
`billing` and `technical` nodes each wrap a small `create_agent(...)` call
scoped to their own tools, and return `Command(goto="supervisor")` so control
returns to the router after each worker turn, until the supervisor emits
`FINISH` → `END`.

**Files:** `src/multi_agent_supervisor/agent.py` (state, supervisor node,
worker nodes, graph wiring), `README.md` covering: supervisor-vs-swarm
tradeoffs, why structured output for routing beats free-text parsing, how
this scales (adding a third specialist = one more node + one more `Literal`
value), and failure modes (mis-routing, infinite supervisor↔worker loops —
mention a max-turns guard).

**New deps:** add `langgraph>=0.2` to `pyproject.toml`.

### 3. `agents/memory-persistent-agent` — Memory & persistence

**Use case:** Personal assistant that remembers stated preferences (e.g.
favorite language, timezone) both **within** a conversation (short-term,
thread-scoped) and **across** separate conversations for the same user
(long-term, cross-thread).

**Architecture:** `create_agent(os.environ["LLM_MODEL"], tools=[...], checkpointer=InMemorySaver())`
for short-term memory — invoke twice with the same `config={"configurable": {"thread_id": "t1"}}`
to show state surviving across `.invoke()` calls, then a fresh `thread_id` to
show it's gone. For long-term memory, add an `InMemoryStore` and two tools,
`remember_fact(key, value)` / `recall_facts()`, namespaced by a `user_id`
passed through config, showing facts persist even under a brand-new
`thread_id` as long as `user_id` matches.

**Files:** `src/memory_persistent_agent/agent.py`, `README.md` covering:
checkpointer = short-term/thread state vs store = long-term/cross-thread
memory (a common interview confusion point), and production notes (swap
`InMemorySaver`/`InMemoryStore` for `PostgresSaver`/a persistent store backend;
what "checkpoint" actually captures — full graph state at each super-step,
enabling replay/time-travel too).

**New deps:** add `langgraph>=0.2`.

### 4. `agents/human-in-the-loop-agent` — Human-in-the-loop

**Use case:** Assistant that can issue refunds, but must pause for explicit
human approval before actually executing `issue_refund(order_id, amount)`
(a "safe" tool like `lookup_order` runs freely, no approval needed).

**Architecture:** Custom `StateGraph` (not `create_agent`, since the pause
needs to happen *inside* the tool-execution path, not just at the top level).
Nodes: `agent` (LLM decides what to call, via `init_chat_model(...).bind_tools([...])`),
a conditional edge to either `safe_tools` (executes immediately) or
`sensitive_tool_gate`, which calls `interrupt({"action": ..., "args": ...})`
to pause the graph and surface the pending action; resuming with
`Command(resume={"approved": True/False})` either executes `issue_refund` or
returns a rejection message, then loops back to `agent`. Requires a
checkpointer (`InMemorySaver`) since interrupt/resume needs persisted state
across the pause.

**Files:** `src/human_in_the_loop_agent/agent.py`, `README.md` with a short
transcript showing: call `.invoke()` → graph pauses and returns the
interrupt payload → caller inspects it → calls `.invoke(Command(resume=...), config)`
to continue. Talking points: interrupt vs a client-side "confirm before you
call this tool" UI hack (the graph-level interrupt persists state properly,
survives process restarts with a durable checkpointer, and composes with
memory); where this fits in production (approval queues, Slack-bot approvals,
audit trails).

**New deps:** add `langgraph>=0.2`.

### 5. Streaming & observability — lightweight addition (do last)

No new agent folder. Add `src/react_tool_agent/stream_demo.py` to agent #1
(reuses its existing tools/agent — nothing new to build) showing the three
common `stream_mode`s: `"values"` (full state each step), `"updates"` (diff
per node), `"messages"` (token-level LLM output) via `agent.stream(...)`.
Add a short **Observability** section to that agent's `README.md`: what each
stream mode is for, plus a note on LangSmith tracing (`LANGCHAIN_TRACING_V2=true`,
`LANGCHAIN_API_KEY` in `.env.example`) as the standard way to get full
run traces/latency/token-cost breakdowns in production, not just
stdout-level debugging.

## Cheat sheet: `LANGGRAPH_INTERVIEW_NOTES.md` (repo root)

One consolidated doc for last-minute review, structured as:

1. **Core concepts glossary** — State/StateGraph, nodes, edges vs conditional
   edges, `Command` (goto + state update in one return), `Send` (fan-out to
   parallel node instances — mention even though no example uses it, likely
   to be asked about), checkpointer vs store, `interrupt`, `create_agent`
   internals vs hand-rolled `StateGraph` (when you need the latter).
2. **Per-agent summary table** — pattern, use case, key primitive, one-line
   "why this architecture" and "production swap" (e.g. InMemorySaver → Postgres).
3. **Likely interview questions + short model answers**, grouped by pattern
   (e.g. "How would you prevent an infinite supervisor loop?", "Difference
   between short-term and long-term memory in an agent?", "How do you handle
   a human approval step that might take hours?").
4. **System-design synthesis** — a short paragraph + list tying the four
   patterns into one hypothetical production system (e.g. a support-bot
   platform: supervisor routes tickets → specialist agents with per-user
   long-term memory → sensitive actions gated by human-in-the-loop → all
   traced via streaming/LangSmith), since the interview explicitly includes
   general system design, not just LangGraph API trivia.

## Build sequencing (today / tomorrow)

- **Today:** agents #1 (ReAct) and #2 (multi-agent supervisor) — these are
  the most likely baseline interview topics. Start #3 (memory) if time
  remains.
- **Tomorrow:** finish #3 (memory), build #4 (human-in-the-loop), add #5
  (streaming/observability addition to #1), then write
  `LANGGRAPH_INTERVIEW_NOTES.md` last, once all four patterns are fresh from
  having just built them.
