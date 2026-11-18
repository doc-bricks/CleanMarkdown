import 'dart:convert';
import 'dart:io';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:share_plus/share_plus.dart';

import '../l10n/app_localizations.dart';
import '../models/session_format.dart';
import '../utils/markdown_cleaner.dart';

class HomeScreen extends StatefulWidget {
  final Locale? currentLocale;
  final ValueChanged<Locale?>? onLocaleChanged;
  final ThemeMode currentThemeMode;
  final ValueChanged<ThemeMode>? onThemeModeChanged;

  const HomeScreen({
    super.key,
    this.currentLocale,
    this.onLocaleChanged,
    this.currentThemeMode = ThemeMode.system,
    this.onThemeModeChanged,
  });

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen>
    with SingleTickerProviderStateMixin {
  static const int _maxHistoryEntries = 50;

  late final TabController _tabController;
  late final TextEditingController _editorController;
  final ScrollController _editorScrollController = ScrollController();
  final ScrollController _previewScrollController = ScrollController();

  final List<String> _undoStack = <String>[];
  final List<String> _redoStack = <String>[];
  String _lastTrackedText = '';
  DateTime _lastEditTimestamp = DateTime.fromMillisecondsSinceEpoch(0);
  bool _isApplyingHistory = false;

  String _lastSavedContent = '';
  String? _currentFilePath;
  String? _currentFileName;
  bool _hasError = false;
  bool _hasUnsavedChanges = false;
  bool _isBusy = false;
  bool _splitViewEnabled = false;
  File? _lastShareTempFile;

  Locale? _localLocaleOverride;
  bool _hasLocalLocaleOverride = false;
  ThemeMode? _localThemeOverride;

  bool get _isMobilePlatform => Platform.isAndroid || Platform.isIOS;

  Locale? get _effectiveLocale =>
      _hasLocalLocaleOverride ? _localLocaleOverride : widget.currentLocale;

  ThemeMode get _effectiveThemeMode =>
      _localThemeOverride ?? widget.currentThemeMode;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _tabController.addListener(_handleTabChanged);
    _editorController = TextEditingController();
    _editorController.addListener(_handleEditorChanged);
  }

  @override
  void dispose() {
    _tabController
      ..removeListener(_handleTabChanged)
      ..dispose();
    _editorController
      ..removeListener(_handleEditorChanged)
      ..dispose();
    _editorScrollController.dispose();
    _previewScrollController.dispose();
    _cleanupShareTempFile();
    super.dispose();
  }

  void _cleanupShareTempFile() {
    final stale = _lastShareTempFile;
    _lastShareTempFile = null;
    if (stale != null) {
      try {
        if (stale.existsSync()) {
          stale.deleteSync();
        }
      } catch (_) {
        // Temp file cleanup is non-critical.
      }
    }
  }

  void _handleTabChanged() {
    if (!mounted || _tabController.indexIsChanging) return;
    setState(() {});
  }

  void _handleEditorChanged() {
    if (!mounted) {
      return;
    }

    final text = _editorController.text;
    final wasEmpty = _lastTrackedText.isEmpty;
    final isNowEmpty = text.isEmpty;
    final undoWasEmpty = _undoStack.isEmpty;
    final redoWasEmpty = _redoStack.isEmpty;

    if (!_isApplyingHistory && text != _lastTrackedText) {
      final now = DateTime.now();
      final lengthDelta = (text.length - _lastTrackedText.length).abs();
      final pauseElapsed =
          now.difference(_lastEditTimestamp) > const Duration(milliseconds: 800);
      if (lengthDelta > 1 || pauseElapsed || _undoStack.isEmpty) {
        _pushUndoSnapshot(_lastTrackedText);
      }
      _redoStack.clear();
      _lastTrackedText = text;
      _lastEditTimestamp = now;
    }

    final hasUnsavedChanges = text != _lastSavedContent;
    if (_hasUnsavedChanges != hasUnsavedChanges ||
        wasEmpty != isNowEmpty ||
        undoWasEmpty != _undoStack.isEmpty ||
        redoWasEmpty != _redoStack.isEmpty) {
      setState(() {
        _hasUnsavedChanges = hasUnsavedChanges;
      });
    }
  }

  void _pushUndoSnapshot(String snapshot) {
    if (_undoStack.isNotEmpty && _undoStack.last == snapshot) {
      return;
    }
    _undoStack.add(snapshot);
    if (_undoStack.length > _maxHistoryEntries) {
      _undoStack.removeAt(0);
    }
  }

  void _applyTextProgrammatically(
    String newText, {
    TextSelection? selection,
    bool recordUndo = true,
  }) {
    final currentText = _editorController.text;
    if (recordUndo && newText != currentText) {
      _pushUndoSnapshot(currentText);
      _redoStack.clear();
    }
    _isApplyingHistory = true;
    final clampedSelection =
        selection ?? TextSelection.collapsed(offset: newText.length);
    _editorController.value = TextEditingValue(
      text: newText,
      selection: clampedSelection,
    );
    _lastTrackedText = newText;
    _isApplyingHistory = false;
    if (mounted) {
      setState(() {
        _hasUnsavedChanges = newText != _lastSavedContent;
      });
    }
  }

  void _undo() {
    if (_undoStack.isEmpty) return;
    final previous = _undoStack.removeLast();
    _redoStack.add(_editorController.text);
    _applyTextProgrammatically(previous, recordUndo: false);
  }

  void _redo() {
    if (_redoStack.isEmpty) return;
    final next = _redoStack.removeLast();
    _pushUndoSnapshot(_editorController.text);
    _applyTextProgrammatically(next, recordUndo: false);
  }

  void _showSnackBar(
    BuildContext ctx,
    String message, {
    SnackBarAction? action,
  }) {
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(
          content: Text(message),
          action: action,
        ),
      );
  }

  Future<void> _pickFile(BuildContext ctx) async {
    final l10n = AppLocalizations.of(ctx);
    setState(() {
      _isBusy = true;
    });

    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: const ['md', 'markdown', 'txt', 'json'],
        withData: true,
      );

      if (!mounted) return;
      // .first statt .single: leere files-Liste (result != null) wirft sonst StateError.
      if (result == null || result.files.isEmpty) {
        return;
      }

      final picked = result.files.first;
      Uint8List? rawBytes;
      if (picked.path != null) {
        rawBytes = await File(picked.path!).readAsBytes();
      } else {
        rawBytes = picked.bytes;
      }

      if (!mounted) return;
      if (rawBytes == null) {
        _showSnackBar(ctx, l10n.errorReadingFile);
        return;
      }

      final decoded = MarkdownCleaner.decodeUtf8Bytes(rawBytes);
      if (!decoded.isSuccess) {
        final hasActiveDocument =
            _editorController.text.isNotEmpty ||
            _currentFilePath != null ||
            _currentFileName != null;
        if (!hasActiveDocument) {
          setState(() {
            _hasError = true;
          });
        }
        final errorMessage = switch (decoded.error) {
          TextDecodeError.tooLarge => l10n.fileTooLarge,
          TextDecodeError.binaryData => l10n.binaryFileError,
          TextDecodeError.invalidUtf8 => l10n.invalidUtf8Error,
          TextDecodeError.none => l10n.errorReadingFile,
        };
        _showSnackBar(ctx, errorMessage);
        return;
      }

      final text = decoded.text!;
      var loadedContent = text;
      var fileName = MarkdownCleaner.sanitizeFileName(
        picked.name,
        fallback: _extractFileName(picked.path) ?? 'document.md',
      );
      String? importedNotice;

      if (CleanMarkdownSession.isSessionJson(text)) {
        try {
          final session = CleanMarkdownSession.fromJsonString(text);
          loadedContent = session.markdown;
          fileName = MarkdownCleaner.sanitizeFileName(
            session.fileName,
            fallback: fileName,
          );
          importedNotice = '${l10n.sessionImported}: $fileName';
          if (session.workspace == 'read') {
            _tabController.animateTo(0);
          } else if (session.workspace == 'write' ||
              session.workspace == 'editor') {
            _tabController.animateTo(1);
          }
        } catch (_) {
          // Fallback to loading raw text when JSON does not parse cleanly.
        }
      }

      _undoStack.clear();
      _redoStack.clear();
      _lastSavedContent = loadedContent;
      _applyTextProgrammatically(loadedContent, recordUndo: false);
      setState(() {
        _hasError = false;
        _hasUnsavedChanges = false;
        _currentFilePath = picked.path;
        _currentFileName = fileName;
      });
      if (importedNotice != null && mounted) {
        _showSnackBar(ctx, importedNotice);
      }
    } catch (e, stackTrace) {
      debugPrint('CleanMarkdown: Fehler beim Lesen der Datei: $e\n$stackTrace');
      if (!mounted) {
        return;
      }
      final hasActiveDocument =
          _editorController.text.isNotEmpty ||
          _currentFilePath != null ||
          _currentFileName != null;
      if (!hasActiveDocument) {
        setState(() {
          _hasError = true;
        });
      }
      _showSnackBar(ctx, l10n.errorReadingFile);
    } finally {
      if (mounted) {
        setState(() {
          _isBusy = false;
        });
      }
    }
  }

  Future<void> _saveFile(BuildContext ctx) async {
    final l10n = AppLocalizations.of(ctx);
    final text = _editorController.text;
    final bytes = Uint8List.fromList(utf8.encode(text));
    final fallbackFileName = _currentFileName ?? 'cleanmarkdown.md';

    setState(() {
      _isBusy = true;
    });

    try {
      var savedPath = _currentFilePath;
      if (savedPath != null && !_isMobilePlatform) {
        await File(savedPath).writeAsString(text, encoding: utf8);
      } else {
        savedPath = await FilePicker.platform.saveFile(
          dialogTitle: l10n.saveFile,
          fileName: fallbackFileName,
          type: FileType.custom,
          allowedExtensions: const ['md', 'markdown', 'txt'],
          bytes: bytes,
        );
        if (!mounted) {
          return;
        }
        if (savedPath == null) {
          return;
        }
        if (!_isMobilePlatform) {
          await File(savedPath).writeAsString(text, encoding: utf8);
        }
      }

      if (!mounted) {
        return;
      }
      _lastSavedContent = text;
      setState(() {
        _hasError = false;
        _hasUnsavedChanges = false;
        _currentFilePath = savedPath;
        _currentFileName = _extractFileName(savedPath) ?? fallbackFileName;
      });
      _showSnackBar(ctx, l10n.saveSuccess);
    } catch (e, stackTrace) {
      debugPrint(
        'CleanMarkdown: Fehler beim Speichern der Datei: $e\n$stackTrace',
      );
      if (!mounted) {
        return;
      }
      _showSnackBar(ctx, l10n.errorSavingFile);
    } finally {
      if (mounted) {
        setState(() {
          _isBusy = false;
        });
      }
    }
  }

  Future<void> _exportSession(BuildContext ctx) async {
    final l10n = AppLocalizations.of(ctx);
    final text = _editorController.text;
    final baseName = (_currentFileName ?? 'document.md').replaceAll(
      RegExp(r'\.(md|markdown|txt)$'),
      '',
    );
    final fallbackFileName = '$baseName.session.json';
    final isDark = Theme.of(ctx).brightness == Brightness.dark;
    final workspace =
        _splitViewEnabled
            ? 'split'
            : (_tabController.index == 0 ? 'read' : 'write');
    final activeLanguage = Localizations.localeOf(ctx).languageCode;

    final session = CleanMarkdownSession(
      fileName: _currentFileName ?? 'document.md',
      markdown: text,
      theme: isDark ? 'night' : 'paper',
      workspace: workspace,
      updatedAt: DateTime.now().toIso8601String(),
      settings: {
        'language': activeLanguage,
        'theme': isDark ? 'night' : 'paper',
      },
    );
    final sessionJson = session.toJsonString(pretty: true);
    final bytes = Uint8List.fromList(utf8.encode(sessionJson));

    setState(() {
      _isBusy = true;
    });

    try {
      final savedPath = await FilePicker.platform.saveFile(
        dialogTitle: l10n.exportSession,
        fileName: fallbackFileName,
        type: FileType.custom,
        allowedExtensions: const ['json'],
        bytes: bytes,
      );
      if (!mounted) return;
      if (savedPath != null && !_isMobilePlatform) {
        await File(savedPath).writeAsString(sessionJson, encoding: utf8);
      }
      if (!mounted) return;
      if (savedPath != null) {
        _showSnackBar(ctx, l10n.sessionExportSuccess);
      }
    } catch (e, stackTrace) {
      debugPrint('CleanMarkdown: Fehler beim Session-Export: $e\n$stackTrace');
      if (!mounted) return;
      _showSnackBar(ctx, l10n.errorExportingSession);
    } finally {
      if (mounted) {
        setState(() {
          _isBusy = false;
        });
      }
    }
  }

  void _clearFormatting(BuildContext ctx) {
    final l10n = AppLocalizations.of(ctx);
    final text = _editorController.text;
    if (text.isEmpty) return;
    final stripped = MarkdownCleaner.stripMarkdown(text);
    if (stripped == text) {
      _showSnackBar(ctx, l10n.cleanerNoChanges);
      return;
    }
    _applyTextProgrammatically(stripped);
    _showSnackBar(
      ctx,
      l10n.clearFormattingSuccess,
      action: SnackBarAction(
        label: l10n.undo,
        onPressed: _undo,
      ),
    );
  }

  Future<void> _copyText(
    BuildContext ctx,
    String content,
    String successMessage,
  ) async {
    if (content.isEmpty) return;
    await Clipboard.setData(ClipboardData(text: content));
    if (!mounted) return;
    _showSnackBar(ctx, successMessage);
  }

  String? _extractFileName(String? path) {
    if (path == null || path.trim().isEmpty) {
      return null;
    }
    try {
      final segments = File(path).uri.pathSegments
          .where((s) => s.isNotEmpty)
          .toList();
      if (segments.isNotEmpty) {
        final decoded = Uri.decodeComponent(segments.last);
        final sanitized = MarkdownCleaner.sanitizeFileName(decoded, fallback: '');
        if (sanitized.isNotEmpty) {
          return sanitized;
        }
      }
    } catch (_) {
      // Fallback below.
    }
    final sanitized = MarkdownCleaner.sanitizeFileName(path, fallback: '');
    return sanitized.isNotEmpty ? sanitized : null;
  }

  Future<void> _newFile(BuildContext ctx) async {
    if (_hasUnsavedChanges) {
      final l10n = AppLocalizations.of(ctx);
      final confirmed = await showDialog<bool>(
        context: ctx,
        builder:
            (dialogCtx) => AlertDialog(
              title: Text(l10n.newFileDiscardTitle),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(dialogCtx, false),
                  child: Text(l10n.newFileDiscardCancel),
                ),
                FilledButton(
                  onPressed: () => Navigator.pop(dialogCtx, true),
                  child: Text(l10n.newFileDiscardConfirm),
                ),
              ],
            ),
      );
      if (!mounted || confirmed != true) return;
    }
    _undoStack.clear();
    _redoStack.clear();
    _lastSavedContent = '';
    _applyTextProgrammatically('', recordUndo: false);
    setState(() {
      _currentFilePath = null;
      _currentFileName = null;
      _hasError = false;
      _hasUnsavedChanges = false;
    });
  }

  Future<void> _shareFile(BuildContext ctx) async {
    final l10n = AppLocalizations.of(ctx);
    final text = _editorController.text;
    if (text.isEmpty) return;

    setState(() {
      _isBusy = true;
    });
    try {
      _cleanupShareTempFile();
      final fileName = MarkdownCleaner.sanitizeFileName(
        _currentFileName ?? 'cleanmarkdown.md',
      );
      final tmpFile = File(
        '${Directory.systemTemp.path}${Platform.pathSeparator}'
        'cleanmd_share_${DateTime.now().millisecondsSinceEpoch}_$fileName',
      );
      await tmpFile.writeAsString(text, encoding: utf8);
      _lastShareTempFile = tmpFile;
      if (!mounted) return;
      await Share.shareXFiles(
        [XFile(tmpFile.path, mimeType: 'text/markdown')],
        subject: fileName,
      );
    } catch (e, stackTrace) {
      debugPrint('CleanMarkdown: Fehler beim Teilen: $e\n$stackTrace');
      if (!mounted) return;
      _showSnackBar(ctx, l10n.errorSharingFile);
    } finally {
      if (mounted) {
        setState(() {
          _isBusy = false;
        });
      }
    }
  }

  void _insertLinePrefix(String prefix) {
    final text = _editorController.text;
    final selection = _editorController.selection;
    final offset =
        selection.isValid
            ? selection.start.clamp(0, text.length)
            : text.length;
    final lineStart = offset == 0 ? 0 : text.lastIndexOf('\n', offset - 1) + 1;
    final updated =
        text.substring(0, lineStart) + prefix + text.substring(lineStart);
    final nextCursor = offset + prefix.length;
    _applyTextProgrammatically(
      updated,
      selection: TextSelection.collapsed(offset: nextCursor),
    );
  }

  void _wrapSelection(String before, String after) {
    final text = _editorController.text;
    final selection = _editorController.selection;
    final start =
        selection.isValid
            ? selection.start.clamp(0, text.length)
            : text.length;
    final end =
        selection.isValid ? selection.end.clamp(0, text.length) : text.length;
    final selected = text.substring(start, end);
    final updated =
        text.substring(0, start) + before + selected + after + text.substring(end);
    final cursorOffset =
        selected.isEmpty
            ? start + before.length
            : start + before.length + selected.length + after.length;
    _applyTextProgrammatically(
      updated,
      selection: TextSelection.collapsed(offset: cursorOffset),
    );
  }

  void _insertBlockSnippet(String snippet) {
    final text = _editorController.text;
    final selection = _editorController.selection;
    final start =
        selection.isValid
            ? selection.start.clamp(0, text.length)
            : text.length;
    final end =
        selection.isValid ? selection.end.clamp(0, text.length) : text.length;
    final needsLeadingNewline = start > 0 && text[start - 1] != '\n';
    final insertion = needsLeadingNewline ? '\n$snippet' : snippet;
    final updated =
        text.substring(0, start) + insertion + text.substring(end);
    _applyTextProgrammatically(
      updated,
      selection: TextSelection.collapsed(offset: start + insertion.length),
    );
  }

  void _setLocale(Locale? locale) {
    if (widget.onLocaleChanged != null) {
      widget.onLocaleChanged!(locale);
    }
    setState(() {
      _hasLocalLocaleOverride = widget.onLocaleChanged == null;
      _localLocaleOverride = locale;
    });
  }

  void _setThemeMode(ThemeMode mode) {
    if (widget.onThemeModeChanged != null) {
      widget.onThemeModeChanged!(mode);
    }
    setState(() {
      _localThemeOverride = mode;
    });
  }

  Future<void> _showLanguagePicker(BuildContext ctx) async {
    final l10n = AppLocalizations.of(ctx);
    final currentCode = _effectiveLocale?.languageCode;
    final selected = await showModalBottomSheet<String>(
      context: ctx,
      showDragHandle: true,
      builder: (sheetCtx) {
        return SafeArea(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(20, 4, 20, 8),
                child: Text(
                  l10n.language,
                  style: Theme.of(sheetCtx).textTheme.titleMedium,
                ),
              ),
              RadioGroup<String>(
                groupValue: currentCode ?? 'system',
                onChanged: (val) => Navigator.pop(sheetCtx, val),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    RadioListTile<String>(
                      value: 'system',
                      title: Text(l10n.languageSystem),
                    ),
                    RadioListTile<String>(
                      value: 'de',
                      title: Text(l10n.languageDe),
                    ),
                    RadioListTile<String>(
                      value: 'en',
                      title: Text(l10n.languageEn),
                    ),
                    RadioListTile<String>(
                      value: 'es',
                      title: Text(l10n.languageEs),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 8),
            ],
          ),
        );
      },
    );
    if (!mounted || selected == null) return;
    _setLocale(selected == 'system' ? null : Locale(selected));
  }

  Future<void> _showThemePicker(BuildContext ctx) async {
    final l10n = AppLocalizations.of(ctx);
    final selected = await showModalBottomSheet<ThemeMode>(
      context: ctx,
      showDragHandle: true,
      builder: (sheetCtx) {
        return SafeArea(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(20, 4, 20, 8),
                child: Text(
                  l10n.theme,
                  style: Theme.of(sheetCtx).textTheme.titleMedium,
                ),
              ),
              RadioGroup<ThemeMode>(
                groupValue: _effectiveThemeMode,
                onChanged: (val) => Navigator.pop(sheetCtx, val),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    RadioListTile<ThemeMode>(
                      value: ThemeMode.system,
                      title: Text(l10n.themeSystem),
                    ),
                    RadioListTile<ThemeMode>(
                      value: ThemeMode.light,
                      title: Text(l10n.themeLight),
                    ),
                    RadioListTile<ThemeMode>(
                      value: ThemeMode.dark,
                      title: Text(l10n.themeDark),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 8),
            ],
          ),
        );
      },
    );
    if (!mounted || selected == null) return;
    _setThemeMode(selected);
  }

  Future<void> _showCleanerPreview(BuildContext ctx) async {
    final l10n = AppLocalizations.of(ctx);
    final raw = _editorController.text;
    if (raw.isEmpty) return;
    final cleaned = MarkdownCleaner.stripMarkdown(raw);
    final rawStats = MarkdownCleaner.calculateStats(raw);
    final cleanStats = MarkdownCleaner.calculateStats(cleaned);

    await showModalBottomSheet<void>(
      context: ctx,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (sheetCtx) {
        final colorScheme = Theme.of(sheetCtx).colorScheme;
        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(20, 0, 20, 16),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  l10n.cleanerPreviewTitle,
                  style: Theme.of(sheetCtx).textTheme.titleMedium,
                ),
                const SizedBox(height: 4),
                Text(
                  '${l10n.statsWords(cleanStats.wordCount)} · '
                  '${l10n.statsChars(cleanStats.characterCount)} '
                  '(${rawStats.characterCount} → ${cleanStats.characterCount})',
                  style: Theme.of(sheetCtx).textTheme.bodySmall?.copyWith(
                    color: colorScheme.onSurfaceVariant,
                  ),
                ),
                const SizedBox(height: 12),
                ConstrainedBox(
                  constraints: const BoxConstraints(maxHeight: 260),
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: colorScheme.surfaceContainerLow,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: colorScheme.outlineVariant),
                    ),
                    child: SingleChildScrollView(
                      child: SelectableText(
                        cleaned.isEmpty ? l10n.cleanerNoChanges : cleaned,
                        style: Theme.of(sheetCtx).textTheme.bodyMedium,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  alignment: WrapAlignment.end,
                  children: [
                    OutlinedButton.icon(
                      style: OutlinedButton.styleFrom(
                        minimumSize: const Size(48, 48),
                      ),
                      icon: const Icon(Icons.copy),
                      label: Text(l10n.copyCleanText),
                      onPressed: () {
                        Navigator.pop(sheetCtx);
                        _copyText(ctx, cleaned, l10n.cleanTextCopied);
                      },
                    ),
                    FilledButton.icon(
                      style: FilledButton.styleFrom(
                        minimumSize: const Size(48, 48),
                      ),
                      icon: const Icon(Icons.format_clear),
                      label: Text(l10n.applyCleanText),
                      onPressed:
                          cleaned == raw
                              ? null
                              : () {
                                Navigator.pop(sheetCtx);
                                _clearFormatting(ctx);
                              },
                    ),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Future<void> _showFormatHelp(BuildContext ctx) async {
    final l10n = AppLocalizations.of(ctx);
    final templates = <({String label, String snippet})>[
      (label: l10n.formatH1, snippet: '# '),
      (label: l10n.formatH2, snippet: '## '),
      (label: l10n.formatBold, snippet: '**Text**'),
      (label: l10n.formatItalic, snippet: '*Text*'),
      (label: l10n.formatCode, snippet: '`code`'),
      (label: l10n.formatList, snippet: '- '),
      (label: l10n.formatQuote, snippet: '> '),
      (label: l10n.formatLink, snippet: '[Text](https://)'),
    ];

    await showModalBottomSheet<void>(
      context: ctx,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (sheetCtx) {
        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(20, 0, 20, 16),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  l10n.formatHelp,
                  style: Theme.of(sheetCtx).textTheme.titleMedium,
                ),
                const SizedBox(height: 4),
                Text(
                  l10n.formatHelpSubtitle,
                  style: Theme.of(sheetCtx).textTheme.bodySmall?.copyWith(
                    color: Theme.of(sheetCtx).colorScheme.onSurfaceVariant,
                  ),
                ),
                const SizedBox(height: 8),
                Flexible(
                  child: ListView.builder(
                    shrinkWrap: true,
                    itemCount: templates.length,
                    itemBuilder: (itemCtx, index) {
                      final entry = templates[index];
                      return ListTile(
                        minVerticalPadding: 10,
                        title: Text(entry.label),
                        trailing: Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color:
                                Theme.of(
                                  sheetCtx,
                                ).colorScheme.surfaceContainerHighest,
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            entry.snippet,
                            style: const TextStyle(fontFamily: 'monospace'),
                          ),
                        ),
                        onTap: () {
                          Navigator.pop(sheetCtx);
                          if (!_splitViewEnabled && _tabController.index != 1) {
                            _tabController.animateTo(1);
                          }
                          _insertBlockSnippet(entry.snippet);
                        },
                      );
                    },
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Localizations.override(
      context: context,
      locale: _hasLocalLocaleOverride ? _localLocaleOverride : null,
      child: Builder(builder: _buildScaffold),
    );
  }

  Widget _buildScaffold(BuildContext ctx) {
    final l10n = AppLocalizations.of(ctx);
    final theme = Theme.of(ctx);
    final colorScheme = theme.colorScheme;
    final screenWidth = MediaQuery.sizeOf(ctx).width;
    final canSplitView = screenWidth >= 720;
    final showSplitView = canSplitView && _splitViewEnabled;
    final showOpenInAppBar = screenWidth >= 420;
    final isPreviewTab = !showSplitView && _tabController.index == 0;

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              l10n.appTitle,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            Text(
              _currentFileName ?? l10n.newDocument,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: theme.textTheme.labelMedium?.copyWith(
                color: colorScheme.onSurfaceVariant,
              ),
            ),
          ],
        ),
        actions: [
          if (canSplitView)
            Semantics(
              button: true,
              label: l10n.splitViewTooltip,
              child: IconButton(
                constraints: const BoxConstraints(minWidth: 48, minHeight: 48),
                icon: Icon(
                  _splitViewEnabled
                      ? Icons.view_agenda_outlined
                      : Icons.vertical_split_outlined,
                ),
                tooltip: l10n.splitViewTooltip,
                onPressed: () {
                  setState(() {
                    _splitViewEnabled = !_splitViewEnabled;
                  });
                },
              ),
            ),
          Semantics(
            button: true,
            label: l10n.newFile,
            child: IconButton(
              constraints: const BoxConstraints(minWidth: 48, minHeight: 48),
              icon: const Icon(Icons.note_add),
              tooltip: l10n.newFile,
              onPressed: _isBusy ? null : () => _newFile(ctx),
            ),
          ),
          if (showOpenInAppBar)
            Semantics(
              button: true,
              label: l10n.openFile,
              child: IconButton(
                constraints: const BoxConstraints(minWidth: 48, minHeight: 48),
                icon: const Icon(Icons.folder_open),
                tooltip: l10n.openFile,
                onPressed: _isBusy ? null : () => _pickFile(ctx),
              ),
            ),
          Semantics(
            button: true,
            label: l10n.shareFile,
            child: IconButton(
              constraints: const BoxConstraints(minWidth: 48, minHeight: 48),
              icon: const Icon(Icons.share),
              tooltip: l10n.shareFile,
              onPressed:
                  _isBusy || _editorController.text.isEmpty
                      ? null
                      : () => _shareFile(ctx),
            ),
          ),
          Semantics(
            button: true,
            label: l10n.saveFile,
            child: IconButton(
              constraints: const BoxConstraints(minWidth: 48, minHeight: 48),
              icon: const Icon(Icons.save),
              tooltip: l10n.saveFile,
              onPressed: _isBusy ? null : () => _saveFile(ctx),
            ),
          ),
          Semantics(
            button: true,
            label: l10n.moreOptions,
            child: PopupMenuButton<String>(
              icon: const Icon(Icons.more_vert),
              tooltip: l10n.moreOptions,
              enabled: !_isBusy,
              onSelected: (action) {
                switch (action) {
                  case 'open_file':
                    _pickFile(ctx);
                  case 'copy_markdown':
                    _copyText(ctx, _editorController.text, l10n.copiedSuccess);
                  case 'copy_clean':
                    _copyText(
                      ctx,
                      MarkdownCleaner.stripMarkdown(_editorController.text),
                      l10n.cleanTextCopied,
                    );
                  case 'cleaner_preview':
                    _showCleanerPreview(ctx);
                  case 'clear_formatting':
                    _clearFormatting(ctx);
                  case 'export_session':
                    _exportSession(ctx);
                  case 'format_help':
                    _showFormatHelp(ctx);
                  case 'language':
                    _showLanguagePicker(ctx);
                  case 'theme':
                    _showThemePicker(ctx);
                }
              },
              itemBuilder: (menuCtx) {
                final hasText = _editorController.text.isNotEmpty;
                return [
                  if (!showOpenInAppBar)
                    PopupMenuItem(
                      value: 'open_file',
                      child: _buildMenuRow(Icons.folder_open, l10n.openFile),
                    ),
                  PopupMenuItem(
                    value: 'copy_markdown',
                    enabled: hasText,
                    child: _buildMenuRow(Icons.copy, l10n.copyMarkdown),
                  ),
                  PopupMenuItem(
                    value: 'copy_clean',
                    enabled: hasText,
                    child: _buildMenuRow(Icons.content_copy, l10n.copyCleanText),
                  ),
                  PopupMenuItem(
                    value: 'cleaner_preview',
                    enabled: hasText,
                    child: _buildMenuRow(
                      Icons.cleaning_services_outlined,
                      l10n.cleanerPreviewTitle,
                    ),
                  ),
                  PopupMenuItem(
                    value: 'clear_formatting',
                    enabled: hasText,
                    child: _buildMenuRow(
                      Icons.format_clear,
                      l10n.clearFormatting,
                    ),
                  ),
                  PopupMenuItem(
                    value: 'export_session',
                    enabled: hasText,
                    child: _buildMenuRow(
                      Icons.import_export,
                      l10n.exportSession,
                    ),
                  ),
                  const PopupMenuDivider(),
                  PopupMenuItem(
                    value: 'format_help',
                    child: _buildMenuRow(Icons.help_outline, l10n.formatHelp),
                  ),
                  PopupMenuItem(
                    value: 'language',
                    child: _buildMenuRow(Icons.language, l10n.language),
                  ),
                  PopupMenuItem(
                    value: 'theme',
                    child: _buildMenuRow(Icons.brightness_6_outlined, l10n.theme),
                  ),
                ];
              },
            ),
          ),
        ],
        bottom:
            showSplitView
                ? null
                : TabBar(
                  controller: _tabController,
                  tabs: [
                    Tab(
                      icon: const Icon(Icons.visibility_outlined),
                      text: l10n.previewTab,
                    ),
                    Tab(
                      icon: const Icon(Icons.edit_outlined),
                      text: l10n.editorTab,
                    ),
                  ],
                ),
      ),
      body: Column(
        children: [
          if (_isBusy) const LinearProgressIndicator(minHeight: 2),
          if (_hasUnsavedChanges)
            Semantics(
              liveRegion: true,
              container: true,
              child: Material(
                color: colorScheme.secondaryContainer,
                child: ListTile(
                  dense: true,
                  leading: Icon(
                    Icons.edit_note,
                    color: colorScheme.onSecondaryContainer,
                  ),
                  title: Text(
                    l10n.unsavedChanges,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: colorScheme.onSecondaryContainer,
                    ),
                  ),
                  trailing: TextButton(
                    style: TextButton.styleFrom(
                      minimumSize: const Size(48, 48),
                    ),
                    onPressed: _isBusy ? null : () => _saveFile(ctx),
                    child: Text(l10n.saveFile),
                  ),
                ),
              ),
            ),
          Expanded(
            child:
                showSplitView
                    ? Row(
                      children: [
                        Expanded(child: _buildEditor(ctx, l10n)),
                        VerticalDivider(
                          width: 1,
                          color: colorScheme.outlineVariant,
                        ),
                        Expanded(child: _buildPreview(ctx, l10n)),
                      ],
                    )
                    : TabBarView(
                      controller: _tabController,
                      children: [
                        _buildPreview(ctx, l10n),
                        _buildEditor(ctx, l10n),
                      ],
                    ),
          ),
          _buildStatsBar(ctx, l10n),
        ],
      ),
      floatingActionButton:
          isPreviewTab
              ? Semantics(
                button: true,
                label: l10n.openFile,
                child: FloatingActionButton.extended(
                  onPressed: _isBusy ? null : () => _pickFile(ctx),
                  icon: const Icon(Icons.folder_open),
                  label: Text(l10n.openFile),
                ),
              )
              : null,
    );
  }

  Widget _buildMenuRow(IconData icon, String label) {
    return Row(
      children: [
        Icon(icon, size: 20),
        const SizedBox(width: 12),
        Flexible(child: Text(label)),
      ],
    );
  }

  Widget _buildStatsBar(BuildContext ctx, AppLocalizations l10n) {
    final theme = Theme.of(ctx);
    final colorScheme = theme.colorScheme;

    return ValueListenableBuilder<TextEditingValue>(
      valueListenable: _editorController,
      builder: (context, value, _) {
        final stats = MarkdownCleaner.calculateStats(value.text);
        final wordsText = l10n.statsWords(stats.wordCount);
        final charsText = l10n.statsChars(stats.characterCount);
        final readingText = l10n.statsReading(stats.readingTimeMinutes);
        final noSpacesText = l10n.statsCharsNoSpaces(
          stats.characterCountNoSpaces,
        );

        return Semantics(
          container: true,
          label:
              '${l10n.statsLabel}: $wordsText, $charsText, $noSpacesText, $readingText',
          child: Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: BoxDecoration(
              color: colorScheme.surfaceContainerLow,
              border: Border(
                top: BorderSide(color: colorScheme.outlineVariant),
              ),
            ),
            child: Wrap(
              spacing: 12,
              runSpacing: 4,
              alignment: WrapAlignment.spaceBetween,
              crossAxisAlignment: WrapCrossAlignment.center,
              children: [
                Tooltip(
                  message: noSpacesText,
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        Icons.analytics_outlined,
                        size: 16,
                        color: colorScheme.onSurfaceVariant,
                      ),
                      const SizedBox(width: 6),
                      Flexible(
                        child: Text(
                          '$wordsText  •  $charsText',
                          softWrap: true,
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: colorScheme.onSurfaceVariant,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                Text(
                  readingText,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: colorScheme.onSurfaceVariant,
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildPreview(BuildContext ctx, AppLocalizations l10n) {
    final theme = Theme.of(ctx);
    final colorScheme = theme.colorScheme;

    if (_hasError) {
      return Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(24, 24, 24, 88),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                Icons.error_outline,
                size: 40,
                color: colorScheme.error,
              ),
              const SizedBox(height: 12),
              Text(
                l10n.errorReadingFile,
                textAlign: TextAlign.center,
                style: theme.textTheme.bodyLarge?.copyWith(
                  color: colorScheme.onSurface,
                ),
              ),
            ],
          ),
        ),
      );
    }

    if (_editorController.text.isEmpty) {
      final hasOpenFile = _currentFilePath != null || _currentFileName != null;
      return Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(24, 24, 24, 88),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                Icons.description_outlined,
                size: 48,
                color: colorScheme.primary,
              ),
              const SizedBox(height: 16),
              Text(
                hasOpenFile ? l10n.emptyPreview : l10n.noFileOpen,
                textAlign: TextAlign.center,
                style: theme.textTheme.bodyLarge?.copyWith(
                  color: colorScheme.onSurface,
                ),
              ),
              const SizedBox(height: 20),
              Wrap(
                spacing: 12,
                runSpacing: 8,
                alignment: WrapAlignment.center,
                children: [
                  OutlinedButton.icon(
                    style: OutlinedButton.styleFrom(
                      minimumSize: const Size(48, 48),
                    ),
                    onPressed:
                        _isBusy
                            ? null
                            : () {
                              if (!_splitViewEnabled) {
                                _tabController.animateTo(1);
                              }
                            },
                    icon: const Icon(Icons.edit_outlined),
                    label: Text(l10n.startWriting),
                  ),
                ],
              ),
            ],
          ),
        ),
      );
    }

    final baseStyleSheet = MarkdownStyleSheet.fromTheme(theme);
    final styleSheet = baseStyleSheet.copyWith(
      p: theme.textTheme.bodyLarge?.copyWith(
        height: 1.55,
        color: colorScheme.onSurface,
      ),
      code: theme.textTheme.bodyMedium?.copyWith(
        fontFamily: 'monospace',
        backgroundColor: colorScheme.surfaceContainerHighest,
        color: colorScheme.onSurface,
      ),
      codeblockDecoration: BoxDecoration(
        color: colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: colorScheme.outlineVariant),
      ),
      blockquoteDecoration: BoxDecoration(
        color: colorScheme.surfaceContainerLow,
        border: Border(
          left: BorderSide(color: colorScheme.primary, width: 4),
        ),
      ),
      horizontalRuleDecoration: BoxDecoration(
        border: Border(
          top: BorderSide(color: colorScheme.outlineVariant, width: 1),
        ),
      ),
      tableBorder: TableBorder.all(color: colorScheme.outlineVariant),
    );

    return Markdown(
      controller: _previewScrollController,
      data: _editorController.text,
      selectable: true,
      styleSheet: styleSheet,
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 88),
      onTapLink: (text, href, title) {
        if (href == null || href.isEmpty) return;
        _copyText(ctx, href, '${l10n.linkCopiedPrefix}: $href');
      },
    );
  }

  Widget _buildEditor(BuildContext ctx, AppLocalizations l10n) {
    final theme = Theme.of(ctx);
    final colorScheme = theme.colorScheme;

    return Column(
      children: [
        _buildFormattingToolbar(ctx, l10n, colorScheme),
        Expanded(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
            child: TextField(
              controller: _editorController,
              scrollController: _editorScrollController,
              expands: true,
              maxLines: null,
              minLines: null,
              keyboardType: TextInputType.multiline,
              textCapitalization: TextCapitalization.none,
              textAlignVertical: TextAlignVertical.top,
              autocorrect: false,
              enableSuggestions: false,
              smartDashesType: SmartDashesType.disabled,
              smartQuotesType: SmartQuotesType.disabled,
              style: theme.textTheme.bodyLarge?.copyWith(
                fontFamily: 'monospace',
                height: 1.5,
              ),
              decoration: InputDecoration(
                border: const OutlineInputBorder(),
                hintText: l10n.editorHint,
                alignLabelWithHint: true,
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildFormattingToolbar(
    BuildContext ctx,
    AppLocalizations l10n,
    ColorScheme colorScheme,
  ) {
    return Material(
      color: colorScheme.surfaceContainerLow,
      child: Container(
        decoration: BoxDecoration(
          border: Border(
            bottom: BorderSide(color: colorScheme.outlineVariant),
          ),
        ),
        child: SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          child: Row(
            children: [
              _ToolbarIconButton(
                icon: Icons.undo,
                tooltip: l10n.undo,
                onPressed: _undoStack.isEmpty ? null : _undo,
              ),
              _ToolbarIconButton(
                icon: Icons.redo,
                tooltip: l10n.redo,
                onPressed: _redoStack.isEmpty ? null : _redo,
              ),
              const SizedBox(width: 4),
              _ToolbarTextButton(
                label: 'H1',
                tooltip: l10n.formatH1,
                onPressed: () => _insertLinePrefix('# '),
              ),
              _ToolbarTextButton(
                label: 'H2',
                tooltip: l10n.formatH2,
                onPressed: () => _insertLinePrefix('## '),
              ),
              _ToolbarIconButton(
                icon: Icons.format_bold,
                tooltip: l10n.formatBold,
                onPressed: () => _wrapSelection('**', '**'),
              ),
              _ToolbarIconButton(
                icon: Icons.format_italic,
                tooltip: l10n.formatItalic,
                onPressed: () => _wrapSelection('*', '*'),
              ),
              _ToolbarIconButton(
                icon: Icons.code,
                tooltip: l10n.formatCode,
                onPressed: () => _wrapSelection('`', '`'),
              ),
              _ToolbarIconButton(
                icon: Icons.format_list_bulleted,
                tooltip: l10n.formatList,
                onPressed: () => _insertLinePrefix('- '),
              ),
              _ToolbarIconButton(
                icon: Icons.format_quote,
                tooltip: l10n.formatQuote,
                onPressed: () => _insertLinePrefix('> '),
              ),
              _ToolbarIconButton(
                icon: Icons.link,
                tooltip: l10n.formatLink,
                onPressed: () => _wrapSelection('[', '](https://)'),
              ),
              _ToolbarIconButton(
                icon: Icons.cleaning_services_outlined,
                tooltip: l10n.cleanerPreviewTitle,
                onPressed:
                    _editorController.text.isEmpty
                        ? null
                        : () => _showCleanerPreview(ctx),
              ),
              _ToolbarIconButton(
                icon: Icons.help_outline,
                tooltip: l10n.formatHelp,
                onPressed: () => _showFormatHelp(ctx),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ToolbarIconButton extends StatelessWidget {
  final IconData icon;
  final String tooltip;
  final VoidCallback? onPressed;

  const _ToolbarIconButton({
    required this.icon,
    required this.tooltip,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      label: tooltip,
      enabled: onPressed != null,
      child: IconButton(
        constraints: const BoxConstraints(minWidth: 48, minHeight: 48),
        icon: Icon(icon, size: 20),
        tooltip: tooltip,
        onPressed: onPressed,
      ),
    );
  }
}

class _ToolbarTextButton extends StatelessWidget {
  final String label;
  final String tooltip;
  final VoidCallback onPressed;

  const _ToolbarTextButton({
    required this.label,
    required this.tooltip,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      label: tooltip,
      child: Tooltip(
        message: tooltip,
        child: TextButton(
          style: TextButton.styleFrom(
            minimumSize: const Size(48, 48),
            padding: const EdgeInsets.symmetric(horizontal: 10),
          ),
          onPressed: onPressed,
          child: Text(
            label,
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
        ),
      ),
    );
  }
}
