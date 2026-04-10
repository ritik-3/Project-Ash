from __future__ import annotations

import ctypes
from pathlib import Path


def _active_window_title() -> str:
    user32 = ctypes.windll.user32
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return "Unknown"
    length = user32.GetWindowTextLengthW(hwnd)
    buffer = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buffer, length + 1)
    return buffer.value or "Unknown"


def summarize_screen_with_ocr() -> str:
    window_title = _active_window_title()
    try:
        import tempfile

        import mss
        from mss import tools

        with tempfile.TemporaryDirectory() as tmp_dir:
            image_path = Path(tmp_dir) / "screen.png"
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                shot = sct.grab(monitor)
                tools.to_png(shot.rgb, shot.size, output=str(image_path))

            try:
                import easyocr

                reader = easyocr.Reader(["en"], gpu=False)
                lines = reader.readtext(str(image_path), detail=0)
                text = " ".join(line.strip() for line in lines if line.strip())
                if text:
                    return f"Window: {window_title}. Vision summary: {text[:400]}"
            except Exception:
                pass

        return f"Window: {window_title}. Vision fallback captured screen, but OCR text was limited."
    except Exception:
        return (
            f"Window: {window_title}. Vision fallback unavailable. Install automation extras (mss/easyocr) "
            "or use browser/desktop structured adapters."
        )
