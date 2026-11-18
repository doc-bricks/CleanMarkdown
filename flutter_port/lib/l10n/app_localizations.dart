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
  String statsCharsNoSpaces(int count);
  String statsReading(int minutes);

  String get undo;
  String get redo;
  String get copyMarkdown;
  String get copyCleanText;
  String get copiedSuccess;
  String get cleanTextCopied;
  String get cleanerPreviewTitle;
  String get cleanerNoChanges;
  String get applyCleanText;
  String get formatHelp;
  String get formatHelpSubtitle;
  String get language;
  String get languageSystem;
  String get languageDe;
  String get languageEn;
  String get languageEs;
  String get theme;
  String get themeSystem;
  String get themeLight;
  String get themeDark;
  String get moreOptions;
  String get startWriting;
  String get fileTooLarge;
  String get invalidUtf8Error;
  String get binaryFileError;
  String get errorSharingFile;
  String get errorExportingSession;
  String get splitViewTooltip;
  String get linkCopiedPrefix;
  String get closeLabel;

  String get formatH1;
  String get formatH2;
  String get formatBold;
  String get formatItalic;
  String get formatCode;
  String get formatList;
  String get formatQuote;
  String get formatLink;
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
  String statsCharsNoSpaces(int count) => '$count ohne Leerzeichen';

  @override
  String statsReading(int minutes) => '~$minutes Min. Lesezeit';

  @override
  String get undo => 'Rückgängig';

  @override
  String get redo => 'Wiederholen';

  @override
  String get copyMarkdown => 'Markdown kopieren';

  @override
  String get copyCleanText => 'Reinen Text kopieren';

  @override
  String get copiedSuccess => 'Markdown in die Zwischenablage kopiert.';

  @override
  String get cleanTextCopied => 'Reiner Text in die Zwischenablage kopiert.';

  @override
  String get cleanerPreviewTitle => 'Cleaner-Vorschau (Reintext)';

  @override
  String get cleanerNoChanges => 'Keine Markdown-Formatierung gefunden.';

  @override
  String get applyCleanText => 'Im Editor anwenden';

  @override
  String get formatHelp => 'Format-Hilfe';

  @override
  String get formatHelpSubtitle =>
      'Tippe auf eine Vorlage, um sie im Editor einzufügen.';

  @override
  String get language => 'Sprache';

  @override
  String get languageSystem => 'Systemsprache';

  @override
  String get languageDe => 'Deutsch';

  @override
  String get languageEn => 'English';

  @override
  String get languageEs => 'Español';

  @override
  String get theme => 'Design';

  @override
  String get themeSystem => 'System';

  @override
  String get themeLight => 'Hell';

  @override
  String get themeDark => 'Dunkel';

  @override
  String get moreOptions => 'Weitere Optionen';

  @override
  String get startWriting => 'Im Editor schreiben';

  @override
  String get fileTooLarge => 'Datei ist zu groß (max. 5 MB).';

  @override
  String get invalidUtf8Error =>
      'Ungültiges UTF-8: Datei konnte nicht geladen werden. Aktueller Text bleibt erhalten.';

  @override
  String get binaryFileError =>
      'Binärdatei erkannt: Nur UTF-8-Textdateien werden unterstützt.';

  @override
  String get errorSharingFile => 'Fehler beim Teilen der Datei.';

  @override
  String get errorExportingSession => 'Fehler beim Exportieren der Session.';

  @override
  String get splitViewTooltip => 'Geteilte Ansicht umschalten';

  @override
  String get linkCopiedPrefix => 'Link kopiert';

  @override
  String get closeLabel => 'Schließen';

  @override
  String get formatH1 => 'Überschrift 1';

  @override
  String get formatH2 => 'Überschrift 2';

  @override
  String get formatBold => 'Fett';

  @override
  String get formatItalic => 'Kursiv';

  @override
  String get formatCode => 'Inline-Code';

  @override
  String get formatList => 'Aufzählung';

  @override
  String get formatQuote => 'Zitat';

  @override
  String get formatLink => 'Link';
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
  String statsCharsNoSpaces(int count) => '$count without spaces';

  @override
  String statsReading(int minutes) => '~$minutes min read';

  @override
  String get undo => 'Undo';

  @override
  String get redo => 'Redo';

  @override
  String get copyMarkdown => 'Copy Markdown';

  @override
  String get copyCleanText => 'Copy plain text';

  @override
  String get copiedSuccess => 'Markdown copied to clipboard.';

  @override
  String get cleanTextCopied => 'Plain text copied to clipboard.';

  @override
  String get cleanerPreviewTitle => 'Cleaner preview (plain text)';

  @override
  String get cleanerNoChanges => 'No Markdown formatting found.';

  @override
  String get applyCleanText => 'Apply in editor';

  @override
  String get formatHelp => 'Formatting help';

  @override
  String get formatHelpSubtitle =>
      'Tap a template to insert it into the editor.';

  @override
  String get language => 'Language';

  @override
  String get languageSystem => 'System default';

  @override
  String get languageDe => 'Deutsch';

  @override
  String get languageEn => 'English';

  @override
  String get languageEs => 'Español';

  @override
  String get theme => 'Theme';

  @override
  String get themeSystem => 'System';

  @override
  String get themeLight => 'Light';

  @override
  String get themeDark => 'Dark';

  @override
  String get moreOptions => 'More options';

  @override
  String get startWriting => 'Start writing';

  @override
  String get fileTooLarge => 'File is too large (max 5 MB).';

  @override
  String get invalidUtf8Error =>
      'Invalid UTF-8: File could not be loaded. Current text preserved.';

  @override
  String get binaryFileError =>
      'Binary file detected: Only UTF-8 text files are supported.';

  @override
  String get errorSharingFile => 'Error sharing file.';

  @override
  String get errorExportingSession => 'Error exporting session.';

  @override
  String get splitViewTooltip => 'Toggle split view';

  @override
  String get linkCopiedPrefix => 'Link copied';

  @override
  String get closeLabel => 'Close';

  @override
  String get formatH1 => 'Heading 1';

  @override
  String get formatH2 => 'Heading 2';

  @override
  String get formatBold => 'Bold';

  @override
  String get formatItalic => 'Italic';

  @override
  String get formatCode => 'Inline code';

  @override
  String get formatList => 'Bullet list';

  @override
  String get formatQuote => 'Quote';

  @override
  String get formatLink => 'Link';
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
  String statsCharsNoSpaces(int count) => '$count sin espacios';

  @override
  String statsReading(int minutes) => '~$minutes min de lectura';

  @override
  String get undo => 'Deshacer';

  @override
  String get redo => 'Rehacer';

  @override
  String get copyMarkdown => 'Copiar Markdown';

  @override
  String get copyCleanText => 'Copiar texto limpio';

  @override
  String get copiedSuccess => 'Markdown copiado al portapapeles.';

  @override
  String get cleanTextCopied => 'Texto limpio copiado al portapapeles.';

  @override
  String get cleanerPreviewTitle => 'Vista previa limpia (texto plano)';

  @override
  String get cleanerNoChanges => 'No se encontró formato Markdown.';

  @override
  String get applyCleanText => 'Aplicar en el editor';

  @override
  String get formatHelp => 'Ayuda de formato';

  @override
  String get formatHelpSubtitle =>
      'Toca una plantilla para insertarla en el editor.';

  @override
  String get language => 'Idioma';

  @override
  String get languageSystem => 'Idioma del sistema';

  @override
  String get languageDe => 'Deutsch';

  @override
  String get languageEn => 'English';

  @override
  String get languageEs => 'Español';

  @override
  String get theme => 'Tema';

  @override
  String get themeSystem => 'Sistema';

  @override
  String get themeLight => 'Claro';

  @override
  String get themeDark => 'Oscuro';

  @override
  String get moreOptions => 'Más opciones';

  @override
  String get startWriting => 'Escribir en el editor';

  @override
  String get fileTooLarge => 'El archivo es demasiado grande (máx. 5 MB).';

  @override
  String get invalidUtf8Error =>
      'UTF-8 no válido: no se pudo cargar el archivo. El texto actual se conserva.';

  @override
  String get binaryFileError =>
      'Archivo binario detectado: solo se admiten archivos de texto UTF-8.';

  @override
  String get errorSharingFile => 'Error al compartir el archivo.';

  @override
  String get errorExportingSession => 'Error al exportar la sesión.';

  @override
  String get splitViewTooltip => 'Alternar vista dividida';

  @override
  String get linkCopiedPrefix => 'Enlace copiado';

  @override
  String get closeLabel => 'Cerrar';

  @override
  String get formatH1 => 'Título 1';

  @override
  String get formatH2 => 'Título 2';

  @override
  String get formatBold => 'Negrita';

  @override
  String get formatItalic => 'Cursiva';

  @override
  String get formatCode => 'Código en línea';

  @override
  String get formatList => 'Lista';

  @override
  String get formatQuote => 'Cita';

  @override
  String get formatLink => 'Enlace';
}
