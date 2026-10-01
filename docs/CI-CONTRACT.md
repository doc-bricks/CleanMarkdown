# CleanMarkdown: CI-Vertrag

Die aktiven Prüfwege sind Desktop-Python, Web-Vertragstests und Flutter. Der
aktuelle Web-Companion ist eine statische Vanilla-JavaScript-Anwendung ohne
`package.json` oder npm-Testsuite. Frühere Aufgabenangaben zu `npm test` und
66 Web-Tests beschreiben einen früheren Stand.

## Desktop und Web

`.github/workflows/tests.yml` führt auf Windows und Linux mit Python
3.10–3.13 Lint, Syntaxprüfung und die gesamte Pytest-Suite aus. Auf Windows
kommt der native Selbsttest hinzu.

Die acht Web-Vertragstests in `tests/test_web_companion.py` sind Bestandteil
dieser Suite. Sie prüfen Assets, Manifest, Service-Worker-Inventar,
Ressourcenreferenzen, Session-Felder, Bedienelemente, Sprachschlüssel und
Desktop-Bereinigungsregeln. Sie führen die Web-Anwendung nicht in einem
Browser aus. Lokal lassen sie sich vom Repository-Stamm starten:

```text
python -m pytest tests/test_web_companion.py
```

## Flutter

Ein separater Ubuntu-Job im selben Workflow läuft bei Push auf `main` und
Pull Requests gegen `main`. Er verwendet Flutter 3.44.0 mit Dart 3.12,
passend zur vorhandenen SDK-Anforderung `^3.12.0`. Die Setup-Action ist auf
einen konkreten Commit gepinnt. Die Paketversionen bleiben durch das
vorhandene `pubspec.lock` gebunden; Abweichungen stoppen die Auflösung.

Alle Befehle laufen in `flutter_port`:

```text
flutter --version
flutter pub get --enforce-lockfile
flutter analyze --no-pub
flutter test --no-pub
```

Analyse- und Testfehler führen zum Fehlschlag des Jobs. Diese Prüfung ist
kein APK-/IPA-Build und ersetzt keine Android-/iOS-Geräteabnahme.

## Source-Smoke

`.github/workflows/source-platform-smoke.yml` führt den eigenständigen
Python-Source-Smoke auf Linux und macOS aus. Änderungen an `main.py`,
`translator.py`, `requirements.txt`, `pyproject.toml`, den Sprachdateien,
Assets, Root-Icons, dem Smoke-Programm und dem Smoke-Workflow lösen die
Prüfung aus. Die Settings-Prüfungen verwenden isolierte Anwendungsprofile.

Die Workflow-Syntax kann mit `actionlint` geprüft werden. Erfolgreiche
Syntaxprüfung ersetzt keinen tatsächlichen GitHub-Lauf der einzelnen Jobs.

SDK- und Action-Vertrag: [Flutter 3.44](https://flutter.dev/blog/whats-new-in-flutter-3-44),
[flutter-action](https://github.com/subosito/flutter-action).
