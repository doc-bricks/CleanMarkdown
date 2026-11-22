import 'dart:convert';
import 'dart:io';

import 'package:cleanmarkdown/l10n/app_localizations.dart';
import 'package:cleanmarkdown/main.dart';
import 'package:cleanmarkdown/screens/home_screen.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';

class _TestFilePicker extends FilePicker {
  final String? filePath;
  final String fileName;
  final Uint8List? fileBytes;
  final bool throwOnPick;

  _TestFilePicker({
    this.filePath,
    this.fileName = 'test.md',
    this.fileBytes,
    this.throwOnPick = false,
  });

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
    if (throwOnPick) {
      throw PlatformException(code: 'IO_ERROR', message: 'Simulated failure');
    }
    if (filePath == null && fileBytes == null) {
      return null;
    }
    return FilePickerResult([
      PlatformFile(
        path: filePath,
        name: fileName,
        size: fileBytes?.length ?? 0,
        bytes: fileBytes,
      ),
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
  }) async => null;

  @override
  Future<bool?> clearTemporaryFiles() async => true;

  @override
  Future<String?> getDirectoryPath({
    String? dialogTitle,
    String? initialDirectory,
    bool lockParentWindow = false,
  }) async => null;
}

Widget _wrapHome({Locale locale = const Locale('de')}) {
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
  testWidgets(
    'Ungültige UTF-8-Datei wird abgelehnt und bestehender Entwurf bleibt erhalten',
    (tester) async {
      final dir = Directory.systemTemp.createTempSync('cleanmd_bad_utf8');
      final badFile = File('${dir.path}/broken.md')
        ..writeAsBytesSync([0xFF, 0xFE, 0x80, 0xC3, 0x28]);
      FilePicker.platform = _TestFilePicker(
        filePath: badFile.path,
        fileName: 'broken.md',
      );
      addTearDown(() {
        try {
          dir.deleteSync(recursive: true);
        } catch (_) {}
      });

      await tester.pumpWidget(_wrapHome());
      await tester.pumpAndSettle();

      await tester.tap(find.text('Editor'));
      await tester.pumpAndSettle();
      await tester.enterText(find.byType(TextField), '# Mein wichtiger Entwurf');
      await tester.pumpAndSettle();

      await tester.tap(find.text('Vorschau'));
      await tester.pumpAndSettle();

      await tester.runAsync(() async {
        await tester.tap(find.byType(FloatingActionButton));
        await Future<void>.delayed(const Duration(milliseconds: 200));
      });
      await tester.pumpAndSettle();

      expect(
        find.textContaining('Ungültiges UTF-8'),
        findsOneWidget,
      );
      expect(find.text('Ungespeicherte Änderungen'), findsOneWidget);
      expect(find.textContaining('Mein wichtiger Entwurf'), findsOneWidget);
    },
  );

  testWidgets(
    'Datei-Laden via Bytes (ohne Pfad, z. B. Android SAF) und leere Datei funktionieren sauber',
    (tester) async {
      FilePicker.platform = _TestFilePicker(
        filePath: null,
        fileName: 'empty.md',
        fileBytes: Uint8List(0),
      );

      await tester.pumpWidget(_wrapHome());
      await tester.pumpAndSettle();

      await tester.runAsync(() async {
        await tester.tap(find.byType(FloatingActionButton));
        await Future<void>.delayed(const Duration(milliseconds: 200));
      });
      await tester.pumpAndSettle();

      expect(find.text('empty.md'), findsOneWidget);
      expect(find.text('Noch kein Markdown zum Anzeigen.'), findsOneWidget);
    },
  );

  testWidgets(
    'UTF-8 BOM wird beim Laden entfernt, sodass Überschrift sauber gerendert wird',
    (tester) async {
      final bomBytes = Uint8List.fromList([
        0xEF,
        0xBB,
        0xBF,
        ...utf8.encode('# Hallo BOM'),
      ]);
      FilePicker.platform = _TestFilePicker(
        filePath: null,
        fileName: 'bom.md',
        fileBytes: bomBytes,
      );

      await tester.pumpWidget(_wrapHome());
      await tester.pumpAndSettle();

      await tester.runAsync(() async {
        await tester.tap(find.byType(FloatingActionButton));
        await Future<void>.delayed(const Duration(milliseconds: 200));
      });
      await tester.pumpAndSettle();

      expect(find.text('Hallo BOM'), findsOneWidget);
    },
  );

  testWidgets(
    'Exception in pickFiles entsperrt _isBusy zuverlässig (finally-Guard)',
    (tester) async {
      FilePicker.platform = _TestFilePicker(throwOnPick: true);

      await tester.pumpWidget(_wrapHome());
      await tester.pumpAndSettle();

      await tester.runAsync(() async {
        await tester.tap(find.byType(FloatingActionButton));
        await Future<void>.delayed(const Duration(milliseconds: 200));
      });
      await tester.pumpAndSettle();

      expect(
        find.descendant(
          of: find.byType(SnackBar),
          matching: find.text('Fehler beim Lesen der Datei.'),
        ),
        findsOneWidget,
      );
      final fab = tester.widget<FloatingActionButton>(
        find.byType(FloatingActionButton),
      );
      expect(fab.onPressed, isNotNull);
    },
  );

  testWidgets(
    'Live-Statistik (Wörter, Zeichen, Lesezeit) aktualisiert sich direkt in der Oberfläche',
    (tester) async {
      await tester.pumpWidget(_wrapHome());
      await tester.pumpAndSettle();

      expect(find.textContaining('0 Wörter'), findsOneWidget);
      expect(find.textContaining('0 Zeichen'), findsOneWidget);
      expect(find.text('~0 Min. Lesezeit'), findsOneWidget);

      await tester.tap(find.text('Editor'));
      await tester.pumpAndSettle();
      await tester.enterText(find.byType(TextField), '# Hallo Welt heute');
      await tester.pumpAndSettle();

      expect(find.textContaining('4 Wörter'), findsOneWidget);
      expect(find.textContaining('18 Zeichen'), findsOneWidget);
      expect(find.text('~1 Min. Lesezeit'), findsOneWidget);
    },
  );

  testWidgets(
    'Editor-Formatierungsleiste, Undo/Redo und Cleaner-Undo-SnackBar funktionieren',
    (tester) async {
      await tester.pumpWidget(_wrapHome());
      await tester.pumpAndSettle();

      await tester.tap(find.text('Editor'));
      await tester.pumpAndSettle();
      await tester.enterText(find.byType(TextField), 'Absatz');
      await tester.pumpAndSettle();

      await tester.tap(find.text('H1'));
      await tester.pumpAndSettle();
      expect(
        tester.widget<TextField>(find.byType(TextField)).controller?.text,
        '# Absatz',
      );

      // Undo setzt auf 'Absatz' zurück
      await tester.tap(find.byIcon(Icons.undo));
      await tester.pumpAndSettle();
      expect(
        tester.widget<TextField>(find.byType(TextField)).controller?.text,
        'Absatz',
      );

      // Redo stellt '# Absatz' wieder her
      await tester.tap(find.byIcon(Icons.redo));
      await tester.pumpAndSettle();
      expect(
        tester.widget<TextField>(find.byType(TextField)).controller?.text,
        '# Absatz',
      );

      // Formatierung entfernen über Menü + Undo via SnackBar
      await tester.tap(find.byIcon(Icons.more_vert));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Formatierung entfernen'));
      await tester.pumpAndSettle();
      expect(
        tester.widget<TextField>(find.byType(TextField)).controller?.text,
        'Absatz',
      );
      expect(find.text('Rückgängig'), findsOneWidget);

      await tester.tap(find.text('Rückgängig'));
      await tester.pumpAndSettle();
      expect(
        tester.widget<TextField>(find.byType(TextField)).controller?.text,
        '# Absatz',
      );
    },
  );

  testWidgets(
    'Cleaner-Vorschau kopiert Reintext in die Zwischenablage mit Feedback',
    (tester) async {
      String? clipboardText;
      tester.binding.defaultBinaryMessenger.setMockMethodCallHandler(
        SystemChannels.platform,
        (call) async {
          if (call.method == 'Clipboard.setData') {
            final args = call.arguments as Map<dynamic, dynamic>;
            clipboardText = args['text'] as String?;
          }
          return null;
        },
      );
      addTearDown(() {
        tester.binding.defaultBinaryMessenger.setMockMethodCallHandler(
          SystemChannels.platform,
          null,
        );
      });

      await tester.pumpWidget(_wrapHome());
      await tester.pumpAndSettle();

      await tester.tap(find.text('Editor'));
      await tester.pumpAndSettle();
      await tester.enterText(find.byType(TextField), '**Fett** Text');
      await tester.pumpAndSettle();

      await tester.tap(find.byIcon(Icons.cleaning_services_outlined));
      await tester.pumpAndSettle();
      expect(find.text('Cleaner-Vorschau (Reintext)'), findsOneWidget);
      expect(find.text('Fett Text'), findsOneWidget);

      await tester.tap(find.text('Reinen Text kopieren'));
      await tester.pumpAndSettle();
      expect(clipboardText, 'Fett Text');
      expect(
        find.text('Reiner Text in die Zwischenablage kopiert.'),
        findsOneWidget,
      );
    },
  );

  testWidgets(
    'Format-Hilfe fügt gewählte Vorlage in den Editor ein',
    (tester) async {
      await tester.pumpWidget(_wrapHome());
      await tester.pumpAndSettle();

      await tester.tap(find.text('Editor'));
      await tester.pumpAndSettle();
      await tester.tap(find.byIcon(Icons.help_outline));
      await tester.pumpAndSettle();

      expect(find.text('Format-Hilfe'), findsOneWidget);
      await tester.tap(find.text('Fett'));
      await tester.pumpAndSettle();

      expect(
        tester.widget<TextField>(find.byType(TextField)).controller?.text,
        '**Text**',
      );
    },
  );

  testWidgets(
    'Barrierefreie Sprachauswahl (DE -> EN -> ES) und Theme-Wechsel in CleanMarkdownApp',
    (tester) async {
      await tester.pumpWidget(
        const CleanMarkdownApp(initialLocale: Locale('de')),
      );
      await tester.pumpAndSettle();
      expect(find.text('Vorschau'), findsOneWidget);

      // Auf Englisch umschalten
      await tester.tap(find.byIcon(Icons.more_vert));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Sprache'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('English'));
      await tester.pumpAndSettle();
      expect(find.text('Preview'), findsOneWidget);
      expect(find.text('New document'), findsOneWidget);
      expect(find.byTooltip('Save'), findsOneWidget);

      // Auf Spanisch umschalten
      await tester.tap(find.byIcon(Icons.more_vert));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Language'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Español'));
      await tester.pumpAndSettle();
      expect(find.text('Vista previa'), findsOneWidget);
      expect(find.text('Nuevo documento'), findsOneWidget);
      expect(find.byTooltip('Guardar'), findsOneWidget);

      // Auf dunkles Design umschalten
      await tester.tap(find.byIcon(Icons.more_vert));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Tema'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Oscuro'));
      await tester.pumpAndSettle();

      final scaffoldCtx = tester.element(find.byType(Scaffold));
      expect(Theme.of(scaffoldCtx).brightness, Brightness.dark);
    },
  );

  testWidgets(
    'WCAG 2.1 AA: Alle IconButtons >= 48dp, Tooltips vorhanden & kein Overflow bei 360dp / 1.5x TextScale',
    (tester) async {
      tester.view.physicalSize = const Size(360, 640);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      await tester.pumpWidget(
        MediaQuery(
          data: const MediaQueryData(textScaler: TextScaler.linear(1.5)),
          child: _wrapHome(),
        ),
      );
      await tester.pumpAndSettle();

      // Editor-Tab öffnen, damit auch die Formatierungs-IconButtons gerendert sind
      await tester.tap(find.text('Editor'));
      await tester.pumpAndSettle();

      final iconButtons = find.byType(IconButton);
      expect(iconButtons, findsWidgets);
      for (final element in iconButtons.evaluate()) {
        final box = element.renderObject as RenderBox;
        final widget = element.widget as IconButton;
        expect(
          box.size.width >= 48.0,
          isTrue,
          reason: 'IconButton (${widget.tooltip}) Breite < 48dp: ${box.size}',
        );
        expect(
          box.size.height >= 48.0,
          isTrue,
          reason: 'IconButton (${widget.tooltip}) Höhe < 48dp: ${box.size}',
        );
        expect(
          widget.tooltip != null && widget.tooltip!.trim().isNotEmpty,
          isTrue,
          reason: 'Jeder IconButton benötigt einen lokalisierten Tooltip',
        );
      }

      final popupButtons = find.byType(PopupMenuButton<String>);
      expect(popupButtons, findsOneWidget);
      final popup = tester.widget<PopupMenuButton<String>>(popupButtons);
      expect(popup.tooltip, isNotNull);
      expect(popup.tooltip!.isNotEmpty, isTrue);
    },
  );

  testWidgets(
    'Split-View-Toggle auf breiten Bildschirmen zeigt Editor & Vorschau parallel',
    (tester) async {
      tester.view.physicalSize = const Size(900, 700);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      await tester.pumpWidget(_wrapHome());
      await tester.pumpAndSettle();

      await tester.tap(find.byIcon(Icons.vertical_split_outlined));
      await tester.pumpAndSettle();

      expect(find.byType(TextField), findsOneWidget);
      expect(find.textContaining('Keine Datei geöffnet'), findsOneWidget);
    },
  );
}
