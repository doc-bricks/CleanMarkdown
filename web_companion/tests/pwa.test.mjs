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
