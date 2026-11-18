import 'dart:convert';
import 'dart:typed_data';

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

    test('Alle 3 Sprachen liefern vollständige, nicht-leere UI-Schlüssel', () {
      final locales = <AppLocalizations>[
        AppLocalizationsDe(),
        AppLocalizationsEn(),
        AppLocalizationsEs(),
      ];

      for (final l10n in locales) {
        final values = [
          l10n.appTitle,
          l10n.openFile,
          l10n.saveFile,
          l10n.previewTab,
          l10n.editorTab,
          l10n.noFileOpen,
          l10n.emptyPreview,
          l10n.errorReadingFile,
          l10n.errorSavingFile,
          l10n.editorHint,
          l10n.newDocument,
          l10n.unsavedChanges,
          l10n.saveSuccess,
          l10n.newFile,
          l10n.shareFile,
          l10n.newFileDiscardTitle,
          l10n.newFileDiscardConfirm,
          l10n.newFileDiscardCancel,
          l10n.exportSession,
          l10n.sessionExportSuccess,
          l10n.sessionImported,
          l10n.clearFormatting,
          l10n.clearFormattingSuccess,
          l10n.statsLabel,
          l10n.statsWords(3),
          l10n.statsChars(12),
          l10n.statsCharsNoSpaces(10),
          l10n.statsReading(1),
          l10n.undo,
          l10n.redo,
          l10n.copyMarkdown,
          l10n.copyCleanText,
          l10n.copiedSuccess,
          l10n.cleanTextCopied,
          l10n.cleanerPreviewTitle,
          l10n.cleanerNoChanges,
          l10n.applyCleanText,
          l10n.formatHelp,
          l10n.formatHelpSubtitle,
          l10n.language,
          l10n.languageSystem,
          l10n.languageDe,
          l10n.languageEn,
          l10n.languageEs,
          l10n.theme,
          l10n.themeSystem,
          l10n.themeLight,
          l10n.themeDark,
          l10n.moreOptions,
          l10n.startWriting,
          l10n.fileTooLarge,
          l10n.invalidUtf8Error,
          l10n.binaryFileError,
          l10n.errorSharingFile,
          l10n.errorExportingSession,
          l10n.splitViewTooltip,
          l10n.linkCopiedPrefix,
          l10n.closeLabel,
          l10n.formatH1,
          l10n.formatH2,
          l10n.formatBold,
          l10n.formatItalic,
          l10n.formatCode,
          l10n.formatList,
          l10n.formatQuote,
          l10n.formatLink,
        ];
        for (final val in values) {
          expect(val.trim().isNotEmpty, isTrue);
        }
      }
    });
  });

  group('Bugsweep: Sicheres UTF-8 Decoding & Dateiname-Sanitizing', () {
    test('Leere Bytes werden sauber als leerer String dekodiert', () {
      final result = MarkdownCleaner.decodeUtf8Bytes(Uint8List(0));
      expect(result.isSuccess, isTrue);
      expect(result.text, '');
      expect(result.hadBom, isFalse);
    });

    test('UTF-8 BOM wird erkannt und sauber entfernt', () {
      final payload = Uint8List.fromList([
        0xEF,
        0xBB,
        0xBF,
        ...utf8.encode('# Titel mit Ümlaut'),
      ]);
      final result = MarkdownCleaner.decodeUtf8Bytes(payload);
      expect(result.isSuccess, isTrue);
      expect(result.hadBom, isTrue);
      expect(result.text, '# Titel mit Ümlaut');
    });

    test('Nur-BOM-Datei ergibt leeren String', () {
      final result = MarkdownCleaner.decodeUtf8Bytes(
        Uint8List.fromList([0xEF, 0xBB, 0xBF]),
      );
      expect(result.isSuccess, isTrue);
      expect(result.hadBom, isTrue);
      expect(result.text, '');
    });

    test('Ungültige UTF-8 Bytes werden mit invalidUtf8 abgelehnt', () {
      final result = MarkdownCleaner.decodeUtf8Bytes(
        Uint8List.fromList([0xFF, 0xFE, 0x80, 0xC3, 0x28]),
      );
      expect(result.isSuccess, isFalse);
      expect(result.error, TextDecodeError.invalidUtf8);
      expect(result.text, isNull);
    });

    test('NUL-Bytes werden als binaryData abgelehnt', () {
      final result = MarkdownCleaner.decodeUtf8Bytes(
        Uint8List.fromList([0x48, 0x69, 0x00, 0x21]),
      );
      expect(result.isSuccess, isFalse);
      expect(result.error, TextDecodeError.binaryData);
    });

    test('Zu große Nutzlast wird mit tooLarge abgelehnt', () {
      final result = MarkdownCleaner.decodeUtf8Bytes(
        Uint8List.fromList([65, 66, 67, 68]),
        maxBytes: 3,
      );
      expect(result.isSuccess, isFalse);
      expect(result.error, TextDecodeError.tooLarge);
    });

    test('sanitizeFileName verhindert Path-Traversal und ungültige Zeichen', () {
      expect(
        MarkdownCleaner.sanitizeFileName('../../etc/passwd'),
        'passwd',
      );
      expect(
        MarkdownCleaner.sanitizeFileName('a:b*c?.md'),
        'a_b_c_.md',
      );
      expect(MarkdownCleaner.sanitizeFileName('..'), 'cleanmarkdown.md');
      expect(MarkdownCleaner.sanitizeFileName('   '), 'cleanmarkdown.md');
    });
  });

  group('Bugsweep: stripMarkdown, Stats & Session Edge Cases', () {
    test('stripMarkdown schützt snake_case und Rechenausdrücke mit *', () {
      const input = 'Nutze my_snake_case_var und rechne 2 * 3 * 4.';
      expect(MarkdownCleaner.stripMarkdown(input), input);
    });

    test('stripMarkdown bewahrt Kommentare und Trennlinien in Codeblöcken', () {
      const input = '```python\n# Kommentar\n---\nprint("ok")\n```';
      expect(
        MarkdownCleaner.stripMarkdown(input),
        '# Kommentar\n---\nprint("ok")',
      );
    });

    test('stripMarkdown entfernt führende, abschließende und aufeinanderfolgende HRs', () {
      const input = '---\n***\nAbsatz\n___\n---';
      expect(MarkdownCleaner.stripMarkdown(input), 'Absatz');
    });

    test('stripMarkdown entfernt Aufgabenlisten-Checkboxen', () {
      const input = '- [ ] Offen\n- [x] Erledigt';
      expect(MarkdownCleaner.stripMarkdown(input), 'Offen\nErledigt');
    });

    test('calculateStats behandelt Whitespace-only und große Texte korrekt', () {
      final emptyWs = MarkdownCleaner.calculateStats('   \n\t  ');
      expect(emptyWs.wordCount, 0);
      expect(emptyWs.characterCount, 0);

      final huge = List.generate(10000, (i) => 'Wort$i').join(' ');
      final hugeStats = MarkdownCleaner.calculateStats(huge);
      expect(hugeStats.wordCount, 10000);
      expect(hugeStats.readingTimeMinutes, 50);
    });

    test('CleanMarkdownSession.fromJson übersteht falsche Feldtypen ohne TypeError', () {
      const malformed =
          '{"version":"cleanmarkdown-session-v1","fileName":null,"markdown":123,"settings":"ungueltig"}';
      expect(CleanMarkdownSession.isSessionJson(malformed), isTrue);
      final parsed = CleanMarkdownSession.fromJsonString(malformed);
      expect(parsed.fileName, 'document.md');
      expect(parsed.markdown, '');
      expect(parsed.settings, isNull);
    });

    test('isSessionJson weist Nicht-Objekte und Markdown schnell ab', () {
      expect(CleanMarkdownSession.isSessionJson(''), isFalse);
      expect(CleanMarkdownSession.isSessionJson('[1, 2, 3]'), isFalse);
      expect(
        CleanMarkdownSession.isSessionJson('{"markdown": 123, "fileName": "a.md"}'),
        isFalse,
      );
    });
  });
}
