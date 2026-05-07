import { useEffect, useMemo, useState } from "react";
import { BridgeClient, ConnectionState, SessionSummary } from "./services/bridge-client";
import { Page } from "./components/layout/Page";
import { Panel } from "./components/layout/Panel";
import { Card } from "./components/layout/Card";
import { WindowSelector } from "./components/controls/WindowSelector";
import { RunControls } from "./components/controls/RunControls";
import { ScriptPanel } from "./components/scripts/ScriptPanel";
import { PreviewCanvas } from "./components/preview/PreviewCanvas";
import "./App.css";

const defaultSession: SessionSummary = {
  runId: null,
  status: "idle",
  platform: "unknown",
  windowId: null,
  windowTitle: null,
  windowMode: null,
  profileId: null,
  profileName: null,
  metrics: { durationSeconds: 0, actionCount: 0, resumeCount: 0 }
};

export function App() {
  const client = useMemo(() => new BridgeClient(), []);
  const [connectionState, setConnectionState] = useState<ConnectionState>("connecting");
  const [heartbeatTs, setHeartbeatTs] = useState<string | null>(null);
  const [session, setSession] = useState<SessionSummary>(defaultSession);
  const [lastError, setLastError] = useState<string | null>(null);

  useEffect(() => {
    const unsubscribe = client.subscribe((event) => {
      if (event.type === "connection/status") {
        setConnectionState(event.payload.state === "connected" ? "connected" : "offline");
        // When connected, fetch initial window list
        if (event.payload.state === "connected") {
          client.listWindows();
        }
      }

      if (event.type === "connection/heartbeat") {
        setHeartbeatTs(event.payload.ts);
      }

      if (event.type === "session/updated") {
        setSession(event.payload);
      }

      if (event.type === "error") {
        setLastError(`${event.payload.code}: ${event.payload.message}`);
      }
    });

    client.connect();

    return () => {
      unsubscribe();
      client.disconnect();
    };
  }, [client]);

  return (
    <Page>
      <Panel>
        <p className="eyebrow">阶段 3: 脚本、Profile 与参数管理</p>
        <h1>KuroNeko Studio</h1>
        <p className="subtitle">Tauri 壳层 + React 前端 + Python bridge 服务</p>
      </Panel>

      <section className="grid">
        <Card>
          <h2>连接状态</h2>
          <strong className={`status ${connectionState}`}>{connectionState}</strong>
          <p>最近心跳：{heartbeatTs ?? "暂无"}</p>
        </Card>

        <Card>
          <h2>当前 Session</h2>
          <p>runId：{session.runId ?? "未启动"}</p>
          <p>status：{session.status}</p>
          <p>platform：{session.platform}</p>
        </Card>

        <Card>
          <h2>目标窗口</h2>
          <div style={{ marginBottom: "16px" }}>
            <WindowSelector client={client} currentWindowId={session.windowId} />
          </div>
          <p>当前：{session.windowTitle ?? "未选择"}</p>
          <p>模式：{session.windowMode ?? "未设置"}</p>
        </Card>

        <Card className="span-2">
          <h2>参数配置</h2>
          <ScriptPanel client={client} connectionState={connectionState} />
        </Card>

        <Card className="span-2">
          <h2>识别预览</h2>
          <PreviewCanvas client={client} />
        </Card>

        <Card className="span-2">
          <h2>运行控制</h2>
          <RunControls client={client} session={session} />
        </Card>
      </section>

      <Panel>
        <h2>Bridge 健康</h2>
        <p>{lastError ?? "未收到错误事件"}</p>
      </Panel>
    </Page>
  );
}
