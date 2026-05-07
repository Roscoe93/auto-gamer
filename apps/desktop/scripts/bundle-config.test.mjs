import test from "node:test";
import assert from "node:assert/strict";
import path from "node:path";

import {
  buildBundleSteps,
  resolveBundlePaths
} from "./bundle-config.mjs";

test("resolveBundlePaths derives repo, tauri, and helper script locations", () => {
  const paths = resolveBundlePaths("/tmp/repo/apps/desktop/scripts");

  assert.equal(paths.desktopRoot, path.resolve("/tmp/repo/apps/desktop"));
  assert.equal(paths.repoRoot, path.resolve("/tmp/repo"));
  assert.equal(paths.tauriRoot, path.resolve("/tmp/repo/apps/desktop/src-tauri"));
  assert.equal(paths.sidecarBuildScript, path.resolve("/tmp/repo/scripts/build_sidecar.py"));
});

test("buildBundleSteps wires sidecar, web, and tauri bundle commands", () => {
  const paths = {
    desktopRoot: "/repo/apps/desktop",
    repoRoot: "/repo",
    tauriRoot: "/repo/apps/desktop/src-tauri",
    sidecarBuildScript: "/repo/scripts/build_sidecar.py",
    nodeBinDir: "/runtime/node/bin",
    pnpmCliPath: "/opt/pnpm.cjs",
    pythonBinPath: "/runtime/python/bin/python3",
    cargoBinDir: "/Users/test/.cargo/bin"
  };

  const steps = buildBundleSteps(paths);

  assert.equal(steps.length, 3);
  assert.deepEqual(
    steps.map(({ name, cwd }) => ({ name, cwd })),
    [
      { name: "sidecar", cwd: "/repo" },
      { name: "frontend", cwd: "/repo/apps/desktop" },
      { name: "tauri-bundle", cwd: "/repo/apps/desktop/src-tauri" }
    ]
  );
  assert.deepEqual(steps[0].args, ["/repo/scripts/build_sidecar.py", "--python", "/runtime/python/bin/python3"]);
  assert.deepEqual(steps[1].args, ["/opt/pnpm.cjs", "build"]);
  assert.deepEqual(steps[2].args, ["tauri", "build", "--bundles", "app"]);
  assert.equal(steps[0].command, "/runtime/python/bin/python3");
  assert.equal(steps[1].command, path.join("/runtime/node/bin", "node"));
  assert.equal(steps[2].command, "cargo");
  assert.match(steps[1].env.PATH, /\/runtime\/node\/bin/);
  assert.match(steps[2].env.PATH, /\/Users\/test\/\.cargo\/bin/);
});
