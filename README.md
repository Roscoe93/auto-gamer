# Quiet Studio 项目说明

## 1. 项目目标

`Quiet Studio` 是一个面向 `Windows + macOS` 的桌面游戏自动化操作台方案，当前聚焦：

- 窗口化 / 无边框窗口化桌面游戏
- 跨平台桌面 UI
- 脚本启停、暂停、继续、停止
- 实时日志、识别预览、运行状态展示
- 可扩展的自动化后端

当前推荐架构：

```text
Tauri 壳层
  -> React + TypeScript 前端
    -> 本地 WebSocket bridge
      -> Python 自动化服务
        -> Windows / macOS 平台适配层
```

## 2. 范围边界

本项目当前明确支持：

- 普通桌面窗口
- 标准窗口模式和无边框窗口模式
- 基于截图、模板匹配、OCR、键鼠输入的自动化
- 非反作弊、非内核保护场景

本项目当前不覆盖：

- 内核级输入注入
- 联网竞技类反作弊环境
- 独占全屏 DirectX 绕过
- 模拟器作为一等目标平台

## 2.1 Node 版本约束

仓库根目录使用 [.nvmrc](/Users/bytedance/git/game-auto-cross-platform-solution/.nvmrc) 锁定 Node 版本：

```text
v24.14.0
```

日常开发和打包建议先在仓库根目录执行：

```bash
cd /Users/bytedance/git/game-auto-cross-platform-solution
nvm use
```

`apps/desktop/package.json` 也通过 `engines.node` 声明了同一版本约束。

如果本机没有 `nvm`，当前项目脚本仍可以回退到仓库使用过的 bundled Node，但文档口径和推荐方式以 `.nvmrc` 为准。

## 3. 工程约束

开发过程中需要遵守下面这些工程约束。

### 3.1 架构约束

- 前端只负责展示、交互和状态呈现，不承载自动化业务逻辑。
- 后端是 run 生命周期、脚本执行、日志、指标和产物的唯一权威来源。
- 前后端通信统一走 bridge 协议，不允许共享隐式状态。
- 核心 runner 不允许出现针对具体游戏的硬编码业务分支。
- 不同游戏的差异通过 `GameAdapter` 承载，同一游戏不同流程通过 `FlowScript` 承载。

### 3.2 脚本扩展约束

- 脚本只调用高层 `ScriptContext` 能力。
- 脚本不直接操作底层平台 API。
- 脚本不自己做分辨率归一化。
- 脚本不直接管理产物落盘。
- 通用导航、恢复逻辑应沉淀到 `helpers`，不要在多个流程里复制。

### 3.3 通信约束

- 前端发命令，后端回结果并推事件。
- run 状态、session 摘要、日志、预览都必须以后端事件为准。
- 非法命令必须返回结构化错误。
- 断连时前端必须能进入明确的 offline 状态。

### 3.4 平台约束

Windows：

- 以普通窗口自动化能力为主
- 重点关注窗口查找、聚焦、截图、输入分发

macOS：

- 需要 Accessibility 权限控制输入
- 需要 Screen Recording 权限用于截图
- 需要额外处理坐标和 Retina 缩放

### 3.5 开发约束

- 阶段性实现必须可演示、可验证，不接受只有代码没有验证结果的提交。
- 新增功能时优先维持模块边界，不通过跨层直接调用“先跑起来”。
- README、技术方案、任务清单三者要同步，避免代码和文档长期漂移。

## 4. 当前目录结构

当前目录结构如下：

```text
game-auto-cross-platform-solution/
  apps/
    desktop/
      src/
      src-tauri/
      scripts/
  automation-core/
    app/
      api/
      core/
    tests/
  prototypes/
  README.md
  quiet-studio-technical-design.md
  quiet-studio-development-tasks.md
  pnpm-workspace.yaml
```

各目录职责：

- `apps/desktop`：桌面前端和 Tauri 壳层
- `automation-core`：Python 自动化后端
- `prototypes`：HTML 视觉原型
- `quiet-studio-technical-design.md`：中文技术设计
- `quiet-studio-development-tasks.md`：开发任务列表与准出标准

## 5. 当前完成状态

当前已经完成阶段 1 的最小骨架：

- React 前端骨架
- Python WebSocket bridge 服务
- Tauri 壳层基础配置
- 前端连接状态页
- `connection/status`、`connection/heartbeat`、`session/get` 最小协议
- 一键开发启动脚本
- 一键开发环境初始化脚本
- 发布态 sidecar 打包链路
- macOS `.app` bundle 产物构建

已验证内容：

- Python bridge 单元测试通过
- 前端 `build` 可以产出静态资源
- Tauri 桌面壳已完成一次本机编译和运行验证
- `pnpm dev` 三进程启动编排已落地
- `pnpm bundle` 可完成 sidecar + 前端 + Tauri bundle 的一键构建
- macOS `.app` 启动时会自动拉起 Python sidecar
- macOS `.app` 退出时会自动关闭 Python sidecar

## 6. 启动方式

### 6.1 Python 后端单独启动

在 `automation-core` 目录下运行：

```bash
python3 -m app.main
```

默认会监听：

```text
ws://127.0.0.1:8765
```

可通过环境变量覆盖：

```bash
QUIET_STUDIO_BRIDGE_HOST=127.0.0.1
QUIET_STUDIO_BRIDGE_PORT=8765
```

### 6.2 前端单独启动

在 `apps/desktop` 目录下运行：

```bash
nvm use
pnpm dev:web
```

默认开发地址：

```text
http://127.0.0.1:1420
```

### 6.3 前后端一起启动

在 `apps/desktop` 目录下运行：

```bash
nvm use
pnpm dev
```

当前 `pnpm dev` 会通过 [apps/desktop/scripts/dev.mjs](/Users/bytedance/git/game-auto-cross-platform-solution/apps/desktop/scripts/dev.mjs) 同时拉起：

- Python bridge 服务
- Vite 前端 dev server
- Tauri 桌面壳

启动顺序为：

1. 先启动 Python bridge
2. 等待 `127.0.0.1:8765` 就绪
3. 启动 Vite dev server
4. 等待 `127.0.0.1:1420` 就绪
5. 启动 Tauri 桌面壳

### 6.4 前端构建

在 `apps/desktop` 目录下运行：

```bash
nvm use
pnpm build
```

产物输出到：

```text
apps/desktop/dist
```

### 6.5 一键初始化开发环境

在仓库根目录执行：

```bash
bash scripts/setup-dev.sh
```

这个脚本会依次完成：

- 读取仓库根目录 `.nvmrc`
- 如果本机可用 `nvm`，自动安装并切换到锁定的 Node 版本
- 检查并安装 Rust 工具链
- 安装 Python 依赖
- 安装前端依赖
- 运行启动编排脚本测试
- 输出后续开发启动命令

### 6.6 一键构建应用包

在 `apps/desktop` 目录下运行：

```bash
nvm use
pnpm bundle
```

当前 `pnpm bundle` 会通过 [apps/desktop/scripts/bundle.mjs](/Users/bytedance/git/game-auto-cross-platform-solution/apps/desktop/scripts/bundle.mjs) 顺序执行：

1. 调用 [scripts/build_sidecar.py](/Users/bytedance/git/game-auto-cross-platform-solution/scripts/build_sidecar.py) 构建 Python sidecar
2. 执行前端 `pnpm build`
3. 执行 `cargo tauri build --bundles app`

辅助编排配置与测试文件：

- [apps/desktop/scripts/bundle-config.mjs](/Users/bytedance/git/game-auto-cross-platform-solution/apps/desktop/scripts/bundle-config.mjs)
- [apps/desktop/scripts/bundle-config.test.mjs](/Users/bytedance/git/game-auto-cross-platform-solution/apps/desktop/scripts/bundle-config.test.mjs)

当前 macOS 产物输出到：

```text
apps/desktop/src-tauri/target/release/bundle/macos/Quiet Studio.app
```

打包后的进程模型为：

```text
双击 Quiet Studio.app
  -> Tauri 主进程启动
  -> Rust setup 中拉起 bundled Python sidecar
  -> 前端连接本地 WebSocket bridge
退出 Quiet Studio.app
  -> window close / app exit 生命周期触发
  -> Rust 回收 sidecar 子进程
```

## 7. 依赖前提

### 7.1 Python 依赖

当前最小 Python 依赖在：

- [automation-core/requirements.txt](/Users/bytedance/git/game-auto-cross-platform-solution/automation-core/requirements.txt)

安装方式：

```bash
python3 -m pip install -r automation-core/requirements.txt
```

### 7.2 前端依赖

在 `apps/desktop` 目录执行：

```bash
nvm use
pnpm install
```

### 7.3 Tauri / Rust 依赖

如果要在本机真正运行 Tauri 桌面壳，需要额外具备：

- `rustc`
- `cargo`

当前仓库已经包含：

- [apps/desktop/src-tauri/tauri.conf.json](/Users/bytedance/git/game-auto-cross-platform-solution/apps/desktop/src-tauri/tauri.conf.json)
- [apps/desktop/src-tauri/Cargo.toml](/Users/bytedance/git/game-auto-cross-platform-solution/apps/desktop/src-tauri/Cargo.toml)
- [apps/desktop/src-tauri/capabilities/default.json](/Users/bytedance/git/game-auto-cross-platform-solution/apps/desktop/src-tauri/capabilities/default.json)

## 8. 已知限制

- 当前 bridge 只实现了阶段 1 最小协议，不包含真实 run 生命周期控制。
- 当前 bundle 已在 macOS 本机验证通过，Windows bundle 还未开始验证。
- 当前前端还是状态页骨架，不是完整产品 UI。
- 当前 Tauri 已完成本机运行验证，但还没有做正式打包验证。
- 当前后端还没有接入真实窗口枚举、截图、OCR、输入控制。

## 9. 下一步建议

建议按下面顺序继续：

1. 完成阶段 2：Session 与运行控制
2. 补窗口选择、run 生命周期、会话头部区
3. 完成阶段 3：脚本、Profile 与参数管理
4. 再接入日志和预览工作区

如果要直接继续开发，推荐优先阅读：

- [quiet-studio-technical-design.md](/Users/bytedance/git/game-auto-cross-platform-solution/quiet-studio-technical-design.md)
- [quiet-studio-development-tasks.md](/Users/bytedance/git/game-auto-cross-platform-solution/quiet-studio-development-tasks.md)
