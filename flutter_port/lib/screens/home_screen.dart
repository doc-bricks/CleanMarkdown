import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:share_plus/share_plus.dart';

import '../l10n/app_localizations.dart';
import '../models/session_format.dart';
import '../utils/markdown_cleaner.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late final TextEditingController _editorController;
  String _lastSavedContent = '';
  String? _currentFilePath;
  String? _currentFileName;
  bool _hasError = false;
  bool _hasUnsavedChanges = false;
  bool _isBusy = false;

  bool get _isMobilePlatform => Platform.isAndroid || Platform.isIOS;

  @override
  void initState() {
    super.initState();
    _editorController = TextEditingController();
    _editorController.addListener(_handleEditorChanged);
  }

  @override
  void dispose() {
    _editorController
      ..removeListener(_handleEditorChanged)
      ..dispose();
    super.dispose();
  }

  void _handleEditorChanged() {
    if (!mounted) {
      return;
    }
    final hasUnsavedChanges = _editorController.text != _lastSavedContent;
    if (_hasUnsavedChanges == hasUnsavedChanges) {
      setState(() {});
      return;
    }
    setState(() {
      _hasUnsavedChanges = hasUnsavedChanges;
    });
  }

  Future<void> _pickFile() async {
    setState(() {
      _isBusy = true;
    });

    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['md', 'markdown', 'txt', 'json'],
    );

    if (!mounted) return;
    // .first statt .single: leere files-Liste (result != null) wirft sonst StateError.
    if (result == null ||
        result.files.isEmpty ||
        result.files.first.path == null) {
      setState(() {
        _isBusy = false;
      });
      return;
    }

    try {
      final text = await File(result.files.first.path!).readAsString();
      if (!mounted) return;

      String loadedContent = text;
      String? fileName = result.files.first.name;

      if (CleanMarkdownSession.isSessionJson(text)) {
        try {
          final session = CleanMarkdownSession.fromJsonString(text);
          loadedContent = session.markdown;
          fileName = session.fileName;
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text('${AppLocalizations.of(context).sessionImported}: $fileName')),
            );
          }
        } catch (_) {
          // Fallback zu normalem Text
        }
      }

      _lastSavedContent = loadedContent;
      _editorController.text = loadedContent;
      setState(() {
        _hasError = false;
        _hasUnsavedChanges = false;
        _currentFilePath = result.files.first.path;
        _currentFileName = fileName;
        _isBusy = false;
      });
    } catch (e, stackTrace) {
      debugPrint('CleanMarkdown: Fehler beim Lesen der Datei: $e\n$stackTrace');
      if (!mounted) {
        return;
      }
      setState(() {
        _hasError = true;
        _isBusy = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(AppLocalizations.of(context).errorReadingFile)),
      );
    }
  }

  Future<void> _saveFile() async {
    final l10n = AppLocalizations.of(context);
    final text = _editorController.text;
    final bytes = Uint8List.fromList(utf8.encode(text));
    final fallbackFileName = _currentFileName ?? 'cleanmarkdown.md';

    setState(() {
      _isBusy = true;
    });

    try {
      String? savedPath = _currentFilePath;
      if (savedPath != null && !_isMobilePlatform) {
        await File(savedPath).writeAsString(text);
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
          setState(() {
            _isBusy = false;
          });
          return;
        }
        if (!_isMobilePlatform) {
          await File(savedPath).writeAsString(text);
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
        _isBusy = false;
      });
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(l10n.saveSuccess)));
    } catch (e, stackTrace) {
      debugPrint(
        'CleanMarkdown: Fehler beim Speichern der Datei: $e\n$stackTrace',
      );
      if (!mounted) {
        return;
      }
      setState(() {
        _isBusy = false;
      });
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(l10n.errorSavingFile)));
    }
  }

  Future<void> _exportSession() async {
    final l10n = AppLocalizations.of(context);
    final text = _editorController.text;
    final baseName = (_currentFileName ?? 'document.md').replaceAll(RegExp(r'\.(md|markdown|txt)$'), '');
    final fallbackFileName = '$baseName.session.json';

    final session = CleanMarkdownSession(
      fileName: _currentFileName ?? 'document.md',
      markdown: text,
      theme: 'paper',
      workspace: 'editor',
      updatedAt: DateTime.now().toIso8601String(),
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
        await File(savedPath).writeAsString(sessionJson);
      }
      if (!mounted) return;
      setState(() {
        _isBusy = false;
      });
      if (savedPath != null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.sessionExportSuccess)),
        );
      }
    } catch (e, stackTrace) {
      debugPrint('CleanMarkdown: Fehler beim Session-Export: $e\n$stackTrace');
      if (!mounted) return;
      setState(() {
        _isBusy = false;
      });
    }
  }

  void _clearFormatting() {
    final text = _editorController.text;
    if (text.isEmpty) return;
    final stripped = MarkdownCleaner.stripMarkdown(text);
    _editorController.text = stripped;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(AppLocalizations.of(context).clearFormattingSuccess)),
    );
  }

  String? _extractFileName(String? path) {
    if (path == null || path.isEmpty) {
      return null;
    }
    try {
      final segments = File(path).uri.pathSegments;
      if (segments.isNotEmpty) {
        return segments.last;
      }
    } catch (_) {
      // Fallback below.
    }
    return path.split(Platform.pathSeparator).last;
  }

  Future<void> _newFile() async {
    if (_hasUnsavedChanges) {
      final l10n = AppLocalizations.of(context);
      final confirmed = await showDialog<bool>(
        context: context,
        builder: (ctx) => AlertDialog(
          title: Text(l10n.newFileDiscardTitle),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: Text(l10n.newFileDiscardCancel),
            ),
            TextButton(
              onPressed: () => Navigator.pop(ctx, true),
              child: Text(l10n.newFileDiscardConfirm),
            ),
          ],
        ),
      );
      if (!mounted || confirmed != true) return;
    }
    _lastSavedContent = '';
    _editorController.text = '';
    setState(() {
      _currentFilePath = null;
      _currentFileName = null;
      _hasError = false;
      _hasUnsavedChanges = false;
    });
  }

  Future<void> _shareFile() async {
    final text = _editorController.text;
    if (text.isEmpty) return;

    setState(() {
      _isBusy = true;
    });
    try {
      final fileName = _currentFileName ?? 'cleanmarkdown.md';
      final tmpFile = File(
        '${Directory.systemTemp.path}/${DateTime.now().millisecondsSinceEpoch}_$fileName',
      );
      await tmpFile.writeAsString(text, encoding: utf8);
      if (!mounted) return;
      await Share.shareXFiles(
        [XFile(tmpFile.path, mimeType: 'text/markdown')],
        subject: fileName,
      );
      try {
        await tmpFile.delete();
      } catch (_) {}
    } catch (e, stackTrace) {
      debugPrint('CleanMarkdown: Fehler beim Teilen: $e\n$stackTrace');
    } finally {
      if (mounted) {
        setState(() {
          _isBusy = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    return DefaultTabController(
      length: 2,
      child: Scaffold(
        appBar: AppBar(
          title: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(l10n.appTitle),
              Text(
                _currentFileName ?? l10n.newDocument,
                style: Theme.of(context).textTheme.labelMedium,
              ),
            ],
          ),
          actions: [
            IconButton(
              icon: const Icon(Icons.note_add),
              tooltip: l10n.newFile,
              onPressed: _isBusy ? null : _newFile,
            ),
            IconButton(
              icon: const Icon(Icons.folder_open),
              tooltip: l10n.openFile,
              onPressed: _isBusy ? null : _pickFile,
            ),
            IconButton(
              icon: const Icon(Icons.share),
              tooltip: l10n.shareFile,
              onPressed:
                  _isBusy || _editorController.text.isEmpty
                      ? null
                      : _shareFile,
            ),
            IconButton(
              icon: const Icon(Icons.save),
              tooltip: l10n.saveFile,
              onPressed: _isBusy ? null : _saveFile,
            ),
            PopupMenuButton<String>(
              icon: const Icon(Icons.more_vert),
              enabled: !_isBusy,
              onSelected: (action) {
                if (action == 'clear_formatting') {
                  _clearFormatting();
                } else if (action == 'export_session') {
                  _exportSession();
                }
              },
              itemBuilder: (ctx) => [
                PopupMenuItem(
                  value: 'clear_formatting',
                  enabled: _editorController.text.isNotEmpty,
                  child: Row(
                    children: [
                      const Icon(Icons.format_clear, size: 20),
                      const SizedBox(width: 12),
                      Text(l10n.clearFormatting),
                    ],
                  ),
                ),
                PopupMenuItem(
                  value: 'export_session',
                  enabled: _editorController.text.isNotEmpty,
                  child: Row(
                    children: [
                      const Icon(Icons.import_export, size: 20),
                      const SizedBox(width: 12),
                      Text(l10n.exportSession),
                    ],
                  ),
                ),
              ],
            ),
          ],
          bottom: TabBar(
            tabs: [
              Tab(text: l10n.previewTab),
              Tab(text: l10n.editorTab),
            ],
          ),
        ),
        body: Column(
          children: [
            if (_hasUnsavedChanges)
              Material(
                color: Theme.of(context).colorScheme.surfaceContainerHighest,
                child: ListTile(
                  dense: true,
                  leading: const Icon(Icons.edit_note),
                  title: Text(l10n.unsavedChanges),
                ),
              ),
            Expanded(
              child: TabBarView(
                children: [_buildPreview(l10n), _buildEditor(l10n)],
              ),
            ),
            _buildStatsBar(l10n),
          ],
        ),
        floatingActionButton: FloatingActionButton.extended(
          onPressed: _isBusy ? null : _pickFile,
          icon: const Icon(Icons.folder_open),
          label: Text(l10n.openFile),
        ),
      ),
    );
  }

  Widget _buildStatsBar(AppLocalizations l10n) {
    final text = _editorController.text;
    if (text.isEmpty) return const SizedBox.shrink();
    final stats = MarkdownCleaner.calculateStats(text);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceContainerLow,
        border: Border(
          top: BorderSide(
            color: Theme.of(context).dividerColor.withValues(alpha: 0.2),
          ),
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              Icon(
                Icons.analytics_outlined,
                size: 14,
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
              const SizedBox(width: 6),
              Text(
                '${l10n.statsWords(stats.wordCount)}  •  ${l10n.statsChars(stats.characterCount)}',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                ),
              ),
            ],
          ),
          Text(
            l10n.statsReading(stats.readingTimeMinutes),
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: Theme.of(context).colorScheme.onSurfaceVariant,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPreview(AppLocalizations l10n) {
    if (_hasError) {
      return Center(child: Text(l10n.errorReadingFile));
    }
    if (_editorController.text.isEmpty) {
      return Center(
        child: Text(
          _currentFilePath == null ? l10n.noFileOpen : l10n.emptyPreview,
          textAlign: TextAlign.center,
          style: Theme.of(context).textTheme.bodyLarge,
        ),
      );
    }
    return Markdown(
      data: _editorController.text,
      padding: const EdgeInsets.all(16),
    );
  }

  Widget _buildEditor(AppLocalizations l10n) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: TextField(
        controller: _editorController,
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
        decoration: InputDecoration(
          border: const OutlineInputBorder(),
          hintText: l10n.editorHint,
          alignLabelWithHint: true,
        ),
      ),
    );
  }
}
