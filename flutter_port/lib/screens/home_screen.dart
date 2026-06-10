import 'dart:io';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import '../l10n/app_localizations.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  String? _content;
  bool _hasError = false;

  Future<void> _pickFile() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['md', 'markdown', 'txt'],
    );
    if (!mounted) return;
    if (result == null || result.files.single.path == null) return;

    try {
      final text = await File(result.files.single.path!).readAsString();
      if (!mounted) return;
      setState(() {
        _content = text;
        _hasError = false;
      });
    } catch (e, stackTrace) {
      debugPrint('CleanMarkdown: Fehler beim Lesen der Datei: $e\n$stackTrace');
      if (!mounted) return;
      setState(() {
        _hasError = true;
        _content = null;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.appTitle),
        actions: [
          IconButton(
            icon: const Icon(Icons.folder_open),
            tooltip: l10n.openFile,
            onPressed: _pickFile,
          ),
        ],
      ),
      body: _buildBody(l10n),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _pickFile,
        icon: const Icon(Icons.folder_open),
        label: Text(l10n.openFile),
      ),
    );
  }

  Widget _buildBody(AppLocalizations l10n) {
    if (_hasError) {
      return Center(child: Text(l10n.errorReadingFile));
    }
    if (_content == null) {
      return Center(
        child: Text(
          l10n.noFileOpen,
          textAlign: TextAlign.center,
          style: Theme.of(context).textTheme.bodyLarge,
        ),
      );
    }
    return Markdown(data: _content!);
  }
}
