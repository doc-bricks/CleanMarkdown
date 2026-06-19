# Windows Store Vorbereitung — CleanMarkdown

**Stand:** 2026-06-20
**Version:** 0.3.1

## Artefakt-Status

| Artefakt | Status | Anmerkung |
|---|---|---|
| `store_package.json` | OK | v0.3.1.0, Kategorie Productivity, DE+EN |
| `STORE_LISTING.md` | OK | DE+EN Listing-Texte vollständig |
| `PRIVACY_POLICY.md` | OK | DE+EN, kein Netzwerkzugriff verifiziert |
| `SUPPORT.md` | OK | DE+EN, FAQ, Kontaktdaten |
| `THIRD_PARTY_LICENSES.txt` | OK | PySide6 (LGPL), Python-Markdown (BSD) |
| Screenshots (3x) | OK | `README/screenshots/store/` (editor-dark, reading-bright, reading-dark) |
| `store_assets/` (Icons) | OK | Generiert aus CleanMarkdown.png |
| Release-EXE | OK | `releases/v0.3.1/CleanMarkdown-0.3.1-win64.exe` |
| `tests/test_store_materials.py` | OK | 6 automatisierte Prüfungen |
| MSIX-Build | OFFEN | Benötigt Partner-Center-Konto |
| WACK-Test | OFFEN | Benötigt MSIX-Paket |

## Offene Punkte

1. **MSIX-Packaging:** Noch kein MSIX-Build erstellt. Benötigt Windows App SDK oder manuelles MSIX-Packaging.
2. **WACK-Test:** Windows App Certification Kit kann erst nach MSIX-Build ausgeführt werden.
3. **SAL-Lizenz:** Source-Available License (SAL) v1.0 — Kompatibilität mit Microsoft Store Richtlinien prüfen.
4. **runFullTrust-Capability:** Notwendig für lokalen Dateizugriff über Dateisystem-Dialoge. Begründung im Store-Listing dokumentieren.

## Hinweise

- `STORE_READINESS.md` existiert als ältere Variante dieser Datei und wird durch `WINDOWS_STORE_PREP.md` abgelöst.
- Die App hat **keinen Netzwerkzugriff** (verifiziert via Code-Grep über alle .py-Dateien).
- Zwei Abhängigkeiten: PySide6 >=6.10, Markdown >=3.10.
