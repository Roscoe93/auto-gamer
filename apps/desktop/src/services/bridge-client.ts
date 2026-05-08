export interface ScriptManifest {
  id: string;
  name: string;
  version: string;
  description: string;
  author: string;
  schema: Record<string, any>;
}

export interface Profile {
  id: string;
  scriptId: string;
  name: string;
  parameters: Record<string, any>;
}

export type ConnectionState = "connecting" | "connected" | "offline";

export interface SessionMetrics {
  durationSeconds: number;
  actionCount: number;
  resumeCount: number;
}

export interface SessionSummary {
  runId: string | null;
  status: "idle" | "running" | "paused";
  platform: string;
  windowId: string | null;
  windowTitle: string | null;
  windowMode: string | null;
  profileId: string | null;
  profileName: string | null;
  metrics: SessionMetrics;
};

export interface PreviewOverlay {
  id: string;
  kind: string;
  label: string;
  score: number;
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface PreviewFrame {
  image: string; // base64 data uri
  overlays: PreviewOverlay[];
  originalWidth: number;
  originalHeight: number;
}

export interface LogEntry {
  timestamp: string;
  level: "debug" | "info" | "warning" | "error" | "critical";
  source: string;
  message: string;
}

type BridgeEvent =
  | { type: "connection/status"; payload: { state: string } }
  | { type: "connection/heartbeat"; payload: { ts: string } }
  | { type: "session/updated"; payload: SessionSummary }
  | { type: "session/windows-listed"; payload: Array<{ id: string; title: string }> }
  | { type: "scripts/listed"; payload: ScriptManifest[] }
  | { type: "profiles/listed"; payload: Profile[] }
  | { type: "profiles/saved"; payload: Profile }
  | { type: "profiles/deleted"; payload: { id: string } }
  | { type: "preview/frame"; payload: PreviewFrame }
  | { type: "log/entry"; payload: LogEntry }
  | { type: "error"; payload: { code: string; message: string } };

type BridgeListener = (event: BridgeEvent) => void;

export class BridgeClient {
  private socket: WebSocket | null = null;
  private listeners = new Set<BridgeListener>();
  private readonly url: string;

  constructor(url = "ws://127.0.0.1:8765") {
    this.url = url;
  }

  connect(): void {
    this.socket = new WebSocket(this.url);
    this.socket.addEventListener("message", (message) => {
      const parsed = JSON.parse(message.data) as BridgeEvent;
      this.listeners.forEach((listener) => listener(parsed));
    });
    this.socket.addEventListener("open", () => {
      this.send({ type: "session/get" });
    });
  }

  disconnect(): void {
    this.socket?.close();
    this.socket = null;
  }

  subscribe(listener: BridgeListener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  send(message: object): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    }
  }

  listWindows(): void {
    this.send({ type: "session/list-windows" });
  }

  selectWindow(windowId: string, windowTitle: string): void {
    this.send({
      type: "session/select-window",
      payload: { windowId, windowTitle }
    });
  }

  startRun(): void {
    this.send({ type: "run/start" });
  }

  pauseRun(): void {
    this.send({ type: "run/pause" });
  }

  resumeRun(): void {
    this.send({ type: "run/resume" });
  }

  stopRun(): void {
    this.send({ type: "run/stop" });
  }

  listScripts(): void {
    this.send({ type: "scripts/list" });
  }

  listProfiles(): void {
    this.send({ type: "profiles/list" });
  }

  saveProfile(profile: Partial<Profile>): void {
    this.send({ type: "profiles/save", payload: profile });
  }

  deleteProfile(id: string): void {
    this.send({ type: "profiles/delete", payload: { id } });
  }
}
