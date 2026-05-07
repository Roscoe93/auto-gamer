import { useEffect, useState } from "react";
import { BridgeClient, PreviewFrame } from "../../../services/bridge-client";
import "./PreviewCanvas.css";

interface PreviewCanvasProps {
  client: BridgeClient;
}

export function PreviewCanvas({ client }: PreviewCanvasProps) {
  const [frame, setFrame] = useState<PreviewFrame | null>(null);

  useEffect(() => {
    const unsubscribe = client.subscribe((event) => {
      // Note: The python backend sends the payload fields directly inside the message
      // So event itself is { type: "preview/frame", image: "...", overlays: [] }
      // We need to type-cast or check properly
      if (event.type === "preview/frame") {
        // The backend POC had payload flat, but let's check if we wrapped it in payload
        // Actually, our bridge server currently just passes the raw message?
        // Wait, looking at the python CaptureService, it sends:
        // { type: "preview/frame", image: "...", overlays: [...], ... }
        // Let's adapt it here
        const data = event as any;
        setFrame({
          image: data.image || (data.payload && data.payload.image),
          overlays: data.overlays || (data.payload && data.payload.overlays) || [],
          originalWidth: data.originalWidth || (data.payload && data.payload.originalWidth) || 800,
          originalHeight: data.originalHeight || (data.payload && data.payload.originalHeight) || 600,
        });
      }
    });

    return () => unsubscribe();
  }, [client]);

  if (!frame) {
    return (
      <div className="preview-canvas empty">
        <p>等待图像推流...</p>
        <p className="hint">请先在上方选择目标窗口</p>
      </div>
    );
  }

  return (
    <div className="preview-canvas">
      <img src={frame.image} alt="Preview Stream" />
      
      <svg 
        className="overlay-layer" 
        viewBox={`0 0 ${frame.originalWidth} ${frame.originalHeight}`}
        preserveAspectRatio="xMidYMid meet"
      >
        {frame.overlays.map((overlay) => {
          let color = "var(--kuroneko-match, #00FF00)";
          if (overlay.kind === "safe_area") color = "var(--kuroneko-safe, #00BFFF)";
          if (overlay.kind === "text") color = "var(--kuroneko-text-highlight, #FFA500)";

          const labelText = `${overlay.label} (${(overlay.score * 100).toFixed(0)}%)`;
          // Rough width estimation for SVG text background
          const textWidth = labelText.length * 9;

          return (
            <g key={overlay.id}>
              <rect
                x={overlay.x}
                y={overlay.y}
                width={overlay.w}
                height={overlay.h}
                className="box-rect"
                stroke={color}
              />
              <rect
                x={overlay.x}
                y={overlay.y - 20}
                width={textWidth}
                height={20}
                className="box-label-bg"
                fill={color}
              />
              <text
                x={overlay.x + 4}
                y={overlay.y - 6}
                className="box-text"
              >
                {labelText}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
