# KuroNeko Studio 技术设计方案

## 1. 目标

将 `KuroNeko Studio` 视觉原型收敛为一份可直接指导开发的桌面产品技术设计，目标范围包括：

- `Windows + macOS`
- `窗口化 / 无边框窗口化桌面游戏`
- `跨平台操作台 UI`
- `支持脚本扩展的自动化运行时`
- `明确前端、后端、桥接层职责`

这份文档是下面两份内容的实现化延伸：

- [README.md](/Users/bytedance/git/game-auto-cross-platform-solution/README.md)
- [prototype-4-organic-studio.html](/Users/bytedance/git/game-auto-cross-platform-solution/prototypes/prototype-4-organic-studio.html)

## 2. 总体架构

采用三层桌面架构：

```text
Tauri 壳层
  -> React 桌面前端
    -> 本地 bridge 客户端
      -> Python 自动化服务
        -> 平台适配层
          -> Windows adapter
          -> macOS adapter
```

技术选型：

- 桌面壳层：`Tauri`
- 前端：`React + TypeScript + Vite`
- 桥接传输：`本地 WebSocket`
- 自动化后端：`Python`
- 视觉识别：`OpenCV + OCR provider`
- 打包方式：`Tauri bundle + Python sidecar`

这样拆分的原因：

- 前端需要高状态密度 UI 和快速迭代
- 后端需要脚本能力、图像识别能力和平台自动化能力
- 桥接层需要把 UI、运行时、平台细节隔开，避免彼此耦合

## 3. 从原型抽出的产品模块

`KuroNeko Studio` 当前页面可以拆成 6 个明确产品模块：

1. 会话头部区
2. 脚本库和配置摘要区
3. 运行控制与状态指标区
4. 识别预览工作区
5. 实时日志控制台
6. 参数、选项、历史记录和产物侧栏

后续开发时，这 6 个模块都需要映射到：

- 前端组件
- 后端能力
- bridge 协议事件

## 4. 按界面区域拆分功能

### 4.1 会话头部区

原型中已有：

- 当前 run id
- 目标窗口名称
- 窗口锁定状态
- 平台和 profile 摘要
- 开始、暂停、继续、停止按钮

需要具备的能力：

- 无 run 时也能展示当前会话状态
- 启动前展示已选目标窗口
- 展示权限状态
- 展示后端连接状态
- 根据状态禁用不可执行操作

实现方式：

- 前端读取 `session summary` 和 `run state`
- 后端维护当前 session 快照
- bridge 以事件形式推送 session 更新

### 4.2 脚本库和配置摘要区

原型中已有：

- 脚本列表
- 当前选中脚本
- profile 摘要
- 热键信息

需要具备的能力：

- 列出所有已安装脚本
- 展示脚本元信息和平台兼容性
- 支持只选择脚本、不立即运行
- 支持加载保存过的参数预设
- 支持展示脚本支持的平台

实现方式：

- 前端拉取脚本目录和当前选择状态
- 后端扫描脚本 manifest 与参数 schema
- bridge 提供查询和选择命令

### 4.3 运行控制与状态指标区

原型中已有：

- 开始运行
- 暂停
- 继续
- 停止
- 运行时长
- 输入动作数
- 匹配置信度
- 恢复次数

需要具备的能力：

- run 生命周期状态安全切换
- 运行时快速刷新 UI
- 明确且可验证的状态流转
- 所有计数都以后端为准

实现方式：

- 前端只发送操作意图
- 后端拥有生命周期状态主导权
- bridge 推送权威状态更新

### 4.4 识别预览工作区

原型中已有：

- 截图预览
- 识别框叠层
- 识别状态标签
- 当前识别说明卡片
- 预览 / 状态图 / 调试视图切换

需要具备的能力：

- 展示最新捕获帧
- 展示结构化 overlay 区域与标签
- 切换不同预览模式
- 展示当前状态机步骤
- 展示当前推断和下一步动作

实现方式：

- 后端产出图像文件路径和 overlay 元数据
- 前端负责渲染图片和标注层
- bridge 推送低频图像更新和高频文本事件

### 4.5 实时日志控制台

原型中已有：

- 搜索输入框
- 日志数量
- 当前 run 标识
- 级别筛选
- 导出动作
- 带时间戳的日志项

需要具备的能力：

- 实时结构化日志流
- 按级别、run、事件类型、关键词过滤
- 导出当前 run 日志
- 可选自动滚动
- 从日志跳转到预览帧或产物

实现方式：

- 后端发出结构化日志事件
- 前端在本地做筛选和视图裁剪
- bridge 支持导出命令和产物定位

### 4.6 参数、选项、历史记录和产物侧栏

原型中已有：

- 脚本参数
- 自动化开关项
- 最近运行记录
- 产物摘要

需要具备的能力：

- 编辑可校验的参数字段
- 启动前切换运行选项
- 展示最近 run 历史
- 打开指定 run 的产物
- 按脚本保存 profile 参数

实现方式：

- 前端按 schema 渲染表单
- 后端负责参数校验和存储
- bridge 交换配置快照和保存结果

## 5. 前端设计

### 5.1 主题与视觉规范

前端 UI 统一使用基于黑猫与科技元素提取的主题色调，确保视觉体验的沉浸感与专业感：

**核心调色板 (CSS Variables)**：
- **极暗渊黑 (Base Dark)**：`--kuroneko-bg-base: #020208`，作为应用的最底层背景。
- **深蓝灰 (Panel/Card)**：`--kuroneko-bg-panel: #10111F`，作为面板和卡片的主背景。
- **主文本色 (Primary Text)**：`--kuroneko-text-primary: #FFFFFF`，高对比度纯白。
- **次文本色 (Secondary Text)**：`--kuroneko-text-secondary: #B4B8F0`，带有蓝紫倾向的亮灰色。
- **科技紫 (Accent)**：`--kuroneko-accent: #4239AE`，主强调色。
- **霓虹蓝 (Accent Glow)**：`--kuroneko-accent-glow: #CCFFFF`，高亮、连接态、Hover 等特效。
- **猫垫粉 (Kawaii Pink)**：`--kuroneko-kawaii-pink: #E995FF`，作为警告、过渡态（如 connecting）及特殊强调色的点缀。
- **霓虹琥珀黄 (Amber)**：`--kuroneko-amber: #FFB86C`，用于暂停、警告等控件的中间态。
- **霓虹猩红 (Crimson)**：`--kuroneko-crimson: #FF2A55`，用于停止、危险等高危操作控件。

**高级质感与渐变**：
- **毛玻璃效果 (Glassmorphism)**：卡片和面板需叠加 `backdrop-filter: blur(10px)`。
- **全局渐变光晕**：`--kuroneko-gradient-glow` 配合 `radial-gradient` 为悬停卡片提供放射状的呼吸光晕。
- **科技感渐变**：`--kuroneko-gradient-primary` 等线性渐变应用于标题发光、边框特效及装饰线条。

### 5.2 控件 UI 与性能规范 (Controls & Performance)

KuroNeko Studio 的核心控制按钮必须体现“桌面客户端的手感”以及“极客发光风格”，但必须兼顾高频渲染性能：
- **零过渡动画原则**：为了避免与底层背景的 `backdrop-filter: blur(10px)` 发生复杂的重绘冲突，所有组件（按钮、卡片、面板、下拉框）**严禁**在 `:hover` 等交互状态下使用 `transition: all`、`transform` 位移、`box-shadow` 发光渐变或 `opacity` 过渡。所有悬停状态应瞬间切换基础的颜色值，确保 GPU 零负担。
- **防止布局抖动**：所有包含动态数字的组件（如运行时长、动作数等指标）必须应用 `font-variant-numeric: tabular-nums`，防止数字宽度变化导致外层容器不断触发重新布局计算（Layout Thrashing）。
- **基础按钮 (`.btn`)**：使用深蓝灰 `rgba(32, 31, 78, 0.4)` 作为底色，带有微妙的 1px 亮色内阴影模拟物理凸起感。圆角为 `999px`（胶囊形状）。
- **主要操作 (`.btn-primary`)**：用于“开始运行”、“继续”。常态为科技紫，Hover 时背景色不变，文字色提亮为霓虹蓝（`#CCFFFF`），边框色变为次级文本色。严禁在此处使用 CSS 渐变色切换。
- **暂停操作 (`.btn-pause`)**：Hover 时触发霓虹琥珀黄（`#FFB86C`）的边框色变化。
- **危险操作 (`.btn-stop`)**：用于“停止”。Hover 时触发霓虹猩红（`#FF2A55`）的强烈警告。
- **禁用态 (`:disabled`)**：直接使用 CSS filter `grayscale(1)` 和 `opacity: 0.5`，移除所有 Hover 交互。

### 5.3 前端职责

前端负责：

- 渲染操作台 UI
- 管理瞬时 UI 状态
- 发送用户命令
- 接收运行时事件
- 过滤并展示日志
- 渲染截图、叠层、表单和历史记录

前端不负责：

- 执行自动化逻辑
- 持有权威 run 状态
- 计算视觉识别结果
- 直接管理最终产物落盘

### 5.2 前端目录建议

```text
apps/desktop/
  src/
    app/
      App.tsx
      routes.tsx
    components/
      layout/
      controls/
      logs/
      preview/
      forms/
    features/
      session/
      scripts/
      runtime/
      preview/
      logs/
      history/
      settings/
    services/
      bridge-client.ts
      image-resolver.ts
      download-service.ts
    state/
      store.ts
    types/
      bridge.ts
      session.ts
      script.ts
      logs.ts
```

### 5.3 前端状态模型

建议使用“小型全局 store + 局部组件状态”：

全局状态域：

- `session`
- `runtime`
- `scripts`
- `preview`
- `logs`
- `history`
- `settings`

建议结构：

```ts
type AppState = {
  session: SessionSummary;
  runtime: RuntimeState;
  scripts: ScriptCatalogState;
  preview: PreviewState;
  logs: LogState;
  history: HistoryState;
  settings: UiSettingsState;
};
```

局部状态适合管理：

- 下拉展开收起
- 输入框焦点
- 提交前的临时表单值
- 面板内 tab 切换

### 5.4 前端组件映射

建议拆分为以下组件：

```text
SessionHeader
ScriptLibraryPanel
ProfileSummaryPanel
RuntimeToolbar
MetricStrip
PreviewTabs
PreviewCanvas
CurrentInferenceCard
RunDetailPanel
LogToolbar
LogList
ParameterFormPanel
AutomationOptionsPanel
RecentRunsPanel
ArtifactsPanel
```

这些组件都应当数据驱动，不要在真实实现阶段继续保留硬编码 mock 文案。

### 5.5 前端实现说明

- 使用单一长连接 bridge client
- 将后端事件统一归一化为类型化 action
- 如果预览更新频率过高，对图像刷新做节流
- 日志筛选尽量放在前端本地完成
- 低风险配置编辑可做轻量 optimistic UI，run 状态不要做乐观更新
- 参数表单优先走 schema 驱动

## 6. 后端设计

### 6.1 后端职责

后端负责：

- session 生命周期
- 脚本加载
- 参数校验
- CV 和 OCR 编排
- 输入分发
- 窗口定位
- 产物落盘
- 结构化日志
- 指标聚合

后端是以下信息的权威来源：

- 当前 run 状态
- 当前 session 快照
- 当前脚本步骤
- 计数与计时
- 预览元数据
- 产物记录

### 6.2 后端目录建议

```text
automation-core/
  app/
    api/
      websocket_server.py
      message_router.py
      handlers/
        session_handler.py
        run_handler.py
        script_handler.py
    core/
      app_service.py
      session_service.py
      config_service.py
      history_service.py
    runner/
      run_controller.py
      state_machine.py
      action_scheduler.py
    scripts/
      loader.py
      registry.py
      schema_validation.py
      builtin/
      custom/
    vision/
      capture_service.py
      match_service.py
      ocr_service.py
      overlay_builder.py
    input/
      input_service.py
    windows/
      window_service.py
    artifacts/
      artifact_store.py
    logging/
      event_logger.py
      metrics.py
    models/
      commands.py
      events.py
      session.py
      run.py
      preview.py
```

### 6.3 后端服务分层

#### API Routing 层

负责桥接网络与内部服务：

- `websocket_server.py`: 维护 WebSocket 连接池与心跳机制，捕获全局异常。
- `message_router.py`: 消息分发路由器，将不同 `type` 的请求路由到具体的 handler。
- `handlers/`: 按业务领域拆分的消息处理器，避免单一文件无限膨胀。

#### App service

顶层负责编排：

- 启动
- 关闭
- adapter 健康检查
- bridge server 启动

#### Session service

负责维护用户视角的 session 快照：

- 当前选中脚本
- 当前选中 profile
- 当前目标窗口
- 当前 run id
- 权限摘要

#### Run controller

负责 run 生命周期：

- `idle -> starting -> running -> paused -> stopping -> completed/failed/aborted`

必须显式拒绝非法状态跳转。

#### Script registry / loader

负责：

- 加载 manifest
- 校验脚本元数据
- 创建脚本实例
- 将 schema 提供给前端

#### Vision service

负责：

- 截图
- 区域裁剪
- 模板匹配
- OCR
- 生成前端可渲染的 overlay 元数据

#### Artifact store

负责：

- 存截图
- 存调试图
- 存日志
- 存 run 摘要

### 6.4 后端运行主循环

建议主循环：

```text
校验 session
聚焦目标窗口
创建 run 记录
调用 script.on_start()
循环直到 stop 或终态:
  截图
  状态识别
  决策下一步动作
  发出预览、日志、指标事件
  执行动作或等待
  更新 run 状态
调用 script.on_stop()
落盘 summary 和 artifacts
```

## 7. Bridge 设计

### 7.1 为什么需要 bridge 层

bridge 层用于隔离：

- 前端展示逻辑
- 后端自动化逻辑
- Tauri 壳层能力

这样可以在不重写 UI 的前提下替换运行时实现，或者调整桌面壳层策略。

### 7.2 Bridge 传输方式

采用 `localhost WebSocket` 作为主桥接通道。

原因：

- 双向通信自然
- 易于事件推送
- 非常适合 React 的状态更新模型
- 能让 Python runtime 与 Tauri API 解耦

Tauri 壳层仍然负责：

- 启动和监管 Python sidecar
- 打开本地文件
- 应用打包

### 7.2.1 发布态进程模型

开发态与发布态需要区分：

开发态：

- `pnpm dev` 拉起 Python bridge
- `pnpm dev` 拉起 Vite dev server
- `pnpm dev` 拉起 Tauri 桌面壳

发布态：

- 用户双击应用
- Tauri 主进程启动
- Rust 在 `setup()` 中拉起 Python sidecar
- 前端连接本地 WebSocket
- 用户退出应用
- Tauri 关闭 sidecar

发布态不应依赖前端代码去拉起后端进程，原因是：

- 生命周期更难统一管理
- 退出回收不可靠
- 权限面会扩大到前端
- 更容易出现前端已开、后端未起的状态不同步

因此，发布态的 sidecar 生命周期应由 Rust 壳层接管。

### 7.2.2 Sidecar 打包方案

建议发布态采用：

- Python 服务先打成独立二进制
- 二进制作为 Tauri `externalBin` sidecar 一起打包

推荐构建链：

- Python 代码 -> `PyInstaller` 单文件可执行程序
- 产物放入 `apps/desktop/src-tauri/binaries/`
- `tauri.conf.json` 使用 `bundle.externalBin`

示例：

```json
{
  "bundle": {
    "externalBin": ["binaries/kuroneko-studio-bridge"]
  }
}
```

注意：

- sidecar 文件名在打包时需要带目标平台 triple 后缀
- macOS Apple Silicon 例如：`kuroneko-studio-bridge-aarch64-apple-darwin`
- Windows 例如：`kuroneko-studio-bridge-x86_64-pc-windows-msvc.exe`

### 7.2.3 Tauri 壳层对 sidecar 的控制职责

Rust 壳层至少负责：

- 应用启动时启动 sidecar
- 保存 sidecar 子进程句柄
- 应用退出时 kill sidecar
- 需要时监听 sidecar 标准输出并转发日志

建议运行逻辑：

```text
Tauri app setup
-> spawn sidecar
-> 保存 child handle 到 tauri::State
-> 前端加载并连接 ws://127.0.0.1:8765
-> 退出应用时 child.kill()
```

### 7.2.4 发布态与开发态的边界

开发态脚本可以继续保留：

- 便于本地联调
- 便于前后端分开调试

但开发态脚本不等于发布态进程模型。

正式发布时必须满足：

- 双击应用即可启动桌面壳和后端
- 不要求用户自行安装 Python
- 不要求用户自行启动 bridge 服务
- 关闭应用后不遗留后端孤儿进程

### 7.3 Bridge 消息分类

前端发给后端的命令：

- session 查询
- 脚本选择
- 参数更新
- 目标窗口选择
- 生命周期控制
- 导出 / 打开产物

后端发给前端的事件：

- 连接状态
- session 快照
- run 状态更新
- 指标更新
- 预览更新
- 日志事件
- 历史记录更新
- 错误事件

### 7.4 命令协议

建议命令：

```json
{ "type": "session/get" }
{ "type": "scripts/list" }
{ "type": "scripts/select", "scriptId": "daily_task" }
{ "type": "profiles/list", "scriptId": "daily_task" }
{ "type": "profiles/save", "payload": { "id": "...", "scriptId": "...", "name": "...", "parameters": {} } }
{ "type": "profiles/delete", "payload": { "id": "..." } }
{ "type": "session/select-window", "windowId": "win_123" }
{ "type": "session/update-params", "params": { "retryLimit": 2 } }
{ "type": "run/start" }
{ "type": "run/pause" }
{ "type": "run/resume" }
{ "type": "run/stop" }
{ "type": "logs/export", "runId": "run_028" }
{ "type": "history/get" }
{ "type": "artifacts/open", "artifactId": "artifact_041" }
```

### 7.5 事件协议

建议事件：

```json
{
  "type": "session/updated",
  "session": {
    "runId": "run_028",
    "scriptId": "daily_task",
    "profileId": "evening-pass",
    "windowTitle": "Aether Chronicles"
  }
}
```

```json
{
  "type": "scripts/listed",
  "payload": [
    {
      "id": "genshin_daily",
      "name": "原神日常自动化",
      "version": "1.0.0",
      "description": "...",
      "author": "KuroNeko",
      "schema": { ... }
    }
  ]
}
```

```json
{
  "type": "profiles/listed",
  "payload": [
    {
      "id": "12345",
      "scriptId": "genshin_daily",
      "name": "配置 12:00:00",
      "parameters": { ... }
    }
  ]
}
```

```json
{
  "type": "run/state",
  "state": "running",
  "step": "reward_confirm",
  "elapsedMs": 1084000
}
```

```json
{
  "type": "preview/frame",
  "framePath": "/.../frame_041.png",
  "overlays": [
    { "kind": "match", "x": 120, "y": 80, "w": 180, "h": 66, "label": "task_button", "score": 0.94 }
  ]
}
```

```json
{
  "type": "logs/event",
  "entry": {
    "ts": "2026-05-07T16:42:04+08:00",
    "level": "info",
    "event": "template_match",
    "message": "Template task_button matched in region 02",
    "runId": "run_028"
  }
}
```

### 7.6 Bridge 错误处理

bridge 层至少要明确暴露这些错误：

- 后端未启动
- 连接断开
- 命令 payload 非法
- 当前 run 状态不支持该操作

前端建议行为：

- 显示 offline 状态
- 连接断开时禁用运行控制
- 保留最后一帧预览和已有日志，等待重连或刷新

## 8. 数据模型

### 8.1 SessionSummary

```ts
type SessionSummary = {
  runId: string | null;
  status: "idle" | "starting" | "running" | "paused" | "stopping" | "error";
  platform: "windows" | "macos";
  windowId: string | null;
  windowTitle: string | null;
  windowMode: "windowed" | "borderless-windowed";
  profileId: string | null;
  profileName: string | null;
  permissionState: {
    input: "ready" | "missing";
    capture: "ready" | "missing";
  };
};
```

### 8.2 ScriptManifest

```ts
type ScriptManifest = {
  id: string;
  name: string;
  version: string;
  description: string;
  platforms: Array<"windows" | "macos">;
  parameterSchema: JsonSchema;
};
```

### 8.3 PreviewState

```ts
type PreviewState = {
  mode: "recognition" | "state-graph" | "debug-overlays";
  framePath: string | null;
  overlays: Array<{
    id: string;
    kind: "match" | "ocr" | "region";
    label: string;
    score?: number;
    x: number;
    y: number;
    w: number;
    h: number;
  }>;
  currentInference: {
    title: string;
    detail: string;
  } | null;
};
```

### 8.4 LogEntry

```ts
type LogEntry = {
  id: string;
  ts: string;
  level: "debug" | "info" | "warning" | "error";
  event: string;
  message: string;
  detail?: string;
  runId: string;
  artifactId?: string;
};
```

## 9. 功能点到实现方式的映射

### 启动运行

前端：

- 收集当前脚本、profile、目标窗口、参数
- 发送 `run/start`
- 启动中禁用非法操作

后端：

- 校验 session 和权限
- 创建 run context
- 切换到 `starting`
- 发出第一份状态快照

bridge：

- 返回命令结果
- 推送生命周期更新和启动错误

### 暂停运行

前端：

- 切换到 paused UI

后端：

- 设置 pause token
- 停止新输入动作分发
- 保留当前 session 状态

bridge：

- 推送 `run/state: paused`

### 继续运行

前端：

- 恢复 active 控件状态

后端：

- 再次确认目标窗口和权限
- 从最后一个安全步骤继续

bridge：

- 推送 resumed 状态和新的指标

### 停止运行

前端：

- 显示 stop requested

后端：

- 安全打断主循环
- 刷新产物落盘
- 写入历史记录

bridge：

- 依次推送 `stopping` 和终态

### 预览渲染

前端：

- 展示最新图像与 overlays

后端：

- 写入图像产物
- 发送图像路径和 overlay 坐标

bridge：

- 以受控频率推送预览事件

### 参数编辑

前端：

- 根据 schema 渲染表单
- 提交前做基础字段校验

后端：

- 用权威 schema 做最终校验
- 持久化 profile 参数

bridge：

- 以字段级错误返回校验结果

## 10. 持久化设计

本地需要持久化的内容：

- 脚本 manifest
- 已保存的 profile
- session 默认值
- run 历史
- artifact 索引
- 结构化 run 日志

建议目录：

```text
data/
  profiles/
  history/
  logs/
  artifacts/
```

## 11. 后端扩展性设计

后端扩展性要同时覆盖两类变化：

- 不同游戏之间的差异
- 同一游戏内部不同自动化流程的差异

这里的核心原则是：

`平台能力、游戏差异、流程逻辑三层分离`

不能把“不同游戏”和“不同流程”的差异直接堆进 runner 里，否则后面一定演化成大量 `if game_id == ...` 的分支。

### 11.1 三层抽象

建议把后端拆成三层能力：

#### 第一层：平台适配与安全输入层 (Platform & Input)

这一层完全不理解具体游戏，只提供通用的操作系统级能力与输入抽象：

- 查找窗口与分辨率坐标归一化
- macOS Quartz / Windows SendInput 硬件级输入注入
- 拟人化延迟抖动与高斯随机偏移
- 截图与区域裁剪
- 模板匹配与 OCR
- 全局安全热键监听 (Kill Switch)

这一层解决的是“系统层面怎么看、怎么安全地动”。

#### 第二层：游戏适配层 (Game Adapter)

这一层封装“某个游戏”的稳定差异，建议每个游戏一个 `GameAdapter`：

- 窗口识别规则
- 分辨率缩放规则
- 常用识别区域
- 模板资源目录
- 通用状态识别逻辑
- 默认超时与节奏参数

这一层解决的是“这个游戏怎么看、怎么定位、怎么归一化”。

#### 第三层：流程脚本层

这一层负责“同一个游戏中的某一条自动化流程”，例如：

- 每日任务
- 资源刷取
- 邮件领取
- 对话跳过

这一层解决的是“当前流程应该怎么走”。

### 11.2 为什么必须这样拆

如果不拆层，很容易出现这种坏味道：

- 平台坐标逻辑写在脚本里
- 模板路径写死在流程代码里
- 不同游戏的差异散落在 runner 中
- 同一游戏的多个流程复制相同状态判断逻辑

后果是：

- 新增游戏成本越来越高
- 同一处状态改动会影响多个脚本
- 流程间难以复用
- 调试成本高

### 11.3 推荐目录结构

建议把“游戏级”和“流程级”扩展点显式拆目录：

```text
automation-core/
  app/
    platform/
      windows/
      macos/
    core/
      session_service.py
      run_controller.py
      history_service.py
    games/
      aether/
        adapter.py
        templates/
        profiles/
          1728x972.json
          1920x1080.json
        flows/
          daily_task.py
          inbox_claim.py
          resource_sweep.py
        helpers/
          navigation.py
          recovery.py
          rewards.py
      another_game/
        adapter.py
        templates/
        profiles/
        flows/
        helpers/
```

推荐职责：

- `platform/*`：操作系统相关能力
- `games/<game_id>/adapter.py`：游戏级适配
- `games/<game_id>/templates/`：模板资源
- `games/<game_id>/profiles/`：分辨率和参数 profile
- `games/<game_id>/flows/`：流程脚本
- `games/<game_id>/helpers/`：可复用子流程

### 11.4 GameAdapter 设计

建议定义统一接口：

```python
from typing import Protocol


class GameAdapter(Protocol):
    game_id: str

    def detect_screen(self, ctx) -> str: ...
    def get_regions(self) -> dict[str, object]: ...
    def get_templates(self) -> dict[str, str]: ...
    def normalize_point(self, point, resolution): ...
    def get_default_runtime_config(self) -> dict: ...
```

这一层应该提供：

- 当前画面属于哪个逻辑 screen
- 各个 screen 下常用 region 定义
- 模板资源索引
- 分辨率坐标归一化
- 当前游戏推荐默认参数

不要在流程脚本里直接写死：

- 模板文件绝对路径
- 固定坐标
- 分辨率换算公式
- 目标窗口匹配规则

这些都应该由 `GameAdapter` 统一提供。

### 11.5 FlowScript 设计

同一游戏内，每条流程都是一个独立 `FlowScript`。

建议接口：

```python
from typing import Protocol


class FlowScript(Protocol):
    script_id: str
    game_id: str

    def on_start(self, ctx) -> None: ...
    def on_tick(self, ctx) -> None: ...
    def on_pause(self, ctx) -> None: ...
    def on_resume(self, ctx) -> None: ...
    def on_stop(self, ctx) -> None: ...
```

关键约束：

- `FlowScript` 只调用高层上下文能力
- `FlowScript` 不直接访问原始平台 API
- `FlowScript` 不自己做分辨率归一化
- `FlowScript` 不直接管理 artifact 落盘

推荐写法：

```python
screen = ctx.detect_screen()

if screen == "main_menu":
    ctx.click_template("task_entry")
elif screen == "task_panel":
    ctx.click_template("claim_button")
else:
    ctx.capture_debug("unknown_state")
    ctx.pause_with_reason("screen_not_recognized")
```

不推荐写法：

```python
if match("/games/aether/templates/task_entry.png", region=(22, 33, 180, 60)):
    click(668, 382)
```

前者是可扩展抽象，后者会把脚本写死在某个版本和分辨率上。

### 11.6 同一游戏多个流程如何复用

同一个游戏内，很多流程会共享部分导航和恢复逻辑，所以建议引入 `helpers` 目录，承载可复用子流程：

- `ensure_home_screen()`
- `open_task_panel()`
- `close_popup_if_present()`
- `recover_focus()`
- `claim_reward_if_available()`

这样做的好处：

- 新流程可以基于已有子流程快速拼装
- 通用行为修复一次即可影响全部流程
- 状态切换逻辑集中，便于排查问题

### 11.7 用状态机而不是线性步骤

为了保证“同一游戏不同流程”仍然可扩展，流程脚本建议统一用状态机表达，而不是从头到尾的线性脚本。

示例：

```text
main_menu
-> task_panel
-> reward_confirm
-> reward_done
-> back_to_home
```

状态机的优势：

- 更容易恢复中断
- 更容易插入分支
- 更容易做失败重试
- 更适合复用局部状态

例如“打开任务面板”可以作为多个流程共享的状态片段，而不是每个流程都复制一次。

### 11.8 配置驱动而不是代码写死

为了降低新增分辨率、新增 profile、新增轻量规则的成本，建议以下内容配置化：

- 分辨率 profile
- 模板资源索引
- 识别阈值
- 超时
- 等待时间
- 重试次数
- 部分流程开关

建议 profile 结构：

```json
{
  "profileId": "1728x972",
  "windowMode": "borderless-windowed",
  "captureRegion": [0, 0, 1728, 972],
  "thresholds": {
    "template": 0.9,
    "ocr": 0.72
  },
  "timings": {
    "settleDelayMs": 600,
    "postClickWaitMs": 800
  }
}
```

这样新增一个新分辨率时，很多情况下只需要补：

- 一个 profile
- 一组模板
- 少量 region 调整

而不需要改 runner 或大量流程代码。

### 11.9 ScriptContext 要提供什么能力

为了让流程脚本保持稳定、易迁移，建议 `ScriptContext` 暴露的是高层能力，而不是平台细节：

- `ctx.detect_screen()`
- `ctx.click_template(template_id)`
- `ctx.match(template_id, threshold=0.9)`
- `ctx.ocr(region=None)`
- `ctx.press(key)`
- `ctx.wait(seconds)`
- `ctx.capture_debug(label)`
- `ctx.pause_with_reason(reason)`
- `ctx.log.info(message)`

不要暴露过多底层实现细节给脚本，例如：

- 原始窗口句柄
- 直接文件系统写权限
- 原始系统级输入对象
- 任意 shell 执行能力

否则脚本很快会绕过统一抽象，扩展性会被破坏。

### 11.10 核心 runner 的边界

最重要的约束之一：

`核心 runner 永远不认识具体游戏业务`

也就是说 runner 只知道：

- 当前选中了哪个 `GameAdapter`
- 当前正在跑哪个 `FlowScript`
- 当前 session 参数是什么

runner 不应该出现这种代码：

```python
if game_id == "aether":
    ...
elif game_id == "another_game":
    ...
```

一旦核心层开始写这种逻辑，扩展性就会迅速塌掉。

### 11.11 扩展路径总结

新增一个新游戏时，应该新增：

- `GameAdapter`
- 模板资源
- profile 配置
- 若干 flow scripts

新增同一游戏的一条新流程时，应该尽量只新增：

- 一个新的 `FlowScript`
- 少量新的 helper
- 必要的模板资源或 profile 配置

理想情况下：

- 加新游戏不需要改核心 runner
- 加新流程不需要改平台层
- 改某个通用导航逻辑只需要改 helper

这才是后端真正可持续扩展的形态。

## 12. Version 1 范围

第一版包含：

- 单 active run
- 单目标窗口
- 单脚本选择
- schema 驱动参数表单
- 实时日志
- 预览帧 + 叠层
- run 历史
- artifact 摘要

第一版暂不包含：

- 多 run 编排
- 多窗口自动化
- 可视化脚本编辑器
- 云同步或远程控制
- 多人协同操作台

## 13. 实施顺序

建议开发顺序：

1. bridge skeleton 和后端启动链路
2. 会话头部区和运行控制
3. 脚本库和 profile 加载
4. start / pause / resume / stop 生命周期
5. 日志流
6. 预览帧与 overlay 渲染
7. 参数表单与校验
8. 历史记录与产物区
9. 错误态与离线态

## 14. 最终建议

把 `KuroNeko Studio` 当作明确的产品契约，而不是单纯的视觉风格。

也就是说：

- 原型上每一个可见区块都对应一个类型明确的前端模块
- 每个模块都对应清晰的后端服务能力
- 所有交互都通过稳定的 bridge 协议完成
- 自动化状态以后端为准
- 前端专注于可见性、控制和复核

这样从原型到真实桌面应用的过程里，不需要再做一轮架构重写或产品语义重构。
