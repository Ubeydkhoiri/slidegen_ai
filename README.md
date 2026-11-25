# SlideGen AI

A web app that generates slide decks with AI. A signed-in user types a topic, an LLM drafts the deck, the user edits it in the browser, then exports it to PPTX, PDF or Google Slides. Every deck is saved to the user's history.

> **Status:** being rebuilt as a FastAPI + React app. The original Streamlit prototype still lives in `app/` and will be removed once its logic is ported. See `agent_docs/architecture.md` for the phase plan and progress.

## Stack

- `backend/`: Python 3.12, FastAPI, SQLAlchemy 2 + Alembic, Pydantic v2, PostgreSQL, managed with `uv`.
- `frontend/`: React + TypeScript + Vite, using npm (`npm install`, `npm run dev` on :5173, `npm test`, `npm run build`).
- LLM: any OpenAI-compatible endpoint, chosen by env vars.
- Exports: python-pptx, LibreOffice headless (PDF), Google Drive API (Google Slides).

## Getting started

```bash
# Database
docker compose up -d db

# Backend
cd backend
cp ../.env.example .env   # then fill in the values
uv sync
uv run uvicorn app.main:app --reload   # http://localhost:8000/health
```

Checks before committing:

```bash
cd backend
uv run ruff check --fix . && uv run ruff format .
uv run pytest
```

## Legacy prototype

The Streamlit prototype needs Azure OpenAI env vars (`AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT_NAME`, `AZURE_OPENAI_API_VERSION`) and `pip install -r requirements.txt`, then `streamlit run app/main.py`. It is deprecated.

## License

MIT License © 2025 Ubeyd Khoiri
