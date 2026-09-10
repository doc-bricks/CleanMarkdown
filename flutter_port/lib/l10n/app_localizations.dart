import 'package:flutter/widgets.dart';

abstract class AppLocalizations {
  static AppLocalizations of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations)!;
  }

  static const List<Locale> supportedLocales = [
    Locale('de'),
    Locale('en'),
    Locale('es'),
  ];

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
  String get newFile;
  String get shareFile;
  String get newFileDiscardTitle;
  String get newFileDiscardConfirm;
  String get newFileDiscardCancel;
  String get exportSession;
  String get sessionExportSuccess;
  String get sessionImported;
  String get clearFormatting;
  String get clearFormattingSuccess;
  String get statsLabel;
  String statsWords(int count);
  String statsChars(int count);
  String statsReading(int minutes);
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) =>
      ['de', 'en', 'es'].contains(locale.languageCode);

  @override
  Future<AppLocalizations> load(Locale locale) async {
    if (locale.languageCode == 'de') {
      return AppLocalizationsDe();
    } else if (locale.languageCode == 'es') {
      return AppLocalizationsEs();
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

  @override
  String get newFile => 'Neue Datei';

  @override
  String get shareFile => 'Teilen';

  @override
  String get newFileDiscardTitle => 'Ungespeicherte Änderungen verwerfen?';

  @override
  String get newFileDiscardConfirm => 'Verwerfen';

  @override
  String get newFileDiscardCancel => 'Abbrechen';

  @override
  String get exportSession => 'Session exportieren';

  @override
  String get sessionExportSuccess => 'Session erfolgreich exportiert.';

  @override
  String get sessionImported => 'Session geladen';

  @override
  String get clearFormatting => 'Formatierung entfernen';

  @override
  String get clearFormattingSuccess => 'Markdown-Formatierung entfernt.';

  @override
  String get statsLabel => 'Statistik';

  @override
  String statsWords(int count) => '$count Wörter';

  @override
  String statsChars(int count) => '$count Zeichen';

  @override
  String statsReading(int minutes) => '~$minutes Min. Lesezeit';
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

  @override
  String get newFile => 'New file';

  @override
  String get shareFile => 'Share';

  @override
  String get newFileDiscardTitle => 'Discard unsaved changes?';

  @override
  String get newFileDiscardConfirm => 'Discard';

  @override
  String get newFileDiscardCancel => 'Cancel';

  @override
  String get exportSession => 'Export session';

  @override
  String get sessionExportSuccess => 'Session exported successfully.';

  @override
  String get sessionImported => 'Session loaded';

  @override
  String get clearFormatting => 'Clear formatting';

  @override
  String get clearFormattingSuccess => 'Markdown formatting stripped.';

  @override
  String get statsLabel => 'Statistics';

  @override
  String statsWords(int count) => '$count words';

  @override
  String statsChars(int count) => '$count chars';

  @override
  String statsReading(int minutes) => '~$minutes min read';
}

class AppLocalizationsEs extends AppLocalizations {
  @override
  String get appTitle => 'CleanMarkdown';

  @override
  String get openFile => 'Abrir archivo';

  @override
  String get saveFile => 'Guardar';

  @override
  String get previewTab => 'Vista previa';

  @override
  String get editorTab => 'Editor';

  @override
  String get noFileOpen =>
      'Ningún archivo abierto.\nToca "Abrir archivo" o empieza a escribir en el editor.';

  @override
  String get emptyPreview => 'Aún no hay Markdown para mostrar.';

  @override
  String get errorReadingFile => 'Error al leer el archivo.';

  @override
  String get errorSavingFile => 'Error al guardar el archivo.';

  @override
  String get editorHint => '# Escribe Markdown aquí';

  @override
  String get newDocument => 'Nuevo documento';

  @override
  String get unsavedChanges => 'Cambios sin guardar';

  @override
  String get saveSuccess => 'Archivo guardado.';

  @override
  String get newFile => 'Nuevo archivo';

  @override
  String get shareFile => 'Compartir';

  @override
  String get newFileDiscardTitle => '¿Descartar cambios sin guardar?';

  @override
  String get newFileDiscardConfirm => 'Descartar';

  @override
  String get newFileDiscardCancel => 'Cancelar';

  @override
  String get exportSession => 'Exportar sesión';

  @override
  String get sessionExportSuccess => 'Sesión exportada con éxito.';

  @override
  String get sessionImported => 'Sesión cargada';

  @override
  String get clearFormatting => 'Limpiar formato';

  @override
  String get clearFormattingSuccess => 'Formato Markdown eliminado.';

  @override
  String get statsLabel => 'Estadísticas';

  @override
  String statsWords(int count) => '$count palabras';

  @override
  String statsChars(int count) => '$count caracteres';

  @override
  String statsReading(int minutes) => '~$minutes min de lectura';
}
