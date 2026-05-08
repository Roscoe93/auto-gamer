import { useEffect, useRef, useState } from "react";
import { BridgeClient, LogEntry } from "../../../services/bridge-client";
import "./LogConsole.css";

interface LogConsoleProps {
  client: BridgeClient;
}

export function LogConsole({ client }: LogConsoleProps) {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const unsubscribe = client.subscribe((event) => {
      if (event.type === "log/entry") {
        setLogs((prev) => {
          // Keep the last 1000 logs to prevent memory leak
          const newLogs = [...prev, event.payload];
          if (newLogs.length > 1000) {
            return newLogs.slice(newLogs.length - 1000);
          }
          return newLogs;
        });
      }
    });

    return () => unsubscribe();
  }, [client]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  const getLevelClass = (level: string) => {
    switch (level) {
      case "debug": return "level-debug";
      case "info": return "level-info";
      case "warning": return "level-warning";
      case "error": return "level-error";
      case "critical": return "level-critical";
      default: return "level-default";
    }
  };

  const formatTime = (isoString: string) => {
    try {
      const d = new Date(isoString);
      return d.toTimeString().split(' ')[0] + '.' + String(d.getMilliseconds()).padStart(3, '0');
    } catch {
      return isoString;
    }
  };

  return (
    <div className="log-console-container">
      <div className="log-console-header">
        <span>SERVICE LOGS</span>
        <button
          onClick={() => setLogs([])}
          className="log-console-clear-btn"
        >
          CLEAR
        </button>
      </div>
      <div className="log-console-body" ref={scrollRef}>
        {logs.length === 0 ? (
          <div className="log-empty">No logs available.</div>
        ) : (
          logs.map((log, i) => (
            <div key={i} className="log-entry">
              <span className="log-time">{formatTime(log.timestamp)}</span>
              <span className={`log-level ${getLevelClass(log.level)}`}>
                {log.level}
              </span>
              <span className="log-source" title={log.source}>
                [{log.source}]
              </span>
              <span className="log-message">{log.message}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}