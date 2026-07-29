from __future__ import annotations

import re
import time
from pathlib import Path

import cv2
import numpy as np

BASE_DIR = Path(__file__).resolve().parent
VIDEOS_DIR = BASE_DIR / "capturas" / "videos"
PHOTOS_DIR = BASE_DIR / "capturas" / "fotos"

WINDOW = "Cámara"
FPS_FALLBACK = 30

BTN_RECORD = (20, 20, 140, 60)
BTN_STOP = (160, 20, 260, 60)
BTN_PHOTO = (280, 20, 400, 60)


def next_path(folder: Path, prefix: str, extension: str) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    pattern = re.compile(rf"^{re.escape(prefix)}_(\d+)\.{re.escape(extension)}$")
    max_index = 0
    for path in folder.iterdir():
        match = pattern.match(path.name)
        if match:
            max_index = max(max_index, int(match.group(1)))
    return folder / f"{prefix}_{max_index + 1:03d}.{extension}"


def draw_button(frame: np.ndarray, rect: tuple[int, int, int, int], label: str, color: tuple[int, int, int]) -> None:
    x1, y1, x2, y2 = rect
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, -1)
    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
    size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
    tx = x1 + (x2 - x1 - size[0]) // 2
    ty = y1 + (y2 - y1 + size[1]) // 2
    cv2.putText(frame, label, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)


def point_in_rect(x: int, y: int, rect: tuple[int, int, int, int]) -> bool:
    x1, y1, x2, y2 = rect
    return x1 <= x <= x2 and y1 <= y <= y2


class CameraApp:
    def __init__(self) -> None:
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise RuntimeError("No se pudo abrir la cámara")

        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or FPS_FALLBACK
        if self.fps <= 0:
            self.fps = FPS_FALLBACK

        w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 640)
        h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 480)
        self.frame_size = (w, h)

        self.writer: cv2.VideoWriter | None = None
        self.recording = False
        self.last_frame: np.ndarray | None = None
        self.status = "Listo — clic en botones o teclas R / S / P / Q"
        self.countdown_until = 0.0
        self.countdown_active = False

        cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(WINDOW, self._on_mouse)

    def _on_mouse(self, event: int, x: int, y: int, _flags: int, _param) -> None:
        if event != cv2.EVENT_LBUTTONDOWN:
            return
        if point_in_rect(x, y, BTN_RECORD):
            self.start_recording()
        elif point_in_rect(x, y, BTN_STOP):
            self.stop_recording()
        elif point_in_rect(x, y, BTN_PHOTO):
            self.start_photo_countdown()

    def start_recording(self) -> None:
        if self.recording or self.countdown_active:
            return

        path = next_path(VIDEOS_DIR, "video", "mp4")
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(str(path), fourcc, self.fps, self.frame_size)
        if not writer.isOpened():
            self.status = "Error al iniciar la grabación"
            return

        self.writer = writer
        self.recording = True
        self.status = f"Grabando → {path.name}"

    def stop_recording(self) -> None:
        if not self.recording:
            return

        self.recording = False
        if self.writer is not None:
            self.writer.release()
            self.writer = None
        self.status = "Video guardado"

    def start_photo_countdown(self) -> None:
        if self.recording or self.countdown_active or self.last_frame is None:
            return

        self.countdown_active = True
        self.countdown_until = time.time() + 3
        self.status = "Foto en 3 segundos..."

    def _save_photo(self) -> None:
        if self.last_frame is None:
            self.status = "No hay frame para guardar"
            return

        path = next_path(PHOTOS_DIR, "foto", "jpg")
        frame = cv2.flip(self.last_frame, 1)
        if cv2.imwrite(str(path), frame):
            self.status = f"Foto guardada → {path.name}"
        else:
            self.status = "Error al guardar la foto"

    def _draw_ui(self, frame: np.ndarray) -> np.ndarray:
        display = cv2.flip(frame, 1)
        h, w = display.shape[:2]

        overlay = display.copy()
        draw_button(overlay, BTN_RECORD, "Grabar", (60, 180, 75))
        draw_button(overlay, BTN_STOP, "Stop", (200, 80, 80))
        draw_button(overlay, BTN_PHOTO, "Foto (3s)", (80, 130, 220))

        if self.recording:
            cv2.circle(overlay, (w - 30, 30), 12, (0, 0, 255), -1)

        if self.countdown_active:
            remaining = max(0, int(self.countdown_until - time.time()) + 1)
            if remaining > 0:
                text = str(remaining)
                scale = 4
                thickness = 8
                size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, thickness)[0]
                tx = (w - size[0]) // 2
                ty = (h + size[1]) // 2
                cv2.putText(overlay, text, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, scale, (255, 255, 255), thickness + 2)
                cv2.putText(overlay, text, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 120, 255), thickness)
            elif time.time() >= self.countdown_until:
                self.countdown_active = False
                self._save_photo()

        cv2.rectangle(overlay, (0, h - 40), (w, h), (40, 40, 40), -1)
        cv2.putText(overlay, self.status[:80], (10, h - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (240, 240, 240), 1)
        cv2.putText(overlay, "R=Grabar  S=Stop  P=Foto  Q=Salir", (10, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)

        return overlay

    def run(self) -> None:
        delay = max(1, int(1000 / self.fps))

        try:
            while True:
                ok, frame = self.cap.read()
                if not ok:
                    self.status = "Error leyendo la cámara"
                    break

                self.last_frame = frame.copy()
                if self.recording and self.writer is not None:
                    self.writer.write(frame)

                display = self._draw_ui(frame)
                cv2.imshow(WINDOW, display)

                key = cv2.waitKey(delay) & 0xFF
                if key in (ord("q"), ord("Q"), 27):
                    break
                if key in (ord("r"), ord("R")):
                    self.start_recording()
                elif key in (ord("s"), ord("S")):
                    self.stop_recording()
                elif key in (ord("p"), ord("P")):
                    self.start_photo_countdown()
        finally:
            if self.recording:
                self.stop_recording()
            self.cap.release()
            cv2.destroyAllWindows()


if __name__ == "__main__":
    CameraApp().run()
