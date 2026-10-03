/**
 * CleanMarkdown Web Companion & PWA Engine
 * Zero-Egress, Offline-First, Local Markdown Processing
 * Implements Session Format: cleanmarkdown-session-v1.json
 */

(function () {
  'use strict';

  const APP_VERSION = '1.0.5';
  const SESSION_VERSION = 'cleanmarkdown-session-v1';

  // Localization Dictionary (DE, EN, ES)
  const I18N = {
    de: {
      app_title: 'CleanMarkdown',
      view_mode: 'Lesemodus',
      edit_mode: 'Editor',
      open_file: 'Öffnen',
      save_md: 'Speichern (.md)',
      export_session: 'Session exportieren',
      import_session: 'Session laden',
      clear_formatting: 'Formatierung entfernen',
      copy_clean: 'Reinen Text kopieren',
      toggle_theme: 'Design wechseln',
      status_words: 'Wörter',
      status_chars: 'Zeichen',
      status_chars_no_space: 'ohne Leerzeichen',
      status_read_time: 'Min. Lesezeit',
      status_offline: '100% Offline (Zero-Egress)',
      notice_copied: 'Reiner Text in die Zwischenablage kopiert!',
      notice_exported: 'Session-Datei erfolgreich exportiert.',
      notice_saved: 'Markdown-Datei heruntergeladen.',
      notice_loaded: 'Datei erfolgreich geladen.',
      notice_cleared: 'Formatierung entfernt.',
      error_invalid_session: 'Fehler: Ungültiges Session-Format (cleanmarkdown-session-v1 erforderlich).',
      error_file_read: 'Fehler beim Lesen der Datei.',
      placeholder_editor: 'Hier Markdown-Text eingeben oder Datei hineinziehen...',
      untitled_doc: 'dokument.md'
    },
    en: {
      app_title: 'CleanMarkdown',
      view_mode: 'Reading Mode',
      edit_mode: 'Editor',
      open_file: 'Open',
      save_md: 'Save (.md)',
      export_session: 'Export Session',
      import_session: 'Load Session',
      clear_formatting: 'Clear Formatting',
      copy_clean: 'Copy Clean Text',
      toggle_theme: 'Toggle Theme',
      status_words: 'Words',
      status_chars: 'Characters',
      status_chars_no_space: 'no spaces',
      status_read_time: 'min read',
      status_offline: '100% Offline (Zero-Egress)',
      notice_copied: 'Clean text copied to clipboard!',
      notice_exported: 'Session file exported successfully.',
      notice_saved: 'Markdown file downloaded.',
      notice_loaded: 'File loaded successfully.',
      notice_cleared: 'Formatting cleared.',
      error_invalid_session: 'Error: Invalid session format (cleanmarkdown-session-v1 required).',
      error_file_read: 'Error reading file.',
      placeholder_editor: 'Type Markdown text here or drag & drop a file...',
      untitled_doc: 'document.md'
    },
    es: {
      app_title: 'CleanMarkdown',
      view_mode: 'Modo lectura',
      edit_mode: 'Editor',
      open_file: 'Abrir',
      save_md: 'Guardar (.md)',
      export_session: 'Exportar sesión',
      import_session: 'Cargar sesión',
      clear_formatting: 'Quitar formato',
      copy_clean: 'Copiar texto limpio',
      toggle_theme: 'Cambiar tema',
      status_words: 'Palabras',
      status_chars: 'Caracteres',
      status_chars_no_space: 'sin espacios',
      status_read_time: 'min de lectura',
      status_offline: '100% Sin conexión (Zero-Egress)',
      notice_copied: '¡Texto limpio copiado al portapapeles!',
      notice_exported: 'Archivo de sesión exportado con éxito.',
      notice_saved: 'Archivo Markdown descargado.',
      notice_loaded: 'Archivo cargado con éxito.',
      notice_cleared: 'Formato eliminado.',
      error_invalid_session: 'Error: Formato de sesión inválido (requiere cleanmarkdown-session-v1).',
      error_file_read: 'Error al leer el archivo.',
      placeholder_editor: 'Escriba texto Markdown aquí o arrastre un archivo...',
      untitled_doc: 'documento.md'
    }
  };

  // State
  let currentLang = localStorage.getItem('cm_lang') || 'de';
  let currentTheme = localStorage.getItem('cm_theme') || 'paper';
  let currentMode = 'editor'; // 'view' or 'editor'
  let currentFileName = 'notiz.md';

  // DOM Elements
  const elTheme = document.documentElement;
  const editorInput = document.getElementById('markdown-editor');
  const previewContainer = document.getElementById('preview-content');
  const fileNameInput = document.getElementById('file-name-input');
  const langSelect = document.getElementById('lang-select');
  const themeToggleBtn = document.getElementById('btn-toggle-theme');
  const tabViewBtn = document.getElementById('tab-view');
  const tabEditBtn = document.getElementById('tab-editor');
  const paneView = document.getElementById('preview-pane');
  const paneEdit = document.getElementById('editor-pane');
  const fileInput = document.getElementById('file-input');
  const toast = document.getElementById('toast-notice');

  // Stat Elements
  const statWords = document.getElementById('stat-words');
  const statChars = document.getElementById('stat-chars');
  const statCharsNoSpaces = document.getElementById('stat-chars-nospace');
  const statReadingTime = document.getElementById('stat-reading-time');

  // -------------------------------------------------------------
  // Markdown Cleaning Logic (Parity with Desktop & Flutter Port)
  // -------------------------------------------------------------
  function stripMarkdown(markdown) {
    if (!markdown) return '';

    let text = markdown.replace(/\r\n/g, '\n').replace(/\r/g, '\n');

    // Remove horizontal rules
    text = text.replace(/(^|\n)\s*([-*_]\s*){3,}\s*(\n|$)/g, '\n');

    // Code blocks: keep inner content
    text = text.replace(/```[a-zA-Z0-9_-]*\n([\s\S]*?)\n```/g, '$1');

    // Images: ![alt](url) -> alt
    text = text.replace(/!\[([^\]]*)\]\([^)]*\)/g, '$1');

    // Links: [text](url) -> text
    text = text.replace(/\[([^\]]+)\]\([^)]*\)/g, '$1');

    // Autolinks: <url> -> url
    text = text.replace(/<((?:https?|ftp|mailto):[^>]+)>/g, '$1');

    // Bold + Italic: ***text*** or ___text___ -> text
    text = text.replace(/(\*{3}|_{3})(.*?)\1/g, '$2');

    // Bold: **text** or __text__ -> text
    text = text.replace(/(\*{2}|_{2})(.*?)\1/g, '$2');

    // Italic: *text* or _text_ -> text
    text = text.replace(/(\*{1}|_{1})(.*?)\1/g, '$2');

    // Strikethrough: ~~text~~ -> text
    text = text.replace(/~~(.*?)~~/g, '$1');

    // Inline code: `code` -> code
    text = text.replace(/`([^`]+)`/g, '$1');

    // Math blocks & inline math
    text = text.replace(/\$\$(.+?)\$\$/gs, '$1');
    text = text.replace(/\\\[(.+?)\\\]/gs, '$1');
    text = text.replace(/\\\((.+?)\\\)/gs, '$1');
    text = text.replace(/(?<!\\)\$(?!\$)(.+?)(?<!\\)\$(?!\$)/gs, '$1');

    // Footnotes
    text = text.replace(/\[\^[^\]]+\]/g, '');

    // Line-by-line rules (headings, quotes, lists)
    const lines = text.split('\n');
    const cleaned = [];

    for (let line of lines) {
      // Table rows: | col | col | -> col col
      if (/^\s*\|.*\|\s*$/.test(line)) {
        if (/^\s*\|[-:\s|]+\|\s*$/.test(line)) {
          continue; // skip table separator
        }
        const cells = line.split('|').map(c => c.trim()).filter(c => c.length > 0);
        line = cells.join(' ');
      }

      // ATX Headings: # Heading -> Heading
      line = line.replace(/^\s{0,3}#{1,6}\s+/, '');

      // Blockquotes: > text -> text
      line = line.replace(/^\s{0,3}>\s?/, '');

      // Unordered list bullets & Task lists: - [ ] item -> item
      line = line.replace(/^\s{0,3}(?:[-+*]|\d+[.)])\s+(?:\[[ xX]\]\s+)?/, '');

      // Footnote definitions: [^1]: text -> text
      line = line.replace(/^\s{0,3}\[\^[^\]]+\]:\s*/, '');

      cleaned.push(line);
    }

    let result = cleaned.join('\n');
    // Normalize excessive empty lines
    result = result.replace(/[ \t]+\n/g, '\n');
    result = result.replace(/\n{3,}/g, '\n\n');

    return result.trim();
  }

  // -------------------------------------------------------------
  // Document Metrics Calculation
  // -------------------------------------------------------------
  function calculateStats(text) {
    if (!text || !text.trim()) {
      return {
        wordCount: 0,
        characterCount: 0,
        characterCountNoSpaces: 0,
        readingTimeMinutes: 0
      };
    }

    const charCount = text.length;
    const charCountNoSpaces = text.replace(/\s/g, '').length;
    const words = text.trim().split(/\s+/).filter(w => w.length > 0);
    const wordCount = words.length;
    const readingTime = wordCount > 0 ? Math.ceil(wordCount / 200.0) : 0;

    return {
      wordCount,
      characterCount: charCount,
      characterCountNoSpaces: charCountNoSpaces,
      readingTimeMinutes: readingTime
    };
  }

  function updateStats() {
    const text = editorInput.value;
    const stats = calculateStats(text);

    statWords.textContent = stats.wordCount.toLocaleString();
    statChars.textContent = stats.characterCount.toLocaleString();
    statCharsNoSpaces.textContent = stats.characterCountNoSpaces.toLocaleString();
    statReadingTime.textContent = stats.readingTimeMinutes.toString();
  }

  // -------------------------------------------------------------
  // Secure Lightweight Markdown-to-HTML Renderer
  // -------------------------------------------------------------
  function escapeHtml(unsafe) {
    return unsafe
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function renderMarkdown(md) {
    if (!md || !md.trim()) {
      return '<p class="text-muted"><em>' + escapeHtml(t('placeholder_editor')) + '</em></p>';
    }

    const lines = md.replace(/\r\n/g, '\n').replace(/\r/g, '\n').split('\n');
    const out = [];
    let inCodeBlock = false;
    let codeBlockLang = '';
    let codeBlockLines = [];
    let inList = false;
    let listType = 'ul';
    let inTable = false;
    let tableRows = [];

    function flushList() {
      if (inList) {
        out.push(`</${listType}>`);
        inList = false;
      }
    }

    function flushTable() {
      if (inTable && tableRows.length > 0) {
        let html = '<table><thead>';
        const headerCells = tableRows[0];
        html += '<tr>' + headerCells.map(c => `<th>${parseInline(c)}</th>`).join('') + '</tr></thead><tbody>';
        for (let r = 1; r < tableRows.length; r++) {
          html += '<tr>' + tableRows[r].map(c => `<td>${parseInline(c)}</td>`).join('') + '</tr>';
        }
        html += '</tbody></table>';
        out.push(html);
        inTable = false;
        tableRows = [];
      }
    }

    function parseInline(str) {
      let s = escapeHtml(str);
      // Math inline
      s = s.replace(/\$(.+?)\$/g, '<code class="math">$1</code>');
      // Images: ![alt](url) -> Figure with caption
      s = s.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (match, alt, src) => {
        return `<figure><img src="${src}" alt="${alt}"><figcaption>${alt}</figcaption></figure>`;
      });
      // Links: [text](url)
      s = s.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
      // Bold + Italic: ***text***
      s = s.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
      // Bold: **text**
      s = s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
      // Italic: *text* or _text_
      s = s.replace(/\*([^*]+)\*/g, '<em>$1</em>');
      s = s.replace(/_([^_]+)_/g, '<em>$1</em>');
      // Strikethrough: ~~text~~
      s = s.replace(/~~(.+?)~~/g, '<del>$1</del>');
      // Inline Code: `code`
      s = s.replace(/`([^`]+)`/g, '<code>$1</code>');
      return s;
    }

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];

      // Code Blocks
      if (line.trim().startsWith('```')) {
        if (!inCodeBlock) {
          flushList();
          flushTable();
          inCodeBlock = true;
          codeBlockLang = line.trim().slice(3).trim();
          codeBlockLines = [];
        } else {
          inCodeBlock = false;
          const codeContent = escapeHtml(codeBlockLines.join('\n'));
          out.push(`<pre><code class="language-${codeBlockLang}">${codeContent}</code></pre>`);
        }
        continue;
      }

      if (inCodeBlock) {
        codeBlockLines.push(line);
        continue;
      }

      // Horizontal Rules
      if (/^\s*([-*_]\s*){3,}$/.test(line)) {
        flushList();
        flushTable();
        out.push('<hr>');
        continue;
      }

      // Tables
      if (/^\s*\|.*\|\s*$/.test(line)) {
        flushList();
        if (/^\s*\|[-:\s|]+\|\s*$/.test(line)) {
          // Table separator row
          inTable = true;
          continue;
        }
        const cells = line.split('|').slice(1, -1).map(c => c.trim());
        tableRows.push(cells);
        continue;
      } else if (inTable) {
        flushTable();
      }

      // Headings
      const headingMatch = line.match(/^\s{0,3}(#{1,6})\s+(.*)$/);
      if (headingMatch) {
        flushList();
        flushTable();
        const level = headingMatch[1].length;
        const text = parseInline(headingMatch[2]);
        out.push(`<h${level}>${text}</h${level}>`);
        continue;
      }

      // Blockquotes
      if (line.trim().startsWith('>')) {
        flushList();
        flushTable();
        const text = parseInline(line.replace(/^\s*>\s?/, ''));
        out.push(`<blockquote><p>${text}</p></blockquote>`);
        continue;
      }

      // Task Lists: - [ ] or - [x]
      const taskMatch = line.match(/^\s{0,3}[-*+]\s+\[([ xX])\]\s+(.*)$/);
      if (taskMatch) {
        flushTable();
        if (!inList || listType !== 'ul') {
          flushList();
          inList = true;
          listType = 'ul';
          out.push('<ul class="task-list">');
        }
        const checked = taskMatch[1].toLowerCase() === 'x' ? 'checked disabled' : 'disabled';
        const text = parseInline(taskMatch[2]);
        out.push(`<li class="task-item"><input type="checkbox" ${checked}> <span>${text}</span></li>`);
        continue;
      }

      // Unordered Lists: - item, * item, + item
      const ulMatch = line.match(/^\s{0,3}[-*+]\s+(.*)$/);
      if (ulMatch) {
        flushTable();
        if (!inList || listType !== 'ul') {
          flushList();
          inList = true;
          listType = 'ul';
          out.push('<ul>');
        }
        out.push(`<li>${parseInline(ulMatch[1])}</li>`);
        continue;
      }

      // Ordered Lists: 1. item
      const olMatch = line.match(/^\s{0,3}\d+\.\s+(.*)$/);
      if (olMatch) {
        flushTable();
        if (!inList || listType !== 'ol') {
          flushList();
          inList = true;
          listType = 'ol';
          out.push('<ol>');
        }
        out.push(`<li>${parseInline(olMatch[1])}</li>`);
        continue;
      }

      flushList();

      // Empty Lines
      if (!line.trim()) {
        continue;
      }

      // Paragraphs
      out.push(`<p>${parseInline(line)}</p>`);
    }

    flushList();
    flushTable();

    return out.join('\n');
  }

  function renderPreview() {
    previewContainer.innerHTML = renderMarkdown(editorInput.value);
  }

  // -------------------------------------------------------------
  // Mode & Workspace Switching
  // -------------------------------------------------------------
  function setMode(mode) {
    currentMode = mode;
    if (mode === 'view') {
      renderPreview();
      paneView.classList.add('active');
      paneEdit.classList.remove('active');
      tabViewBtn.classList.add('active');
      tabEditBtn.classList.remove('active');
    } else {
      paneEdit.classList.add('active');
      paneView.classList.remove('active');
      tabEditBtn.classList.add('active');
      tabViewBtn.classList.remove('active');
      editorInput.focus();
    }
  }

  // -------------------------------------------------------------
  // Theme Switching
  // -------------------------------------------------------------
  function setTheme(theme) {
    currentTheme = theme === 'night' ? 'night' : 'paper';
    elTheme.setAttribute('data-theme', currentTheme);
    localStorage.setItem('cm_theme', currentTheme);
  }

  function toggleTheme() {
    setTheme(currentTheme === 'paper' ? 'night' : 'paper');
  }

  // -------------------------------------------------------------
  // Localization (I18N)
  // -------------------------------------------------------------
  function t(key) {
    const dict = I18N[currentLang] || I18N.de;
    return dict[key] || key;
  }

  function applyLanguage(lang) {
    if (!I18N[lang]) lang = 'de';
    currentLang = lang;
    localStorage.setItem('cm_lang', lang);
    langSelect.value = lang;

    // Retranslate UI elements with data-i18n
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (key && t(key)) {
        el.textContent = t(key);
      }
    });

    // Retranslate tooltips and placeholders
    document.querySelectorAll('[data-i18n-title]').forEach(el => {
      const key = el.getAttribute('data-i18n-title');
      if (key && t(key)) {
        el.setAttribute('title', t(key));
      }
    });

    editorInput.setAttribute('placeholder', t('placeholder_editor'));
    if (currentMode === 'view') {
      renderPreview();
    }
  }

  // -------------------------------------------------------------
  // Session Exchange Format v1 (cleanmarkdown-session-v1.json)
  // -------------------------------------------------------------
  function exportSession() {
    const fileName = fileNameInput.value.trim() || 'notiz.md';
    const payload = {
      version: SESSION_VERSION,
      appVersion: APP_VERSION,
      fileName: fileName,
      markdown: editorInput.value,
      theme: currentTheme,
      workspace: currentMode,
      updatedAt: new Date().toISOString().replace(/\.\d{3}Z$/, ''),
      settings: {
        language: currentLang,
        theme: currentTheme,
        defaultMode: currentMode,
        autosaveEnabled: true,
        autosaveIntervalSeconds: 12,
        exportMode: 'source',
        exportConfirm: true,
        outputDir: '',
        fileToolbarVisible: true,
        editorToolbarCollapsed: false,
        syncScrollPositions: true
      }
    };

    const jsonStr = JSON.stringify(payload, null, 2);
    const sessionName = fileName.replace(/\.[^/.]+$/, '') + `.${SESSION_VERSION}.json`;
    downloadFile(sessionName, jsonStr, 'application/json');
    showNotice(t('notice_exported'));
  }

  function importSessionData(data) {
    if (!data || typeof data !== 'object' || data.version !== SESSION_VERSION || typeof data.markdown !== 'string') {
      alert(t('error_invalid_session'));
      return false;
    }

    editorInput.value = data.markdown;
    if (data.fileName) {
      fileNameInput.value = data.fileName;
      currentFileName = data.fileName;
    }

    // Apply theme
    if (data.theme) {
      setTheme(data.theme);
    }

    // Apply settings if present
    if (data.settings && typeof data.settings === 'object') {
      if (data.settings.language && I18N[data.settings.language]) {
        applyLanguage(data.settings.language);
      }
      if (data.settings.theme) {
        setTheme(data.settings.theme);
      }
      if (data.settings.defaultMode) {
        setMode(data.settings.defaultMode === 'view' ? 'view' : 'editor');
      }
    } else if (data.workspace) {
      setMode(data.workspace === 'view' || data.workspace === 'read' ? 'view' : 'editor');
    }

    updateStats();
    if (currentMode === 'view') {
      renderPreview();
    }
    showNotice(t('notice_loaded'));
    return true;
  }

  // -------------------------------------------------------------
  // File Download & Clipboard
  // -------------------------------------------------------------
  function downloadFile(filename, content, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 100);
  }

  function saveMarkdownFile() {
    let name = fileNameInput.value.trim() || 'notiz.md';
    if (!name.endsWith('.md') && !name.endsWith('.markdown') && !name.endsWith('.txt')) {
      name += '.md';
    }
    downloadFile(name, editorInput.value, 'text/markdown;charset=utf-8');
    showNotice(t('notice_saved'));
  }

  function copyCleanText() {
    const clean = stripMarkdown(editorInput.value);
    navigator.clipboard.writeText(clean).then(() => {
      showNotice(t('notice_copied'));
    }).catch(() => {
      // Fallback
      const ta = document.createElement('textarea');
      ta.value = clean;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      showNotice(t('notice_copied'));
    });
  }

  function clearFormattingAction() {
    const start = editorInput.selectionStart;
    const end = editorInput.selectionEnd;
    const fullText = editorInput.value;

    if (start !== end) {
      const selected = fullText.slice(start, end);
      const cleaned = stripMarkdown(selected);
      editorInput.setRangeText(cleaned, start, end, 'select');
    } else {
      editorInput.value = stripMarkdown(fullText);
    }
    updateStats();
    if (currentMode === 'view') {
      renderPreview();
    }
    showNotice(t('notice_cleared'));
  }

  function showNotice(msg) {
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add('visible');
    setTimeout(() => {
      toast.classList.remove('visible');
    }, 2800);
  }

  // -------------------------------------------------------------
  // File Loading & Drag-and-Drop
  // -------------------------------------------------------------
  function handleFile(file) {
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function (e) {
      const content = e.target.result;
      if (file.name.endsWith('.json')) {
        try {
          const parsed = JSON.parse(content);
          importSessionData(parsed);
        } catch (err) {
          alert(t('error_invalid_session'));
        }
      } else {
        editorInput.value = content;
        fileNameInput.value = file.name;
        currentFileName = file.name;
        updateStats();
        if (currentMode === 'view') {
          renderPreview();
        }
        showNotice(t('notice_loaded'));
      }
    };
    reader.onerror = function () {
      alert(t('error_file_read'));
    };
    reader.readAsText(file, 'UTF-8');
  }

  // -------------------------------------------------------------
  // Event Listeners & Initialization
  // -------------------------------------------------------------
  function init() {
    // Apply saved theme & language
    setTheme(currentTheme);
    applyLanguage(currentLang);
    setMode('editor');
    updateStats();

    // Editor live updates
    editorInput.addEventListener('input', () => {
      updateStats();
      if (currentMode === 'view') {
        renderPreview();
      }
    });

    // Tab buttons
    tabViewBtn.addEventListener('click', () => setMode('view'));
    tabEditBtn.addEventListener('click', () => setMode('editor'));

    // Theme toggle
    themeToggleBtn.addEventListener('click', toggleTheme);

    // Language dropdown
    langSelect.addEventListener('change', (e) => applyLanguage(e.target.value));

    // File buttons
    document.getElementById('btn-open').addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', (e) => {
      if (e.target.files && e.target.files.length > 0) {
        handleFile(e.target.files[0]);
        fileInput.value = '';
      }
    });

    document.getElementById('btn-save-md').addEventListener('click', saveMarkdownFile);
    document.getElementById('btn-export-session').addEventListener('click', exportSession);
    document.getElementById('btn-clear-formatting').addEventListener('click', clearFormattingAction);
    document.getElementById('btn-copy-clean').addEventListener('click', copyCleanText);

    // Drag and Drop support
    window.addEventListener('dragover', (e) => {
      e.preventDefault();
      e.stopPropagation();
    });

    window.addEventListener('drop', (e) => {
      e.preventDefault();
      e.stopPropagation();
      if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        handleFile(e.dataTransfer.files[0]);
      }
    });

    // Keyboard Shortcuts
    window.addEventListener('keydown', (e) => {
      const isCtrlOrCmd = e.ctrlKey || e.metaKey;

      // Ctrl/Cmd + 1 -> View mode
      if (isCtrlOrCmd && e.key === '1') {
        e.preventDefault();
        setMode('view');
      }
      // Ctrl/Cmd + 2 -> Editor mode
      else if (isCtrlOrCmd && e.key === '2') {
        e.preventDefault();
        setMode('editor');
      }
      // Ctrl/Cmd + O -> Open file
      else if (isCtrlOrCmd && e.key === 'o') {
        e.preventDefault();
        fileInput.click();
      }
      // Ctrl/Cmd + Shift + S -> Export Session
      else if (isCtrlOrCmd && e.shiftKey && (e.key === 's' || e.key === 'S')) {
        e.preventDefault();
        exportSession();
      }
      // Ctrl/Cmd + S -> Save Markdown
      else if (isCtrlOrCmd && !e.shiftKey && (e.key === 's' || e.key === 'S')) {
        e.preventDefault();
        saveMarkdownFile();
      }
      // Ctrl/Cmd + Shift + K -> Clear Formatting
      else if (isCtrlOrCmd && e.shiftKey && (e.key === 'k' || e.key === 'K')) {
        e.preventDefault();
        clearFormattingAction();
      }
    });

    // Register Service Worker for offline PWA functionality
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('./sw.js').catch(() => {
          // Silent offline fallback
        });
      });
    }
  }

  // Expose API for automated testing & headless evaluation
  window.CleanMarkdownWeb = {
    APP_VERSION,
    SESSION_VERSION,
    stripMarkdown,
    calculateStats,
    renderMarkdown,
    exportSession,
    importSessionData,
    setTheme,
    applyLanguage,
    setMode
  };

  document.addEventListener('DOMContentLoaded', init);
})();
