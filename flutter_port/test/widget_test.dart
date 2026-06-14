import 'dart:io';
import 'dart:typed_data';

import 'package:cleanmarkdown/l10n/app_localizations.dart';
import 'package:cleanmarkdown/screens/home_screen.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';

class _FakeFilePicker extends FilePicker {
  final String? filePath;
  final String? savePath;
  int saveInvocations = 0;
  Uint8List? savedBytes;

  _FakeFilePicker({this.filePath, this.savePath});

  @override
  Future<FilePickerResult?> pickFiles({
    String? dialogTitle,
    String? initialDirectory,
    FileType type = FileType.any,
    List<String>? allowedExtensions,
    Function(FilePickerStatus)? onFileLoading,
    bool allowCompression = true,
    int compressionQuality = 30,
    bool allowMultiple = false,
    bool withData = false,
    bool withReadStream = false,
    bool lockParentWindow = false,
    bool readSequential = false,
  }) async {
    if (filePath == null) {
      return null;
    }
    return FilePickerResult([
      PlatformFile(path: filePath, name: 'test.md', size: 0),
    ]);
  }

  @override
  Future<String?> saveFile({
    String? dialogTitle,
    String? fileName,
    String? initialDirectory,
    FileType type = FileType.any,
    List<String>? allowedExtensions,
    Uint8List? bytes,
    bool lockParentWindow = false,
  }) async {
    saveInvocations += 1;
    savedBytes = bytes;
    return savePath;
  }

  @override
  Future<bool?> clearTemporaryFiles() async => true;

  @override
  Future<String?> getDirectoryPath({
    String? dialogTitle,
    String? initialDirectory,
    bool lockParentWindow = false,
  }) async => null;
}

Widget _buildTestApp({Locale locale = const Locale('de')}) {
  return MaterialApp(
    localizationsDelegates: const [
      AppLocalizations.delegate,
      GlobalMaterialLocalizations.delegate,
      GlobalWidgetsLocalizations.delegate,
      GlobalCupertinoLocalizations.delegate,
    ],
    supportedLocales: AppLocalizations.supportedLocales,
    locale: locale,
    home: const HomeScreen(),
  );
}

void main() {
  testWidgets('HomeScreen zeigt Platzhaltertext wenn keine Datei geöffnet', (
    tester,
  ) async {
    await tester.pumpWidget(_buildTestApp());
    await tester.pumpAndSettle();
    expect(find.textContaining('Keine Datei geöffnet'), findsOneWidget);
  });

  testWidgets('HomeScreen zeigt Open-File-Button', (tester) async {
    await tester.pumpWidget(_buildTestApp());
    await tester.pumpAndSettle();
    expect(find.byIcon(Icons.folder_open), findsWidgets);
  });

  testWidgets('L10n DE: appTitle ist CleanMarkdown', (tester) async {
    await tester.pumpWidget(_buildTestApp());
    await tester.pumpAndSettle();
    expect(find.text('CleanMarkdown'), findsOneWidget);
  });

  testWidgets('L10n EN: appTitle ist CleanMarkdown', (tester) async {
    await tester.pumpWidget(_buildTestApp(locale: const Locale('en')));
    await tester.pumpAndSettle();
    expect(find.text('CleanMarkdown'), findsOneWidget);
  });

  testWidgets('_pickFile lädt .md-Datei und zeigt Markdown-Inhalt', (
    tester,
  ) async {
    final dir = Directory.systemTemp.createTempSync('cleanmd_test');
    final file = File('${dir.path}/test.md')..writeAsStringSync('# Hallo Welt');
    FilePicker.platform = _FakeFilePicker(filePath: file.path);
    addTearDown(() {
      try {
        dir.deleteSync(recursive: true);
      } catch (_) {}
    });

    await tester.pumpWidget(_buildTestApp());
    await tester.pumpAndSettle();

    await tester.runAsync(() async {
      await tester.tap(find.byType(FloatingActionButton));
      await Future<void>.delayed(const Duration(milliseconds: 200));
    });
    await tester.pumpAndSettle();

    expect(find.textContaining('Hallo Welt'), findsOneWidget);
  });

  testWidgets('Editor speichert neuen Markdown-Text über Save-Dialog', (
    tester,
  ) async {
    final dir = Directory.systemTemp.createTempSync('cleanmd_save_test');
    final saveFile = File('${dir.path}/saved.md');
    final picker = _FakeFilePicker(savePath: saveFile.path);
    FilePicker.platform = picker;
    addTearDown(() {
      try {
        dir.deleteSync(recursive: true);
      } catch (_) {}
    });

    await tester.pumpWidget(_buildTestApp());
    await tester.pumpAndSettle();

    await tester.tap(find.text('Editor'));
    await tester.pumpAndSettle();
    await tester.enterText(find.byType(TextField), '# Neu');
    await tester.pumpAndSettle();
    await tester.runAsync(() async {
      await tester.tap(find.byIcon(Icons.save));
      await Future<void>.delayed(const Duration(milliseconds: 200));
    });
    await tester.pumpAndSettle();

    expect(saveFile.existsSync(), isTrue);
    expect(saveFile.readAsStringSync(), '# Neu');
    expect(picker.saveInvocations, 1);
    expect(picker.savedBytes, isNotNull);
  });

  testWidgets(
    'Editor deaktiviert Autokorrektur und Smart Punctuation für Markdown',
    (tester) async {
      await tester.pumpWidget(_buildTestApp());
      await tester.pumpAndSettle();

      await tester.tap(find.text('Editor'));
      await tester.pumpAndSettle();

      final textField = tester.widget<TextField>(find.byType(TextField));
      expect(textField.autocorrect, isFalse);
      expect(textField.enableSuggestions, isFalse);
      expect(textField.smartDashesType, SmartDashesType.disabled);
      expect(textField.smartQuotesType, SmartQuotesType.disabled);
      expect(textField.textCapitalization, TextCapitalization.none);
    },
  );

  testWidgets(
    'Ungespeicherte Änderungen werden angezeigt und nach dem Speichern zurückgesetzt',
    (tester) async {
      final dir = Directory.systemTemp.createTempSync('cleanmd_unsaved_test');
      final saveFile = File('${dir.path}/unsaved.md');
      final picker = _FakeFilePicker(savePath: saveFile.path);
      FilePicker.platform = picker;
      addTearDown(() {
        try {
          dir.deleteSync(recursive: true);
        } catch (_) {}
      });

      await tester.pumpWidget(_buildTestApp());
      await tester.pumpAndSettle();

      await tester.tap(find.text('Editor'));
      await tester.pumpAndSettle();
      await tester.enterText(find.byType(TextField), '# Mobil\n\n- Bearbeiten');
      await tester.pumpAndSettle();

      expect(find.text('Ungespeicherte Änderungen'), findsOneWidget);

      await tester.tap(find.text('Vorschau'));
      await tester.pumpAndSettle();
      expect(find.textContaining('Bearbeiten'), findsOneWidget);

      await tester.runAsync(() async {
        await tester.tap(find.byIcon(Icons.save));
        await Future<void>.delayed(const Duration(milliseconds: 200));
      });
      await tester.pumpAndSettle();

      expect(saveFile.existsSync(), isTrue);
      expect(find.text('Ungespeicherte Änderungen'), findsNothing);
    },
  );

  testWidgets(
    'Speichern nutzt vorhandenen Dateipfad ohne zweiten Save-Dialog',
    (tester) async {
      final dir = Directory.systemTemp.createTempSync('cleanmd_update_test');
      final file = File('${dir.path}/existing.md')..writeAsStringSync('# Alt');
      final picker = _FakeFilePicker(
        filePath: file.path,
        savePath: '${dir.path}/unused.md',
      );
      FilePicker.platform = picker;
      addTearDown(() {
        try {
          dir.deleteSync(recursive: true);
        } catch (_) {}
      });

      await tester.pumpWidget(_buildTestApp());
      await tester.pumpAndSettle();

      await tester.runAsync(() async {
        await tester.tap(find.byType(FloatingActionButton));
        await Future<void>.delayed(const Duration(milliseconds: 200));
      });
      await tester.pumpAndSettle();

      await tester.tap(find.text('Editor'));
      await tester.pumpAndSettle();
      await tester.enterText(find.byType(TextField), '# Aktualisiert');
      await tester.pumpAndSettle();
      await tester.runAsync(() async {
        await tester.tap(find.byIcon(Icons.save));
        await Future<void>.delayed(const Duration(milliseconds: 200));
      });
      await tester.pumpAndSettle();

      expect(file.readAsStringSync(), '# Aktualisiert');
      expect(picker.saveInvocations, 0);
    },
  );

  testWidgets('Neue-Datei-Button existiert in AppBar', (tester) async {
    await tester.pumpWidget(_buildTestApp());
    await tester.pumpAndSettle();
    expect(find.byIcon(Icons.note_add), findsOneWidget);
  });

  testWidgets('Teilen-Button existiert in AppBar', (tester) async {
    await tester.pumpWidget(_buildTestApp());
    await tester.pumpAndSettle();
    expect(find.byIcon(Icons.share), findsOneWidget);
  });

  testWidgets(
    'Neue Datei setzt Editor-Inhalt zurück (keine ungespeicherten Änderungen)',
    (tester) async {
      final dir = Directory.systemTemp.createTempSync('cleanmd_new_test');
      final file = File('${dir.path}/test.md')..writeAsStringSync('# Vorhandene Datei');
      FilePicker.platform = _FakeFilePicker(filePath: file.path);
      addTearDown(() {
        try {
          dir.deleteSync(recursive: true);
        } catch (_) {}
      });

      await tester.pumpWidget(_buildTestApp());
      await tester.pumpAndSettle();

      // Datei öffnen
      await tester.runAsync(() async {
        await tester.tap(find.byType(FloatingActionButton));
        await Future<void>.delayed(const Duration(milliseconds: 200));
      });
      await tester.pumpAndSettle();
      expect(find.textContaining('Vorhandene Datei'), findsOneWidget);

      // Neue Datei — keine ungespeicherten Änderungen → kein Dialog
      await tester.tap(find.byIcon(Icons.note_add));
      await tester.pumpAndSettle();

      // Editor sollte leer sein, Platzhaltertext zurück
      expect(find.textContaining('Keine Datei geöffnet'), findsOneWidget);
    },
  );

  testWidgets(
    'Neue Datei zeigt Bestätigungsdialog bei ungespeicherten Änderungen',
    (tester) async {
      FilePicker.platform = _FakeFilePicker();

      await tester.pumpWidget(_buildTestApp());
      await tester.pumpAndSettle();

      // Text eingeben → ungespeicherte Änderungen
      await tester.tap(find.text('Editor'));
      await tester.pumpAndSettle();
      await tester.enterText(find.byType(TextField), '# Entwurf');
      await tester.pumpAndSettle();
      expect(find.text('Ungespeicherte Änderungen'), findsOneWidget);

      // Neue Datei tippen → Dialog erscheint
      await tester.tap(find.byIcon(Icons.note_add));
      await tester.pumpAndSettle();
      expect(find.text('Ungespeicherte Änderungen verwerfen?'), findsOneWidget);

      // Abbrechen → Inhalt bleibt
      await tester.tap(find.text('Abbrechen'));
      await tester.pumpAndSettle();
      expect(find.text('Ungespeicherte Änderungen'), findsOneWidget);

      // Neue Datei erneut → Verwerfen bestätigen
      await tester.tap(find.byIcon(Icons.note_add));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Verwerfen'));
      await tester.pumpAndSettle();
      expect(find.text('Ungespeicherte Änderungen'), findsNothing);
      // Preview-Tab: Platzhaltertext prüfen
      await tester.tap(find.text('Vorschau'));
      await tester.pumpAndSettle();
      expect(find.textContaining('Keine Datei geöffnet'), findsOneWidget);
    },
  );
}
