#!/usr/bin/env python3
"""Preflight Windows Store readiness audit for CleanMarkdown.

Prüft alle Windows Store Release Readiness Artefakte auf Vollständigkeit,
Konsistenz und Richtlinienkonformität nach dem Tier-2 6-Sprachen-Standard (Policy P-006).
"""

from __future__ import annotations

import argparse
import json
import re
import struct
from pathlib import Path
from xml.etree import ElementTree as ET

REQUIRED_CANONICAL_PUBLISHER = "CN=52596601-BAB4-4F3F-B182-E8F3F273B202"
TIER2_LANGUAGES = ["de-DE", "en-US", "es-ES", "zh-CN", "ja-JP", "ru-RU"]
TIER2_LANGUAGE_CODES = ["de", "en", "es", "zh", "ja", "ru"]

REQUIRED_DOCUMENTS = [
    "CleanMarkdown.spec",
    "build_exe.bat",
    "store_package.json",
    "STORE_LISTING.md",
    "PRIVACY_POLICY.md",
    "SUPPORT.md",
    "THIRD_PARTY_LICENSES.txt",
    "WINDOWS_STORE_PREP.md",
    "PORTIERUNGSPLAN.md",
    "scripts/store_assets.py",
    "scripts/generate_store_screenshots.py",
    "releases/windowsstore/BUILD.md",
    "releases/windowsstore/WACK_PROTOCOL.md",
    "releases/windowsstore/store_settings.json",
    "releases/windowsstore/StoreLogo.png",
    "releases/windowsstore/store_listing_de.md",
    "releases/windowsstore/store_listing_en.md",
    "releases/windowsstore/store_listing_es.md",
    "releases/windowsstore/store_listing_zh.md",
    "releases/windowsstore/store_listing_ja.md",
    "releases/windowsstore/store_listing_ru.md",
]

REQUIRED_STORE_ICONS = {
    "icon_44x44.png": (44, 44),
    "icon_50x50.png": (50, 50),
    "icon_150x150.png": (150, 150),
    "icon_310x150.png": (310, 150),
    "icon_310x310.png": (310, 310),
    "SplashScreen.png": (620, 300),
}

REQUIRED_LEGACY_STORE_ASSETS = [
    "Square44x44Logo.png",
    "StoreLogo.png",
    "Square150x150Logo.png",
    "Square310x310Logo.png",
    "Wide310x150Logo.png",
    "SplashScreen.png",
    "AppxManifest.xml",
]

REQUIRED_STORE_SCREENSHOTS = [
    "01_lesemodus-vorschau.png",
    "02_raw-editor-struktur.png",
    "03_dark-mode-theme.png",
    "04_mobile-companion-session.png",
]

RESTRICTED_TRADEMARKS = [
    "windows",
    "microsoft",
    "office",
    "word",
    "apple",
    "ios",
    "android",
    "google",
    "adobe",
    "outlook",
]


def _png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path.name} ist keine gültige PNG-Datei")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def run_store_readiness_check(
    project_root: Path | None = None,
    *,
    require_executable: bool = False,
) -> list[str]:
    if project_root is None:
        project_root = Path(__file__).resolve().parents[1]

    findings: list[str] = []

    # 1. Document Existence Check
    for doc in REQUIRED_DOCUMENTS:
        doc_path = project_root / doc
        if not doc_path.exists():
            findings.append(f"Fehlendes Store-Pflichtdokument: {doc}")

    # 2. Package JSON Validation
    package_json_path = project_root / "store_package.json"
    package_data: dict = {}
    if package_json_path.exists():
        try:
            with open(package_json_path, "r", encoding="utf-8") as f:
                package_data = json.load(f)

            app_name = package_data.get("app_name")
            if app_name != "CleanMarkdown":
                findings.append(f"Ungültiger app_name in store_package.json: {app_name}")

            identity_name = package_data.get("identity_name") or package_data.get("package_id")
            if identity_name != "Geiger.CleanMarkdown":
                findings.append(f"Ungültiger identity_name / package_id: {identity_name}")

            publisher = package_data.get("publisher") or package_data.get("publisher_id")
            if publisher != REQUIRED_CANONICAL_PUBLISHER:
                findings.append(f"Publisher stimmt nicht mit kanonischem CN überein: {publisher}")

            version = package_data.get("version", "")
            if not re.match(r"^\d+\.\d+\.\d+\.\d+$", version):
                findings.append(f"Ungültiges Versionsformat in store_package.json: {version}")

            capabilities = package_data.get("capabilities", "")
            cap_str = capabilities if isinstance(capabilities, str) else " ".join(capabilities)
            if "runFullTrust" not in cap_str:
                findings.append("Fehlende Berechtigung runFullTrust in store_package.json")

            languages = package_data.get("languages", [])
            for req_lang in TIER2_LANGUAGES:
                if req_lang not in languages:
                    findings.append(f"store_package.json: Fehlende Tier-2 Sprache: {req_lang}")

            for code in TIER2_LANGUAGE_CODES:
                desc_k = f"description_{code}"
                if desc_k in package_data:
                    if len(package_data[desc_k]) > 100:
                        findings.append(f"store_package.json {desc_k} überschreitet 100 Zeichen ({len(package_data[desc_k])})")
                else:
                    findings.append(f"store_package.json: {desc_k} fehlt")

                kw_k = f"keywords_{code}"
                if kw_k in package_data:
                    kws = package_data[kw_k]
                    if len(kws) != 7:
                        findings.append(f"store_package.json {kw_k} hat {len(kws)} Keywords (genau 7 erwartet)")
                    for kw in kws:
                        if len(kw) > 30:
                            findings.append(f"store_package.json {kw_k} Keyword '{kw}' > 30 Zeichen")
                        for tm in RESTRICTED_TRADEMARKS:
                            if tm in kw.lower():
                                findings.append(f"store_package.json {kw_k} enthält verbotene Marke '{tm}' in '{kw}'")
                else:
                    findings.append(f"store_package.json: {kw_k} fehlt")

        except Exception as e:
            findings.append(f"store_package.json ist kein gültiges JSON: {e}")

    # 3. Executable Validation (if required)
    if require_executable:
        exe_name = package_data.get("executable", "CleanMarkdown.exe")
        exe_path = project_root / "releases" / "v1.0.2" / "CleanMarkdown-fast" / exe_name
        if not exe_path.exists():
            findings.append(f"Store-Executable nicht gefunden: {exe_path}")

    # 4. Store Listing (Tier-2 6-Sprachen) & Partner Center Policy 10.1.3 Compliance
    store_listing_path = project_root / "STORE_LISTING.md"
    if store_listing_path.exists():
        content = store_listing_path.read_text(encoding="utf-8")

        lang_headers = [
            ("Deutsch", "## Deutsch"),
            ("English", "## English"),
            ("Español", "## Español"),
            ("Chinesisch", "## 简体中文"),
            ("Japanisch", "## 日本語"),
            ("Russisch", "## Русский"),
        ]
        for name, header in lang_headers:
            if header not in content:
                findings.append(f"STORE_LISTING.md: Abschnitt '{header}' ({name}) fehlt")

        # Policy 10.1.3 Keywords Audit für alle 6 Sprachen
        lang_sections = [
            ("Deutsch", r"## Deutsch[\s\S]*?(?:### Suchbegriffe|### Schlüsselwörter)[^\n]*\n+([^\n#]+)"),
            ("English", r"## English[\s\S]*?(?:### Search Keywords|### Keywords)[^\n]*\n+([^\n#]+)"),
            ("Español", r"## Español[\s\S]*?### Palabras clave[^\n]*\n+([^\n#]+)"),
            ("Chinesisch", r"## 简体中文[\s\S]*?### 关键词[^\n]*\n+([^\n#]+)"),
            ("Japanisch", r"## 日本語[\s\S]*?### キーワード[^\n]*\n+([^\n#]+)"),
            ("Russisch", r"## Русский[\s\S]*?### Ключевые слова[^\n]*\n+([^\n#]+)"),
        ]
        for lang_name, pattern in lang_sections:
            m = re.search(pattern, content)
            if m:
                raw_kws = m.group(1).strip()
                kws = [k.strip() for k in raw_kws.split(",") if k.strip()]
                if len(kws) > 7:
                    findings.append(f"STORE_LISTING.md ({lang_name}): Zu viele Keywords ({len(kws)} > 7)")
                elif len(kws) == 0:
                    findings.append(f"STORE_LISTING.md ({lang_name}): Keine Keywords gefunden")
                for kw in kws:
                    if len(kw) > 30:
                        findings.append(f"STORE_LISTING.md ({lang_name}): Keyword zu lang (>30 Zeichen): '{kw}'")
                    for tm in RESTRICTED_TRADEMARKS:
                        if tm in kw.lower():
                            findings.append(f"STORE_LISTING.md ({lang_name}): Markenname '{tm}' in Keyword gefunden: '{kw}'")
            else:
                findings.append(f"STORE_LISTING.md: Keywords-Abschnitt für {lang_name} nicht gefunden")

        if "Screenshots" not in content:
            findings.append("STORE_LISTING.md: Screenshots-Tabelle fehlt")

    # 5. Privacy Policy Compliance
    privacy_path = project_root / "PRIVACY_POLICY.md"
    if privacy_path.exists():
        p_text = privacy_path.read_text(encoding="utf-8").lower()
        if "lokal" not in p_text and "local" not in p_text:
            findings.append("PRIVACY_POLICY.md erwähnt keine lokale Datenhaltung")
        if "settings.json" not in p_text:
            findings.append("PRIVACY_POLICY.md erwähnt den kanonischen SettingsStore settings.json nicht")
        if "qsettings" in p_text:
            findings.append("PRIVACY_POLICY.md enthält unzulässigen Verweis auf QSettings")

    # 6. Support Documentation
    support_path = project_root / "SUPPORT.md"
    if support_path.exists():
        s_text = support_path.read_text(encoding="utf-8")
        if "http" not in s_text and "github.com" not in s_text:
            findings.append("SUPPORT.md enthält keine URL oder Kontaktmöglichkeit")
        if "settings.json" not in s_text:
            findings.append("SUPPORT.md erwähnt den kanonischen Settings-Pfad settings.json nicht")

    # 7. Store Package Icons
    icons_dir = project_root / "store_package" / "CleanMarkdown" / "icons"
    if not icons_dir.exists():
        findings.append(f"Icons-Verzeichnis fehlt: {icons_dir}")
    else:
        for icon_name, (req_w, req_h) in REQUIRED_STORE_ICONS.items():
            icon_file = icons_dir / icon_name
            if not icon_file.exists():
                findings.append(f"Store-Icon fehlt: {icon_name}")
            else:
                try:
                    w, h = _png_size(icon_file)
                    if (w, h) != (req_w, req_h):
                        findings.append(
                            f"Falsche Bildgröße für {icon_name}: ({w}, {h}) statt ({req_w}, {req_h})"
                        )
                except Exception as err:
                    findings.append(f"Fehler beim Lesen von {icon_name}: {err}")

    # 8. Legacy Store Assets
    store_assets_dir = project_root / "store_assets"
    if not store_assets_dir.exists():
        findings.append(f"store_assets Verzeichnis fehlt: {store_assets_dir}")
    else:
        for asset_name in REQUIRED_LEGACY_STORE_ASSETS:
            asset_file = store_assets_dir / asset_name
            if not asset_file.exists():
                findings.append(f"Legacy Store-Asset fehlt in store_assets: {asset_name}")

    # 9. Store Screenshots Validation (16:9, >=1366x768)
    screenshots_dirs = [
        project_root / "store_package" / "CleanMarkdown" / "screenshots",
        project_root / "README" / "screenshots" / "store",
    ]
    for s_dir in screenshots_dirs:
        if not s_dir.exists():
            findings.append(f"Screenshots-Verzeichnis fehlt: {s_dir}")
        else:
            for s_name in REQUIRED_STORE_SCREENSHOTS:
                s_file = s_dir / s_name
                if not s_file.exists():
                    findings.append(f"Store-Screenshot fehlt in {s_dir.name}: {s_name}")
                else:
                    try:
                        w, h = _png_size(s_file)
                        if w < 1366 or h < 768:
                            findings.append(f"Screenshot {s_name} zu klein (<1366x768): ({w}, {h})")
                        aspect = round(w / h, 2)
                        if aspect != 1.78:  # 16:9 is 1.7777...
                            findings.append(
                                f"Screenshot {s_name} hat kein 16:9-Format: ({w}, {h}, ratio {aspect})"
                            )
                    except Exception as err:
                        findings.append(f"Fehler beim Prüfen von Screenshot {s_name}: {err}")

    # 10. AppxManifest.xml Validation
    manifest_path = project_root / "store_package" / "CleanMarkdown" / "AppxManifest.xml"
    if not manifest_path.exists():
        findings.append(f"AppxManifest.xml fehlt: {manifest_path}")
    else:
        try:
            tree = ET.parse(manifest_path)
            root = tree.getroot()

            ns = {
                "m": "http://schemas.microsoft.com/appx/manifest/foundation/windows10",
                "uap": "http://schemas.microsoft.com/appx/manifest/uap/windows10",
                "rescap": "http://schemas.microsoft.com/appx/manifest/foundation/windows10/restrictedcapabilities",
            }

            identity = root.find("m:Identity", ns)
            if identity is None:
                findings.append("AppxManifest.xml: Identity-Element fehlt")
            else:
                if identity.attrib.get("Name") != "Geiger.CleanMarkdown":
                    findings.append(f"AppxManifest.xml: Falscher Name: {identity.attrib.get('Name')}")
                if identity.attrib.get("Publisher") != REQUIRED_CANONICAL_PUBLISHER:
                    findings.append(
                        f"AppxManifest.xml: Falscher Publisher: {identity.attrib.get('Publisher')}"
                    )

            run_full_trust = False
            for cap in root.findall(".//rescap:Capability", ns):
                if cap.attrib.get("Name") == "runFullTrust":
                    run_full_trust = True
                    break
            if not run_full_trust:
                findings.append("AppxManifest.xml: restrictedcapability runFullTrust fehlt")

            app_node = root.find(".//m:Application", ns)
            if app_node is not None:
                exe = app_node.attrib.get("Executable")
                if exe != "CleanMarkdown.exe":
                    findings.append(f"AppxManifest.xml: Falsches Executable: {exe}")

            # Check 6 Resource Languages in manifest
            manifest_langs = [r.attrib.get("Language", "") for r in root.findall(".//m:Resource", ns)]
            for req_lang in TIER2_LANGUAGES:
                if req_lang not in manifest_langs:
                    findings.append(f"AppxManifest.xml: Resource Language '{req_lang}' fehlt")

        except Exception as e:
            findings.append(f"AppxManifest.xml ist kein valides XML: {e}")

    # 11. Portierungsplan Integrity
    port_plan_path = project_root / "PORTIERUNGSPLAN.md"
    if port_plan_path.exists():
        p_text = port_plan_path.read_text(encoding="utf-8")
        if "Windows Desktop" not in p_text:
            findings.append("PORTIERUNGSPLAN.md erwähnt Windows Desktop nicht")
        if "Windows Store" not in p_text:
            findings.append("PORTIERUNGSPLAN.md erwähnt Windows Store nicht")
        if "flutter_port" not in p_text:
            findings.append("PORTIERUNGSPLAN.md erwähnt flutter_port nicht")
        if "cleanmarkdown-session-v1" not in p_text:
            findings.append("PORTIERUNGSPLAN.md erwähnt Session-Format v1 nicht")

    # 12. PyInstaller Spec Validation
    spec_path = project_root / "CleanMarkdown.spec"
    if spec_path.exists():
        spec_text = spec_path.read_text(encoding="utf-8")
        if "console=False" not in spec_text:
            findings.append("CleanMarkdown.spec: console=False fehlt")
        if "name='CleanMarkdown'" not in spec_text and 'name="CleanMarkdown"' not in spec_text:
            findings.append("CleanMarkdown.spec: name='CleanMarkdown' fehlt")

    # 13. Release Staging Validation (releases/windowsstore/)
    staging_dir = project_root / "releases" / "windowsstore"
    if not staging_dir.exists():
        findings.append(f"Release-Staging-Verzeichnis fehlt: {staging_dir}")
    else:
        # Check StoreLogo.png in staging
        staging_logo = staging_dir / "StoreLogo.png"
        if staging_logo.exists():
            try:
                w, h = _png_size(staging_logo)
                if (w, h) != (50, 50):
                    findings.append(f"releases/windowsstore/StoreLogo.png falsche Dimension: ({w}, {h}) != (50, 50)")
            except Exception as e:
                findings.append(f"releases/windowsstore/StoreLogo.png Bildfehler: {e}")

        # Check store_settings.json in staging
        settings_file = staging_dir / "store_settings.json"
        if settings_file.exists():
            try:
                s_data = json.loads(settings_file.read_text(encoding="utf-8"))
                if s_data.get("publisher") != REQUIRED_CANONICAL_PUBLISHER:
                    findings.append(f"store_settings.json publisher mismatch: {s_data.get('publisher')}")
                if s_data.get("identity_name") != "Geiger.CleanMarkdown":
                    findings.append(f"store_settings.json identity mismatch: {s_data.get('identity_name')}")
                s_langs = s_data.get("languages", [])
                for req_lang in TIER2_LANGUAGES:
                    if req_lang not in s_langs:
                        findings.append(f"store_settings.json: Sprache {req_lang} fehlt")
                for code in TIER2_LANGUAGE_CODES:
                    dk = f"description_{code}"
                    if dk in s_data:
                        if len(s_data[dk]) > 100:
                            findings.append(f"store_settings.json {dk} überschreitet 100 Zeichen")
                    else:
                        findings.append(f"store_settings.json: {dk} fehlt")

                    kk = f"keywords_{code}"
                    if kk in s_data:
                        kws = s_data[kk]
                        if len(kws) != 7:
                            findings.append(f"store_settings.json {kk} hat {len(kws)} Keywords (7 erwartet)")
                        for kw in kws:
                            if len(kw) > 30:
                                findings.append(f"store_settings.json {kk} Keyword '{kw}' > 30 Zeichen")
                            for tm in RESTRICTED_TRADEMARKS:
                                if tm in kw.lower():
                                    findings.append(f"store_settings.json {kk} enthält verbotene Marke '{tm}' in '{kw}'")
                    else:
                        findings.append(f"store_settings.json: {kk} fehlt")
            except Exception as e:
                findings.append(f"store_settings.json Parsefehler: {e}")

        # Check 6 localized store_listing files
        for code in TIER2_LANGUAGE_CODES:
            listing_f = staging_dir / f"store_listing_{code}.md"
            if listing_f.exists():
                if listing_f.stat().st_size < 50:
                    findings.append(f"releases/windowsstore/store_listing_{code}.md zu klein (<50 Bytes)")
            else:
                findings.append(f"releases/windowsstore/store_listing_{code}.md fehlt")

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Preflight Store Readiness Audit")
    parser.add_argument(
        "--require-exe",
        action="store_true",
        help="Prüft zwingend das Vorhandensein des kompilierten Executables",
    )
    args = parser.parse_args()

    findings = run_store_readiness_check(require_executable=args.require_exe)
    if findings:
        print(f"[FEHLER] Preflight-Store-Audit fehlgeschlagen ({len(findings)} Findings):")
        for f in findings:
            print(f"  - {f}")
        return 1

    print("[OK] Preflight-Store-Audit erfolgreich: Alle Kriterien erfuellt (0 Findings)!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
