# Quiet Studio 开发任务列表与准出标准

> **适用范围：** Windows + macOS 桌面游戏自动化操作台  
> **对应文档：**
> - [技术设计方案](/Users/bytedance/git/game-auto-cross-platform-solution/quiet-studio-technical-design.md)
> - [视觉原型](/Users/bytedance/git/game-auto-cross-platform-solution/prototypes/prototype-4-organic-studio.html)

## 1. 目标

把 `Quiet Studio` 从视觉原型推进到可运行的第一版桌面产品。  
任务列表按“前端 / 后端 / bridge / 集成”拆分，并为每个阶段定义准出标准，便于排期、分工和验收。

## 2. 总体分期

建议分为 6 个阶段：

1. 项目骨架与运行链路
2. Session 与运行控制
3. 脚本、Profile 与参数管理
4. 识别预览与日志控制台
5. 后端扩展能力与产物体系
6. 集成联调、异常处理与打包

每个阶段都应满足：

- 功能可演示
- 核心路径可验证
- 至少具备基础错误处理
- 关键模块有最小测试覆盖

## 3. 开发任务列表

### 阶段 1：项目骨架与运行链路

**目标：** 把前端、Python 后端、Tauri 壳层、WebSocket bridge 跑通。

**任务列表：**

- 创建桌面前端工程骨架
- 创建 Python 自动化服务骨架
- 建立 Tauri sidecar 启动机制
- 建立 WebSocket bridge 基础连接
- 完成前后端心跳与连接状态展示
- 约定基础命令与事件格式
- 建立基础日志输出机制

**涉及模块：**

- 前端：`apps/desktop`
- 后端：`automation-core/app/api`
- 壳层：`apps/desktop/src-tauri`

**准出标准：**

- 启动桌面应用后，前端能自动连接 Python 后端
- 后端未启动或断连时，前端能显示明确离线状态
- 前端能收到至少一条心跳事件和一条状态事件
- bridge 基础协议已固定，至少包含 `session/get` 和 `connection/status`
- 本阶段代码可在 Windows 和 macOS 两端启动成功

### 阶段 2：Session 与运行控制

**目标：** 实现会话头部区、目标窗口选择、运行按钮和状态流转。

**任务列表：**

- 定义 `SessionSummary` 数据模型
- 实现 session service
- 实现窗口枚举接口
- 实现目标窗口选择与锁定
- 实现运行按钮状态控制
- 实现 `start / pause / resume / stop` 生命周期
- 实现基础 metrics：运行时长、动作数、恢复次数
- 前端接入会话头部与控制区

**涉及模块：**

- 前端：`session`, `runtime`
- 后端：`session_service`, `run_controller`, `window_service`
- bridge：`session/*`, `run/*`

**准出标准：**

- 前端能展示当前窗口、profile、run 状态
- 运行按钮会根据状态正确禁用或启用
- `start -> running -> pause -> resume -> stop` 生命周期可完整演示
- 非法状态切换会被后端拒绝，并返回明确错误信息
- 窗口未选择时禁止启动
- 会话摘要与状态指标以事件驱动刷新，而不是轮询拼装

### 阶段 3：脚本、Profile 与参数管理

**目标：** 让不同脚本、不同 profile、不同参数配置可以被选择、保存和校验。

**任务列表：**

- 定义脚本 manifest 结构
- 实现脚本扫描与注册
- 实现 profile 读取与保存
- 实现参数 schema 校验
- 实现参数表单渲染
- 实现 profile 与脚本联动加载
- 实现默认参数注入
- 前端接入脚本库、profile 摘要和参数面板

**涉及模块：**

- 前端：`scripts`, `forms`, `settings`
- 后端：`loader.py`, `registry.py`, `schema_validation.py`, `config_service.py`
- 存储：`data/profiles`

**准出标准：**

- 能列出所有已安装脚本
- 切换脚本后，参数表单自动刷新
- 选中 profile 后，参数值自动带入
- 提交非法参数时，前端收到字段级错误并可定位
- 参数保存后重启应用仍可恢复
- 新增一个 manifest + schema 的脚本后，无需改前端代码即可显示基础表单

### 阶段 4：识别预览与日志控制台

**目标：** 把视觉识别过程和运行日志以操作台方式完整展示出来。

**任务列表：**

- 实现截图采集与帧产物存储
- 实现 overlay 元数据结构
- 实现前端预览图与识别框渲染
- 实现预览模式切换：识别预览 / 状态图 / 调试叠层
- 实现结构化日志模型
- 实现日志事件推送
- 实现前端日志搜索与级别筛选
- 实现日志导出

**涉及模块：**

- 前端：`preview`, `logs`
- 后端：`capture_service`, `overlay_builder`, `event_logger`
- bridge：`preview/*`, `logs/*`

**准出标准：**

- 前端能展示最新截图和 overlay 标注
- 后端每次关键识别步骤都能产生日志事件
- 日志支持按级别过滤和关键词搜索
- 日志导出后能得到结构化文件
- 点击日志项时，至少能定位到关联 run 或 artifact id
- 预览更新频率受控，不会明显拖慢 UI

### 阶段 5：后端扩展能力与产物体系

**目标：** 确保系统能够扩展到不同游戏，以及同一游戏的不同流程。

**任务列表：**

- 实现 `GameAdapter` 接口
- 实现 `FlowScript` 接口
- 实现脚本上下文 `ScriptContext`
- 实现至少一个游戏的 adapter
- 实现至少两个 flow scripts
- 抽出同游戏公共 helper
- 实现 profile 与模板资源索引
- 实现 run artifacts：截图、日志、summary、debug frame

**涉及模块：**

- 后端：`games/<game_id>/adapter.py`, `flows/`, `helpers/`, `artifacts/`
- 存储：`data/artifacts`, `data/history`, `data/logs`

**准出标准：**

- 核心 runner 不包含具体游戏业务分支
- 新增同一游戏的一条流程时，不需要修改 runner
- 新增一个新游戏时，不需要修改前端协议
- `GameAdapter` 能提供 screen 检测、region、模板索引、默认运行参数
- `FlowScript` 只依赖 `ScriptContext` 高层能力
- 每个 run 完成后都能生成 summary、日志和截图产物

### 阶段 6：集成联调、异常处理与打包

**目标：** 让整个产品达到可交付、可演示、可安装状态。

**任务列表：**

- 统一异常码与错误提示
- 实现后端断连、权限缺失、窗口丢失等错误态
- 实现前端 offline 态和 disabled controls
- 完成 Windows 权限提示与说明
- 完成 macOS Accessibility / Screen Recording 权限提示
- 完成历史记录与产物打开能力
- 将 Python bridge 打成独立 sidecar 二进制
- 配置 `tauri.conf.json > bundle.externalBin`
- 在 Rust 壳层中接管 sidecar 生命周期
- 实现应用退出时自动关闭 sidecar
- 完成 Tauri 打包流程
- 产出最小操作说明

**涉及模块：**

- 前端：错误提示、空态、离线态
- 后端：错误码、异常映射、权限检测
- 壳层：sidecar 生命周期、打包配置

**准出标准：**

- 在 Windows 和 macOS 都能打包出可安装版本
- 双击应用后会自动拉起 Python sidecar
- 用户不需要手动启动 bridge 服务
- 关闭应用后 sidecar 不会残留为孤儿进程
- 权限缺失时有明确提示，不会静默失败
- 断开后端连接时，前端状态可恢复或明确失败
- run 失败后，历史记录和错误产物仍可查看
- 按照操作说明，新用户可以独立完成一次脚本运行

## 4. 模块级准出标准

### 前端准出标准

- 关键页面按原型布局落地
- 所有运行控制均由后端状态驱动
- 不存在明显的溢出、错位、遮挡问题
- 断连、空态、无窗口、无脚本等状态有明确 UI
- 日志、预览、参数、历史区块都能独立工作

### 后端准出标准

- 生命周期状态机稳定
- 参数校验与脚本加载稳定
- 截图、匹配、OCR、输入控制链路可调用
- artifacts、history、logs 均可落盘
- 不同游戏和不同流程的扩展入口清晰

### Bridge 准出标准

- 命令格式固定且可校验
- 事件格式固定且有版本兼容策略
- 断连重连行为明确
- 非法命令能返回结构化错误
- 前后端不会共享未定义的隐式状态

## 5. 联调准出标准

至少完成以下联调场景：

1. 启动应用，前端连接后端成功
2. 选择窗口、脚本、profile，成功启动 run
3. 运行中能看到 metrics、预览、日志同步更新
4. 暂停后无新输入动作发出
5. 恢复后从安全状态继续
6. 停止后生成历史记录和产物
7. 故意制造一次识别失败，系统能输出错误信息和调试截图

## 6. 测试建议

建议至少覆盖以下测试层级：

### 单元测试

- 参数 schema 校验
- session 状态流转
- run 生命周期状态机
- log/event 格式化
- profile 读取与保存

### 集成测试

- WebSocket bridge 命令与事件
- 脚本注册与加载
- start / pause / resume / stop 主流程
- artifact 落盘

### 手工验证

- Windows 权限和窗口选择
- macOS 权限申请链路
- 预览与日志联动
- 异常恢复与错误提示

## 7. 第一版总体验收标准

可以把第一版验收标准压缩成下面 8 条：

1. 应用可在 Windows 和 macOS 启动
2. 双击应用会自动拉起 sidecar，不需要用户手动起服务
3. 关闭应用后 sidecar 会自动退出
4. 可以选择目标窗口、脚本和 profile
5. 可以完成一次完整 `start -> run -> stop`
6. 可以完成一次完整 `start -> pause -> resume -> stop`
7. 运行时可看到预览、日志和指标更新
8. 失败时可查看错误提示和调试产物

补充扩展性验收：

- 新增同一游戏流程时不需要修改 runner
- 新增新游戏时不需要修改前端协议

## 8. 推荐分工方式

如果多人协作，建议按下面的边界拆：

- A：前端骨架、Session、运行控制、日志 UI
- B：Python runtime、session service、run controller、bridge server
- C：游戏适配层、FlowScript、helpers、artifact 体系
- D：打包、权限处理、安装验证、跨平台联调

这样拆分的好处是：

- 前后端边界清楚
- 游戏逻辑不阻塞 UI 开发
- 打包和权限问题可以尽早并行验证

## 9. 最终建议

开发过程中不要把这份任务列表当“功能愿望单”，而要当作验收清单。

也就是说每完成一个阶段，都要回答三件事：

- 这个阶段是否已经能演示
- 这个阶段是否已经能验证
- 这个阶段的失败路径是否已经可观察

只有这样，最后交付出来的才会是一个真的能跑、能查、能扩的桌面自动化产品，而不是一组拼起来的界面和脚本。
