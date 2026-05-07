import { useEffect, useMemo, useState } from "react";

import { BridgeClient, ConnectionState, SessionSummary } from "./services/bridge-client";

const defaultSession: SessionSummary = {
  runId: null,
  status: "idle",
  platform: "unknown",
  windowId: null,
  windowTitle: null,
  windowMode: null,
  profileId: null,
  profileName: null
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
    <main className="page">
      <section className="panel">
        <p className="eyebrow">阶段 1 骨架</p>
        <h1>KuroNeko Studio Desktop</h1>
        <p className="subtitle">Tauri 壳层 + React 前端 + Python bridge 服务</p>
      </section>

      <section className="grid">
        <article className="card">
          <h2>连接状态</h2>
          <strong className={`status ${connectionState}`}>{connectionState}</strong>
          <p>最近心跳：{heartbeatTs ?? "暂无"}</p>
        </article>

        <article className="card">
          <h2>当前 Session</h2>
          <p>runId：{session.runId ?? "未启动"}</p>
          <p>status：{session.status}</p>
          <p>platform：{session.platform}</p>
        </article>

        <article className="card">
          <h2>窗口与 Profile</h2>
          <p>window：{session.windowTitle ?? "未选择"}</p>
          <p>mode：{session.windowMode ?? "未设置"}</p>
          <p>profile：{session.profileName ?? "未设置"}</p>
        </article>
      </section>

      <section className="panel">
        <h2>Bridge 健康</h2>
        <p>{lastError ?? "未收到错误事件"}</p>
      </section>
    </main>
  );
}
