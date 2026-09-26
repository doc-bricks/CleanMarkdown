"""Vertragstests für App-Icons und Asset-Suiten von CleanMarkdown.

Prüft Master-Icons, Multi-Layer Windows-ICOs, Assets-Parität,
Mobile/PWA-Suite, Windows Store Readiness und App-Icon-Lader.
"""

from __future__ import annotations

import json
from pathlib import Path
import struct

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _read_ico_sizes(ico_path: Path) -> list[tuple[int, int]]:
    with open(ico_path, "rb") as f:
        _reserved, ico_type, count = struct.unpack("<HHH", f.read(6))
        assert ico_type == 1, f"{ico_path.name} ist keine gültige ICO-Datei"
        sizes: list[tuple[int, int]] = []
        for _ in range(count):
            w, h, _colors, _res, _planes, _bpp, _size, _offset = struct.unpack(
                "<BBBBHHII", f.read(16)
            )
            sizes.append((w or 256, h or 256))
        return sizes


def test_master_icons_exist() -> None:
    desktop_png = PROJECT_ROOT / "DesktopIcon.png"
    icon_png = PROJECT_ROOT / "icon.png"
    clean_ico = PROJECT_ROOT / "CleanMarkdown.ico"
    desktop_ico = PROJECT_ROOT / "DesktopIcon.ico"
    root_ico = PROJECT_ROOT / "icon.ico"

    assert desktop_png.is_file(), "DesktopIcon.png fehlt im Root"
    assert icon_png.is_file(), "icon.png fehlt im Root"
    assert clean_ico.is_file(), "CleanMarkdown.ico fehlt im Root"
    assert desktop_ico.is_file(), "DesktopIcon.ico fehlt im Root"
    assert root_ico.is_file(), "icon.ico fehlt im Root"

    with Image.open(desktop_png) as img:
        assert img.size == (1024, 1024), "DesktopIcon.png muss 1024x1024 sein"

    with Image.open(icon_png) as img:
        assert img.size == (1024, 1024), "icon.png muss 1024x1024 sein"

    sizes = _read_ico_sizes(clean_ico)
    assert len(sizes) == 7, f"CleanMarkdown.ico muss 7 Layer haben, hat {len(sizes)}"
    assert (16, 16) in sizes and (24, 24) in sizes and (32, 32) in sizes and (256, 256) in sizes

    sizes_desktop = _read_ico_sizes(desktop_ico)
    assert len(sizes_desktop) == 7, "DesktopIcon.ico muss 7 Layer haben"

    sizes_icon = _read_ico_sizes(root_ico)
    assert len(sizes_icon) == 7, "icon.ico muss 7 Layer haben"


def test_assets_folder_parity() -> None:
    assets_dir = PROJECT_ROOT / "assets"
    assert assets_dir.is_dir(), "assets/ Verzeichnis fehlt"

    icon_png = assets_dir / "icon.png"
    icon_ico = assets_dir / "icon.ico"
    cleanmarkdown_ico = assets_dir / "cleanmarkdown.ico"
    favicon_png = assets_dir / "favicon.png"
    favicon_ico = assets_dir / "favicon.ico"

    assert icon_png.is_file(), "assets/icon.png fehlt"
    assert icon_ico.is_file(), "assets/icon.ico fehlt"
    assert cleanmarkdown_ico.is_file(), "assets/cleanmarkdown.ico fehlt"
    assert favicon_png.is_file(), "assets/favicon.png fehlt"
    assert favicon_ico.is_file(), "assets/favicon.ico fehlt"

    with Image.open(icon_png) as img:
        assert img.size == (1024, 1024), "assets/icon.png muss 1024x1024 sein"

    with Image.open(favicon_png) as img:
        assert img.size == (32, 32), "assets/favicon.png muss 32x32 sein"

    clean_sizes = _read_ico_sizes(cleanmarkdown_ico)
    assert len(clean_sizes) == 7, "assets/cleanmarkdown.ico muss 7 Layer haben"
    assert (24, 24) in clean_sizes, "assets/cleanmarkdown.ico fehlt 24x24 Layer"

    icon_sizes = _read_ico_sizes(icon_ico)
    assert len(icon_sizes) == 7, "assets/icon.ico muss 7 Layer haben"

    fav_sizes = _read_ico_sizes(favicon_ico)
    assert (16, 16) in fav_sizes and (32, 32) in fav_sizes


def test_mobile_pwa_icons_and_manifest() -> None:
    mobile_dir = PROJECT_ROOT / "mobile_icons"
    assert mobile_dir.is_dir(), "mobile_icons/ Verzeichnis fehlt"

    required_files = [
        "icon.png",
        "icon-192.png",
        "icon-512.png",
        "icon-maskable-192.png",
        "icon-maskable-512.png",
        "apple-touch-icon.png",
        "favicon.png",
        "favicon.ico",
        "manifest.json",
    ]
    for fname in required_files:
        path = mobile_dir / fname
        assert path.is_file(), f"mobile_icons/{fname} fehlt"

    with Image.open(mobile_dir / "icon.png") as img:
        assert img.size == (1024, 1024)
    with Image.open(mobile_dir / "icon-192.png") as img:
        assert img.size == (192, 192)
    with Image.open(mobile_dir / "icon-512.png") as img:
        assert img.size == (512, 512)
    with Image.open(mobile_dir / "icon-maskable-192.png") as img:
        assert img.size == (192, 192)
    with Image.open(mobile_dir / "icon-maskable-512.png") as img:
        assert img.size == (512, 512)
    with Image.open(mobile_dir / "apple-touch-icon.png") as img:
        assert img.size == (180, 180)

    # Prüfe Unterordner icons/
    icons_sub = mobile_dir / "icons"
    assert icons_sub.is_dir(), "mobile_icons/icons/ fehlt"
    for fname in ("Icon-192.png", "Icon-512.png", "Icon-maskable-192.png", "Icon-maskable-512.png"):
        assert (icons_sub / fname).is_file(), f"mobile_icons/icons/{fname} fehlt"

    # W3C Web App Manifest Validierung
    manifest_data = json.loads((mobile_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest_data["name"] == "CleanMarkdown"
    assert manifest_data["short_name"] == "CleanMarkdown"
    assert len(manifest_data["icons"]) >= 4
    for icon_entry in manifest_data["icons"]:
        icon_path = mobile_dir / icon_entry["src"]
        assert icon_path.is_file(), f"Manifest-Icon nicht gefunden: {icon_entry['src']}"


def test_store_assets() -> None:
    store_dir = PROJECT_ROOT / "store_assets"
    assert store_dir.is_dir(), "store_assets/ Verzeichnis fehlt"

    expected_sizes = {
        "icon_44x44.png": (44, 44),
        "icon_50x50.png": (50, 50),
        "icon_150x150.png": (150, 150),
        "icon_310x150.png": (310, 150),
        "icon_310x310.png": (310, 310),
    }
    for filename, expected_size in expected_sizes.items():
        file_path = store_dir / filename
        assert file_path.is_file(), f"store_assets/{filename} fehlt"
        with Image.open(file_path) as img:
            assert img.size == expected_size, (
                f"{filename} hat Größe {img.size}, erwartet {expected_size}"
            )


def test_app_icon_loader_returns_valid_icon() -> None:
    from PySide6.QtWidgets import QApplication
    from main import load_app_icon

    _app = QApplication.instance() or QApplication([])
    icon = load_app_icon()
    assert not icon.isNull(), "load_app_icon() liefert ein leeres (null) QIcon zurück"


def _ico_frame_on_white(ico_path: Path, size: int) -> Image.Image | None:
    """Same technique as .SOFTWARE/_STORE/icon_consistency_check.py, kept as
    a small self-contained copy here (not imported) so this test runs in CI
    without the OneDrive-only shared-tooling checkout being present."""
    img = Image.open(ico_path)
    if size not in {s[0] for s in img.info.get("sizes", [])}:
        return None
    img = Image.open(ico_path)
    try:
        img.size = (size, size)
        img.load()
    except (ValueError, OSError):
        return None
    rgba = img.convert("RGBA")
    bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    bg.alpha_composite(rgba)
    return bg.convert("RGB")


def _perceptual_diff(a: Image.Image, b: Image.Image, size: int = 32) -> float:
    a = a.resize((size, size), Image.LANCZOS)
    b = b.resize((size, size), Image.LANCZOS)
    a_bytes, b_bytes = a.tobytes(), b.tobytes()
    return sum(abs(x - y) for x, y in zip(a_bytes, b_bytes)) / (len(a_bytes) * 255)


CROSS_FILE_THRESHOLD = 0.20

# Every .ico that load_app_icon() (main.py) can hand to setWindowIcon()/the
# EXE resource, in its own fallback order, plus the browser favicon -- and
# every PNG master/fallback that feeds one of those .ico files or is used
# directly as a fallback icon. Review of PR#5 (T-20260926-864299616) found
# that fixing only the first two .ico candidates left the PNG masters
# (icon.png/DesktopIcon.png/assets/icon.png, load_app_icon's PNG fallback)
# and the favicon un-rebranded -- still pointing at the pre-fix design.
ALL_ICO_FILES = (
    "assets/cleanmarkdown.ico",
    "assets/icon.ico",
    "CleanMarkdown.ico",
    "icon.ico",
    "DesktopIcon.ico",
    "assets/favicon.ico",
)
ALL_MASTER_PNGS = ("icon.png", "DesktopIcon.png", "assets/icon.png", "assets/favicon.png")


def test_window_icon_matches_store_tile_branding() -> None:
    """Regression test for T-20260926-864299616 (CleanMarkdown 1.0.3): the
    Store tile/taskbar icon was correct after a rebrand, but the desktop
    icons feeding the EXE resource and the runtime window titlebar icon
    (via load_app_icon()) still carried an older, different design --
    caught here by comparing every frame of every icon file against the
    Store tile directly, in the built-bundle sense that matters (the actual
    pixels Windows draws), not just "a QIcon exists".
    """
    store_tile = PROJECT_ROOT / "store_assets" / "Square310x310Logo.png"
    assert store_tile.is_file(), "store_assets/Square310x310Logo.png fehlt"
    tile_img = Image.open(store_tile).convert("RGBA")
    bg = Image.new("RGBA", tile_img.size, (255, 255, 255, 255))
    bg.alpha_composite(tile_img)
    tile_rgb = bg.convert("RGB")

    checked = 0
    for ico_name in ALL_ICO_FILES:
        ico_path = PROJECT_ROOT / ico_name
        assert ico_path.is_file(), f"{ico_name} fehlt"
        img = Image.open(ico_path)
        sizes = sorted({s[0] for s in img.info.get("sizes", [])})
        assert sizes, f"{ico_name}: keine Groessen im .ico-Verzeichnis gefunden"
        for size in sizes:
            frame = _ico_frame_on_white(ico_path, size)
            if frame is None:
                continue  # directory/loader mismatch for this size -- not this test's concern
            diff = _perceptual_diff(frame, tile_rgb)
            checked += 1
            assert diff <= CROSS_FILE_THRESHOLD, (
                f"{ico_name} ({size}x{size}) weicht von {store_tile.name} um {diff:.2f} ab "
                f"(Grenze {CROSS_FILE_THRESHOLD}) -- Desktop-Icon und Store-Kachel zeigen "
                "unterschiedliche Designs. Signatur von T-20260926-864299616: eines wurde "
                "neu gebrandet, das andere nicht. .ico aus derselben Quelle wie die "
                "Store-Kachel neu erzeugen."
            )
    assert checked > 0, "kein einziger .ico-Frame konnte geprueft werden"

    for png_name in ALL_MASTER_PNGS:
        png_path = PROJECT_ROOT / png_name
        assert png_path.is_file(), f"{png_name} fehlt"
        png_img = Image.open(png_path).convert("RGBA")
        png_bg = Image.new("RGBA", png_img.size, (255, 255, 255, 255))
        png_bg.alpha_composite(png_img)
        diff = _perceptual_diff(png_bg.convert("RGB"), tile_rgb)
        assert diff <= CROSS_FILE_THRESHOLD, (
            f"{png_name} weicht von {store_tile.name} um {diff:.2f} ab "
            f"(Grenze {CROSS_FILE_THRESHOLD}) -- Master-/Fallback-PNG zeigt ein anderes "
            "Design als die Store-Kachel. Aus derselben Quelle neu erzeugen."
        )
