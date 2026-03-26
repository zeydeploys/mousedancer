"""
Move Mouse - Prototip v0.1
--------------------------
Kurulum:
    pip install pyautogui pystray pillow

Çalıştırma:
    python move_mouse.py
"""

import threading
import time
import math
import pyautogui
import pystray
from PIL import Image, ImageDraw

# ── Ayarlar ──────────────────────────────────────────────
INTERVAL_SECONDS = 60       # Her kaç saniyede bir hareket etsin
MOVE_RADIUS = 5             # Kaç pixel çember çizsin (0 = küçük sarsıntı)
# ─────────────────────────────────────────────────────────

pyautogui.FAILSAFE = False  # Köşeye götürünce çökmesini önle

class MoveMouse:
    def __init__(self):
        self.running = False
        self.thread = None

    # ── Fare hareketi ──
    def _move(self):
        """Mevcut konumdan küçük bir çember çizer, sonra geri döner."""
        x, y = pyautogui.position()
        steps = 12
        for i in range(steps + 1):
            angle = 2 * math.pi * i / steps
            nx = x + int(MOVE_RADIUS * math.cos(angle))
            ny = y + int(MOVE_RADIUS * math.sin(angle))
            pyautogui.moveTo(nx, ny, duration=0.05)
        pyautogui.moveTo(x, y, duration=0.05)  # başlangıç noktasına dön

    # ── Ana döngü ──
    def _loop(self):
        while self.running:
            self._move()
            # INTERVAL boyunca uyku (1'er saniyelik dilimlerle, durdurulabilir)
            for _ in range(INTERVAL_SECONDS):
                if not self.running:
                    break
                time.sleep(1)

    # ── Başlat / Durdur ──
    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._loop, daemon=True)
            self.thread.start()
            print("[MoveMouse] Başladı")

    def stop(self):
        self.running = False
        print("[MoveMouse] Durdu")


# ── Tray ikonu oluştur ──
def make_icon(active: bool) -> Image.Image:
    """16x16 basit ikon: aktifse yeşil, pasifse gri daire."""
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    color = (80, 200, 120) if active else (150, 150, 150)
    draw.ellipse([8, 8, 56, 56], fill=color)
    return img


# ── Tray menüsü ──
def run_tray(app: MoveMouse):
    state = {"active": False}

    def toggle(icon, item):
        state["active"] = not state["active"]
        if state["active"]:
            app.start()
        else:
            app.stop()
        icon.icon = make_icon(state["active"])
        icon.title = "Move Mouse — Aktif" if state["active"] else "Move Mouse — Beklemede"

    def quit_app(icon, item):
        app.stop()
        icon.stop()

    menu = pystray.Menu(
        pystray.MenuItem("▶ Başlat / ⏹ Durdur", toggle, default=True),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("❌ Çıkış", quit_app),
    )

    icon = pystray.Icon(
        name="move_mouse",
        icon=make_icon(False),
        title="Move Mouse — Beklemede",
        menu=menu,
    )
    icon.run()


# ── Giriş noktası ──
if __name__ == "__main__":
    app = MoveMouse()
    print("Move Mouse başlatıldı. Sistem tepsisine bakın.")
    run_tray(app)
