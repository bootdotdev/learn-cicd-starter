import { Router } from "express";
import { pool } from "../db";

const JOB_LIMIT = 20;

export const dashboardRouter = Router();

async function fetchSummary() {
  const { rows } = await pool.query(
    `SELECT status, count(*) AS count
     FROM jobs
     WHERE created_at >= NOW() - INTERVAL '1 hour'
     GROUP BY status`
  );
  const map = new Map<string, number>();
  rows.forEach((row) => map.set(row.status, Number(row.count)));
  return map;
}

async function fetchSnapshot() {
  const { rows } = await pool.query(
    `SELECT COUNT(*) FILTER (WHERE status = 'succeeded') AS succeeded,
            COUNT(*) FILTER (WHERE status = 'pending') AS pending,
            COUNT(*) FILTER (WHERE status = 'failed') AS failed
     FROM jobs`
  );
  return rows[0];
}

async function fetchJobsWithDeliveries(): Promise<DashboardJob[]> {
  const { rows } = await pool.query(
    `SELECT j.id AS job_id,
            j.status AS job_status,
            j.retry_count,
            j.created_at AS job_created_at,
            j.updated_at AS job_updated_at,
            p.name AS pipeline_name,
            p.action_type,
            COALESCE(
              JSON_AGG(
                JSONB_BUILD_OBJECT(
                  'deliveryId', d.id,
                  'status', d.status,
                  'attemptCount', d.attempt_count,
                  'targetUrl', s.target_url,
                  'lastError', d.last_error,
                  'nextAttemptAt', d.next_attempt_at,
                  'createdAt', d.created_at
                )
              ) FILTER (WHERE d.id IS NOT NULL),
              '[]'
            ) AS deliveries
     FROM jobs j
     JOIN events e ON e.id = j.event_id
     JOIN pipelines p ON p.id = e.pipeline_id
     LEFT JOIN deliveries d ON d.job_id = j.id
     LEFT JOIN subscribers s ON s.id = d.subscriber_id
     GROUP BY j.id, p.name, p.action_type
     ORDER BY j.created_at DESC
     LIMIT $1`,
    [JOB_LIMIT]
  );
  return rows.map((row) => ({
    jobId: row.job_id,
    status: row.job_status,
    retryCount: row.retry_count,
    createdAt: row.job_created_at,
    updatedAt: row.job_updated_at,
    pipeline: row.pipeline_name,
    action: row.action_type,
    deliveries: (Array.isArray(row.deliveries) ? row.deliveries : []) as DashboardDelivery[]
  }));
}

export interface DashboardStats {
  lastHourSucceeded: number;
  lastHourPending: number;
  lastHourFailed: number;
  totalJobs: number;
  totalDeliveries: number;
}

export interface DashboardDelivery {
  deliveryId: string;
  status: string;
  attemptCount: number;
  targetUrl: string | null;
  lastError: string | null;
  nextAttemptAt: string | null;
  createdAt: string | null;
}

export interface DashboardJob {
  jobId: string;
  status: string;
  retryCount: number;
  createdAt: string;
  updatedAt: string;
  pipeline: string;
  action: string;
  deliveries: DashboardDelivery[];
}

dashboardRouter.get("/", async (req, res, next) => {
  try {
    const [summaryMap, snapshot, jobsResult, deliveriesCount] = await Promise.all([
      fetchSummary(),
      fetchSnapshot(),
      fetchJobsWithDeliveries(),
      pool.query("SELECT COUNT(*) AS count FROM deliveries")
    ]);

    const stats: DashboardStats = {
      lastHourSucceeded: summaryMap.get("succeeded") ?? 0,
      lastHourPending: summaryMap.get("pending") ?? 0,
      lastHourFailed: summaryMap.get("failed") ?? 0,
      totalJobs:
        Number(snapshot.succeeded ?? 0) +
        Number(snapshot.pending ?? 0) +
        Number(snapshot.failed ?? 0),
      totalDeliveries: Number(deliveriesCount.rows[0]?.count ?? 0)
    };

    const jobs = jobsResult;

    if (req.query.format === "json") {
      return res.json({ stats, jobs });
    }

    const html = [
      `<html>`,
      `<head>`,
      `<meta charset="utf-8"/>`,
      `<title>Pipeline Dashboard</title>`,
      `<style>
            body { font-family: 'Inter', system-ui, sans-serif; color: #0f172a; background: #f5f5ff; margin: 0; }
            main { padding: 2rem; max-width: 1200px; margin: 0 auto; }
            h1 { margin-bottom: 0.5rem; }
            .summary { display: flex; flex-wrap: wrap; gap: 0.75rem; margin-bottom: 1.5rem; }
            .pill { background: white; border-radius: 999px; padding: 0.35rem 0.9rem; font-weight: 600; box-shadow: 0 2px 6px rgba(15,23,42,0.08); }
            .job-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1rem; }
            .job-card { background: white; border-radius: 16px; padding: 1rem; box-shadow: 0 8px 18px rgba(15,23,42,0.08); }
            .job-card h3 { margin: 0 0 0.35rem; font-size: 1rem; }
            .badge { display: inline-flex; align-items: center; gap: 0.25rem; border-radius: 999px; padding: 0.2rem 0.65rem; font-size: 0.75rem; font-weight: 600; }
            .badge.ok { background: #16a34a; color: white; }
            .badge.pending { background: #facc15; color: #1f2937; }
            .badge.failed { background: #dc2626; color: white; }
            table { width: 100%; border-collapse: collapse; margin-top: 0.5rem; }
            th, td { padding: 0.35rem 0.6rem; font-size: 0.8rem; color: #0f172a; }
            th { background: #e2e8f0; text-align: left; }
            td { border-bottom: 1px solid #e2e8f0; }
            tbody tr:last-child td { border-bottom: none; }
            .empty { font-size: 0.85rem; color: #475569; }
          </style>`,
      `</head>`,
      `<body>`,
      `<main>`,
      `<h1>Pipeline observability</h1>`,
      `<p class="empty">Last updated: ${new Date().toISOString()}</p>`,
      `<div class="summary">`,
      `<span class="pill">Last hour succeeded: ${stats.lastHourSucceeded}</span>`,
      `<span class="pill">Last hour pending: ${stats.lastHourPending}</span>`,
      `<span class="pill">Last hour failed: ${stats.lastHourFailed}</span>`,
      `<span class="pill">Total jobs: ${stats.totalJobs}</span>`,
      `<span class="pill">Total deliveries: ${stats.totalDeliveries}</span>`,
      `</div>`,
      `<p class="empty">Showing ${jobsResult.length} most recent jobs</p>`,
      `<div class="job-grid">`
    ];

    const badgeClass = (status: string) => {
      if (status === "succeeded") return "badge ok";
      if (status === "failed") return "badge failed";
      return "badge pending";
    };

    for (const job of jobs) {
      html.push(
        `<article class="job-card">
            <h3>${job.pipeline} / ${job.action}</h3>
            <p><strong>Job</strong> ${job.jobId}</p>
            <p>
              <span class="${badgeClass(job.status)}">${job.status}</span>
              <span class="empty">retries: ${job.retryCount}</span>
            </p>
            <p class="empty">Updated at: ${new Date(job.updatedAt).toISOString()}</p>
            <div>
              <p style="margin-bottom:0.25rem"><strong>Deliveries</strong></p>
              ${job.deliveries.length ? `
                <table>
                  <thead>
                    <tr>
                      <th>Subscriber</th>
                      <th>Status</th>
                      <th>Attempts</th>
                      <th>Last error</th>
                    </tr>
                  </thead>
                  <tbody>
                    ${job.deliveries
                      .map((delivery) => `
                        <tr>
                          <td>${delivery.targetUrl ?? "-"}</td>
                          <td>${delivery.status}</td>
                          <td>${delivery.attemptCount}</td>
                          <td>${delivery.lastError ?? "-"}</td>
                        </tr>
                      `)
                      .join("")}
                  </tbody>
                </table>
              ` : `<p class="empty">No deliveries yet.</p>`}
            </div>
          </article>`
      );
    }

    html.push("</div>", "</main>", "</body>", "</html>");

    res.setHeader("Content-Type", "text/html; charset=utf-8");
    res.send(html.join("\n"));
  } catch (error) {
    next(error);
  }
});
