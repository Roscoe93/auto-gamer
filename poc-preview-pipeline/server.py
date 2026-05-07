import asyncio
import base64
import json
import time
import cv2
import numpy as np
import mss
import websockets
from rapidocr_onnxruntime import RapidOCR

# 初始化 OCR 引擎 (基于 ONNX，跨平台且极速，无需配置 GPU)
ocr = RapidOCR()

async def send_frames(websocket):
    print("Client connected!")
    with mss.mss() as sct:
        # 获取主显示器
        monitor = sct.monitors[1]

        # 为了演示和性能，我们截取屏幕中间的区域
        region = {
            "top": monitor["top"] + 200,
            "left": monitor["left"] + 200,
            "width": 1000,
            "height": 800
        }

        # 频率控制：OCR 毕竟是 CPU 计算，为了不拖垮推流，我们每 5 帧做一次 OCR
        frame_count = 0
        last_ocr_overlays = []

        while True:
            start_time = time.time()
            frame_count += 1

            # 1. 截图采集层
            sct_img = sct.grab(region)
            img = np.array(sct_img)

            # 2. 识别与组装层
            _, buffer = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), 60])
            b64_img = base64.b64encode(buffer).decode('utf-8')

            overlays = []

            # 降频执行 OCR (每 5 帧，约半秒执行一次)
            if frame_count % 5 == 1:
                # rapidocr 期望的是 BGR 格式
                img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR) if img.shape[2] == 4 else img
                # 执行文本检测
                ocr_result, _ = ocr(img_bgr)

                new_ocr_overlays = []
                if ocr_result:
                    for dt_box, rec_text, score in ocr_result:
                        # dt_box 是包含 4 个点的多边形，为了简单起见，我们取外接矩形
                        pts = np.array(dt_box, dtype=np.int32)
                        x, y, w, h = cv2.boundingRect(pts)

                        new_ocr_overlays.append({
                            "id": f"text_{x}_{y}",
                            "kind": "text",
                            "label": f"OCR: {rec_text}",
                            "score": float(score),
                            "x": int(x),
                            "y": int(y),
                            "w": int(w),
                            "h": int(h)
                        })
                last_ocr_overlays = new_ocr_overlays

            # 将最新的 OCR 结果加入 overlay
            overlays.extend(last_ocr_overlays)

            # 组装协议 Payload
            payload = {
                "type": "preview/frame",
                "image": f"data:image/jpeg;base64,{b64_img}",
                "overlays": overlays,
                "originalWidth": region["width"],
                "originalHeight": region["height"]
            }

            # 3. 传输层 (Transport)
            try:
                await websocket.send(json.dumps(payload))
            except websockets.exceptions.ConnectionClosed:
                print("Client disconnected.")
                break

            # 4. 节流层 (Throttle): 强制控制在约 10 FPS (100ms)
            elapsed = time.time() - start_time
            sleep_time = max(0, 0.1 - elapsed)
            await asyncio.sleep(sleep_time)

async def main():
    async with websockets.serve(send_frames, "127.0.0.1", 8766, process_request=process_request):
        print("🚀 POC Server running on ws://127.0.0.1:8766", flush=True)
        print("⏳ Waiting for frontend to connect...", flush=True)
        await asyncio.Future()  # run forever

# 添加一个简单的 CORS 处理（允许所有跨域）
async def process_request(connection, request):
    return None # 返回 None 表示接受请求

if __name__ == "__main__":
    asyncio.run(main())
