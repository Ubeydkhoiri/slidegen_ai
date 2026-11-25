# Architecture

## Request flow

1. The user signs in with Google. The backend creates or updates the `users` row and sets a session cookie.
2. `POST /api/generate {prompt, slide_count, language?}` makes the LLM client return a validated `Deck`. The backend saves it as a new `decks` row and returns its id.
3. The editor loads `GET /api/decks/{id}`. Edits autosave through `PUT /api/decks/{id}` (debounced). The request sends the `updated_at` it last saw; a stale value gets `409` so two tabs can't silently overwrite each other.
4. `POST /api/decks/{id}/export {format: "pptx" | "pdf" | "gslides"}`: PPTX and PDF stream back as files, and Google Slides returns a Drive link.
5. The history page lists `GET /api/decks` (the current user's decks only, newest first, paginated).

## Database tables

| table | key columns | notes |
|---|---|---|
| `users` | id (uuid), google_sub (unique), email (unique), name, avatar_url, created_at | |
| `oauth_accounts` | user_id, provider, refresh_token (encrypted), scopes, expires_at | Needed for the Drive export. Encrypt tokens with a key from env. |
| `decks` | id (uuid), user_id (FK, indexed), title, prompt, content (JSON, JSONB on Postgres), schema_version, created_at, updated_at, deleted_at | Soft delete. `content` is a serialized `Deck`. |
| `llm_generations` | id, user_id, deck_id (nullable), provider, model, prompt_version, prompt_tokens, completion_tokens, latency_ms, status, error, created_at | Used for per-user rate limits and cost tracking. |
| `deck_revisions` | deck_id, content, created_at | Phase 5, for restoring older versions. |

Use SQLAlchemy's `JSON` type with a JSONB variant on Postgres so tests can run on SQLite.

## Phase plan

Tick each item when it's merged, so the next session knows where things stand.

- [x] **Phase 0, foundations:** create the `backend/` skeleton (pyproject + uv, ruff, pytest, settings, `/health`); `docker-compose.yml` with Postgres; `.env.example`; create the `frontend/` Vite skeleton; add CI (GitHub Actions running lint, tests and build); fix `.gitignore` (it ignores `data/*`, but those files are committed anyway).
- [ ] **Phase 1, generation:** add the `Deck` schema, the LLM client with OpenAI-compatible providers and a fake provider, and `POST /api/generate`. Port the prompt from `app/llm/prompt_templates.py`.
- [ ] **Phase 2, auth and storage:** add Google sign-in, the `users` and `decks` tables with migrations, deck CRUD with ownership checks, and the history page.
- [ ] **Phase 3, editor:** build a 16:9 canvas with inline text editing, add, delete and reorder slides, change a slide's layout, pick a theme, autosave, and speaker notes.
- [ ] **Phase 4, exports:** add PPTX (port `app/utils/pptx_generator.py`), PDF through LibreOffice, and Google Slides.
- [ ] **Phase 5, polish:** let the AI regenerate or rewrite a single slide, add per-user daily limits in the UI, deck revisions, images, deployment. Then delete `app/` and `data/`.

## Deployment notes

- Keep costs near zero: a free or low-cost container host plus a free-tier managed Postgres.
- The backend has to run as a Docker image because the PDF exporter needs LibreOffice and fonts installed (see `exports.md`).
- The frontend is static (`npm run build`) and can be served by any static host or by the backend.
