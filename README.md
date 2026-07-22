# NarrativeOS

An autonomous, multi-client B2B outbound narrative platform. It grounds outreach in an evidence ledger, creates a five-stage narrative blueprint, and generates only the next required email. The seller profile is the only normal human approval point.

## Run locally

1. Copy `.env.example` to `.env`. Add `OPENAI_API_KEY` for model-generated profiles and copy; without it, the complete deterministic safety-first mode is used.
2. Run `docker compose up --build`.
3. Open `http://localhost:3000`. API documentation is at `http://localhost:8000/docs`.

FRAM and VIVA example clients and campaigns are seeded automatically. They are explicitly labeled examples; regenerate their profiles from approved source material before production use.

## Product flow

`Create client → ingest URLs/files → generate profile → edit/approve once → campaign → prospects/CSV → research → strategic intersection + blueprint → next email → export/send → outcome → next action`

PDF, PowerPoint, text, Markdown, and CSV source materials are supported. Seller sources are cached as extracted text. Prospect evidence is stored with source, fact, type, confidence, timestamp, volatility, and epistemic class. Copy falls down this ladder: verified company evidence → supported role evidence → market pressure → business-model inference → seller proof → industry pattern. Unknown evidence is never eligible.

## Targeted Decomposition Engine

The named GitHub repository was not visible to the connected GitHub installation, so the integration uses a deliberately narrow HTTP contract instead of guessing its internal code. Set:

```env
TDE_BASE_URL=https://your-tde-service.up.railway.app
TDE_API_TOKEN=...
```

The adapter calls `POST {TDE_BASE_URL}/api/decompose` with bearer authentication and this shape:

```json
{"seller_profile":{},"prospect":{"company_name":"","company_url":"","contact_title":""},"evidence":[{"source":"","fact":"","kind":"verified_fact","confidence":0.96}],"objective":"Find the most defensible seller-capability/prospect-opportunity intersection."}
```

The response may be any JSON object; it is stored as `targeted_decomposition` strategy context. Timeouts and errors fail open, allowing the evidence-safe built-in strategy to continue. Once repository access is available, align its route or add a small compatibility route with this contract.

## Railway

Create a Railway project with PostgreSQL and two services from this repository:

- API: root directory `/`, uses `railway.json`; set `DATABASE_URL`, `OPENAI_API_KEY`, `CORS_ORIGINS`, and optional TDE variables.
- Web: root directory `frontend`, Dockerfile `frontend/Dockerfile`; set `NEXT_PUBLIC_API_URL` to the API public URL at build time.

Railway supplies `PORT`. The API image seeds idempotently and exposes `/health`. For production, use private service networking for TDE and PostgreSQL, public networking only for web/API, and store tokens as Railway secrets.

## Batch contract

Import requires `company_url`. Supported standard columns are `company_name,contact_name,contact_title,contact_email,linkedin_url,additional_urls,notes,external_campaign_id`; unknown columns become custom fields. Separate additional URLs with `|`.

`GET /api/batch/export/{campaign_id}` returns only actionable next emails with all required automation fields. Repeated generation returns the existing ready email, so a run cannot create multiple sequence stages. Sent, stopped, replied, meeting, closed, and suppressed records are excluded as appropriate.

## Verification

From `backend`, install development dependencies and run `pytest`. Tests cover confidence thresholds, evidence-light language, one-email-only generation, stop conditions, reply classification, and CSV escaping/schema.

## Grounded decisions

- Strong and inexpensive models are independently configurable.
- Web research failures degrade to explicit evidence-light mode.
- Seller profile approval gates campaign creation.
- Ready email generation is idempotent.
- Reply outcomes stop or reschedule the state machine automatically.
- The CTA is auto-selected but remains editable in the copy workspace as requested.
- `create_all` is intentionally idempotent for the first Railway release; `migrations/001_initial.sql` records the initial migration boundary. Adopt Alembic before the first breaking schema change.
# DRiX-Mail-v2
