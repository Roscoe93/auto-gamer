#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DESKTOP_ROOT="$REPO_ROOT/apps/desktop"
BACKEND_ROOT="$REPO_ROOT/automation-core"
NVMRC_PATH="$REPO_ROOT/.nvmrc"

BUNDLED_NODE="/Users/bytedance/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
PNPM_CLI="/opt/homebrew/lib/node_modules/pnpm/bin/pnpm.cjs"
BUNDLED_PYTHON="/Users/bytedance/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"
RUSTUP_INSTALL_URL="https://sh.rustup.rs"

echo "[kuroneko-studio] 初始化开发环境"

if [ -f "$NVMRC_PATH" ]; then
  REQUIRED_NODE_VERSION="$(tr -d '[:space:]' < "$NVMRC_PATH")"
else
  echo "[kuroneko-studio] 缺少 .nvmrc，无法确认 Node 版本约束"
  exit 1
fi

if [ -z "${NVM_DIR:-}" ]; then
  NVM_DIR="$HOME/.nvm"
fi

if [ -s "$NVM_DIR/nvm.sh" ]; then
  # shellcheck disable=SC1090
  source "$NVM_DIR/nvm.sh"
fi

if [ -x "$BUNDLED_PYTHON" ]; then
  PYTHON_CMD="$BUNDLED_PYTHON"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD="$(command -v python3)"
else
  echo "[kuroneko-studio] 未找到 python3"
  exit 1
fi

if command -v nvm >/dev/null 2>&1; then
  echo "[kuroneko-studio] 使用 nvm 安装并切换 Node $REQUIRED_NODE_VERSION"
  nvm install "$REQUIRED_NODE_VERSION"
  nvm use "$REQUIRED_NODE_VERSION"
fi

if command -v node >/dev/null 2>&1; then
  NODE_VERSION="$(node -v)"
else
  NODE_VERSION=""
fi

if [ "$NODE_VERSION" != "$REQUIRED_NODE_VERSION" ] && [ -x "$BUNDLED_NODE" ]; then
  echo "[kuroneko-studio] 当前 Node 版本为 ${NODE_VERSION:-missing}，脚本将使用 bundled Node $("$BUNDLED_NODE" -v)"
fi

if [ "$NODE_VERSION" = "$REQUIRED_NODE_VERSION" ] && command -v pnpm >/dev/null 2>&1; then
  PNPM_CMD=("$(command -v pnpm)")
elif [ -x "$BUNDLED_NODE" ] && [ -f "$PNPM_CLI" ]; then
  PNPM_CMD=("$BUNDLED_NODE" "$PNPM_CLI")
else
  echo "[kuroneko-studio] 未找到 pnpm，也没有可用的 bundled node + pnpm"
  exit 1
fi

if ! command -v rustc >/dev/null 2>&1 || ! command -v cargo >/dev/null 2>&1; then
  echo "[kuroneko-studio] 未检测到 Rust 工具链，开始安装 rustup"
  curl "$RUSTUP_INSTALL_URL" -sSf | sh -s -- -y
  # shellcheck disable=SC1090
  source "$HOME/.cargo/env"
fi

echo "[kuroneko-studio] 安装 Python 依赖"
"$PYTHON_CMD" -m pip install -r "$BACKEND_ROOT/requirements.txt"

echo "[kuroneko-studio] 安装前端依赖"
(
  cd "$DESKTOP_ROOT"
  "${PNPM_CMD[@]}" install
)

echo "[kuroneko-studio] 验证前端脚本测试"
(
  cd "$DESKTOP_ROOT"
  "${PNPM_CMD[@]}" test:scripts
)

echo "[kuroneko-studio] 开发环境初始化完成"
echo "[kuroneko-studio] Node 版本锁定为：$REQUIRED_NODE_VERSION"
echo "[kuroneko-studio] 启动开发环境："
echo "  cd \"$REPO_ROOT\" && nvm use && cd \"$DESKTOP_ROOT\" && ${PNPM_CMD[*]} dev"
