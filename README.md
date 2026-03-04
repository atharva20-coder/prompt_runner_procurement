# Prompt Runner

A multi-stage LLM conversation agent with dynamic tool support, designed for debt resolution voice flows. It orchestrates structured conversations through configurable stages (Intro → Investigation → Recovery → Exit), with each stage having its own system prompt, tool set, and transition rules.

## What Does It Do?

Prompt Runner simulates a debt resolution agent that conducts structured phone conversations with customers. It:

1. **Greets the customer** (Intro), identifies the reason for payment delay, and routes accordingly.
2. **Investigates the delay** (Investigation) by loading a reason-specific script (e.g. job loss, medical, salary delay) and asking targeted questions.
3. **Negotiates resolution** (Recovery) — payment commitment, follow-up scheduling, or escalation.
4. **Closes the call** (Exit) — logs the outcome and ends the session.

Customer data (name, loan details, outstanding amounts, etc.) is injected into prompts at runtime via `{placeholder}` tokens, making each conversation personalized.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                          main.py (CLI)                           │
│         Parses args, creates provider, picks run mode            │
└──────────┬───────────────────────────────────┬───────────────────┘
           │                                   │
   Single-stage mode                  Orchestrator mode
           │                                   │
           ▼                                   ▼
┌──────────────────┐              ┌─────────────────────────┐
│   Agent (1 stage)│              │   orchestrator.py        │
│   Interactive    │              │   Chains stages via      │
│   REPL           │              │   StageTransitionSignal  │
└──────────────────┘              └────────┬────────────────┘
                                           │
                          ┌────────────────┼────────────────┐
                          ▼                ▼                ▼
                     ┌─────────┐    ┌─────────┐     ┌─────────┐
                     │  Agent  │    │  Agent  │     │  Agent  │
                     │ (Intro) │───▶│ (Invest)│────▶│(Recover)│──▶ …
                     └─────────┘    └─────────┘     └─────────┘
```

### Core Modules

| Module | Role |
|---|---|
| `main.py` | CLI entry point. Loads config, creates the LLM provider, and runs in either single-stage or orchestrator mode. |
| `orchestrator.py` | Stage chaining engine. Pre-builds and warms up agents for every stage, then runs them sequentially, passing structured handoff data between stages. |
| `agent.py` | Multi-turn conversation loop with streaming, structured JSON output (`state` and `agent` fields), tool call execution, and an interactive REPL. |
| `litellm_provider.py` | Unified LiteLLM implementation for interacting with Vertex AI, OpenRouter, local models (Ollama), and others, with built-in explicit prompt caching. |
| `config_loader.py` | Pydantic-validated YAML config loading for LLM settings, tools, orchestrator, and logging. |
| `prompt_composer.py` | Runtime prompt templating — injects customer data, date/time, and handoff context into stage prompts. |
| `tool_registry.py` | Abstract `Tool` base class and `ToolRegistry` for registering, listing, and executing tools. |

### Configuration Files

| File | Purpose |
|---|---|
| `config.yaml` | Root config — LLM provider/model, `thinking_budget`, prompt caching, temperature, streaming, enabled tools, orchestrator toggle. |
| `stages.yaml` | Stage pipeline definition — name, prompt file, tools, and allowed transitions for each stage. |
| `customer_data.yaml` | Customer & loan information injected into prompts as `{placeholder}` values. |

### Tools (`tools/`)

| Tool | Stage | Purpose |
|---|---|---|
| `intro_next_stage` | Intro | Validates exit criteria and routes to Investigation, Dispute Handler, or Recovery with structured handoff. |
| `get_delay_script` | Investigation | Loads a delay-reason-specific script (9 categories: job loss, medical, accident, etc.) from the `scripts/` directory. |
| `investigation_next_stage` | Investigation | Transitions to Recovery with collected investigation data. |
| `recovery_next_stage` | Recovery | Transitions to Exit with resolution details. |
| `end_call` | Exit | Logs the call outcome (payment received, follow-up booked, or escalated) and ends the session. |

---

## Major Flows

### 1. Orchestrator Flow (Chained Stages)

This is the primary mode. Enabled via `orchestrator.enabled: true` in `config.yaml`.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         STARTUP                                     │
│  1. Load config, customer data, stages.yaml                         │
│  2. Pre-build Agent + ToolRegistry for every stage                  │
│  3. Warmup all stage prompts (triggers LLM prompt caching)          │
└─────────────┬───────────────────────────────────────────────────────┘
              ▼
┌─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐
│  STAGE LOOP (while current_stage_name is set)                       │
│                                                                     │
│  1. Reset the pre-built agent (clear conversation history)          │
│  2. Send handoff_data as first user message (or {action: begin})    │
│  3. Run agent.run() → streaming response + tool loop                │
│  4. Run agent.run_interactive() → user REPL                         │
│  5. If a next-stage tool raises StageTransitionSignal:               │
│     - Capture handoff_data                                          │
│     - Look up next stage name from transitions map                  │
│     - Loop back to step 1 with the new stage                        │
│  6. Special case: DISPUTE_HANDLER → print message and end           │
└─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘
```

**Stage transition mechanism:** Each stage has a "next stage" tool (e.g. `intro_next_stage`). When the LLM determines exit criteria are met, it calls this tool. The tool validates the criteria and raises a `StageTransitionSignal` exception. The orchestrator catches this, extracts the handoff data, and starts the next stage.

### 2. Single-Stage Testing Mode

For iterating on individual stage prompts. Set `orchestrator.enabled: false` and uncomment a `system_prompt` + `enabled` tools block in `config.yaml`.

```
Load config → Compose prompt → Create Agent → Warmup → Interactive REPL
```

If a stage transition tool fires, the signal is caught and printed (not chained).

### 3. Agent Turn Loop

Inside each stage, the `Agent` runs a multi-turn loop (max 10 turns). The conversation history is smartly filtered to send only agent text for older assistant messages but full content for the latest.

```
User message
  └──▶ LLM call (with prompt caching; structured JSON output separating `state` and `agent`)
         ├── Tool call(s) → execute → feed results back → re-call LLM
         └── Text response (`agent` field) → print to terminal
                                                            └── repeat...
```

**Safety net:** If the model outputs `exit_criteria_matched: true` in text but forgets the tool call, the agent auto-nudges the model to make the call.

### 4. Prompt Composition

```
prompt_template.md  +  customer_data.yaml  +  {current_date, current_time}
        │                     │                         │
        └─────────────────────┴─────────────────────────┘
                              │
                    PromptComposer.compose()
                              │
                    Fully resolved system prompt
```

Only known `{placeholder}` keys are substituted — JSON examples and code blocks in prompts are left untouched.

---

## Running

```bash
# Install dependencies
uv sync

# Orchestrator mode (default — chained stages)
uv run python main.py

# Single prompt (non-interactive)
uv run python main.py --prompt "Hello, I'm calling about my loan"

# Custom config
uv run python main.py --config my_config.yaml
```

### Requirements

- See pyproject.toml and use `uv` to install and run the project.
