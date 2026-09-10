import 'package:cleanmarkdown/l10n/app_localizations.dart';
import 'package:cleanmarkdown/models/session_format.dart';
import 'package:cleanmarkdown/utils/markdown_cleaner.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('MarkdownCleaner.stripMarkdown Tests', () {
    test('Entfernt ATX-Headings (#, ##, ###)', () {
      const input = '# Haupttitel\n## Untertitel\n### Sektion';
      final output = MarkdownCleaner.stripMarkdown(input);
      expect(output, 'Haupttitel\nUntertitel\nSektion');
    });

    test('Entfernt Fett- und Kursivformatierungen', () {
      const input = '**Fett** und *kursiv* und __unterstrichen-fett__ sowie _einfach_';
      final output = MarkdownCleaner.stripMarkdown(input);
      expect(output, 'Fett und kursiv und unterstrichen-fett sowie einfach');
    });

    test('Entfernt Links und Bilder, behält Beschriftungen', () {
      const input = 'Hier ist ein [Dokumenten-Link](https://doc-bricks.org) und ein Bild: ![Diagramm](assets/chart.png)';
      final output = MarkdownCleaner.stripMarkdown(input);
      expect(output, 'Hier ist ein Dokumenten-Link und ein Bild: Diagramm');
    });

    test('Entfernt Inline-Code und Code-Blöcke', () {
      const input = 'Nutze `cleanmarkdown`:\n```python\nprint("hello")\n```';
      final output = MarkdownCleaner.stripMarkdown(input);
      expect(output, 'Nutze cleanmarkdown:\nprint("hello")');
    });

    test('Entfernt Blockquotes und Aufzählungszeichen', () {
      const input = '> Zitatzeile\n- Punkt 1\n* Punkt 2\n1. Nummer 1';
      final output = MarkdownCleaner.stripMarkdown(input);
      expect(output, 'Zitatzeile\nPunkt 1\nPunkt 2\nNummer 1');
    });

    test('Entfernt horizontale Trennlinien (---, ***)', () {
      const input = 'Absatz 1\n---\nAbsatz 2\n***\nAbsatz 3';
      final output = MarkdownCleaner.stripMarkdown(input);
      expect(output, 'Absatz 1\nAbsatz 2\nAbsatz 3');
    });

    test('Behält reinen Text und Umlaute unverändert', () {
      const input = 'Öffentlicher Prüfbericht für Übertragungen in Ägypten & Zürich.';
      final output = MarkdownCleaner.stripMarkdown(input);
      expect(output, input);
    });
  });

  group('MarkdownCleaner.calculateStats Tests', () {
    test('Leerer Text liefert 0-Werte', () {
      final stats = MarkdownCleaner.calculateStats('');
      expect(stats.wordCount, 0);
      expect(stats.characterCount, 0);
      expect(stats.characterCountNoSpaces, 0);
      expect(stats.readingTimeMinutes, 0);
    });

    test('Text mit Leerzeichen liefert korrekte Zählung', () {
      const text = 'CleanMarkdown bietet schnellen und ablenkungsfreien Lesemodus.';
      final stats = MarkdownCleaner.calculateStats(text);
      expect(stats.wordCount, 6);
      expect(stats.characterCount, text.length);
      expect(stats.characterCountNoSpaces, text.replaceAll(' ', '').length);
      expect(stats.readingTimeMinutes, 1);
    });

    test('Langer Text berechnet Lesezeit nach 200 WPM', () {
      final words = List.generate(450, (i) => 'Wort$i').join(' ');
      final stats = MarkdownCleaner.calculateStats(words);
      expect(stats.wordCount, 450);
      expect(stats.readingTimeMinutes, 3);
    });
  });

  group('CleanMarkdownSession Format Tests', () {
    test('isSessionJson erkennt gültiges Session-JSON', () {
      const validJson = '{"version":"cleanmarkdown-session-v1","fileName":"test.md","markdown":"# Titel","theme":"paper","workspace":"editor","updatedAt":"2026-09-10T12:00:00Z"}';
      expect(CleanMarkdownSession.isSessionJson(validJson), isTrue);
    });

    test('isSessionJson weist normales Markdown oder Plain-Text ab', () {
      expect(CleanMarkdownSession.isSessionJson('# Hallo Welt'), isFalse);
      expect(CleanMarkdownSession.isSessionJson('{ "other": 123 }'), isFalse);
    });

    test('Serialisierung und Deserialisierung bleiben verlustfrei', () {
      const session = CleanMarkdownSession(
        fileName: 'notizen.md',
        markdown: '# Notiz\n\nInhalt hier.',
        theme: 'dark',
        workspace: 'split',
        updatedAt: '2026-09-10T14:30:00.000Z',
      );

      final jsonStr = session.toJsonString();
      final restored = CleanMarkdownSession.fromJsonString(jsonStr);

      expect(restored.version, 'cleanmarkdown-session-v1');
      expect(restored.fileName, 'notizen.md');
      expect(restored.markdown, '# Notiz\n\nInhalt hier.');
      expect(restored.theme, 'dark');
      expect(restored.workspace, 'split');
      expect(restored.updatedAt, '2026-09-10T14:30:00.000Z');
    });
  });

  group('Lokalisierung & Spanisch Tests', () {
    test('supportedLocales enthält de, en und es', () {
      final codes = AppLocalizations.supportedLocales.map((l) => l.languageCode).toList();
      expect(codes, containsAll(['de', 'en', 'es']));
    });

    test('AppLocalizationsEs liefert spanische Übersetzungen', () {
      final l10nEs = AppLocalizationsEs();
      expect(l10nEs.appTitle, 'CleanMarkdown');
      expect(l10nEs.openFile, 'Abrir archivo');
      expect(l10nEs.saveFile, 'Guardar');
      expect(l10nEs.exportSession, 'Exportar sesión');
      expect(l10nEs.clearFormatting, 'Limpiar formato');
      expect(l10nEs.statsWords(5), '5 palabras');
    });

    test('AppLocalizationsDe und En liefern Session- und Cleaner-Keys', () {
      final de = AppLocalizationsDe();
      final en = AppLocalizationsEn();

      expect(de.exportSession, 'Session exportieren');
      expect(en.exportSession, 'Export session');
      expect(de.clearFormatting, 'Formatierung entfernen');
      expect(en.clearFormatting, 'Clear formatting');
    });
  });
}
