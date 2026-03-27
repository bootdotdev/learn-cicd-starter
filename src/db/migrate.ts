import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { pool } from "./index";

async function run() {
  const sqlPath = resolve(process.cwd(), "src/db/schema.sql");
  const sql = readFileSync(sqlPath, "utf8");
  await pool.query(sql);
  console.log("Migrations applied");
  await pool.end();
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
