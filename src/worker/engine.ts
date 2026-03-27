import { randomUUID } from "node:crypto";
import { pool, withTx } from "../db";
import { applyAction } from "../utils/actionProcessor";
import { PipelineAction } from "../types";
import { config } from "../config";
import { nextDelayMs } from "./retry";

async function claimPendingJob() {
  return withTx(async (client) => {
    const jobResult = await client.query(
      `SELECT id, event_id
       FROM jobs
       WHERE status = 'pending'
       ORDER BY created_at ASC
       FOR UPDATE SKIP LOCKED
       LIMIT 1`
    );

    if (!jobResult.rowCount) return null;

    const job = jobResult.rows[0];

    await client.query(
      `UPDATE jobs SET status = 'processing', updated_at = NOW() WHERE id = $1`,
      [job.id]
    );

    return { id: job.id as string, eventId: job.event_id as string };
  });
}

async function processJob(jobId: string, eventId: string) {
  try {
    const eventResult = await pool.query(
      `SELECT e.id, e.raw_payload, p.id AS pipeline_id, p.action_type, p.action_config
       FROM events e
       JOIN pipelines p ON p.id = e.pipeline_id
       WHERE e.id = $1`,
      [eventId]
    );

    if (!eventResult.rowCount) {
      await pool.query(
        `UPDATE jobs SET status = 'failed', last_error = $2, updated_at = NOW() WHERE id = $1`,
        [jobId, "Event not found"]
      );
      return;
    }

    const row = eventResult.rows[0];
    const action: PipelineAction = {
      type: row.action_type,
      config: row.action_config
    };

    const processed = applyAction(action, row.raw_payload, row.id);

    await withTx(async (client) => {
      await client.query(
        `UPDATE events SET processed_payload = $2::jsonb, processed_at = NOW() WHERE id = $1`,
        [row.id, JSON.stringify(processed)]
      );

      const subsResult = await client.query(
        `SELECT id FROM subscribers WHERE pipeline_id = $1`,
        [row.pipeline_id]
      );

      for (const sub of subsResult.rows) {
        await client.query(
          `INSERT INTO deliveries (id, job_id, subscriber_id, status, next_attempt_at)
           VALUES ($1, $2, $3, 'pending', NOW())
           ON CONFLICT (job_id, subscriber_id) DO NOTHING`,
          [randomUUID(), jobId, sub.id]
        );
      }

      await client.query(
        `UPDATE jobs SET status = 'dispatching', updated_at = NOW(), last_error = NULL WHERE id = $1`,
        [jobId]
      );
    });
  } catch (error) {
    const msg = error instanceof Error ? error.message : "Unknown processing error";

    await pool.query(
      `UPDATE jobs
       SET retry_count = retry_count + 1,
           status = CASE WHEN retry_count + 1 >= $2 THEN 'failed' ELSE 'pending' END,
           last_error = $3,
           updated_at = NOW()
       WHERE id = $1`,
      [jobId, config.jobMaxRetries, msg]
    );
  }
}

async function claimDelivery() {
  return withTx(async (client) => {
    const result = await client.query(
      `SELECT d.id, d.attempt_count, d.job_id, s.target_url, e.processed_payload, e.id AS event_id
       FROM deliveries d
       JOIN subscribers s ON s.id = d.subscriber_id
       JOIN jobs j ON j.id = d.job_id
       JOIN events e ON e.id = j.event_id
       WHERE d.status IN ('pending', 'retry')
         AND d.next_attempt_at <= NOW()
       ORDER BY d.created_at ASC
       FOR UPDATE SKIP LOCKED
       LIMIT 1`
    );

    if (!result.rowCount) return null;

    const row = result.rows[0];

    await client.query(
      `UPDATE deliveries
       SET status = 'retry', attempt_count = attempt_count + 1, updated_at = NOW()
       WHERE id = $1`,
      [row.id]
    );

    return {
      id: row.id as string,
      jobId: row.job_id as string,
      targetUrl: row.target_url as string,
      payload: row.processed_payload,
      eventId: row.event_id as string,
      attempt: (row.attempt_count as number) + 1
    };
  });
}

async function processDelivery(delivery: {
  id: string;
  jobId: string;
  targetUrl: string;
  payload: unknown;
  eventId: string;
  attempt: number;
}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), config.deliveryTimeoutMs);

  try {
    const response = await fetch(delivery.targetUrl, {
      method: "POST",
      headers: {
        "content-type": "application/json"
      },
      body: JSON.stringify({
        eventId: delivery.eventId,
        data: delivery.payload
      }),
      signal: controller.signal
    });

    clearTimeout(timeout);

    if (response.ok) {
      await pool.query(
        `UPDATE deliveries
         SET status = 'succeeded', response_status = $2, last_error = NULL, updated_at = NOW()
         WHERE id = $1`,
        [delivery.id, response.status]
      );
      return;
    }

    throw new Error(`HTTP ${response.status}`);
  } catch (error) {
    clearTimeout(timeout);

    const msg = error instanceof Error ? error.message : "Delivery failed";
    const failed = delivery.attempt >= config.deliveryMaxRetries;

    if (failed) {
      await pool.query(
        `UPDATE deliveries
         SET status = 'failed', last_error = $2, updated_at = NOW()
         WHERE id = $1`,
        [delivery.id, msg]
      );
      return;
    }

    const delayMs = nextDelayMs(config.deliveryBackoffBaseMs, delivery.attempt);

    await pool.query(
      `UPDATE deliveries
       SET status = 'retry',
           last_error = $2,
           next_attempt_at = NOW() + ($3 || ' milliseconds')::interval,
           updated_at = NOW()
       WHERE id = $1`,
      [delivery.id, msg, `${delayMs}`]
    );
  }
}

async function finalizeDispatchingJobs() {
  const result = await pool.query(
    `SELECT j.id,
            SUM(CASE WHEN d.status IN ('pending', 'retry') THEN 1 ELSE 0 END) AS active_count,
            SUM(CASE WHEN d.status = 'failed' THEN 1 ELSE 0 END) AS failed_count
     FROM jobs j
     LEFT JOIN deliveries d ON d.job_id = j.id
     WHERE j.status = 'dispatching'
     GROUP BY j.id`
  );

  for (const row of result.rows) {
    const active = Number(row.active_count);
    if (active > 0) continue;

    const failed = Number(row.failed_count);
    const status = failed > 0 ? "failed" : "succeeded";

    await pool.query(
      `UPDATE jobs SET status = $2, updated_at = NOW() WHERE id = $1`,
      [row.id, status]
    );
  }
}

export async function runWorkerCycle() {
  const job = await claimPendingJob();
  if (job) await processJob(job.id, job.eventId);

  const delivery = await claimDelivery();
  if (delivery) await processDelivery(delivery);

  await finalizeDispatchingJobs();
}
