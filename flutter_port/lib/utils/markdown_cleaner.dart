/// Utility functions for Markdown manipulation and document metrics.
class MarkdownCleaner {
  /// Strips Markdown markup and returns clean plain text.
  /// Preserves paragraph structure and line breaks.
  static String stripMarkdown(String markdown) {
    if (markdown.isEmpty) return '';

    String text = markdown;

    // Normalize Windows CRLF to LF
    text = text.replaceAll('\r\n', '\n');

    // 0. Horizontal rules (---, ***, ___ on standalone lines) - do before bold/italic!
    text = text.replaceAll(RegExp(r'(^|\n)\s*([-*_]\s*){3,}\s*(\n|$)'), '\n');

    // 1. Remove code blocks fences (keep inner content)
    text = text.replaceAllMapped(
      RegExp(r'```[a-zA-Z0-9_-]*\n([\s\S]*?)\n```'),
      (m) => m[1] ?? '',
    );

    // 2. Images: ![alt](url) -> alt
    text = text.replaceAllMapped(
      RegExp(r'!\[([^\]]*)\]\([^)]*\)'),
      (m) => m[1] ?? '',
    );

    // 3. Links: [text](url) -> text
    text = text.replaceAllMapped(
      RegExp(r'\[([^\]]+)\]\([^)]*\)'),
      (m) => m[1] ?? '',
    );

    // 4. Bold + Italic: ***text*** or ___text___ -> text
    text = text.replaceAllMapped(
      RegExp(r'(\*{3}|_{3})(.*?)\1'),
      (m) => m[2] ?? '',
    );

    // 5. Bold: **text** or __text__ -> text
    text = text.replaceAllMapped(
      RegExp(r'(\*{2}|_{2})(.*?)\1'),
      (m) => m[2] ?? '',
    );

    // 6. Italic: *text* or _text_ -> text
    text = text.replaceAllMapped(
      RegExp(r'(\*{1}|_{1})(.*?)\1'),
      (m) => m[2] ?? '',
    );

    // 7. Strikethrough: ~~text~~ -> text
    text = text.replaceAllMapped(
      RegExp(r'~~(.*?)~~'),
      (m) => m[1] ?? '',
    );

    // 8. Inline code: `code` -> code
    text = text.replaceAllMapped(
      RegExp(r'`([^`]+)`'),
      (m) => m[1] ?? '',
    );

    // Split into lines for line-based rules
    final lines = text.split('\n');
    final cleanedLines = <String>[];

    for (final line in lines) {
      String l = line;

      // ATX Headings: # Heading -> Heading
      l = l.replaceAll(RegExp(r'^\s{0,3}#{1,6}\s+'), '');

      // Blockquotes: > text -> text
      l = l.replaceAll(RegExp(r'^\s{0,3}>\s*'), '');

      // Unordered list bullets: - item, * item, + item -> item
      l = l.replaceAll(RegExp(r'^\s{0,3}[-*+]\s+'), '');

      // Ordered list numbers: 1. item -> item
      l = l.replaceAll(RegExp(r'^\s{0,3}\d+\.\s+'), '');

      cleanedLines.add(l);
    }

    return cleanedLines.join('\n');
  }

  /// Calculates statistical metrics for a document.
  static DocumentStats calculateStats(String text) {
    if (text.trim().isEmpty) {
      return const DocumentStats(
        wordCount: 0,
        characterCount: 0,
        characterCountNoSpaces: 0,
        readingTimeMinutes: 0,
      );
    }

    final charCount = text.length;
    final charCountNoSpaces = text.replaceAll(RegExp(r'\s'), '').length;

    final words = text
        .trim()
        .split(RegExp(r'\s+'))
        .where((w) => w.isNotEmpty)
        .toList();
    final wordCount = words.length;

    // Average reading speed: 200 words per minute
    final readingTime = wordCount > 0 ? (wordCount / 200.0).ceil() : 0;

    return DocumentStats(
      wordCount: wordCount,
      characterCount: charCount,
      characterCountNoSpaces: charCountNoSpaces,
      readingTimeMinutes: readingTime,
    );
  }
}

/// Immutable record holding document statistics.
class DocumentStats {
  final int wordCount;
  final int characterCount;
  final int characterCountNoSpaces;
  final int readingTimeMinutes;

  const DocumentStats({
    required this.wordCount,
    required this.characterCount,
    required this.characterCountNoSpaces,
    required this.readingTimeMinutes,
  });
}
