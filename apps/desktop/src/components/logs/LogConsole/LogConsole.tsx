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

  const getLevelColor = (level: string) => {
    switch (level) {
      case "debug": return "text-zinc-500";
      case "info": return "text-blue-400";
      case "warning": return "text-yellow-500";
      case "error": return "text-red-500";
      case "critical": return "text-red-600 font-bold";
      default: return "text-zinc-300";
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
    <div className="log-console-container bg-zinc-950 text-zinc-300 border-t border-zinc-800">
      <div className="log-console-header px-2 py-1 text-xs font-semibold tracking-wider text-zinc-500 border-b border-zinc-900 flex justify-between bg-zinc-950 z-10">
        <span>SERVICE LOGS</span>
        <button 
          onClick={() => setLogs([])}
          className="hover:text-zinc-300 cursor-pointer focus:outline-none"
        >
          CLEAR
        </button>
      </div>
      <div className="log-console-body p-2 overflow-y-auto tabular-nums font-mono text-[11px] leading-tight" ref={scrollRef}>
        {logs.length === 0 ? (
          <div className="text-zinc-600 italic">No logs available.</div>
        ) : (
          logs.map((log, i) => (
            <div key={i} className="flex gap-2 hover:bg-zinc-900/50 py-[1px]">
              <span className="text-zinc-600 shrink-0">{formatTime(log.timestamp)}</span>
              <span className={`shrink-0 w-12 uppercase ${getLevelColor(log.level)}`}>
                {log.level}
              </span>
              <span className="text-zinc-500 shrink-0 w-24 truncate" title={log.source}>
                [{log.source}]
              </span>
              <span className="break-all whitespace-pre-wrap">{log.message}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}