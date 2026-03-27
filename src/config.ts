import dotenv from "dotenv";

dotenv.config();

function intEnv(name: string, fallback: number): number {
  const raw = process.env[name];
  if (!raw) return fallback;
  const parsed = Number(raw);
  return Number.isFinite(parsed) ? parsed : fallback;
}

export const config = {
  port: intEnv("PORT", 8080),
  databaseUrl:
    process.env.DATABASE_URL ??
    "postgresql://pipeline:pipeline@localhost:5432/pipeline_db",
  baseUrl: process.env.BASE_URL ?? "http://localhost:8080",
  workerPollIntervalMs: intEnv("WORKER_POLL_INTERVAL_MS", 1000),
  jobMaxRetries: intEnv("JOB_MAX_RETRIES", 5),
  deliveryMaxRetries: intEnv("DELIVERY_MAX_RETRIES", 5),
  deliveryBackoffBaseMs: intEnv("DELIVERY_BACKOFF_BASE_MS", 1000),
  deliveryTimeoutMs: intEnv("DELIVERY_TIMEOUT_MS", 5000)
};
