import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:cleanmarkdown/l10n/app_localizations.dart';
import 'package:cleanmarkdown/screens/home_screen.dart';

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
}
