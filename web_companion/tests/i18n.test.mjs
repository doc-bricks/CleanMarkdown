import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import path from 'node:path'

const __dir = path.dirname(fileURLToPath(import.meta.url))
const de = JSON.parse(readFileSync(path.join(__dir, '../src/locales/de.json'), 'utf8'))
const en = JSON.parse(readFileSync(path.join(__dir, '../src/locales/en.json'), 'utf8'))

// ── Key completeness ───────────────────────────────────────────────────────

test('de and en have identical key sets', () => {
  const deKeys = Object.keys(de).sort()
  const enKeys = Object.keys(en).sort()
  assert.deepEqual(deKeys, enKeys, 'Key sets must match between locales')
})

// ── No empty values ────────────────────────────────────────────────────────

test('no de value is empty', () => {
  for (const [key, val] of Object.entries(de)) {
    assert.ok(typeof val === 'string' && val.length > 0, `de.${key} must not be empty`)
  }
})

test('no en value is empty', () => {
  for (const [key, val] of Object.entries(en)) {
    assert.ok(typeof val === 'string' && val.length > 0, `en.${key} must not be empty`)
  }
})

// ── Required keys present ─────────────────────────────────────────────────

const REQUIRED_KEYS = [
  'heroEyebrow', 'heroHeadline', 'heroText',
  'btnOpen', 'btnSaveMd', 'btnExportSession', 'btnDemo',
  'metaUpdatedPrefix',
  'statFile', 'statWords', 'statChars', 'statReadTime',
  'ariaView', 'ariaTheme', 'ariaMetrics', 'ariaLanguage',
  'toggleRead', 'toggleSplit', 'toggleWrite',
  'togglePaper', 'toggleNight',
  'surfaceReaderLabel', 'surfaceReaderTitle', 'surfaceReaderDesc',
  'surfaceWriterLabel', 'surfaceWriterTitle', 'surfaceWriterDesc',
  'fieldFilename', 'fieldContent',
  'footnote1', 'footnote2', 'footnoteDropLabel',
  'statusInitial', 'statusLoaded',
  'statusMarkdownExported', 'statusSessionExported', 'statusDemoRestored',
  'errorCannotRead', 'errorInvalidSession',
  'timestampUnknown', 'dateLocale',
]

test('de has all required keys', () => {
  for (const key of REQUIRED_KEYS) {
    assert.ok(Object.prototype.hasOwnProperty.call(de, key), `de missing key: ${key}`)
  }
})

test('en has all required keys', () => {
  for (const key of REQUIRED_KEYS) {
    assert.ok(Object.prototype.hasOwnProperty.call(en, key), `en missing key: ${key}`)
  }
})

// ── Locales are correct ───────────────────────────────────────────────────

test('de uses de-DE date locale', () => {
  assert.equal(de.dateLocale, 'de-DE')
})

test('en uses en-US date locale', () => {
  assert.equal(en.dateLocale, 'en-US')
})

// ── statusLoaded uses {file} placeholder ─────────────────────────────────

test('de.statusLoaded contains {file} placeholder', () => {
  assert.ok(de.statusLoaded.includes('{file}'), 'de.statusLoaded must contain {file}')
})

test('en.statusLoaded contains {file} placeholder', () => {
  assert.ok(en.statusLoaded.includes('{file}'), 'en.statusLoaded must contain {file}')
})

// ── fillIn helper (pure function, tested inline) ──────────────────────────

function fillIn(template, values) {
  return Object.entries(values).reduce(
    (str, [key, val]) => str.replace(`{${key}}`, val),
    template,
  )
}

test('fillIn replaces {file} in de.statusLoaded', () => {
  const result = fillIn(de.statusLoaded, { file: 'test.md' })
  assert.ok(result.includes('test.md'), 'filename must appear in result')
  assert.ok(!result.includes('{file}'), '{file} placeholder must be replaced')
})

test('fillIn replaces {file} in en.statusLoaded', () => {
  const result = fillIn(en.statusLoaded, { file: 'test.md' })
  assert.ok(result.includes('test.md'), 'filename must appear in result')
  assert.ok(!result.includes('{file}'), '{file} placeholder must be replaced')
})

// ── formatTimestamp locale behaviour (pure function, tested inline) ───────

function formatTimestamp(value, dateLocale, unknownLabel) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return unknownLabel
  }
  return new Intl.DateTimeFormat(dateLocale, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date)
}

test('formatTimestamp returns unknown label for invalid date', () => {
  assert.equal(formatTimestamp('not-a-date', 'de-DE', de.timestampUnknown), de.timestampUnknown)
  assert.equal(formatTimestamp('not-a-date', 'en-US', en.timestampUnknown), en.timestampUnknown)
})

test('formatTimestamp returns non-empty string for valid ISO date', () => {
  const result = formatTimestamp('2026-06-07T10:00:00.000Z', de.dateLocale, de.timestampUnknown)
  assert.ok(result.length > 0, 'formatted date must not be empty')
  assert.notEqual(result, de.timestampUnknown, 'must not return unknown for valid date')
})

test('de and en format the same date differently', () => {
  const iso = '2026-06-07T10:00:00.000Z'
  const deResult = formatTimestamp(iso, de.dateLocale, de.timestampUnknown)
  const enResult = formatTimestamp(iso, en.dateLocale, en.timestampUnknown)
  assert.notEqual(deResult, enResult, 'DE and EN date formats must differ')
})
