const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { test } = require('node:test');

// Exercise the shipped renderer without starting the UI or evaluating its HTML.
const source = fs.readFileSync(path.join(__dirname, '../web_companion/app.js'), 'utf8');
const start = source.indexOf('  function escapeHtml(');
const end = source.indexOf('  function renderPreview()', start);
assert.ok(start >= 0 && end > start);
const renderer = { t: () => '' };
vm.createContext(renderer);
vm.runInContext(source.slice(start, end), renderer);

test('ordinary fenced code preserves language and escapes body', () => {
  assert.equal(renderer.renderMarkdown('```python\n<x> & "quoted"\n```'),
    '<pre><code class="language-python">&lt;x&gt; &amp; &quot;quoted&quot;</code></pre>');
});

for (const language of ['"><img src=x onerror=probe>', '" onmouseover="probe',
  "'<> &", '&quot;><img src=x>', '日本語']) {
  test(`fence language remains one escaped attribute: ${JSON.stringify(language)}`, () => {
    const output = renderer.renderMarkdown('```' + language + '\nbody\n```');
    assert.equal(output, '<pre><code class="language-' + renderer.escapeHtml(language)
      + '">body</code></pre>');
    assert.deepEqual(output.match(/<[^>]+>/g), ['<pre>',
      '<code class="language-' + renderer.escapeHtml(language) + '">', '</code>', '</pre>']);
  });
}
