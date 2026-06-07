import 'package:flutter/widgets.dart';

abstract class AppLocalizations {
  static AppLocalizations of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations)!;
  }

  static const List<Locale> supportedLocales = [
    Locale('de'),
    Locale('en'),
  ];

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  String get appTitle;
  String get openFile;
  String get noFileOpen;
  String get errorReadingFile;
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) =>
      ['de', 'en'].contains(locale.languageCode);

  @override
  Future<AppLocalizations> load(Locale locale) async {
    if (locale.languageCode == 'de') return AppLocalizationsDe();
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
  String get noFileOpen => 'Keine Datei geöffnet.\nTippe auf „Datei öffnen".';
  @override
  String get errorReadingFile => 'Fehler beim Lesen der Datei.';
}

class AppLocalizationsEn extends AppLocalizations {
  @override
  String get appTitle => 'CleanMarkdown';
  @override
  String get openFile => 'Open file';
  @override
  String get noFileOpen => 'No file open.\nTap "Open file".';
  @override
  String get errorReadingFile => 'Error reading file.';
}
