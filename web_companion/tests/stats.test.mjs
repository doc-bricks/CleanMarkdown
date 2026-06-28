/**
 * stats.test.mjs – Node:test-Suite für markdownStats.mjs + App.tsx-Integration.
 *
 * Läuft ohne Build-Schritt: node --test tests/stats.test.mjs
 */

import { test, describe } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { countLines, countLinks } from '../src/lib/markdownStats.mjs'

const __dirname = dirname(fileURLToPath(import.meta.url))
const root = resolve(__dirname, '..')

// ---------------------------------------------------------------------------
// i18n-Paritätscheck
// ---------------------------------------------------------------------------

describe('i18n-Parität (de + en)', () => {
  test('de.json und en.json haben dieselben Keys', () => {
    const de = JSON.parse(readFileSync(resolve(root, 'src/locales/de.json'), 'utf8'))
    const en = JSON.parse(readFileSync(resolve(root, 'src/locales/en.json'), 'utf8'))
    const deKeys = Object.keys(de).sort()
    const enKeys = Object.keys(en).sort()
    assert.deepStrictEqual(deKeys, enKeys, 'de.json und en.json haben unterschiedliche Keys')
  })

  test('statLines key vorhanden in de.json', () => {
    const de = JSON.parse(readFileSync(resolve(root, 'src/locales/de.json'), 'utf8'))
    assert.ok('statLines' in de, 'statLines fehlt in de.json')
  })

  test('statLinks key vorhanden in de.json', () => {
    const de = JSON.parse(readFileSync(resolve(root, 'src/locales/de.json'), 'utf8'))
    assert.ok('statLinks' in de, 'statLinks fehlt in de.json')
  })

  test('btnCopy key vorhanden in de.json', () => {
    const de = JSON.parse(readFileSync(resolve(root, 'src/locales/de.json'), 'utf8'))
    assert.ok('btnCopy' in de, 'btnCopy fehlt in de.json')
  })

  test('statusCopied key vorhanden in de.json', () => {
    const de = JSON.parse(readFileSync(resolve(root, 'src/locales/de.json'), 'utf8'))
    assert.ok('statusCopied' in de, 'statusCopied fehlt in de.json')
  })

  test('statusCopyFailed key vorhanden in de.json', () => {
    const de = JSON.parse(readFileSync(resolve(root, 'src/locales/de.json'), 'utf8'))
    assert.ok('statusCopyFailed' in de, 'statusCopyFailed fehlt in de.json')
  })
})

// ---------------------------------------------------------------------------
// countLines
// ---------------------------------------------------------------------------

describe('countLines', () => {
  test('leerer String → 0', () => {
    assert.strictEqual(countLines(''), 0)
  })

  test('null → 0', () => {
    assert.strictEqual(countLines(null), 0)
  })

  test('undefined → 0', () => {
    assert.strictEqual(countLines(undefined), 0)
  })

  test('eine Zeile ohne Newline', () => {
    assert.strictEqual(countLines('Hallo'), 1)
  })

  test('zwei Zeilen', () => {
    assert.strictEqual(countLines('Zeile 1\nZeile 2'), 2)
  })

  test('drei Zeilen mit Leerzeile', () => {
    assert.strictEqual(countLines('a\n\nb'), 3)
  })

  test('trailing newline zählt als extra Zeile', () => {
    assert.strictEqual(countLines('a\nb\n'), 3)
  })

  test('Markdown-typischer Inhalt', () => {
    const md = '# Titel\n\nAbs 1\nAbs 2\n\n- Item 1\n- Item 2\n'
    assert.strictEqual(countLines(md), 8)
  })
})

// ---------------------------------------------------------------------------
// countLinks
// ---------------------------------------------------------------------------

describe('countLinks', () => {
  test('leerer String → 0', () => {
    assert.strictEqual(countLinks(''), 0)
  })

  test('null → 0', () => {
    assert.strictEqual(countLinks(null), 0)
  })

  test('undefined → 0', () => {
    assert.strictEqual(countLinks(undefined), 0)
  })

  test('kein Link → 0', () => {
    assert.strictEqual(countLinks('Normaler Text ohne Links'), 0)
  })

  test('ein Inline-Link', () => {
    assert.strictEqual(countLinks('[Beispiel](https://example.com)'), 1)
  })

  test('zwei Inline-Links', () => {
    assert.strictEqual(countLinks('[A](https://a.com) und [B](https://b.com)'), 2)
  })

  test('Bild wird NICHT gezählt', () => {
    assert.strictEqual(countLinks('![Alt-Text](bild.png)'), 0)
  })

  test('Bild + Link → 1', () => {
    assert.strictEqual(countLinks('![img](a.png) und [Link](https://b.com)'), 1)
  })

  test('leerer Link-Text zählt', () => {
    assert.strictEqual(countLinks('[](https://example.com)'), 1)
  })

  test('Link mit Markdown-Formatierung im Text', () => {
    assert.strictEqual(countLinks('[**fett**](https://example.com)'), 1)
  })

  test('Inline-Code enthält keine Links', () => {
    assert.strictEqual(countLinks('`[nicht](kein-link)`'), 0)
  })
})

// ---------------------------------------------------------------------------
// App.tsx-Integrationscheck (Source als Text gelesen)
// ---------------------------------------------------------------------------

describe('App.tsx — Statistik-Integration', () => {
  test('App.tsx importiert countLines', () => {
    const src = readFileSync(resolve(root, 'src/App.tsx'), 'utf8')
    assert.ok(src.includes('countLines'), 'App.tsx verwendet countLines nicht')
  })

  test('App.tsx importiert countLinks', () => {
    const src = readFileSync(resolve(root, 'src/App.tsx'), 'utf8')
    assert.ok(src.includes('countLinks'), 'App.tsx verwendet countLinks nicht')
  })

  test('App.tsx hat handleCopy mit navigator.clipboard', () => {
    const src = readFileSync(resolve(root, 'src/App.tsx'), 'utf8')
    assert.ok(
      src.includes('handleCopy') && src.includes('navigator.clipboard'),
      'App.tsx hat keinen handleCopy-Handler mit navigator.clipboard'
    )
  })

  test('App.tsx hat statLines in JSX', () => {
    const src = readFileSync(resolve(root, 'src/App.tsx'), 'utf8')
    assert.ok(src.includes('statLines'), 'App.tsx hat keine statLines-StatCard')
  })

  test('App.tsx hat statLinks in JSX', () => {
    const src = readFileSync(resolve(root, 'src/App.tsx'), 'utf8')
    assert.ok(src.includes('statLinks'), 'App.tsx hat keine statLinks-StatCard')
  })

  test('App.tsx hat btnCopy in JSX', () => {
    const src = readFileSync(resolve(root, 'src/App.tsx'), 'utf8')
    assert.ok(src.includes('btnCopy'), 'App.tsx hat keinen btnCopy-Button')
  })
})
