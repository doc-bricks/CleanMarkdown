import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dir = dirname(fileURLToPath(import.meta.url));
const root = join(__dir, '..');
const pub = join(root, 'public');

describe('PWA vite.config icons', () => {
  const cfg = readFileSync(join(root, 'vite.config.ts'), 'utf8');

  test('vite.config defines SVG icon-192', () => {
    assert.ok(cfg.includes('icon-192.svg'), 'icon-192.svg missing from vite.config icons');
  });

  test('vite.config defines SVG icon-512', () => {
    assert.ok(cfg.includes('icon-512.svg'), 'icon-512.svg missing from vite.config icons');
  });

  test('vite.config defines icon-maskable-192.png', () => {
    assert.ok(cfg.includes('icon-maskable-192.png'), 'icon-maskable-192.png missing from vite.config icons');
  });

  test('vite.config defines icon-maskable-512.png', () => {
    assert.ok(cfg.includes('icon-maskable-512.png'), 'icon-maskable-512.png missing from vite.config icons');
  });

  test('vite.config has maskable purpose', () => {
    assert.ok(cfg.includes("purpose: 'maskable'") || cfg.includes('"maskable"'), 'maskable purpose missing from vite.config');
  });
});

describe('PWA index.html integration', () => {
  const html = readFileSync(join(root, 'index.html'), 'utf8');

  test('index.html has lang="de"', () => {
    assert.ok(html.includes('lang="de"'), 'lang=de missing');
  });

  test('index.html has theme-color meta', () => {
    assert.ok(html.includes('theme-color'), 'theme-color meta missing');
  });

  test('index.html has apple-touch-icon', () => {
    assert.ok(html.includes('apple-touch-icon'), 'apple-touch-icon link missing');
  });
});

describe('PWA icon files', () => {
  test('icon-192.svg exists in public/icons/', () => {
    assert.ok(existsSync(join(pub, 'icons', 'icon-192.svg')), 'icon-192.svg missing from public/icons/');
  });

  test('apple-touch-icon.png exists in public/', () => {
    assert.ok(existsSync(join(pub, 'apple-touch-icon.png')), 'apple-touch-icon.png missing from public/');
  });

  test('icon-maskable-192.png exists in public/', () => {
    assert.ok(existsSync(join(pub, 'icon-maskable-192.png')), 'icon-maskable-192.png missing from public/');
  });

  test('icon-maskable-512.png exists in public/', () => {
    assert.ok(existsSync(join(pub, 'icon-maskable-512.png')), 'icon-maskable-512.png missing from public/');
  });
});

// --- Bug-Fix-Regressionstests ---

describe('Bug-Fix-Regressionstests', () => {
  const appSrc = readFileSync(join(root, 'src', 'App.tsx'), 'utf8');
  const pkgSrc = readFileSync(join(root, 'package.json'), 'utf8');

  test('App.tsx triggerDownload hängt Link an DOM vor click() (Bug #1 Fix — iOS Safari/Firefox download)', () => {
    assert.match(appSrc, /document\.body\.append\(link\)/);
    assert.match(appSrc, /link\.remove\(\)/);
  });

  test('App.tsx triggerDownload revokeObjectURL nach link.remove() (Bug #1 Fix — kein Race)', () => {
    const downloadFn = appSrc.match(/function triggerDownload[\s\S]*?^}/m)?.[0] ?? '';
    const revokeIdx = downloadFn.indexOf('revokeObjectURL');
    const removeIdx = downloadFn.indexOf('link.remove()');
    assert.ok(removeIdx !== -1 && revokeIdx !== -1 && removeIdx < revokeIdx,
      'revokeObjectURL muss nach link.remove() stehen');
  });

  test('App.tsx readImportedFile hat try/catch um JSON.parse (Bug #2 Fix — user message statt SyntaxError)', () => {
    assert.match(appSrc, /try\s*\{\s*parsed\s*=\s*JSON\.parse/);
    assert.match(appSrc, /catch\s*\{[\s\S]*?throw new Error\(errorInvalidSession\)/);
  });

  test('package.json test-Skript zeigt auf existierende pwa.test.mjs (Bug #3 Fix)', () => {
    assert.match(pkgSrc, /pwa\.test\.mjs/);
    assert.doesNotMatch(pkgSrc, /i18n\.test\.mjs/);
  });

  test('App.tsx handleDragLeave prüft relatedTarget explizit (Bug #4 Fix — kein as-Node-Cast, kein Flackern)', () => {
    assert.match(appSrc, /!\s*event\.relatedTarget\s*\|\|/);
    assert.match(appSrc, /event\.currentTarget\.contains\(event\.relatedTarget\)/);
  });
});
