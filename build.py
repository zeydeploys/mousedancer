#!/usr/bin/env python3
"""
build.py — Move Mouse için tek komutla executable üretir.

Kullanım:
    python build.py

Çıktı:
    dist/MoveMouse          (macOS/Linux)
    dist/MoveMouse.exe      (Windows)
"""

import subprocess
import sys
import platform
import shutil
from pathlib import Path

OS = platform.system()  # "Windows" | "Darwin" | "Linux"

REQUIRED_PACKAGES = [
    "pyautogui",
    "pystray",
    "pillow",
    "pyinstaller",
]

# Linux'ta ekstra sistem paketi gerekebilir
LINUX_EXTRA = [
    "python3-gi",       # GTK için (apt)
    "gir1.2-appindicator3-0.1",
]


def run(cmd: list, **kwargs):
    print(f"\n▶ {' '.join(cmd)}\n")
    result = subprocess.run(cmd, **kwargs)
    if result.returncode != 0:
        print(f"❌ Hata! Çıkış kodu: {result.returncode}")
        sys.exit(result.returncode)


def install_packages():
    print("📦 Gerekli Python paketleri kuruluyor...")
    run([sys.executable, "-m", "pip", "install", "--upgrade"] + REQUIRED_PACKAGES)

    if OS == "Linux":
        print("\n⚠️  Linux'ta sistem paketlerine de ihtiyaç olabilir:")
        print("   sudo apt install python3-gi gir1.2-appindicator3-0.1")
        print("   (GTK/AppIndicator tray için)\n")


def clean():
    """Önceki build'i temizle."""
    for folder in ["build", "dist", "__pycache__"]:
        if Path(folder).exists():
            shutil.rmtree(folder)
            print(f"🗑  {folder}/ temizlendi")


def build():
    print(f"\n🔨 {OS} için build başlıyor...\n")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",           # Tek dosya
        "--windowed",          # Terminal penceresi açma (macOS/Windows)
        "--name", "MoveMouse",
        "--clean",
    ]

    # Platform'a özel hidden import'lar
    hidden = [
        "PIL._tkinter_finder",
        "PIL.Image",
        "PIL.ImageDraw",
        "pyautogui",
        "pynput",
        "pynput.mouse",
        "pynput.keyboard",
    ]

    if OS == "Windows":
        hidden += ["pystray._win32"]
    elif OS == "Darwin":
        hidden += ["pystray._darwin"]
        cmd += ["--target-arch", "universal2"]  # Apple Silicon + Intel
    else:  # Linux
        hidden += ["pystray._gtk", "pystray._appindicator"]

    for h in hidden:
        cmd += ["--hidden-import", h]

    # Gereksiz modülleri dışla (daha küçük dosya)
    for exc in ["matplotlib", "numpy", "scipy", "_tkinter"]:
        cmd += ["--exclude-module", exc]

    cmd.append("move_mouse.py")
    run(cmd)


def report():
    exe_name = "MoveMouse.exe" if OS == "Windows" else "MoveMouse"
    exe_path = Path("dist") / exe_name
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / 1024 / 1024
        print(f"\n✅ Build başarılı!")
        print(f"   📁 Dosya : {exe_path.resolve()}")
        print(f"   📏 Boyut : {size_mb:.1f} MB")
        print(f"\n   Çalıştırmak için:")
        if OS == "Windows":
            print(f"   .\\dist\\MoveMouse.exe")
        elif OS == "Darwin":
            print(f"   open dist/MoveMouse")
        else:
            print(f"   chmod +x dist/MoveMouse && ./dist/MoveMouse")
    else:
        print(f"\n❌ Executable bulunamadı: {exe_path}")


if __name__ == "__main__":
    print("=" * 50)
    print("  Move Mouse — Build Script")
    print(f"  Platform: {OS} / Python {sys.version.split()[0]}")
    print("=" * 50)

    install_packages()
    clean()
    build()
    report()
