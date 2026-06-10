import 'dart:io';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:cleanmarkdown/l10n/app_localizations.dart';
import 'package:cleanmarkdown/screens/home_screen.dart';

class _FakeFilePicker extends FilePicker {
  final String filePath;
  _FakeFilePicker(this.filePath);

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
    return FilePickerResult([
      PlatformFile(path: filePath, name: 'test.md', size: 0),
    ]);
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

Widget _buildTestApp() {
  return MaterialApp(
    localizationsDelegates: const [
      AppLocalizations.delegate,
      GlobalMaterialLocalizations.delegate,
      GlobalWidgetsLocalizations.delegate,
      GlobalCupertinoLocalizations.delegate,
    ],
    supportedLocales: AppLocalizations.supportedLocales,
    locale: const Locale('de'),
    home: const HomeScreen(),
  );
}

void main() {
  testWidgets('HomeScreen zeigt Platzhaltertext wenn keine Datei geöffnet', (tester) async {
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
    await tester.pumpWidget(MaterialApp(
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: AppLocalizations.supportedLocales,
      locale: const Locale('en'),
      home: const HomeScreen(),
    ));
    await tester.pumpAndSettle();
    expect(find.text('CleanMarkdown'), findsOneWidget);
  });

  testWidgets('_pickFile lädt .md-Datei und zeigt Markdown-Inhalt', (tester) async {
    final dir = Directory.systemTemp.createTempSync('cleanmd_test');
    final file = File('${dir.path}/test.md')..writeAsStringSync('# Hallo Welt');
    FilePicker.platform = _FakeFilePicker(file.path);
    addTearDown(() {
      try { dir.deleteSync(recursive: true); } catch (_) {}
    });

    await tester.pumpWidget(_buildTestApp());
    await tester.pumpAndSettle();

    // runAsync erlaubt echte Datei-I/O (readAsString) im Test-Event-Loop
    await tester.runAsync(() async {
      await tester.tap(find.byType(FloatingActionButton));
      await Future<void>.delayed(const Duration(milliseconds: 200));
    });
    await tester.pumpAndSettle();

    expect(find.textContaining('Hallo Welt'), findsOneWidget);
  });
}
