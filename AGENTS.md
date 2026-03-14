# AGENTS.md — Litigación con Tarjetas de Crédito Visa

Instruction material for AI coding agents (GitHub Copilot, Claude, etc.)
working on this repository.

---

## Project purpose

A **read-only MCP server** that surfaces 'Merchants dispute management guidelines' data and a merchant history database as five structured tools. The agent reasoning loop lives entirely in the **MCP client** (GitHub Copilot, Claude Desktop, …).
This server is the data and retrieval layer only — no LLM calls are made server-side.

---

## Repository layout

```
src/litigiosVisa/
  server.py          ← FastMCP tool definitions (authoritative interface)
  chroma_store.py    ← ChromaDB wrapper for semantic search
  sqlite_store.py    ← SQLAlchemy DDL + CRUD helpers
  sql_generator.py   ← NL → SQL template engine
  ingest.py          ← PDF → ChromaDB + SQLite ingestion pipeline

scripts/
  seed_dispute.py   ← Seeds demo dispute data into SQLite

data/
  merchants-dispute-management-guidelines.pdf        ← Source PDF (not committed — add locally)
  chroma/            ← Persisted ChromaDB vector store (generated)
  dispute.db       ← SQLite database (generated)
```

---

## Tool contract (never break these signatures)

| Tool | Python signature | Returns |
|---|---|---|
| `search_dispute_categories` | `(scenario: str)` | `list[dict]` — candidates with category_id, name, snippet, score |
| `get_full_dispute_condition` | `(category_id: str)` | `dict` — full dispute condition fields |
| `check_interactions` | `(category: list[str])` | `list[dict]` — interaction pairs |
| `generate_sql_query` | `(intent: str)` | `str` — SELECT SQL |
| `execute_sql_query` | `(sql: str)` | `list[dict]` — result rows |

All tools are synchronous and return JSON-serialisable values. Do not add `async` to tool functions without updating the FastMCP configuration.

---

## Technology choices

| Concern | Choice | Rationale |
|---|---|---|
| MCP server | `fastmcp` | Pythonic, minimal boilerplate |
| Vector store | `chromadb` (persistent) | Local, no external service |
| Embeddings | `chromadb` `DefaultEmbeddingFunction` (`all-MiniLM-L6-v2` via ONNXRuntime) | No PyTorch / CUDA required |
| Relational DB | SQLite via `sqlalchemy` | Zero-config, file-based |
| PDF parsing | `pdfplumber` | Handles WHO PDF multi-column layout |
| Data transforms | `polars` | All ingestion transforms use Polars DataFrames |
| Package manager | `uv` | Fast, reproducible, single lock file |

---

## Coding conventions

- Python ≥ 3.11. Use `from __future__ import annotations` in every module.
- All data transformations in `ingest.py` and array/table operations in `sql_generator.py` must use **Polars** — never pandas.
- Format with `ruff format`, lint with `ruff check --fix`.
- No secrets in source — all paths come from environment variables loaded  via `python-dotenv` (see `.env.example`).
- `execute_sql_query` must reject any non-SELECT statement before touching the database. The guard is in `sqlite_store.py::execute_readonly`.
- Always use `upsert_interaction`, never raw INSERT in new code.

---

## Development commands

```bash
# Install all dependencies (creates .venv automatically)
uv sync

# Run the MCP server — stdio transport (default for MCP clients)
uv run visa-dispute

# Run with FastMCP dev inspector — browser UI on http://localhost:5173
uv run fastmcp dev src/litigiosVisa/server.py

# Lint + format
uv run ruff check --fix src/
uv run ruff format src/

# Tests
uv run pytest
```

---

## Data pipeline commands

```bash
# 1. Place WHO-doc.pdf in data/
cp /path/to/Dispute-doc.pdf data/Dispute-doc.pdf

# 2. Run ingestion (PDF → ChromaDB + SQLite)
uv run python -m merchants-dispute-guidelines.ingest

# 3. Seed demo patients
uv run python scripts/seed_dispute.py
```

---

## Agent reasoning flow

The MCP client is expected to follow this sequence:

```
merchants dispute scenario (free text)
  └─► search_dispute_categories      ← always first; returns ranked candidates
        └─► get_full_category     ← call for each relevant candidate (1-N)
              ├─► check_interactions   ← if two or more guidelines in the scenario
              └─► generate_sql_query   ← only when dispute-specific data needed
                    └─► execute_sql_query
                          └─► emit structured recommendation:
                                RECOMMEND | CONTRAINDICATED | 
                                + dispute reasoning
```

---

## Extending the system

### Adding a new tool
1. Define it as a `@mcp.tool()` decorated function in `server.py`.
2. Add its signature to the Tool contract table above.
3. Write a unit test in `tests/`.

### Improving NL→SQL coverage
Add a new `(pattern, template)` tuple to `_TEMPLATES` in `sql_generator.py`.
Pattern groups must exactly match the `{placeholder}` names in the template.

### Changing the embedding model
Update `EMBEDDING_MODEL` in `chroma_store.py`, then re-run ingestion so the collection is rebuilt with the new model's vector space.

---

## MCP client configuration

```json
{
  "$schema": "https://opencode.ai/config.json",
  "servers": {
    "merchants-dispute-advisor": {
      "command": "uv",
      "args": ["run", "dispute-advisor"],
      "cwd": "/absolute/path/to/merchants-dispute-advisor"
    }
  }
}
```
---
For **GitHub Copilot in VS Code**, place this in `.vscode/mcp.json`.
