import asyncio
import base64
import json
import time
import logging
from typing import Callable, List, Optional, Dict, Any

import cv2
import mss
import numpy as np
from rapidocr_onnxruntime import RapidOCR

from app.core.session_service import SessionService
from app.windows.window_service import WindowService

logger = logging.getLogger("kuroneko.capture")

class CaptureService:
    def __init__(self, session_service: SessionService, window_service: WindowService):
        self.session_service = session_service
        self.window_service = window_service
        self.ocr = RapidOCR()
        self.is_running = False
        self._task: Optional[asyncio.Task] = None
        self._listeners: list[Callable[[dict], None]] = []

    def start(self):
        if not self.is_running:
            logger.info("Starting CaptureService...")
            self.is_running = True
            self._task = asyncio.create_task(self._capture_loop())
        else:
            logger.warning("CaptureService is already running.")

    def stop(self):
        logger.info("Stopping CaptureService...")
        self.is_running = False
        if self._task:
            self._task.cancel()

    def add_listener(self, callback: Callable[[dict], None]):
        self._listeners.append(callback)

    def remove_listener(self, callback: Callable[[dict], None]):
        if callback in self._listeners:
            self._listeners.remove(callback)

    async def _capture_loop(self):
        frame_count = 0
        last_ocr_overlays = []

        with mss.mss() as sct:
            while self.is_running:
                start_time = time.time()

                # Check current target window
                summary = self.session_service.get_summary()
                window_id = summary.windowId

                if not window_id:
                    if frame_count % 30 == 0:
                        logger.debug("No window_id selected in session, skipping capture.")
                    frame_count += 1
                    await asyncio.sleep(0.1)
                    continue

                # 1. Get dynamic window rect
                rect = self.window_service.get_window_rect(window_id)
                if not rect or rect.width <= 0 or rect.height <= 0:
                    if frame_count % 10 == 0:
                        logger.warning(f"Cannot get valid rect for window_id {window_id}: {rect}")
                    frame_count += 1
                    await asyncio.sleep(0.5)
                    continue

                # 2. Capture Region
                # 兼容 macOS Retina 屏幕 (物理像素通常是逻辑坐标的 2 倍)
                # 这里为了稳妥，先用逻辑坐标截取。如果遇到 Retina，mss 可能会截到错位的区域
                # 最好的做法是用 mss.monitors 获取缩放比例，但在 POC 阶段先放宽限制
                region = {
                    "top": int(rect.y),
                    "left": int(rect.x),
                    "width": int(rect.width),
                    "height": int(rect.height)
                }

                try:
                    sct_img = sct.grab(region)
                except Exception as e:
                    if frame_count % 10 == 0:
                        logger.error(f"Screenshot grab error for region {region}: {e}")
                    frame_count += 1
                    await asyncio.sleep(0.5)
                    continue

                img = np.array(sct_img)

                if frame_count % 30 == 0:
                    logger.debug(f"Captured frame for window {window_id}, size: {img.shape}")
                frame_count += 1

                # 3. Recognition & Overlay
                _, buffer = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), 60])
                b64_img = base64.b64encode(buffer).decode('utf-8')

                overlays = []

                # Throttled OCR (every 5 frames)
                if frame_count % 5 == 1:
                    img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR) if img.shape[2] == 4 else img
                    ocr_result, _ = self.ocr(img_bgr)

                    new_ocr_overlays = []
                    if ocr_result:
                        for dt_box, rec_text, score in ocr_result:
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

                overlays.extend(last_ocr_overlays)

                # Payload
                payload = {
                    "type": "preview/frame",
                    "image": f"data:image/jpeg;base64,{b64_img}",
                    "overlays": overlays,
                    "originalWidth": region["width"],
                    "originalHeight": region["height"]
                }

                # Broadcast
                for listener in self._listeners:
                    # We might need to schedule these safely
                    try:
                        listener(payload)
                    except Exception as e:
                        logger.error(f"Error broadcasting frame: {e}")

                # 4. Throttle (10 FPS max)
                elapsed = time.time() - start_time
                sleep_time = max(0, 0.1 - elapsed)
                await asyncio.sleep(sleep_time)
