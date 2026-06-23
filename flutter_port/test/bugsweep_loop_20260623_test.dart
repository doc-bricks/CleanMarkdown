// Regressionstest fuer den Mobile-Bugsweep 2026-06-23 (CleanMarkdown/flutter_port, RE-SWEEP).
//
// Statische Quelltext-Assertion, da `flutter`/`dart` auf der Workstation nicht im
// PATH ist (kein Laufzeit-Harness). Laut /bugsweep-Skill valide. Red-on-revert.
import 'dart:io';
import 'package:flutter_test/flutter_test.dart';

void main() {
  final homeSrc = File('lib/screens/home_screen.dart').readAsStringSync();

  test('_pickFile nutzt nicht mehr .single (StateError-Schutz bei leerer Liste)',
      () {
    expect(homeSrc.contains('result.files.single'), isFalse,
        reason: '.single wirft StateError bei leerer files-Liste (result != null)');
    expect(homeSrc.contains('result.files.isEmpty'), isTrue,
        reason: 'isEmpty-Guard + .first ersetzen das unsichere .single');
  });
}
