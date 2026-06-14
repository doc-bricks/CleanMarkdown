import 'package:flutter/widgets.dart';

abstract class AppLocalizations {
  static AppLocalizations of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations)!;
  }

  static const List<Locale> supportedLocales = [Locale('de'), Locale('en')];

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  String get appTitle;
  String get openFile;
  String get saveFile;
  String get previewTab;
  String get editorTab;
  String get noFileOpen;
  String get emptyPreview;
  String get errorReadingFile;
  String get errorSavingFile;
  String get editorHint;
  String get newDocument;
  String get unsavedChanges;
  String get saveSuccess;
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) => ['de', 'en'].contains(locale.languageCode);

  @override
  Future<AppLocalizations> load(Locale locale) async {
    if (locale.languageCode == 'de') {
      return AppLocalizationsDe();
    }
    return AppLocalizationsEn();
  }

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

class AppLocalizationsDe extends AppLocalizations {
  @override
  String get appTitle => 'CleanMarkdown';

  @override
  String get openFile => 'Datei öffnen';

  @override
  String get saveFile => 'Speichern';

  @override
  String get previewTab => 'Vorschau';

  @override
  String get editorTab => 'Editor';

  @override
  String get noFileOpen =>
      'Keine Datei geöffnet.\nTippe auf „Datei öffnen“ oder beginne direkt im Editor.';

  @override
  String get emptyPreview => 'Noch kein Markdown zum Anzeigen.';

  @override
  String get errorReadingFile => 'Fehler beim Lesen der Datei.';

  @override
  String get errorSavingFile => 'Fehler beim Speichern der Datei.';

  @override
  String get editorHint => '# Markdown hier schreiben';

  @override
  String get newDocument => 'Neue Datei';

  @override
  String get unsavedChanges => 'Ungespeicherte Änderungen';

  @override
  String get saveSuccess => 'Datei gespeichert.';
}

class AppLocalizationsEn extends AppLocalizations {
  @override
  String get appTitle => 'CleanMarkdown';

  @override
  String get openFile => 'Open file';

  @override
  String get saveFile => 'Save';

  @override
  String get previewTab => 'Preview';

  @override
  String get editorTab => 'Editor';

  @override
  String get noFileOpen =>
      'No file open.\nTap "Open file" or start writing in the editor.';

  @override
  String get emptyPreview => 'No Markdown to preview yet.';

  @override
  String get errorReadingFile => 'Error reading file.';

  @override
  String get errorSavingFile => 'Error saving file.';

  @override
  String get editorHint => '# Start writing Markdown here';

  @override
  String get newDocument => 'New document';

  @override
  String get unsavedChanges => 'Unsaved changes';

  @override
  String get saveSuccess => 'File saved.';
}
