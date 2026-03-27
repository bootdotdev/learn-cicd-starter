import { Router } from "express";
import crypto from "node:crypto";
import { pool, withTx } from "../db";
import { config } from "../config";
import { pipelineSchema } from "./validators";

export const pipelinesRouter = Router();

async function getPipelineById(id: string) {
  const pipelineResult = await pool.query(
    `SELECT id, name, webhook_key, action_type, action_config, created_at, updated_at
     FROM pipelines
     WHERE id = $1`,
    [id]
  );

  if (!pipelineResult.rowCount) return null;

  const subsResult = await pool.query(
    `SELECT target_url FROM subscribers WHERE pipeline_id = $1 ORDER BY created_at ASC`,
    [id]
  );

  const row = pipelineResult.rows[0];

  return {
    id: row.id,
    name: row.name,
    sourceUrl: `${config.baseUrl}/webhooks/${row.webhook_key}`,
    action: {
      type: row.action_type,
      config: row.action_config
    },
    subscribers: subsResult.rows.map((s) => s.target_url),
    createdAt: row.created_at,
    updatedAt: row.updated_at
  };
}

pipelinesRouter.post("/", async (req, res) => {
  const parsed = pipelineSchema.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ error: parsed.error.flatten() });
  }

  const webhookKey = crypto.randomBytes(12).toString("hex");

  const id = await withTx(async (client) => {
    const inserted = await client.query(
      `INSERT INTO pipelines (name, webhook_key, action_type, action_config)
       VALUES ($1, $2, $3, $4::jsonb)
       RETURNING id`,
      [
        parsed.data.name,
        webhookKey,
        parsed.data.action.type,
        JSON.stringify(parsed.data.action.config ?? {})
      ]
    );

    const pipelineId = inserted.rows[0].id as string;

    for (const targetUrl of parsed.data.subscribers) {
      await client.query(
        `INSERT INTO subscribers (pipeline_id, target_url) VALUES ($1, $2)
         ON CONFLICT (pipeline_id, target_url) DO NOTHING`,
        [pipelineId, targetUrl]
      );
    }

    return pipelineId;
  });

  const pipeline = await getPipelineById(id);
  return res.status(201).json(pipeline);
});

pipelinesRouter.get("/", async (_req, res) => {
  const result = await pool.query(
    `SELECT id FROM pipelines ORDER BY created_at DESC`
  );

  const pipelines = await Promise.all(result.rows.map((row) => getPipelineById(row.id)));
  return res.json(pipelines.filter(Boolean));
});

pipelinesRouter.get("/:id", async (req, res) => {
  const pipeline = await getPipelineById(req.params.id);
  if (!pipeline) return res.status(404).json({ error: "Pipeline not found" });
  return res.json(pipeline);
});

pipelinesRouter.put("/:id", async (req, res) => {
  const parsed = pipelineSchema.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ error: parsed.error.flatten() });
  }

  const exists = await pool.query(`SELECT id FROM pipelines WHERE id = $1`, [req.params.id]);
  if (!exists.rowCount) return res.status(404).json({ error: "Pipeline not found" });

  await withTx(async (client) => {
    await client.query(
      `UPDATE pipelines
       SET name = $1, action_type = $2, action_config = $3::jsonb, updated_at = NOW()
       WHERE id = $4`,
      [
        parsed.data.name,
        parsed.data.action.type,
        JSON.stringify(parsed.data.action.config ?? {}),
        req.params.id
      ]
    );

    await client.query(`DELETE FROM subscribers WHERE pipeline_id = $1`, [req.params.id]);

    for (const targetUrl of parsed.data.subscribers) {
      await client.query(
        `INSERT INTO subscribers (pipeline_id, target_url) VALUES ($1, $2)
         ON CONFLICT (pipeline_id, target_url) DO NOTHING`,
        [req.params.id, targetUrl]
      );
    }
  });

  const pipeline = await getPipelineById(req.params.id);
  return res.json(pipeline);
});

pipelinesRouter.delete("/:id", async (req, res) => {
  const result = await pool.query(`DELETE FROM pipelines WHERE id = $1 RETURNING id`, [req.params.id]);
  if (!result.rowCount) return res.status(404).json({ error: "Pipeline not found" });
  return res.status(204).send();
});
