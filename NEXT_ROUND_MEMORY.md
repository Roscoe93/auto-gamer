# 下一轮对话记忆文件

## 1. 当前目标背景

项目是 `Quiet Studio`，一个 `Windows + macOS` 的桌面游戏自动化操作台。

当前方向已经明确：

- UI 采用 `Quiet Studio` 视觉方向
- 架构采用 `Tauri + React + TypeScript + Python bridge`
- 通信采用本地 `WebSocket`
- 后端扩展性通过 `GameAdapter + FlowScript + helpers + profile/templates`

## 2. 当前文档状态

已存在并已更新的文档：

- [README.md](/Users/bytedance/git/game-auto-cross-platform-solution/README.md)
- [quiet-studio-technical-design.md](/Users/bytedance/git/game-auto-cross-platform-solution/quiet-studio-technical-design.md)
- [quiet-studio-development-tasks.md](/Users/bytedance/git/game-auto-cross-platform-solution/quiet-studio-development-tasks.md)

本轮已额外补充：

- 技术设计里增加了“发布态 sidecar 打包与生命周期管理”说明
- 任务清单里增加了“Python sidecar 打包、externalBin、Rust 接管 sidecar 生命周期、退出自动关闭 sidecar”的任务和准出标准
- README 已补充 `pnpm bundle` 用法、bundle 产物位置和 sidecar 生命周期说明
- 仓库根目录已新增 `.nvmrc`，锁定 Node 版本为 `v24.14.0`

## 3. 当前代码状态

### 已完成

阶段 1 基本已落地：

- Python bridge 最小实现：
  - `connection/status`
  - `connection/heartbeat`
  - `session/get`
- Python 测试通过：
  - `automation-core/tests/test_websocket_server.py`
- React 前端骨架已落地：
  - 连接状态
  - 心跳
  - session 摘要展示
- Tauri 基础工程已落地
- `pnpm build` 可通过
- Rust 工具链已安装
- Tauri 已经在本机成功 `cargo run`
- Python sidecar 已可构建为独立二进制并复制到 `src-tauri/binaries`
- Tauri CLI 已安装
- `pnpm bundle` 已打通
- macOS `.app` 启动时会自动拉起 sidecar，退出时会自动关闭 sidecar
- `apps/desktop/package.json` 已增加 `engines.node = 24.14.0`
- `scripts/setup-dev.sh` 已接入 `.nvmrc` 检查，并在可用时自动执行 `nvm install` / `nvm use`

### 已完成的一键启动能力

当前 `pnpm dev` 已经是真正的一键启动，会按顺序拉起：

1. Python bridge
2. Vite dev server
3. Tauri desktop shell

关键文件：

- [apps/desktop/scripts/dev.mjs](/Users/bytedance/git/game-auto-cross-platform-solution/apps/desktop/scripts/dev.mjs)
- [apps/desktop/scripts/dev-config.mjs](/Users/bytedance/git/game-auto-cross-platform-solution/apps/desktop/scripts/dev-config.mjs)
- [apps/desktop/scripts/dev-config.test.mjs](/Users/bytedance/git/game-auto-cross-platform-solution/apps/desktop/scripts/dev-config.test.mjs)

### 已完成的一键初始化能力

已新增：

- [scripts/setup-dev.sh](/Users/bytedance/git/game-auto-cross-platform-solution/scripts/setup-dev.sh)

它会：

- 检查并安装 Rust 工具链
- 安装 Python 依赖
- 安装前端依赖
- 跑脚本测试

### 已完成的一键 bundle 能力

已新增：

- [scripts/build_sidecar.py](/Users/bytedance/git/game-auto-cross-platform-solution/scripts/build_sidecar.py)
- [apps/desktop/scripts/bundle.mjs](/Users/bytedance/git/game-auto-cross-platform-solution/apps/desktop/scripts/bundle.mjs)
- [apps/desktop/scripts/bundle-config.mjs](/Users/bytedance/git/game-auto-cross-platform-solution/apps/desktop/scripts/bundle-config.mjs)
- [apps/desktop/scripts/bundle-config.test.mjs](/Users/bytedance/git/game-auto-cross-platform-solution/apps/desktop/scripts/bundle-config.test.mjs)

当前 `pnpm bundle` 会顺序执行：

1. 构建 Python sidecar
2. 构建前端静态资源
3. 构建 Tauri macOS `.app` bundle

## 4. 已验证结果

本轮已经实测通过：

- `python -m unittest automation-core/tests/test_websocket_server.py -v`
- `pnpm test:scripts`
- `pnpm build`
- `pnpm dev`
- `cargo run`（在 `apps/desktop/src-tauri` 下）
- `cargo test`（在 `apps/desktop/src-tauri` 下）
- `cargo tauri build --bundles app`
- `pnpm bundle`
- `node -v`（bundled Node）=`v24.14.0`

本轮也做了 bundle 生命周期实测：

1. 启动 `/Users/bytedance/git/game-auto-cross-platform-solution/apps/desktop/src-tauri/target/release/bundle/macos/Quiet Studio.app`
2. 确认主进程 `quiet_studio_desktop` 和 sidecar `quiet-studio-bridge` 同时启动
3. 退出应用
4. 确认主进程和 sidecar 均已退出，无残留进程

## 5. 当前未完成事项

发布态 macOS bundle 已经打通，当前主要未完成的是后续产品能力，不再是 bundle 本身。

下一批主要空白：

1. 阶段 2 的会话头部区和窗口选择
2. `start / pause / resume / stop` 真正的 run 生命周期
3. 更完整的前后端桥接协议
4. Python 自动化核心从最小 bridge 扩到 runner / script loader / adapter
5. Windows bundle 实测与签名分发策略

## 6. 下一轮建议优先做什么

下一轮优先任务建议按这个顺序：

1. 进入阶段 2，先做 SessionSummary 扩展和窗口选择
2. 做 `start / pause / resume / stop` 生命周期
3. 把 bundle 流程补上 Windows 目标的验证路径

## 7. 关键实现约束

下一轮一定要继续坚持：

- 发布态 sidecar 由 Rust 管理，不由前端 JS 管理
- 核心 runner 不允许写具体游戏业务分支
- 前端只连 WebSocket，不负责启动后端
- 开发态和发布态进程模型分离

## 8. 当前 bundle 相关关键文件

本轮已经修改或新增的 bundle 关键文件：

- `apps/desktop/src-tauri/tauri.conf.json`
- `apps/desktop/src-tauri/Cargo.toml`
- `apps/desktop/src-tauri/src/main.rs`
- `apps/desktop/src-tauri/capabilities/default.json`
- `apps/desktop/src-tauri/binaries/quiet-studio-bridge-aarch64-apple-darwin`
- `scripts/build_sidecar.py`
- `apps/desktop/scripts/bundle.mjs`
- `apps/desktop/scripts/bundle-config.mjs`
- `apps/desktop/scripts/bundle-config.test.mjs`
- `.nvmrc`
- `scripts/setup-dev.sh`

## 9. 下一轮高概率会改的核心文件

下一轮高概率会修改：

- `apps/desktop/src/App.tsx`
- `apps/desktop/src/services/bridge-client.ts`
- `automation-core/app/core/session_service.py`
- `automation-core/app/api/websocket_server.py`
- `quiet-studio-technical-design.md`
- `quiet-studio-development-tasks.md`
