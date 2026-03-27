import { config } from "./config";
import { runWorkerCycle } from "./worker/engine";

async function loop() {
  console.log("Worker started");
  while (true) {
    try {
      await runWorkerCycle();
    } catch (err) {
      console.error("Worker cycle failed", err);
    }
    await new Promise((resolve) => setTimeout(resolve, config.workerPollIntervalMs));
  }
}

loop().catch((err) => {
  console.error(err);
  process.exit(1);
});
