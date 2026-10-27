import 'dart:convert';

/// Data model representing a CleanMarkdown session file (cleanmarkdown-session-v1.json).
/// Conforms to the canonical specification in EXPORTFORMAT.md.
class CleanMarkdownSession {
  static const String currentVersion = 'cleanmarkdown-session-v1';
  static const Set<String> _supportedThemes = {'paper', 'night'};
  static const Set<String> _supportedWorkspaces = {'read', 'write', 'split'};

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

  /// Factory constructor to parse a versioned session contract from a JSON map.
  ///
  /// The fields checked here are the mandatory fields from EXPORTFORMAT.md.
  /// Rejecting a malformed or future session is safer than silently importing
  /// it as an empty document and losing the user's context.
  factory CleanMarkdownSession.fromJson(Map<String, dynamic> json) {
    final version = _requiredString(json, 'version');
    if (version != currentVersion) {
      throw FormatException('Nicht unterstützte Session-Version: $version');
    }

    final fileName = _requiredString(json, 'fileName');
    final markdown = _requiredString(json, 'markdown');
    final theme = _requiredString(json, 'theme');
    final workspace = _requiredString(json, 'workspace');
    final updatedAt = _requiredString(json, 'updatedAt');
    if (!_supportedThemes.contains(theme)) {
      throw FormatException('Ungültiges Session-Theme: $theme');
    }
    if (!_supportedWorkspaces.contains(workspace)) {
      throw FormatException('Ungültiger Session-Arbeitsbereich: $workspace');
    }
    if (DateTime.tryParse(updatedAt) == null) {
      throw FormatException('Ungültiger Session-Zeitstempel: $updatedAt');
    }

    final settingsValue = json['settings'];
    if (settingsValue != null && settingsValue is! Map) {
      throw const FormatException('Ungültige Session-Einstellungen');
    }

    return CleanMarkdownSession(
      version: version,
      fileName: fileName,
      markdown: markdown,
      theme: theme,
      workspace: workspace,
      updatedAt: updatedAt,
      settings: settingsValue == null
          ? null
          : Map<String, dynamic>.from(settingsValue),
    );
  }

  static String _requiredString(Map<String, dynamic> json, String field) {
    final value = json[field];
    if (value is! String || value.isEmpty) {
      throw FormatException('Session-Feld "$field" fehlt oder ist ungültig');
    }
    return value;
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
        CleanMarkdownSession.fromJson(decoded);
        return true;
      }
    } catch (_) {
      // Not valid JSON
    }
    return false;
  }
}
