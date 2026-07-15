import assert from 'node:assert/strict'
import { existsSync, readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import test from 'node:test'
import { fileURLToPath } from 'node:url'

const projectRoot = dirname(dirname(fileURLToPath(import.meta.url)))

function read(relativePath) {
  return readFileSync(join(projectRoot, relativePath), 'utf8')
}

test('package.json exposes Capacitor Android handoff scripts', () => {
  const pkg = JSON.parse(read('package.json'))

  assert.equal(pkg.scripts['cap:sync'], 'npm run build && cap sync')
  assert.equal(pkg.scripts['cap:android'], 'cap open android')
  assert.equal(pkg.scripts['cap:ios'], 'cap open ios')
  assert.equal(pkg.scripts['cap:doctor'], 'node --test tests/capacitor.test.mjs')

  assert.ok(pkg.dependencies['@capacitor/core'])
  assert.ok(pkg.dependencies['@capacitor/android'])
  assert.ok(pkg.dependencies['@capacitor/ios'])
  assert.ok(pkg.devDependencies['@capacitor/cli'])
})

test('Capacitor config keeps the CleanMarkdown app identity', () => {
  const config = read('capacitor.config.ts')

  assert.match(config, /appId:\s*'com\.lukas\.cleanmarkdown'/)
  assert.match(config, /appName:\s*'CleanMarkdown'/)
  assert.match(config, /webDir:\s*'dist'/)
})

test('Android wrapper source is present without generated build output', () => {
  for (const path of [
    'android/settings.gradle',
    'android/build.gradle',
    'android/variables.gradle',
    'android/gradlew.bat',
    'android/app/build.gradle',
    'android/app/src/main/AndroidManifest.xml',
    'android/app/src/main/java/com/lukas/cleanmarkdown/MainActivity.java',
    'android/app/src/main/res/values/strings.xml',
    'android/app/src/androidTest/java/com/lukas/cleanmarkdown/ExampleInstrumentedTest.java',
    'android/app/src/test/java/com/lukas/cleanmarkdown/ExampleUnitTest.java'
  ]) {
    assert.ok(existsSync(join(projectRoot, path)), `${path} fehlt`)
  }

  const ignore = read('android/.gitignore')
  assert.match(ignore, /local\.properties/)
  assert.match(ignore, /app\/src\/main\/assets\/public/)
  assert.match(ignore, /app\/src\/main\/assets\/capacitor\.config\.json/)
})

test('Android wrapper uses the CleanMarkdown package and version', () => {
  const gradle = read('android/app/build.gradle')
  assert.match(gradle, /namespace "com\.lukas\.cleanmarkdown"/)
  assert.match(gradle, /applicationId "com\.lukas\.cleanmarkdown"/)
  assert.match(gradle, /versionCode 1/)
  assert.match(gradle, /versionName "0\.1\.0"/)

  const mainActivity = read('android/app/src/main/java/com/lukas/cleanmarkdown/MainActivity.java')
  assert.match(mainActivity, /package com\.lukas\.cleanmarkdown;/)
  assert.match(mainActivity, /extends BridgeActivity/)

  const strings = read('android/app/src/main/res/values/strings.xml')
  assert.match(strings, /<string name="app_name">CleanMarkdown<\/string>/)
  assert.match(strings, /<string name="package_name">com\.lukas\.cleanmarkdown<\/string>/)

  const instrumentedTest = read(
    'android/app/src/androidTest/java/com/lukas/cleanmarkdown/ExampleInstrumentedTest.java'
  )
  assert.match(instrumentedTest, /package com\.lukas\.cleanmarkdown;/)
  assert.match(instrumentedTest, /"com\.lukas\.cleanmarkdown"/)
})
