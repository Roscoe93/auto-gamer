import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  buildBundleSteps,
  resolveBundlePaths
} from "./bundle-config.mjs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function runStep(step) {
  return new Promise((resolve, reject) => {
    const child = spawn(step.command, step.args, {
      cwd: step.cwd,
      env: step.env,
      stdio: "inherit"
    });

    child.on("error", reject);
    child.on("exit", (code, signal) => {
      if (code === 0) {
        resolve();
        return;
      }

      reject(new Error(`${step.name} exited with code ${code ?? "null"} signal ${signal ?? "null"}`));
    });
  });
}

async function main() {
  const paths = resolveBundlePaths(__dirname);
  const steps = buildBundleSteps(paths);

  for (const step of steps) {
    console.log(`\n==> ${step.name}`);
    await runStep(step);
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
