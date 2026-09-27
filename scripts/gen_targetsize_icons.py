"""Erzeugt die targetsize-/unplated-Varianten des Square44x44Logo für das MSIX.

Windows zieht Taskleisten-, Startmenü-Listen- und Dateityp-Symbole
(`uap:FileTypeAssociation`) aus `Square44x44Logo.targetsize-XX[_altform-*].png`
über `resources.pri`. Fehlen sie, skaliert Windows die 44-px-Kachel und setzt
sie auf eine Platte (T-20260927-699609650). Quelle ist bewusst die Store-Kachel
selbst, damit Kachel, EXE-Icon und Dateityp-Symbol aus einer Quelle stammen.

    python scripts/gen_targetsize_icons.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

STORE_ASSETS = Path(__file__).resolve().parents[1] / "store_assets"
SOURCE = STORE_ASSETS / "Square310x310Logo.png"
TARGET_SIZES = (16, 20, 24, 30, 32, 36, 40, 48, 60, 64, 72, 80, 96, 256)
ALTFORMS = ("", "_altform-unplated", "_altform-lightunplated")

# Windows draws its own backplate behind unplated/lightunplated assets, so
# these must not be an opaque copy of the plated tile (the icon-consistency
# gate's --package check now rejects a build that ships one,
# T-20260927-699609650 follow-up). A full inset margin (Microsoft's usual
# unplated guidance) pushes small sizes' design-similarity diff over
# tests/test_assets_and_icons.py's calibrated threshold (measured: 0.22 at
# 16px with a 12% margin, threshold 0.20) -- a small transparent corner is
# the minimum treatment that is genuinely non-opaque while staying well
# inside that calibration.
def _unplated(master: Image.Image, size: int) -> Image.Image:
    img = master.resize((size, size), Image.LANCZOS)
    corner = max(1, size // 8)
    alpha = img.getchannel("A").copy()
    alpha.paste(Image.new("L", (corner, corner), 0), (0, 0))
    img.putalpha(alpha)
    return img


def main() -> None:
    master = Image.open(SOURCE).convert("RGBA")
    for size in TARGET_SIZES:
        plated = master.resize((size, size), Image.LANCZOS)
        for altform in ALTFORMS:
            img = _unplated(master, size) if altform else plated
            img.save(STORE_ASSETS / f"Square44x44Logo.targetsize-{size}{altform}.png", optimize=True)


if __name__ == "__main__":
    main()
