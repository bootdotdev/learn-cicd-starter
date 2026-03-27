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
            :root { color-scheme: light; }
            body {
              font-family: 'Inter', system-ui, sans-serif;
              color: #0f172a;
              margin: 0;
              background: linear-gradient(180deg, #eef2ff 0%, #f6f6f6 45%, #e8ebff 100%);
            }
            .page-shell {
              padding: 2.5rem 1rem 4rem;
              min-height: 100vh;
            }
            main {
              padding: 2.5rem;
              max-width: 1200px;
              margin: 0 auto;
              background: #ffffff;
              border-radius: 28px;
              box-shadow: 0 30px 50px rgba(15, 23, 42, 0.12);
              border: 1px solid rgba(148, 163, 184, 0.2);
            }
            h1 {
              margin-bottom: 0.25rem;
              font-size: 2.1rem;
            }
            .page-subtitle {
              margin: 0;
              color: #475569;
              font-size: 0.95rem;
            }
            .summary {
              display: grid;
              grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
              gap: 0.75rem;
              margin: 1.25rem 0;
            }
            .pill {
              background: #ffffff;
              border-radius: 999px;
              padding: 0.5rem 1rem;
              font-weight: 600;
              font-size: 0.9rem;
              box-shadow: 0 15px 25px rgba(15, 23, 42, 0.12);
              text-align: center;
            }
            .header-actions {
              margin-bottom: 1rem;
              display: flex;
              flex-wrap: wrap;
              gap: 0.5rem;
              align-items: center;
            }
            .badge {
              display: inline-flex;
              align-items: center;
              gap: 0.25rem;
              border-radius: 999px;
              padding: 0.3rem 0.8rem;
              font-size: 0.8rem;
              font-weight: 700;
              text-transform: capitalize;
            }
            .badge.ok {
              background: linear-gradient(135deg, #4ade80, #16a34a);
              color: white;
              box-shadow: 0 6px 15px rgba(34, 197, 94, 0.35);
            }
            .badge.pending {
              background: linear-gradient(135deg, #fde047, #f97316);
              color: #1f2937;
            }
            .badge.failed {
              background: linear-gradient(135deg, #fb7185, #dc2626);
              color: white;
              box-shadow: 0 6px 15px rgba(220, 38, 38, 0.35);
            }
            .button {
              display: inline-flex;
              align-items: center;
              gap: 0.5rem;
              padding: 0.6rem 1.4rem;
              border-radius: 999px;
              border: none;
              background: #2563eb;
              color: white;
              text-decoration: none;
              font-weight: 600;
              font-size: 0.9rem;
              transition: transform 0.15s ease, box-shadow 0.15s ease;
              box-shadow: 0 10px 20px rgba(37, 99, 235, 0.35);
            }
            .button:hover {
              transform: translateY(-2px);
              box-shadow: 0 14px 25px rgba(37, 99, 235, 0.35);
            }
            .button--ghost {
              background: rgba(37, 99, 235, 0.08);
              color: #2563eb;
              box-shadow: none;
              border: 1px solid rgba(37, 99, 235, 0.4);
            }
            .job-grid {
              display: grid;
              grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
              gap: 1rem;
            }
            .job-card {
              background: linear-gradient(180deg, #ffffff 0%, #fefefe 100%);
              border-radius: 26px;
              padding: 1.6rem;
              box-shadow: 0 20px 45px rgba(15, 23, 42, 0.08);
              border: 1px solid rgba(148, 163, 184, 0.18);
            }
            .job-card__top {
              display: flex;
              justify-content: space-between;
              gap: 1rem;
              align-items: flex-start;
            }
            .job-card h3 {
              margin: 0;
              font-size: 1.15rem;
            }
            .job-card__meta {
              margin: 0.15rem 0 0;
              color: #475569;
              font-size: 0.85rem;
            }
            .job-card__status-group {
              text-align: right;
            }
            .job-card__retry {
              display: block;
              margin-top: 0.25rem;
              color: #475569;
              font-size: 0.8rem;
            }
            .job-card__id {
              margin: 0.85rem 0 0;
              font-size: 0.95rem;
              color: #0f172a;
              font-weight: 600;
            }
            .job-card__timestamp {
              margin: 0.2rem 0 0.6rem;
              font-size: 0.78rem;
              color: #64748b;
            }
            .job-card__summary {
              margin: 0;
              font-size: 0.85rem;
              font-weight: 600;
              color: #1f2937;
            }
            .job-card__deliveries-title {
              margin: 1rem 0 0.4rem;
              font-size: 0.9rem;
              font-weight: 600;
              color: #1f2937;
            }
            .job-card__deliveries {
              overflow-x: auto;
              margin-top: 0.2rem;
              border-radius: 12px;
              background: #f8fafc;
              padding: 0.25rem;
            }
            table {
              width: 100%;
              border-collapse: collapse;
              margin-top: 0.4rem;
              font-size: 0.8rem;
              table-layout: fixed;
            }
            th,
            td {
              padding: 0.35rem 0.6rem;
              color: #0f172a;
              word-break: break-word;
            }
            th {
              background: #e2e8f0;
              font-weight: 600;
              font-size: 0.75rem;
              letter-spacing: 0.01em;
            }
            td {
              border-bottom: 1px solid #e2e8f0;
            }
            tbody tr:last-child td {
              border-bottom: none;
            }
            .empty {
              font-size: 0.85rem;
              color: #475569;
            }
          </style>`,
      `</head>`,
      `<body>`,
      `<div class="page-shell">`,
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
      `<p class="page-subtitle">Here are the most recent runs that hit your subscribers. Refresh the page to see live updates.</p>`,
      `<div class="header-actions">`,
      `<a class="button" href="?format=json" target="_blank">Download JSON</a>`,
      `<a class="button button--ghost" href="javascript:location.reload()">Refresh</a>`,
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
    const successfulDeliveries = job.deliveries.filter((d) => d.status === "succeeded").length;
    const deliverySummary = job.deliveries.length
      ? `${successfulDeliveries} succeeded / ${job.deliveries.length} total`
      : "No deliveries yet";

    html.push(
      `<article class="job-card">
            <div class="job-card__top">
              <div>
                <h3>${job.pipeline} / ${job.action}</h3>
                <p class="job-card__meta">${job.pipeline} · ${job.action}</p>
              </div>
              <div class="job-card__status-group">
                <span class="${badgeClass(job.status)}">${job.status}</span>
                <span class="job-card__retry">Retries: ${job.retryCount}</span>
              </div>
            </div>
            <p class="job-card__id">Job ${job.jobId}</p>
            <p class="job-card__timestamp">Updated ${new Date(job.updatedAt).toLocaleString()}</p>
            <p class="job-card__summary">${deliverySummary}</p>
            <div class="job-card__deliveries">
              <p class="job-card__deliveries-title">Deliveries</p>
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

    html.push("</div>", "</main>", "</div>", "</body>", "</html>");

    res.setHeader("Content-Type", "text/html; charset=utf-8");
    res.send(html.join("\n"));
  } catch (error) {
    next(error);
  }
});
