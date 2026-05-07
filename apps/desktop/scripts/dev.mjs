import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";

import { buildManagedProcesses, resolvePaths } from "./dev-config.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const paths = resolvePaths(__dirname);
const children = [];

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function waitForPort(host, port, timeoutMs = 30_000) {
  const startedAt = Date.now();

  while (Date.now() - startedAt < timeoutMs) {
    const isOpen = await new Promise((resolve) => {
      const socket = new net.Socket();

      socket
        .once("connect", () => {
          socket.destroy();
          resolve(true);
        })
        .once("error", () => {
          socket.destroy();
          resolve(false);
        })
        .connect(port, host);
    });

    if (isOpen) {
      return;
    }

    await sleep(250);
  }

  throw new Error(`Timed out waiting for ${host}:${port}`);
}

async function waitForWebSocket(url, timeoutMs = 30_000) {
  const startedAt = Date.now();

  while (Date.now() - startedAt < timeoutMs) {
    const isReady = await new Promise((resolve) => {
      const socket = new WebSocket(url);

      socket.addEventListener("open", () => {
        socket.close();
        resolve(true);
      });
      socket.addEventListener("error", () => resolve(false));
    });

    if (isReady) {
      return;
    }

    await sleep(250);
  }

  throw new Error(`Timed out waiting for websocket ${url}`);
}

async function waitForHttp(url, timeoutMs = 30_000) {
  const startedAt = Date.now();

  while (Date.now() - startedAt < timeoutMs) {
    try {
      const response = await fetch(url);
      if (response.ok) {
        return;
      }
    } catch {
      // keep waiting
    }

    await sleep(250);
  }

  throw new Error(`Timed out waiting for http ${url}`);
}

function startProcess(spec) {
  const child = spawn(spec.command, spec.args, {
    cwd: spec.cwd,
    stdio: "inherit",
    env: spec.env
  });

  children.push(child);
  child.on("exit", (code) => {
    if (code && code !== 0) {
      stopAll(code);
    }
  });

  return child;
}

function stopAll(exitCode = 0) {
  while (children.length > 0) {
    const child = children.pop();
    if (child && !child.killed) {
      child.kill("SIGTERM");
    }
  }

  process.exit(exitCode);
}

process.on("SIGINT", () => stopAll(0));
process.on("SIGTERM", () => stopAll(0));

async function main() {
  const [bridgeSpec, frontendSpec, tauriSpec] = buildManagedProcesses(paths);

  startProcess(bridgeSpec);
  await waitForWebSocket("ws://127.0.0.1:8765");

  startProcess(frontendSpec);
  await waitForHttp("http://127.0.0.1:1420");

  startProcess(tauriSpec);
}

main().catch((error) => {
  console.error("[kuroneko-studio] dev bootstrap failed:", error);
  stopAll(1);
});
