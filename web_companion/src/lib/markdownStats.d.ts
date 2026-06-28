/** Zählt Zeilen in einem Markdown-String. Falsy-Eingabe → 0. */
export declare function countLines(markdown: string | null | undefined): number

/** Zählt Inline-Links [text](url); Bilder ![alt](url) werden nicht gezählt. */
export declare function countLinks(markdown: string | null | undefined): number
