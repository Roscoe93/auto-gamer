import { useEffect, useState, memo } from "react";
import { BridgeClient } from "../../../services/bridge-client";
import { Button } from "../../ui/Button";
import { Select } from "../../ui/Select";

interface WindowOption {
  id: string;
  title: string;
}

export const WindowSelector = memo(function WindowSelector({
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

  const selectOptions = windows.map((w) => ({ label: w.title, value: w.id }));

  return (
    <div className="flex-row">
      <div className="flex-1">
        <Select
          value={currentWindowId || ""}
          onChange={handleSelect}
          options={selectOptions}
          placeholder="-- 选择目标游戏窗口 --"
        />
      </div>
      <Button onClick={handleRefresh} disabled={loading}>
        {loading ? "刷新中..." : "刷新列表"}
      </Button>
    </div>
  );
});
