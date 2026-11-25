# SlideGen AI

A web app that generates slide decks with AI. A signed-in user types a topic, an LLM drafts the deck, the user edits it in the browser, then exports it to PPTX, PDF or Google Slides. Every deck is saved to the user's history.

## Current state (read first)

- `app/` is the original Streamlit prototype: Azure OpenAI through LangChain, python-pptx, one user, files written to `data/`. It is being **replaced, not extended**. When you port its logic (the prompt in `app/llm/prompt_templates.py`, PPTX building in `app/utils/pptx_generator.py`), delete the ported part afterwards.
- The target stack below is built in phases. `agent_docs/architecture.md` has the phase plan and what exists so far. If a command below doesn't exist yet, set it up as part of your task. Don't skip verification.

## Stack (target)

- `backend/`: Python 3.12, FastAPI, SQLAlchemy 2 + Alembic, Pydantic v2, PostgreSQL. Managed with `uv`.
- `frontend/`: React + TypeScript + Vite, using npm.
- LLM: any OpenAI-compatible endpoint (Gemini free tier, Groq, OpenRouter `:free` models, local Ollama), chosen by env vars. Model ids are never hardcoded.
- Exports: python-pptx → `.pptx`; LibreOffice headless → `.pdf`; Google Drive API → Google Slides.
- Auth: Google sign-in (OAuth/OIDC) with an httpOnly session cookie.

## Map

```
backend/app/
  api/        HTTP routers: auth, decks, generate, export
  core/       settings (pydantic-settings, reads .env), security, dependencies
  db/         SQLAlchemy models and session; migrations live in backend/alembic/
  slides/     Deck schema: the single source of truth for slide data
  llm/        provider client with failover, prompts, deck generation
  exporters/  pptx.py, pdf.py, google_slides.py
backend/tests/
frontend/src/
  pages/      login, history (deck list), editor
  editor/     slide canvas, thumbnails, inline editing
  api/        typed client generated from the backend's OpenAPI schema
```

## Rules that apply to every task

1. **The deck JSON is the source of truth** (`backend/app/slides/schema.py`). The editor edits it, the database stores it, and every exporter reads only a validated `Deck`. Never build a PPTX and parse it back.
2. Changing the deck schema means bumping `schema_version` and adding an upgrade step for stored decks (see `agent_docs/slide_schema.md`).
3. LLM output is untrusted. Validate it against the schema, and render it escaped in the UI (no `dangerouslySetInnerHTML`).
4. Every deck query filters by the current user's id. A user must never be able to read, edit or export another user's deck by guessing an id.
5. All LLM calls go through `backend/app/llm/client.py`, which handles failover, rate limits and usage logging. Tests never call a real LLM; they use the fake provider.
6. The developer works on Windows and the app deploys on Linux. Use `pathlib`, never hardcode `\` or `/` in paths, and keep commands runnable in PowerShell. Don't add Windows-only dependencies (comtypes, COM automation).
7. Secrets come from env vars through `core/config.py`. When you add one, also add it to `.env.example`. Never commit `.env`. Generated files go to a temp dir or get streamed back to the client; never write them into the repo.
8. Database changes go through an Alembic migration. Never call `create_all` against a real database.

## Working conventions

- Use the superpowers skills for every task (brainstorming before new features, TDD, verification before completion).
- Use a git worktree per branch, and tmux for parallel work.
- Always use git with conventional commits (`feat:`, `fix:`, `docs:`, `chore:`...) and conventional branch names (`feat/...`, `fix/...`, `docs/...`, `chore/...`).
- Python: always use `uv`, `ruff` and Pydantic.
- GCP: use the `gcloud` CLI. The playground project id is `lv-playground-genai`.

## Commands

Backend (run in `backend/`):
- `uv sync`: install dependencies
- `uv run uvicorn app.main:app --reload`: dev server on :8000
- `uv run pytest`: tests
- `uv run ruff check --fix .` then `uv run ruff format .`: lint and format
- `uv run alembic upgrade head` / `uv run alembic revision --autogenerate -m "msg"`: migrations

Frontend (run in `frontend/`):
- `npm install`, `npm run dev` (:5173), `npm run build` (also type-checks), `npm run lint`, `npm test`
- `npm run gen:api`: regenerate the typed API client after backend schema changes

Local database: `docker compose up -d db` from the repo root.

**Before calling a task done:** run the tests and the linter for the parts you touched, plus `npm run build` if you changed the frontend, and fix whatever fails.

## Read before working on...

- `agent_docs/architecture.md`: phase plan and progress, request flow, database tables, API endpoints
- `agent_docs/slide_schema.md`: deck JSON format, layouts, themes, versioning
- `agent_docs/llm.md`: providers, env vars, prompts, failover, structured output, rate limits
- `agent_docs/exports.md`: PPTX, PDF and Google Slides export, Google OAuth scopes

Read the files that apply to your task before you start.
