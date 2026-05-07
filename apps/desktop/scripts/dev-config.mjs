import path from "node:path";

export function resolvePaths(scriptsDir) {
  const desktopRoot = path.resolve(scriptsDir, "..");
  const repoRoot = path.resolve(desktopRoot, "..", "..");

  return {
    desktopRoot,
    repoRoot,
    backendRoot: path.resolve(repoRoot, "automation-core"),
    tauriRoot: path.resolve(desktopRoot, "src-tauri"),
    nodeBinDir: process.execPath ? path.dirname(process.execPath) : "",
    pnpmCliPath: "/opt/homebrew/lib/node_modules/pnpm/bin/pnpm.cjs",
    pythonBinPath:
      process.env.QUIET_STUDIO_PYTHON ??
      "/Users/bytedance/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3",
    cargoBinDir: path.resolve(process.env.HOME ?? "~", ".cargo", "bin")
  };
}

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

export function buildManagedProcesses(paths) {
  return [
    {
      name: "bridge",
      command: paths.pythonBinPath,
      args: ["-m", "app.main"],
      cwd: paths.backendRoot,
      env: { ...process.env }
    },
    {
      name: "frontend",
      command: paths.nodeBinDir ? path.join(paths.nodeBinDir, "node") : "node",
      args: [paths.pnpmCliPath, "dev:web", "--host", "127.0.0.1", "--port", "1420"],
      cwd: paths.desktopRoot,
      env: withPathEnv(process.env, paths.nodeBinDir)
    },
    {
      name: "tauri",
      command: "cargo",
      args: ["run"],
      cwd: paths.tauriRoot,
      env: withPathEnv(process.env, paths.cargoBinDir)
    }
  ];
}
