import 'dart:io';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('Bug 1 fix: mounted-Guard vor setState in _pickFile', () {
    test('home_screen.dart enthält mounted-Guard nach pickFiles-await', () {
      final source = File('lib/screens/home_screen.dart').readAsStringSync();
      // Guard muss nach dem ersten await (pickFiles) vorhanden sein
      expect(
        source.contains('if (!mounted) return;'),
        isTrue,
        reason: 'mounted-Guard fehlt — setState nach await kann auf disposed Widget werfen',
      );
    });

    test('home_screen.dart enthält mindestens zwei mounted-Guards', () {
      final source = File('lib/screens/home_screen.dart').readAsStringSync();
      final count = 'if (!mounted) return;'.allMatches(source).length;
      expect(
        count >= 2,
        isTrue,
        reason: '_pickFile hat zwei await-Punkte, beide brauchen einen mounted-Guard',
      );
    });
  });

  group('Bug 1 fix: catch-Block logt Fehlerdetails', () {
    test('home_screen.dart catch verwendet (e, stackTrace) statt (_)', () {
      final source = File('lib/screens/home_screen.dart').readAsStringSync();
      expect(
        source.contains('catch (e, stackTrace)'),
        isTrue,
        reason: "catch (_) verschluckt alle Fehlerdetails — (e, stackTrace) erforderlich",
      );
      expect(
        source.contains('catch (_)'),
        isFalse,
        reason: "stummes catch (_) muss entfernt sein",
      );
    });

    test('home_screen.dart ruft debugPrint bei Lesefehler auf', () {
      final source = File('lib/screens/home_screen.dart').readAsStringSync();
      expect(
        source.contains('debugPrint('),
        isTrue,
        reason: 'Fehler müssen per debugPrint protokolliert werden',
      );
    });
  });

  group('Bug 2 fix: ungenutzte path_provider-Abhängigkeit entfernt', () {
    test('pubspec.yaml enthält kein path_provider', () {
      final pubspec = File('pubspec.yaml').readAsStringSync();
      expect(
        pubspec.contains('path_provider'),
        isFalse,
        reason: 'path_provider war nie importiert — unnötige Abhängigkeit entfernt',
      );
    });

    test('kein Dart-File importiert path_provider', () {
      final libDir = Directory('lib');
      final dartFiles = libDir.listSync(recursive: true).whereType<File>()
          .where((f) => f.path.endsWith('.dart'));
      for (final file in dartFiles) {
        final src = file.readAsStringSync();
        expect(
          src.contains('path_provider'),
          isFalse,
          reason: '${file.path} importiert path_provider obwohl es entfernt wurde',
        );
      }
    });
  });
}
