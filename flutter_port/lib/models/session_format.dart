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

  /// Factory constructor to parse a session from a JSON map safely.
  factory CleanMarkdownSession.fromJson(Map<String, dynamic> json) {
    final rawFileName = json['fileName'];
    final fileName =
        rawFileName is String && rawFileName.trim().isNotEmpty
            ? rawFileName.trim()
            : 'document.md';
    final rawVersion = json['version'];
    final rawMarkdown = json['markdown'];
    final rawTheme = json['theme'];
    final rawWorkspace = json['workspace'];
    final rawUpdatedAt = json['updatedAt'];
    final rawSettings = json['settings'];

    return CleanMarkdownSession(
      version:
          rawVersion is String && rawVersion.isNotEmpty
              ? rawVersion
              : currentVersion,
      fileName: fileName,
      markdown: rawMarkdown is String ? rawMarkdown : '',
      theme: rawTheme is String && rawTheme.isNotEmpty ? rawTheme : 'paper',
      workspace:
          rawWorkspace is String && rawWorkspace.isNotEmpty
              ? rawWorkspace
              : 'editor',
      updatedAt:
          rawUpdatedAt is String && rawUpdatedAt.isNotEmpty
              ? rawUpdatedAt
              : DateTime.now().toIso8601String(),
      settings:
          rawSettings is Map
              ? Map<String, dynamic>.from(rawSettings)
              : null,
    );
  }

  /// Factory constructor to parse a session from raw JSON string.
  factory CleanMarkdownSession.fromJsonString(String jsonString) {
    final dynamic decoded = jsonDecode(jsonString);
    if (decoded is! Map<String, dynamic>) {
      throw const FormatException(
        'Ungültiges JSON-Wurzelelement für CleanMarkdownSession',
      );
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
    final trimmed = content.trimLeft();
    if (trimmed.isEmpty || !trimmed.startsWith('{')) {
      return false;
    }
    try {
      final dynamic decoded = jsonDecode(trimmed);
      if (decoded is Map<String, dynamic>) {
        return decoded['version'] == currentVersion ||
            (decoded['markdown'] is String && decoded['fileName'] is String);
      }
    } catch (_) {
      // Not valid JSON
    }
    return false;
  }
}
