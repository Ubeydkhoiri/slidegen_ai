# LLM integration

## Providers

Every supported provider exposes an OpenAI-compatible Chat Completions API, so the backend uses the `openai` Python SDK with a custom `base_url`. The prototype's LangChain and Azure dependencies are dropped.

The provider list is ordered and set entirely through env vars:

```
LLM_PROVIDERS=gemini,groq,openrouter        # tried in this order; "fake" in tests
LLM_GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
LLM_GEMINI_API_KEY=...
LLM_GEMINI_MODEL=...                         # set in .env, never in code
LLM_GROQ_BASE_URL=https://api.groq.com/openai/v1
LLM_OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
LLM_<NAME>_JSON_MODE=true|false              # whether the provider supports response_format json_object
LLM_DAILY_LIMIT_PER_USER=20
```

Local Ollama (`http://localhost:11434/v1`) works the same way for offline development.

Free models get renamed and retired often, so model ids live only in `.env` / `.env.example`. If a call fails with "model not found", fix the env and leave the code alone.

## Generation pipeline (`backend/app/llm/`)

1. Build the prompt from `prompts.py` with these parameters: topic, `slide_count` (default 8, range 3–20), language (default: the same language as the user's prompt), and an optional audience or tone. The first slide uses the `title` layout. Log `PROMPT_VERSION` with every generation.
2. Call the provider: 60 s timeout, and JSON mode when it's supported.
3. Parse the response: strip ```` ``` ```` fences before calling `json.loads`, then validate against `GeneratedDeck`.
4. If validation fails, retry once with the same provider and include the validation error in the retry. If it fails again, move on to the next provider.
5. On 429, 5xx or a timeout, move on to the next provider immediately. If every provider fails, return a clear `503` that the UI can show.
6. Write an `llm_generations` row for every attempt, whether it succeeded or failed.

## Rate limits and privacy

- Before calling any provider, check the user's generation count for the day against `LLM_DAILY_LIMIT_PER_USER`, and return `429` with a friendly message when they're over it. Free tiers have daily caps of their own, and this keeps one user from using them all up.
- Free tiers may use prompts to train their models. The UI shows a short notice, and the backend never adds the user's email or other personal data to prompts.

## Testing

- `FakeProvider` returns fixture decks from `backend/tests/fixtures/`. Tests set `LLM_PROVIDERS=fake`.
- Cover these cases: a valid response, fenced JSON, invalid JSON with a successful repair, a 429 that fails over to the next provider, and every provider failing.
