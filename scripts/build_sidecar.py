from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
AUTOMATION_ROOT = REPO_ROOT / "automation-core"
TAURI_BINARIES = REPO_ROOT / "apps" / "desktop" / "src-tauri" / "binaries"
DIST_DIR = AUTOMATION_ROOT / "dist"
BUILD_DIR = AUTOMATION_ROOT / "build"
SPEC_DIR = AUTOMATION_ROOT


def parse_target_triple(rustc_output: str) -> str:
    for line in rustc_output.splitlines():
        if line.startswith("host:"):
            return line.split(":", 1)[1].strip()
    raise ValueError("Failed to parse target triple from rustc output")


def output_binary_name(base_name: str, target_triple: str) -> str:
    extension = ".exe" if "windows" in target_triple else ""
    return f"{base_name}-{target_triple}{extension}"


def detect_target_triple() -> str:
    result = subprocess.run(
        ["rustc", "-Vv"],
        check=True,
        capture_output=True,
        text=True,
    )
    return parse_target_triple(result.stdout)


def build_sidecar(base_name: str, python_executable: str) -> Path:
    target_triple = detect_target_triple()
    output_name = output_binary_name(base_name, target_triple)

    subprocess.run(
        [
            python_executable,
            "-m",
            "PyInstaller",
            "--onefile",
            "--name",
            base_name,
            "app/main.py",
        ],
        check=True,
        cwd=AUTOMATION_ROOT,
        env=os.environ.copy(),
    )

    built_binary = DIST_DIR / f"{base_name}{'.exe' if output_name.endswith('.exe') else ''}"
    if not built_binary.exists():
        raise FileNotFoundError(f"Expected sidecar binary not found: {built_binary}")

    TAURI_BINARIES.mkdir(parents=True, exist_ok=True)
    final_binary = TAURI_BINARIES / output_name
    shutil.copy2(built_binary, final_binary)
    final_binary.chmod(0o755)
    return final_binary


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Quiet Studio Python bridge sidecar.")
    parser.add_argument("--name", default="quiet-studio-bridge")
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args()

    final_binary = build_sidecar(args.name, args.python)
    print(final_binary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
