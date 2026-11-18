import 'dart:convert';
import 'dart:typed_data';

/// Error classification when decoding local text or Markdown bytes.
enum TextDecodeError {
  none,
  tooLarge,
  binaryData,
  invalidUtf8,
}

/// Result of safely decoding file bytes into UTF-8 text.
class TextDecodeResult {
  final String? text;
  final TextDecodeError error;
  final bool hadBom;

  const TextDecodeResult._({
    this.text,
    required this.error,
    this.hadBom = false,
  });

  const TextDecodeResult.success(String text, {bool hadBom = false})
    : this._(text: text, error: TextDecodeError.none, hadBom: hadBom);

  const TextDecodeResult.failure(TextDecodeError error)
    : this._(error: error);

  bool get isSuccess => error == TextDecodeError.none && text != null;
}

/// Utility functions for Markdown manipulation, safe UTF-8 decoding, and document metrics.
class MarkdownCleaner {
  /// Default upper limit (5 MB) to keep mobile editor & preview responsive.
  static const int defaultMaxFileBytes = 5 * 1024 * 1024;

  static final RegExp _fenceOpenPattern = RegExp(r'^\s*(`{3,}|~{3,})');
  static final RegExp _hrPattern = RegExp(r'^\s*([-*_]\s*){3,}$');
  static final RegExp _imagePattern = RegExp(r'!\[([^\]]*)\]\([^)]*\)');
  static final RegExp _linkPattern = RegExp(r'\[([^\]]+)\]\([^)]*\)');
  static final RegExp _boldItalicStarPattern = RegExp(
    r'\*\*\*([^\s*](?:.*?\S)?)\*\*\*',
  );
  static final RegExp _boldItalicUnderscorePattern = RegExp(
    r'(?<!\w)___([^\s_](?:.*?\S)?)___(?!\w)',
  );
  static final RegExp _boldStarPattern = RegExp(
    r'\*\*([^\s*](?:.*?\S)?)\*\*',
  );
  static final RegExp _boldUnderscorePattern = RegExp(
    r'(?<!\w)__([^\s_](?:.*?\S)?)__(?!\w)',
  );
  static final RegExp _italicStarPattern = RegExp(
    r'\*([^\s*](?:.*?\S)?)\*',
  );
  static final RegExp _italicUnderscorePattern = RegExp(
    r'(?<!\w)_([^\s_](?:.*?\S)?)_(?!\w)',
  );
  static final RegExp _strikePattern = RegExp(r'~~(.*?)~~');
  static final RegExp _inlineCodePattern = RegExp(r'`([^`]+)`');
  static final RegExp _headingPattern = RegExp(r'^\s{0,3}#{1,6}\s+');
  static final RegExp _blockquotePattern = RegExp(r'^\s{0,3}>\s*');
  static final RegExp _listPattern = RegExp(
    r'^\s{0,3}(?:[-*+]|\d+[.)])\s+(?:\[[ xX]\]\s+)?',
  );
  static final RegExp _nonWhitespaceRunPattern = RegExp(r'\S+');

  /// Decodes raw bytes as strict UTF-8 (stripping optional UTF-8 BOM).
  /// Rejects oversized payloads, NUL-containing binary data, and invalid UTF-8
  /// sequences before any active document state is replaced.
  static TextDecodeResult decodeUtf8Bytes(
    Uint8List bytes, {
    int maxBytes = defaultMaxFileBytes,
  }) {
    if (bytes.length > maxBytes) {
      return const TextDecodeResult.failure(TextDecodeError.tooLarge);
    }

    var effectiveBytes = bytes;
    var hadBom = false;
    if (bytes.length >= 3 &&
        bytes[0] == 0xEF &&
        bytes[1] == 0xBB &&
        bytes[2] == 0xBF) {
      effectiveBytes = bytes.sublist(3);
      hadBom = true;
    }

    if (effectiveBytes.isEmpty) {
      return TextDecodeResult.success('', hadBom: hadBom);
    }

    if (effectiveBytes.contains(0)) {
      return const TextDecodeResult.failure(TextDecodeError.binaryData);
    }

    try {
      final decoded = utf8.decode(effectiveBytes, allowMalformed: false);
      return TextDecodeResult.success(decoded, hadBom: hadBom);
    } on FormatException {
      return const TextDecodeResult.failure(TextDecodeError.invalidUtf8);
    }
  }

  /// Sanitizes a user-supplied or URI-derived filename for safe local/temp file use.
  static String sanitizeFileName(
    String? rawName, {
    String fallback = 'cleanmarkdown.md',
  }) {
    if (rawName == null || rawName.trim().isEmpty) {
      return fallback;
    }
    var base = rawName.trim().split(RegExp(r'[/\\]')).lastWhere(
      (segment) => segment.isNotEmpty,
      orElse: () => '',
    );
    base = base.replaceAll(RegExp(r'[\\/:*?"<>|\x00-\x1F]'), '_').trim();
    if (base.isEmpty || RegExp(r'^\.+$').hasMatch(base)) {
      return fallback;
    }
    return base;
  }

  /// Strips Markdown markup and returns clean plain text.
  /// Preserves paragraph structure, line breaks, and code block contents.
  static String stripMarkdown(String markdown) {
    if (markdown.isEmpty) return '';

    final normalized = markdown.replaceAll('\r\n', '\n').replaceAll('\r', '\n');
    final lines = normalized.split('\n');
    final cleanedLines = <String>[];

    var inFence = false;
    var fenceChar = '';
    var fenceLength = 0;

    for (final line in lines) {
      final fenceMatch = _fenceOpenPattern.firstMatch(line);
      if (fenceMatch != null) {
        final marker = fenceMatch.group(1)!;
        final trimmedAfter = line.substring(fenceMatch.end).trim();
        if (!inFence) {
          inFence = true;
          fenceChar = marker[0];
          fenceLength = marker.length;
          continue;
        } else if (marker[0] == fenceChar &&
            marker.length >= fenceLength &&
            trimmedAfter.isEmpty) {
          inFence = false;
          fenceChar = '';
          fenceLength = 0;
          continue;
        }
      }

      if (inFence) {
        cleanedLines.add(line);
        continue;
      }

      if (_hrPattern.hasMatch(line)) {
        continue;
      }

      var l = line;
      l = l.replaceAllMapped(_imagePattern, (m) => m[1] ?? '');
      l = l.replaceAllMapped(_linkPattern, (m) => m[1] ?? '');
      l = l.replaceAllMapped(_boldItalicStarPattern, (m) => m[1] ?? '');
      l = l.replaceAllMapped(_boldItalicUnderscorePattern, (m) => m[1] ?? '');
      l = l.replaceAllMapped(_boldStarPattern, (m) => m[1] ?? '');
      l = l.replaceAllMapped(_boldUnderscorePattern, (m) => m[1] ?? '');
      l = l.replaceAllMapped(_italicStarPattern, (m) => m[1] ?? '');
      l = l.replaceAllMapped(_italicUnderscorePattern, (m) => m[1] ?? '');
      l = l.replaceAllMapped(_strikePattern, (m) => m[1] ?? '');
      l = l.replaceAllMapped(_inlineCodePattern, (m) => m[1] ?? '');

      l = l.replaceAll(_headingPattern, '');
      l = l.replaceAll(_blockquotePattern, '');
      l = l.replaceAll(_listPattern, '');

      cleanedLines.add(l);
    }

    return cleanedLines.join('\n');
  }

  /// Calculates statistical metrics for a document in a single O(n) pass.
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
    var wordCount = 0;
    var charCountNoSpaces = 0;

    for (final match in _nonWhitespaceRunPattern.allMatches(text)) {
      wordCount += 1;
      charCountNoSpaces += match.end - match.start;
    }

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
