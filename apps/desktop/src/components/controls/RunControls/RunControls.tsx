import { BridgeClient, SessionSummary } from "../../../services/bridge-client";
import { Button } from "../../ui/Button";
import "./RunControls.css";

export function RunControls({
  client,
  session
}: {
  client: BridgeClient;
  session: SessionSummary;
}) {
  const { status, windowId, metrics } = session;

  const handleStart = () => client.startRun();
  const handlePause = () => client.pauseRun();
  const handleResume = () => client.resumeRun();
  const handleStop = () => client.stopRun();

  const formatDuration = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  };

  return (
    <div className="flex-col">
      <div className="flex-row">
        {status === "idle" && (
          <Button
            variant="primary"
            onClick={handleStart}
            disabled={!windowId}
          >
            ▶ 开始运行
          </Button>
        )}

        {status === "running" && (
          <Button
            variant="pause"
            onClick={handlePause}
          >
            ⏸ 暂停
          </Button>
        )}

        {status === "paused" && (
          <Button
            variant="primary"
            onClick={handleResume}
          >
            ▶ 继续
          </Button>
        )}

        {(status === "running" || status === "paused") && (
          <Button
            variant="stop"
            onClick={handleStop}
          >
            ⏹ 停止
          </Button>
        )}
      </div>

      <div className="metrics-panel">
        <div className="metric-item">
          <span className="metric-label">运行时长</span>
          <div className="metric-value">
            {formatDuration(metrics.durationSeconds)}
          </div>
        </div>
        <div className="metric-item">
          <span className="metric-label">执行动作</span>
          <div className="metric-value">
            {metrics.actionCount}
          </div>
        </div>
        <div className="metric-item">
          <span className="metric-label">恢复次数</span>
          <div className="metric-value">
            {metrics.resumeCount}
          </div>
        </div>
      </div>
    </div>
  );
}
