import { pool } from "./index";

async function run() {
  const inserted = await pool.query(
    `INSERT INTO pipelines (name, webhook_key, action_type, action_config)
     VALUES ($1, $2, $3, $4::jsonb)
     ON CONFLICT (webhook_key) DO UPDATE SET name = EXCLUDED.name
     RETURNING id, webhook_key`,
    ["Demo Pipeline", "demo-webhook", "add_metadata", "{}"]
  );

  const pipelineId = inserted.rows[0].id as string;

  await pool.query(
    `INSERT INTO subscribers (pipeline_id, target_url)
     VALUES ($1, $2)
     ON CONFLICT (pipeline_id, target_url) DO NOTHING`,
    [pipelineId, "http://host.docker.internal:9000/mock-subscriber"]
  );

  console.log("Seed complete");
  await pool.end();
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
