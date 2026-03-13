# Webhook-Driven Task Processing Pipeline

TypeScript service that receives webhooks, queues background jobs, processes payloads, and delivers results to subscribers with retry logic.

## Architecture

- `API service` (Express):
  - CRUD for pipelines
  - webhook ingestion endpoint `/webhooks/:webhookKey`
- `PostgreSQL`:
  - stores pipelines, events, jobs, and per-subscriber delivery attempts
- `Worker service`:
  - pulls pending jobs
  - applies action types
  - delivers results to subscribers with exponential backoff retries

## Action Types

1. `uppercase`: uppercases all string values in payload recursively
2. `pick_fields`: keeps only selected fields (`config.fields`)
3. `add_metadata`: appends processing metadata (`eventId`, `processedAt`)

## Data Flow

1. Create pipeline via `POST /pipelines`
2. Send webhook to generated `sourceUrl`
3. API stores event and enqueues job (`202 Accepted`)
4. Worker processes action and creates delivery rows
5. Worker POSTs to subscribers with retry on failure
6. Job becomes `succeeded` or `failed`

## API

### Create pipeline

`POST /pipelines`

```json
{
  "name": "Order pipeline",
  "action": {
    "type": "pick_fields",
    "config": { "fields": ["orderId", "status"] }
  },
  "subscribers": [
    "https://example.com/hook-1",
    "https://example.com/hook-2"
  ]
}
```

### List pipelines

`GET /pipelines`

### Get pipeline

`GET /pipelines/:id`

### Update pipeline

`PUT /pipelines/:id`

### Delete pipeline

`DELETE /pipelines/:id`

### Ingest webhook

`POST /webhooks/:webhookKey`

Body: any JSON payload.

## Local Run (Docker)

```bash
cp .env.example .env
docker compose up --build
```

API base URL: `http://localhost:8080`

Health check:

```bash
curl http://localhost:8080/health
```

## Local Run (without Docker)

```bash
npm ci
cp .env.example .env
npm run migrate
npm run dev
```

In another terminal:

```bash
npm run dev:worker
```

## Demo flow (ready-made script)

Run the helper once the Docker stack is healthy to capture the entire end-to-end experience:

```bash
cp .env.example .env
npm run build
docker compose up --build -d
curl http://localhost:8080/health        # must return {"ok":true }
./scripts/demo-flow.sh
```

Output includes:
1. `sourceUrl` from pipeline creation and the webhook `Accepted` response.
2. Worker log segment showing job pickup and delivery.
3. Latest `jobs`/`deliveries` rows from PostgreSQL.
4. The mock subscriber log with the final payload (includes `_metadata`).

Use `./scripts/demo-flow.sh | tee demo-output.log` to preserve the narrative for your video.

## Observability UI

The new `/dashboard` route gives you a live view of the pipeline runtime data without dropping to SQL:

- **Summary pills** track succeeded/pending/failed counts for the last hour and the total number of jobs/deliveries so you can talk about overall health at a glance.
- **Job grid** shows the 20 most recent jobs with status badges, retry counts, timestamps, and the pipeline + action that created them.
- **Delivery tables** under each job card list every subscriber, attempt count, and last error to explain why retries happen.
- **JSON export**: add `?format=json` for the same payload as structured data, which you can plug into monitoring dashboards or automated alerts.

Pointing your browser to `http://localhost:8080/dashboard` after starting the stack (`npm run build && docker compose up --build -d`) is enough to exercise the UI.

## CI/CD status

- `ci.yml` (Node build + tests) passes on the main branch and mirrors the local `npm ci`, `npm test`, and `npm run build` workflow.
- `cd.yml` builds the Docker image and deploys to Cloud Run but currently requires a linked GCP billing account because the Cloud Build step fails if the `notely-dana` project billing is not active (`google-github-actions/auth` and `gcloud builds submit`). Run `gh workflow run cd` after enabling billing and supplying the required secrets (`DATABASE_URL`, `GCP_CREDENTIALS` or workload identity inputs).

During the demo video, narrate:
1. Stack composition (API + worker + Postgres). 2. Pipeline creation + webhook ingestion. 3. Job lifecycle (`jobs` rows showing `dispatching -> succeeded`). 4. Delivery retries/exhaustion and the mock subscriber log confirming payload delivery. 5. CI/CD status and next steps for finishing the Cloud Run publish.
