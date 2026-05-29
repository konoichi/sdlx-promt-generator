# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

1. Think Before Coding
Don't assume. Don't hide confusion. Surface tradeoffs.

Before implementing:

State your assumptions explicitly. If uncertain, ask.
If multiple interpretations exist, present them - don't pick silently.
If a simpler approach exists, say so. Push back when warranted.
If something is unclear, stop. Name what's confusing. Ask.
2. Simplicity First
Minimum code that solves the problem. Nothing speculative.

No features beyond what was asked.
No abstractions for single-use code.
No "flexibility" or "configurability" that wasn't requested.
No error handling for impossible scenarios.
If you write 200 lines and it could be 50, rewrite it.
Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

3. Surgical Changes
Touch only what you must. Clean up only your own mess.

When editing existing code:

Don't "improve" adjacent code, comments, or formatting.
Don't refactor things that aren't broken.
Match existing style, even if you'd do it differently.
If you notice unrelated dead code, mention it - don't delete it.
When your changes create orphans:

Remove imports/variables/functions that YOUR changes made unused.
Don't remove pre-existing dead code unless asked.
The test: Every changed line should trace directly to the user's request.

4. Goal-Driven Execution
Define success criteria. Loop until verified.

Transform tasks into verifiable goals:

"Add validation" → "Write tests for invalid inputs, then make them pass"
"Fix the bug" → "Write a test that reproduces it, then make it pass"
"Refactor X" → "Ensure tests pass before and after"
For multi-step tasks, state a brief plan:

1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]


## Commands

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then add ANTHROPIC_API_KEY

# Run
python run.py          # http://127.0.0.1:5000
```

Environment variables are loaded from `.env` via `python-dotenv`. Key vars: `ANTHROPIC_API_KEY`, `DEFAULT_PROVIDER` (`anthropic` or `ollama`), `DATA_DIR` (default: `data/`), `HOST`, `PORT`, `DEBUG`.

## Architecture

Hexagonal architecture — the core never imports adapters directly.

```
app/core/          ← Business logic, no framework dependencies
  ports.py         ← LLMPort and StoragePort (ABCs)
  character.py     ← Character dataclass (pure data model)
  prompt_generator.py ← Orchestrates LLM call + storage

app/adapters/
  llm/             ← Implementations of LLMPort
    anthropic_adapter.py
    ollama_adapter.py
  storage/
    json_storage.py ← Implements StoragePort, persists to data/*.json

app/config.py      ← Dependency injection: instantiates adapters, wires them together
app/web/app.py     ← Flask routes only — no business logic
```

**Request flow:** Flask route → `get_generator(provider)` from `config.py` → `PromptGenerator.generate(character)` → `LLMPort.generate()` → parses JSON response → `StoragePort.save_prompt_history()`.

## Adding a new LLM provider

1. Create `app/adapters/llm/<name>_adapter.py` implementing `LLMPort` (`generate`, `is_available`, `name`, `available_models`)
2. Instantiate and register it in `app/config.py` under `PROVIDERS`

The UI and all routes pick it up automatically.

## Prompt structure

The LLM is instructed to return pure JSON (no markdown). The system prompt in `prompt_generator.py` defines four zones:
- `zone1` — quality tokens (RAW photo, weights, skin detail)
- `zone2_face` — face, hair, expression
- `zone3_body` — body build (skipped for portrait phase 1)
- `zone4_context` — lighting, background, composition
- `negative` — comma-separated negative tokens

Each zone has a `prompt` string and a `tokens` array with `name` + `explanation` (German). The positive prompt is assembled by joining all four zone prompts with double newlines.

## Data persistence

Characters and prompt history are stored as flat JSON files in `data/` (`characters.json`, `prompt_history.json`). The `data/` directory is auto-created on first write. Back up by copying the folder.
