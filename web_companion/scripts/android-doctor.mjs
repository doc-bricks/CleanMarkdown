import { spawnSync } from 'node:child_process'
import { existsSync, readFileSync, readdirSync } from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const scriptDir = path.dirname(fileURLToPath(import.meta.url))
const projectRoot = path.resolve(scriptDir, '..')
const androidRoot = path.join(projectRoot, 'android')
const args = new Set(process.argv.slice(2))

const APP_ID = 'com.lukas.cleanmarkdown'
const REQUIRED_NODE_MAJOR = 20
const REQUIRED_JAVA_MAJOR = 17
const REQUIRED_COMPILE_SDK = 35
const COMMAND_TIMEOUT_MS = 15_000
const GRADLE_TIMEOUT_MS = 30_000

const checks = []

function addCheck(status, name, detail, hint = '') {
  checks.push({ status, name, detail, hint })
}

function projectPath(relativePath) {
  return path.join(projectRoot, relativePath)
}

function read(relativePath) {
  return readFileSync(projectPath(relativePath), 'utf8')
}

function checkFile(relativePath, name) {
  if (existsSync(projectPath(relativePath))) {
    addCheck('PASS', name, relativePath)
    return true
  }

  addCheck('BLOCKER', name, `${relativePath} fehlt`)
  return false
}

function unique(values) {
  return [...new Set(values.filter(Boolean))]
}

function commandResult(command, commandArgs, options = {}) {
  const completed = spawnSync(command, commandArgs, {
    cwd: options.cwd ?? projectRoot,
    encoding: 'utf8',
    env: options.env ?? process.env,
    shell: process.platform === 'win32' && /\.(?:bat|cmd)$/i.test(command),
    timeout: options.timeout ?? COMMAND_TIMEOUT_MS,
  })

  const output = `${completed.stdout ?? ''}${completed.stderr ?? ''}`.trim()
  if (completed.error) {
    const timedOut = completed.error.code === 'ETIMEDOUT'
    return {
      ok: false,
      timedOut,
      output: timedOut ? `Timeout nach ${options.timeout ?? COMMAND_TIMEOUT_MS} ms` : completed.error.message,
    }
  }

  return { ok: completed.status === 0, timedOut: false, output }
}

function parseMajor(versionText) {
  const match = versionText.match(/(?:version\s+["]?)?v?(\d+)(?:\.(\d+))?/i)
  if (!match) {
    return null
  }

  const first = Number.parseInt(match[1], 10)
  return first === 1 && match[2] ? Number.parseInt(match[2], 10) : first
}

function detectAndroidSdk() {
  const candidates = unique([
    process.env.ANDROID_HOME,
    process.env.ANDROID_SDK_ROOT,
    path.join(process.env.LOCALAPPDATA ?? '', 'Android', 'Sdk'),
    path.join(os.homedir(), 'AppData', 'Local', 'Android', 'Sdk'),
    path.join(os.homedir(), 'Library', 'Android', 'sdk'),
    path.join(os.homedir(), 'Android', 'Sdk'),
    'C:\\dev\\Android\\Sdk',
  ])

  return candidates.find((candidate) => existsSync(candidate)) ?? ''
}

function javaCandidates() {
  const executable = process.platform === 'win32' ? 'java.exe' : 'java'
  return unique([
    process.env.JAVA_HOME ? path.join(process.env.JAVA_HOME, 'bin', executable) : '',
    process.platform === 'win32'
      ? path.join('C:\\Program Files\\Android\\Android Studio\\jbr', 'bin', executable)
      : '',
    'java',
  ])
}

function checkStructure() {
  checkFile('package-lock.json', 'NPM-Lockfile')
  checkFile('capacitor.config.ts', 'Capacitor-Konfiguration')
  checkFile('android/gradlew', 'Gradle-Wrapper Unix')
  checkFile('android/gradlew.bat', 'Gradle-Wrapper Windows')
  checkFile('android/variables.gradle', 'Android SDK-Konfiguration')
  checkFile('android/app/build.gradle', 'Android App-Builddatei')
  checkFile('android/app/src/main/AndroidManifest.xml', 'Android Manifest')

  if (existsSync(projectPath('package.json'))) {
    const pkg = JSON.parse(read('package.json'))
    const capacitorPackages = [
      pkg.dependencies?.['@capacitor/core'],
      pkg.dependencies?.['@capacitor/android'],
      pkg.devDependencies?.['@capacitor/cli'],
    ]
    const allVersionSeven = capacitorPackages.every((value) => typeof value === 'string' && /\b7\./.test(value))
    addCheck(
      allVersionSeven ? 'PASS' : 'BLOCKER',
      'Capacitor-Paketlinie',
      allVersionSeven ? capacitorPackages.join(', ') : 'Core, Android und CLI müssen auf Major 7 liegen',
    )
  }

  if (existsSync(projectPath('capacitor.config.ts'))) {
    const config = read('capacitor.config.ts')
    const valid = config.includes(`appId: '${APP_ID}'`) && config.includes("webDir: 'dist'")
    addCheck(
      valid ? 'PASS' : 'BLOCKER',
      'Capacitor App-ID/WebDir',
      valid ? `${APP_ID}, dist` : 'App-ID oder webDir weicht ab',
    )
  }

  if (existsSync(projectPath('android/variables.gradle'))) {
    const variables = read('android/variables.gradle')
    const valid =
      variables.includes(`compileSdkVersion = ${REQUIRED_COMPILE_SDK}`) &&
      variables.includes(`targetSdkVersion = ${REQUIRED_COMPILE_SDK}`)
    addCheck(
      valid ? 'PASS' : 'BLOCKER',
      'Android SDK-Zielversion',
      valid ? `compileSdk/targetSdk ${REQUIRED_COMPILE_SDK}` : `API ${REQUIRED_COMPILE_SDK} nicht konsistent`,
    )
  }

  if (existsSync(projectPath('android/app/build.gradle'))) {
    const gradle = read('android/app/build.gradle')
    const valid = gradle.includes(`applicationId "${APP_ID}"`)
    addCheck(valid ? 'PASS' : 'BLOCKER', 'Android applicationId', valid ? APP_ID : 'applicationId weicht ab')
  }
}

function checkToolchain() {
  const node = commandResult(process.execPath, ['--version'])
  const nodeMajor = node.ok ? parseMajor(node.output) : null
  const nodeReady = node.ok && nodeMajor !== null && nodeMajor >= REQUIRED_NODE_MAJOR
  addCheck(
    nodeReady ? 'PASS' : 'BLOCKER',
    'Node.js',
    node.ok ? node.output : 'nicht ausführbar',
    nodeReady ? '' : `Node.js ${REQUIRED_NODE_MAJOR}+ erforderlich`,
  )

  const hasCapacitorCli = existsSync(projectPath('node_modules/@capacitor/cli'))
  addCheck(
    hasCapacitorCli ? 'PASS' : 'BLOCKER',
    'Capacitor CLI lokal',
    hasCapacitorCli
      ? 'node_modules/@capacitor/cli'
      : 'lokale CLI fehlt',
    hasCapacitorCli ? '' : 'npm ci ausführen',
  )

  let java = null
  for (const candidate of javaCandidates()) {
    const probe = commandResult(candidate, ['-version'])
    if (probe.ok) {
      const output = probe.output.split(/\r?\n/)[0]
      java = { candidate, output, major: parseMajor(output) }
      break
    }
  }
  const javaReady = java && java.major !== null && java.major >= REQUIRED_JAVA_MAJOR
  addCheck(
    javaReady ? 'PASS' : 'BLOCKER',
    'Java über Android Studio/JAVA_HOME/PATH',
    java ? `${java.candidate}: ${java.output}` : 'kein ausführbares Java gefunden',
    javaReady ? '' : `AGP 8.x benötigt JDK ${REQUIRED_JAVA_MAJOR}+; Android Studio installieren oder JAVA_HOME setzen`,
  )

  const sdk = detectAndroidSdk()
  if (!sdk) {
    addCheck('BLOCKER', 'Android SDK', 'kein SDK-Pfad gefunden', 'ANDROID_HOME oder ANDROID_SDK_ROOT setzen')
    addCheck('BLOCKER', `Android Plattform ${REQUIRED_COMPILE_SDK}`, 'ohne SDK nicht prüfbar')
    addCheck('BLOCKER', 'Android Build-Tools', 'ohne SDK nicht prüfbar')
    addCheck('BLOCKER', 'adb', 'ohne SDK nicht prüfbar')
    return
  }

  addCheck('PASS', 'Android SDK', sdk)
  const platform = path.join(sdk, 'platforms', `android-${REQUIRED_COMPILE_SDK}`)
  addCheck(
    existsSync(platform) ? 'PASS' : 'BLOCKER',
    `Android Plattform ${REQUIRED_COMPILE_SDK}`,
    platform,
    `SDK Platform android-${REQUIRED_COMPILE_SDK} installieren`,
  )

  const buildTools = path.join(sdk, 'build-tools')
  const buildToolVersions = existsSync(buildTools)
    ? readdirSync(buildTools, { withFileTypes: true }).filter((entry) => entry.isDirectory()).map((entry) => entry.name)
    : []
  addCheck(
    buildToolVersions.length > 0 ? 'PASS' : 'BLOCKER',
    'Android Build-Tools',
    buildToolVersions.length > 0 ? buildToolVersions.join(', ') : 'keine Build-Tools gefunden',
  )

  const adb = path.join(sdk, 'platform-tools', process.platform === 'win32' ? 'adb.exe' : 'adb')
  addCheck(existsSync(adb) ? 'PASS' : 'BLOCKER', 'adb', adb, 'Android Platform-Tools installieren')
}

function checkGradle() {
  if (!args.has('--gradle')) {
    addCheck('SKIP', 'Gradle-Wrapper-Lauf', 'nur mit --gradle; Standard-Doctor bleibt nicht blockierend')
    return
  }

  const wrapper = process.platform === 'win32' ? projectPath('android/gradlew.bat') : './gradlew'
  const gradle = commandResult(wrapper, ['--version'], { cwd: androidRoot, timeout: GRADLE_TIMEOUT_MS })
  addCheck(
    gradle.ok ? 'PASS' : 'BLOCKER',
    'Gradle-Wrapper-Lauf',
    gradle.ok ? gradle.output.split(/\r?\n/).find((line) => line.includes('Gradle ')) ?? 'ausführbar' : gradle.output,
    gradle.timedOut ? 'Netzwerk/Gradle-Cache prüfen; Prozess wurde nach 30 s beendet' : '',
  )
}

function buildReport() {
  const blockers = checks.filter((item) => item.status === 'BLOCKER').length
  const passed = checks.filter((item) => item.status === 'PASS').length
  return {
    appId: APP_ID,
    requiredNodeMajor: REQUIRED_NODE_MAJOR,
    requiredJavaMajor: REQUIRED_JAVA_MAJOR,
    requiredCompileSdk: REQUIRED_COMPILE_SDK,
    gradleChecked: args.has('--gradle'),
    status: blockers === 0 ? 'ready' : 'blocked',
    summary: { passed, blockers, skipped: checks.filter((item) => item.status === 'SKIP').length },
    checks,
  }
}

function printText(report) {
  console.log('CleanMarkdown Android Doctor')
  console.log(`Projekt: ${projectRoot}`)
  console.log('')
  for (const item of report.checks) {
    const hint = item.hint ? ` — ${item.hint}` : ''
    console.log(`[${item.status}] ${item.name}: ${item.detail}${hint}`)
  }
  console.log('')
  console.log(report.status === 'ready' ? 'Android-Toolchain ist bereit.' : `Android-Toolchain blockiert: ${report.summary.blockers} Punkt(e) offen.`)
}

checkStructure()
checkToolchain()
checkGradle()

const report = buildReport()
if (args.has('--json')) {
  console.log(JSON.stringify(report, null, 2))
} else {
  printText(report)
}

if (report.status === 'blocked' && !args.has('--allow-blockers')) {
  process.exitCode = 1
}
