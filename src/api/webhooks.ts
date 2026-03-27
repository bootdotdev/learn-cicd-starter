import { Router } from "express";
import { withTx } from "../db";

export const webhooksRouter = Router();

webhooksRouter.post("/:webhookKey", async (req, res) => {
  const payload = req.body ?? {};

  const created = await withTx(async (client) => {
    const pipelineResult = await client.query(
      `SELECT id FROM pipelines WHERE webhook_key = $1`,
      [req.params.webhookKey]
    );

    if (!pipelineResult.rowCount) return null;

    const pipelineId = pipelineResult.rows[0].id as string;

    const eventResult = await client.query(
      `INSERT INTO events (pipeline_id, raw_payload)
       VALUES ($1, $2::jsonb)
       RETURNING id`,
      [pipelineId, JSON.stringify(payload)]
    );

    const eventId = eventResult.rows[0].id as string;

    const jobResult = await client.query(
      `INSERT INTO jobs (event_id, status)
       VALUES ($1, 'pending')
       RETURNING id`,
      [eventId]
    );

    return {
      eventId,
      jobId: jobResult.rows[0].id
    };
  });

  if (!created) {
    return res.status(404).json({ error: "Webhook source not found" });
  }

  return res.status(202).json({ message: "Accepted", ...created });
});
