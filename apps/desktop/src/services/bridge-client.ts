export type ConnectionState = "connecting" | "connected" | "offline";

export type SessionSummary = {
  runId: string | null;
  status: string;
  platform: string;
  windowId: string | null;
  windowTitle: string | null;
  windowMode: string | null;
  profileId: string | null;
  profileName: string | null;
};

type BridgeEvent =
  | { type: "connection/status"; payload: { state: string } }
  | { type: "connection/heartbeat"; payload: { ts: string } }
  | { type: "session/updated"; payload: SessionSummary }
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
}
