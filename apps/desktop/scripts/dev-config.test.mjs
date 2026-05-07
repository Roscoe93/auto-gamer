import test from "node:test";
import assert from "node:assert/strict";
import path from "node:path";

import {
  buildManagedProcesses,
  resolvePaths
} from "./dev-config.mjs";

test("resolvePaths derives repo, backend, and tauri directories", () => {
  const paths = resolvePaths("/tmp/repo/apps/desktop/scripts");

  assert.equal(paths.desktopRoot, path.resolve("/tmp/repo/apps/desktop"));
  assert.equal(paths.repoRoot, path.resolve("/tmp/repo"));
  assert.equal(paths.backendRoot, path.resolve("/tmp/repo/automation-core"));
  assert.equal(paths.tauriRoot, path.resolve("/tmp/repo/apps/desktop/src-tauri"));
});

test("buildManagedProcesses wires python, vite, and tauri commands", () => {
  const paths = {
    desktopRoot: "/repo/apps/desktop",
    repoRoot: "/repo",
    backendRoot: "/repo/automation-core",
    tauriRoot: "/repo/apps/desktop/src-tauri",
    nodeBinDir: "/runtime/node/bin",
    pnpmCliPath: "/opt/pnpm.cjs",
    pythonBinPath: "/runtime/python/bin/python3",
    cargoBinDir: "/Users/test/.cargo/bin"
  };

  const processes = buildManagedProcesses(paths);

  assert.equal(processes.length, 3);

  assert.deepEqual(
    processes.map(({ name, cwd }) => ({ name, cwd })),
    [
      { name: "bridge", cwd: "/repo/automation-core" },
      { name: "frontend", cwd: "/repo/apps/desktop" },
      { name: "tauri", cwd: "/repo/apps/desktop/src-tauri" }
    ]
  );

  assert.deepEqual(processes[0].args, ["-m", "app.main"]);
  assert.deepEqual(processes[1].args, ["/opt/pnpm.cjs", "dev:web", "--host", "127.0.0.1", "--port", "1420"]);
  assert.deepEqual(processes[2].args, ["run"]);
  assert.equal(processes[2].command, "cargo");
  assert.match(processes[2].env.PATH, /\/Users\/test\/\.cargo\/bin/);
  assert.match(processes[1].env.PATH, /\/runtime\/node\/bin/);
});
