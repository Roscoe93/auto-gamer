import path from "node:path";

function prependPath(nextPath, currentPath) {
  if (!currentPath) {
    return nextPath;
  }

  return `${nextPath}:${currentPath}`;
}

function withPathEnv(currentEnv, extraPath) {
  return {
    ...currentEnv,
    PATH: prependPath(extraPath, currentEnv.PATH ?? "")
  };
}

export function resolveBundlePaths(scriptsDir) {
  const desktopRoot = path.resolve(scriptsDir, "..");
  const repoRoot = path.resolve(desktopRoot, "..", "..");

  return {
    desktopRoot,
    repoRoot,
    tauriRoot: path.resolve(desktopRoot, "src-tauri"),
    sidecarBuildScript: path.resolve(repoRoot, "scripts", "build_sidecar.py"),
    nodeBinDir: process.execPath ? path.dirname(process.execPath) : "",
    pnpmCliPath: "/opt/homebrew/lib/node_modules/pnpm/bin/pnpm.cjs",
    pythonBinPath:
      process.env.KURONEKO_STUDIO_PYTHON ??
      "/Users/bytedance/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3",
    cargoBinDir: path.resolve(process.env.HOME ?? "~", ".cargo", "bin")
  };
}

export function buildBundleSteps(paths) {
  return [
    {
      name: "sidecar",
      command: paths.pythonBinPath,
      args: [paths.sidecarBuildScript, "--python", paths.pythonBinPath],
      cwd: paths.repoRoot,
      env: { ...process.env }
    },
    {
      name: "frontend",
      command: paths.nodeBinDir ? path.join(paths.nodeBinDir, "node") : "node",
      args: [paths.pnpmCliPath, "build"],
      cwd: paths.desktopRoot,
      env: withPathEnv(process.env, paths.nodeBinDir)
    },
    {
      name: "tauri-bundle",
      command: "cargo",
      args: ["tauri", "build", "--bundles", "app"],
      cwd: paths.tauriRoot,
      env: withPathEnv(process.env, paths.cargoBinDir)
    }
  ];
}
