import { useEffect, useState } from "react";
import { BridgeClient } from "../../services/bridge-client";

interface WindowOption {
  id: string;
  title: string;
}

export function WindowSelector({
  client,
  currentWindowId
}: {
  client: BridgeClient;
  currentWindowId: string | null;
}) {
  const [windows, setWindows] = useState<WindowOption[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const unsubscribe = client.subscribe((event) => {
      if (event.type === "session/windows-listed") {
        setWindows(event.payload);
        setLoading(false);
      }
    });

    return unsubscribe;
  }, [client]);

  const handleRefresh = () => {
    setLoading(true);
    client.listWindows();
  };

  const handleSelect = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const winId = e.target.value;
    if (!winId) {
      client.selectWindow("", "");
      return;
    }
    const win = windows.find((w) => w.id === winId);
    if (win) {
      client.selectWindow(win.id, win.title);
    }
  };

  return (
    <div className="window-selector">
      <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
        <select
          value={currentWindowId || ""}
          onChange={handleSelect}
          style={{
            flex: 1,
            padding: "6px 12px",
            background: "var(--kuroneko-bg-base)",
            color: "var(--kuroneko-text-primary)",
            border: "1px solid var(--kuroneko-text-muted)",
            borderRadius: "4px",
            outline: "none"
          }}
        >
          <option value="">-- 选择目标游戏窗口 --</option>
          {windows.map((w) => (
            <option key={w.id} value={w.id}>
              {w.title}
            </option>
          ))}
        </select>
        <button
          onClick={handleRefresh}
          disabled={loading}
          style={{
            padding: "6px 12px",
            background: "var(--kuroneko-bg-panel)",
            color: "var(--kuroneko-text-primary)",
            border: "1px solid var(--kuroneko-text-muted)",
            borderRadius: "4px",
            cursor: "pointer",
            whiteSpace: "nowrap"
          }}
        >
          {loading ? "刷新中..." : "刷新列表"}
        </button>
      </div>
    </div>
  );
}
