/**
 * markdownStats.mjs – Pure-ESM-Hilfsfunktionen für Markdown-Statistiken.
 *
 * Diese Datei hat absichtlich keine Build-Abhängigkeiten, damit
 * `node --test` sie direkt importieren kann (kein tsx, kein ts-node nötig).
 */

/**
 * Zählt die Zeilen in einem Markdown-String.
 * Leerer String oder falsy → 0.
 * Eine abschließende Leerzeile (trailing \n) zählt als extra Zeile.
 *
 * @param {string | null | undefined} markdown
 * @returns {number}
 */
export function countLines(markdown) {
  if (!markdown) return 0
  return markdown.split('\n').length
}

/**
 * Zählt Markdown-Inline-Links [text](url).
 * Bilder ![alt](url) werden NICHT gezählt (negativer Lookbehind `(?<!!)` vor `[`).
 * Inline-Code-Segmente (`...`) werden vor dem Zählen ausgeblendet.
 *
 * @param {string | null | undefined} markdown
 * @returns {number}
 */
export function countLinks(markdown) {
  if (!markdown) return 0
  // Inline-Code-Segmente durch gleichlange Leerzeichen ersetzen,
  // damit darin enthaltene Klammern nicht als Links erkannt werden.
  const withoutCode = markdown.replace(/`[^`\n]*`/g, (m) => ' '.repeat(m.length))
  const matches = withoutCode.match(/(?<!!)\[[^\]]*\]\([^)]*\)/g)
  return matches ? matches.length : 0
}
