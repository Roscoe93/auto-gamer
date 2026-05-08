import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { BridgeClient, PreviewFrame } from "../../../services/bridge-client";
import "./PreviewCanvas.css";

interface PreviewCanvasProps {
  client: BridgeClient;
}

export function PreviewCanvas({ client }: PreviewCanvasProps) {
  const [frame, setFrame] = useState<PreviewFrame | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);

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
      } else if (event.type === "session/updated") {
        if (event.payload.status === "idle") {
          setFrame(null);
        }
      }
    });

    return () => unsubscribe();
  }, [client]);

  if (!frame) {
    return (
      <div className="preview-canvas empty">
        <p>等待图像推流...</p>
        <p className="hint">请先选择目标窗口并开始运行</p>
      </div>
    );
  }

  const innerContent = (
    <>
      {isFullscreen && (
        <button
          className="preview-close-btn"
          onClick={(e) => {
            e.stopPropagation();
            setIsFullscreen(false);
          }}
        >
          CLOSE
        </button>
      )}
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
    </>
  );

  const fullscreenNode = isFullscreen ? createPortal(
    <div
      className="preview-canvas fullscreen"
      onClick={() => setIsFullscreen(false)}
      title="Click to exit fullscreen"
    >
      {innerContent}
    </div>,
    document.body
  ) : null;

  return (
    <>
      <div
        className={`preview-canvas ${isFullscreen ? 'placeholder' : ''}`}
        onClick={() => !isFullscreen && setIsFullscreen(true)}
        title={!isFullscreen ? "Click to enter fullscreen" : ""}
      >
        {!isFullscreen && innerContent}
        {isFullscreen && (
          <>
            <img src={frame.image} alt="Preview Stream" />
            <div className="placeholder-hint">全屏展示中...</div>
          </>
        )}
      </div>
      {fullscreenNode}
    </>
  );
}
