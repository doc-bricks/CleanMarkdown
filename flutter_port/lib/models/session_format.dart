import 'dart:convert';

/// Data model representing a CleanMarkdown session file (cleanmarkdown-session-v1.json).
/// Conforms to the canonical specification in EXPORTFORMAT.md.
class CleanMarkdownSession {
  static const String currentVersion = 'cleanmarkdown-session-v1';

  final String version;
  final String fileName;
  final String markdown;
  final String theme;
  final String workspace;
  final String updatedAt;
  final Map<String, dynamic>? settings;

  const CleanMarkdownSession({
    this.version = currentVersion,
    required this.fileName,
    required this.markdown,
    this.theme = 'paper',
    this.workspace = 'editor',
    required this.updatedAt,
    this.settings,
  });

  /// Factory constructor to parse a session from a JSON map.
  factory CleanMarkdownSession.fromJson(Map<String, dynamic> json) {
    return CleanMarkdownSession(
      version: json['version'] as String? ?? currentVersion,
      fileName: json['fileName'] as String? ?? 'document.md',
      markdown: json['markdown'] as String? ?? '',
      theme: json['theme'] as String? ?? 'paper',
      workspace: json['workspace'] as String? ?? 'editor',
      updatedAt: json['updatedAt'] as String? ?? DateTime.now().toIso8601String(),
      settings: json['settings'] != null ? Map<String, dynamic>.from(json['settings'] as Map) : null,
    );
  }

  /// Factory constructor to parse a session from raw JSON string.
  factory CleanMarkdownSession.fromJsonString(String jsonString) {
    final dynamic decoded = jsonDecode(jsonString);
    if (decoded is! Map<String, dynamic>) {
      throw const FormatException('Ungueltiges JSON-Wurzelelement fuer CleanMarkdownSession');
    }
    return CleanMarkdownSession.fromJson(decoded);
  }

  /// Converts the session to a JSON-encodable map.
  Map<String, dynamic> toJson() {
    return {
      'version': version,
      'fileName': fileName,
      'markdown': markdown,
      'theme': theme,
      'workspace': workspace,
      'updatedAt': updatedAt,
      if (settings != null) 'settings': settings,
    };
  }

  /// Encodes the session into a formatted JSON string.
  String toJsonString({bool pretty = true}) {
    if (pretty) {
      return const JsonEncoder.withIndent('  ').convert(toJson());
    }
    return jsonEncode(toJson());
  }

  /// Determines whether a given text looks like a valid cleanmarkdown session JSON.
  static bool isSessionJson(String content) {
    try {
      final dynamic decoded = jsonDecode(content);
      if (decoded is Map<String, dynamic>) {
        return decoded['version'] == currentVersion ||
            (decoded.containsKey('markdown') && decoded.containsKey('fileName'));
      }
    } catch (_) {
      // Not valid JSON
    }
    return false;
  }
}
