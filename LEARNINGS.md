# Learnings — Learn CI/CD (Notely)

Notes from Boot.dev’s Learn CI/CD course, applied to this Notely Go app.

## Continuous Integration (CI)

- **Trigger on PRs, not only on merge.** The `ci` workflow runs on `pull_request` to `main`, so broken tests or style issues are caught before merge.
- **Separate concerns into parallel jobs.** `tests` and `style` run as independent jobs on `ubuntu-latest`. Failures are clearer, and the pipeline finishes faster when they run in parallel.
- **Pin the toolchain.** `actions/setup-go` with an explicit `go-version` keeps local and CI builds aligned.
- **Tests belong in CI.** `go test ./... -cover` runs on every PR. A failing test (intentionally or not) blocks the pipeline — that feedback loop is the point.
- **Style is automated, not optional.**
  - `go fmt`: `test -z $(go fmt ./...)` fails if any file would be reformatted.
  - `staticcheck`: catches bugs and smell that the compiler misses.
- **Security scanning in CI.** `gosec ./...` looks for common Go security issues. Treat findings as build failures, then fix them (don’t just silence the tool).
- **Status badges.** A badge in the README (e.g. for `ci.yml`) makes pipeline health visible without opening the Actions tab.

## Continuous Deployment (CD)

- **Deploy on push to `main`.** The `cd` workflow assumes `main` is the release branch: merge → build → ship.
- **Build for the target platform.** `scripts/buildprod.sh` cross-compiles with `CGO_ENABLED=0 GOOS=linux GOARCH=amd64` so the binary runs in a Linux container even if you develop on macOS.
- **Keep the image thin.** The Dockerfile is a slim Debian image that only adds the prebuilt `notely` binary and CA certs — no Go toolchain in the runtime image.
- **Migrations before (or with) deploy.** Run Goose (`./scripts/migrateup.sh`) in CD so the schema is ready before the new Cloud Run revision serves traffic.
- **Cap scale early.** `--max-instances=4` on Cloud Run limits surprise cost while learning.

## Secrets & config

- **Never commit secrets.** `.env` is gitignored. CI/CD reads `DATABASE_URL` and `GCP_CREDENTIALS` from GitHub Actions secrets.
- **Same app, different envs.** Locally, missing `DATABASE_URL` means “no DB mode.” In CD, the secret must be set or migrations and CRUD fail.
- **Service account JSON in Actions.** `google-github-actions/auth` with `credentials_json` from a secret authenticates `gcloud` without interactive login.

## Google Cloud pieces

- **Artifact Registry** stores the Docker image (`…/notely-ar-repo/notely:latest`).
- **Cloud Build** builds and pushes from the repo (`gcloud builds submit --tag …`).
- **Cloud Run** runs the container (`gcloud run deploy … --allow-unauthenticated` for a public demo).
- **IAM matters.** The default Compute Engine service account needs roles like Cloud Build builder and Storage object viewer on the Cloud Build bucket — otherwise you get errors such as `Permission 'storage.objects.get' denied`. Fixing IAM is part of making CD work, not optional ops trivia. See `CLOUD_BUILD_SETUP.md` for the exact bindings used here.

## Workflow habits that stuck

1. Open a PR → watch CI (tests, fmt, staticcheck, gosec).
2. Merge to `main` → CD builds Linux binary → Cloud Build image → migrate DB → deploy Cloud Run.
3. Prefer small, reversible steps: add a CI step, confirm it fails correctly, then make it pass.
4. Document one-off GCP/IAM fixes so the next deploy doesn’t start from “why is permission denied?”

## Stack at a glance

| Layer | Choice |
| --- | --- |
| App | Go + Chi, Turso/libSQL, Goose migrations |
| CI | GitHub Actions (`ci.yml`) |
| CD | GitHub Actions (`cd.yml`) → GCP |
| Runtime | Cloud Run + Artifact Registry |

## Takeaway

CI is the automated gate on every change; CD is the automated path from a green `main` to a running service. Most of the friction was not YAML syntax — it was making tests honest, keeping secrets out of git, and giving GCP service accounts the right permissions end to end.
