import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { spawnSync } from 'node:child_process'
import test from 'node:test'
import { fileURLToPath } from 'node:url'

const projectRoot = dirname(dirname(fileURLToPath(import.meta.url)))

test('Android Doctor liefert auch ohne lokale SDK-Toolchain einen strukturierten Bericht', () => {
  const completed = spawnSync(
    process.execPath,
    [join(projectRoot, 'scripts', 'android-doctor.mjs'), '--json', '--allow-blockers'],
    { cwd: projectRoot, encoding: 'utf8' }
  )

  assert.equal(completed.status, 0, completed.stderr)
  const report = JSON.parse(completed.stdout)
  assert.equal(report.appId, 'com.lukas.cleanmarkdown')
  assert.equal(report.requiredNodeMajor, 20)
  assert.equal(report.requiredJavaMajor, 17)
  assert.equal(report.requiredCompileSdk, 35)
  assert.ok(['ready', 'blocked'].includes(report.status))
  assert.equal(report.summary.passed + report.summary.blockers + report.summary.skipped, report.checks.length)

  const names = new Set(report.checks.map((item) => item.name))
  for (const expected of [
    'Capacitor-Paketlinie',
    'Capacitor App-ID/WebDir',
    'Android SDK-Zielversion',
    'Node.js',
    'Android SDK',
    'Gradle-Wrapper-Lauf'
  ]) {
    assert.ok(names.has(expected), `${expected} fehlt im Doctor-Bericht`)
  }
})

test('package.json exponiert getrennte Doctor-, JSON- und Gradle-Gates', () => {
  const pkg = JSON.parse(readFileSync(join(projectRoot, 'package.json'), 'utf8'))
  assert.equal(pkg.scripts['android:doctor'], 'node scripts/android-doctor.mjs')
  assert.equal(pkg.scripts['android:doctor:json'], 'node scripts/android-doctor.mjs --json --allow-blockers')
  assert.equal(pkg.scripts['android:gradle-doctor'], 'node scripts/android-doctor.mjs --gradle')
  assert.equal(pkg.scripts['test:android-doctor'], 'node --test tests/android-doctor.test.mjs')
})
