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


def main() -> None:
    master = Image.open(SOURCE).convert("RGBA")
    for size in TARGET_SIZES:
        img = master.resize((size, size), Image.LANCZOS)
        for altform in ALTFORMS:
            img.save(STORE_ASSETS / f"Square44x44Logo.targetsize-{size}{altform}.png", optimize=True)


if __name__ == "__main__":
    main()
