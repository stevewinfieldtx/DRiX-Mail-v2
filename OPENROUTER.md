# OpenRouter configuration

NarrativeOS supports OpenRouter through its OpenAI-compatible API. Copy
`.env.openrouter.example` to `.env`, then set your real values:

```env
OPENROUTER_API_KEY=...
OPENROUTER_MODEL_ID=...
```

`OPENROUTER_MODEL_ID` is used for both evidence extraction/classification and
strategic narrative/copy. The two stages remain separate in the application, so
different OpenRouter model IDs can be added later without changing the workflow.

When `OPENROUTER_API_KEY` is present it takes precedence over `OPENAI_API_KEY`.
If neither is present, the deterministic evidence-safe fallback remains active.

For Railway, add both variables to the API service. Do not expose the key to the
web service or prefix it with `NEXT_PUBLIC_`.
