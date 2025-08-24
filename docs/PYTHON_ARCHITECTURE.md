## BK25 Python Architecture

### Overview
BK25 in Python mirrors the original design and keeps the same public API. It swaps Express for FastAPI and Node SQLite bindings for Python's `sqlite3`.

### Modules
- `bk25/core.py`
  - Orchestrates conversations, automation generation, and calls generators
  - Handles Ollama via HTTP when enabled; otherwise uses mock mode

- `bk25/memory.py`
  - SQLite-backed store with tables: `conversations`, `automations`, `patterns`

- `bk25/persona_manager.py`
  - Loads JSON personas from `old/personas/`, validates, switches personas

- `bk25/channel_manager.py`
  - Provides channel catalog and builders for artifacts (Slack, Teams, Web, etc.)

- `bk25/generators/*`
  - Build prompts, parse code blocks, extract documentation, generate filenames

- `bk25/server.py`
  - FastAPI app exposing routes; serves static UI from `old/web/`

### Configuration
- Env vars:
  - `PORT` server port (default 3000)
  - `OLLAMA_URL` base URL for Ollama
  - `BK25_MODEL` model name
  - `BK25_MOCK=1` enable mock LLM mode (used in tests/CI)

### Development
- Install: `pip install -e .[dev]`
- Run server: `bk25` or `python -m bk25`
- Run tests: `pytest -q`

