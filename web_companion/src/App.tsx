import DOMPurify from 'dompurify'
import { marked } from 'marked'
import {
  ChangeEvent,
  DragEvent,
  ReactNode,
  startTransition,
  useDeferredValue,
  useEffect,
  useId,
  useRef,
  useState
} from 'react'
import { useLocale } from './LocaleContext.tsx'
import { fillIn } from './i18n.ts'
import { countLines, countLinks } from './lib/markdownStats.mjs'

type ThemeMode = 'paper' | 'night'
type WorkspaceMode = 'read' | 'write' | 'split'

type CompanionSession = {
  version: 'cleanmarkdown-session-v1'
  fileName: string
  markdown: string
  theme: ThemeMode
  workspace: WorkspaceMode
  updatedAt: string
}

const STORAGE_KEY = 'cleanmarkdown-companion-state-v1'

const STARTER_MARKDOWN = `# CleanMarkdown Companion

Willkommen in der mobilen Web-Linie von **CleanMarkdown**.

## Wofür diese App gedacht ist

- Markdown-Dateien lokal öffnen
- Kleine Korrekturen unterwegs schreiben
- Lesemodus und Rohtext nebeneinander prüfen
- Ergebnis wieder als \`.md\` oder Session exportieren

## Hinweise

1. Die Desktop-App bleibt die volle Referenz.
2. Diese PWA speichert deinen letzten Stand lokal im Browser.
3. Relative Assets werden noch nicht als Bundle transportiert.

> Echte Umlaute bleiben erhalten: ä ö ü Ä Ö Ü ß

\`\`\`md
- Checklisten
- Codeblöcke
- Tabellen
\`\`\`

| Bereich | Status |
| --- | --- |
| Lesen | bereit |
| Bearbeiten | bereit |
| Export | bereit |
`

function createDefaultSession(): CompanionSession {
  return {
    version: 'cleanmarkdown-session-v1',
    fileName: 'cleanmarkdown-notiz.md',
    markdown: STARTER_MARKDOWN,
    theme: 'paper',
    workspace: 'split',
    updatedAt: new Date().toISOString()
  }
}

function readStoredSession(): CompanionSession {
  if (typeof window === 'undefined') {
    return createDefaultSession()
  }

  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (!raw) {
      return createDefaultSession()
    }

    const parsed = JSON.parse(raw) as Partial<CompanionSession>
    if (
      parsed.version !== 'cleanmarkdown-session-v1' ||
      typeof parsed.fileName !== 'string' ||
      typeof parsed.markdown !== 'string'
    ) {
      return createDefaultSession()
    }

    return {
      version: 'cleanmarkdown-session-v1',
      fileName: parsed.fileName,
      markdown: parsed.markdown,
      theme: parsed.theme === 'night' ? 'night' : 'paper',
      workspace:
        parsed.workspace === 'read' || parsed.workspace === 'write' || parsed.workspace === 'split'
          ? parsed.workspace
          : 'split',
      updatedAt:
        typeof parsed.updatedAt === 'string' ? parsed.updatedAt : new Date().toISOString()
    }
  } catch {
    return createDefaultSession()
  }
}

function countWords(markdown: string): number {
  const words = markdown
    .replace(/[`*_>#|[\]()!-]/g, ' ')
    .trim()
    .match(/\S+/g)

  return words?.length ?? 0
}

function estimateReadingMinutes(wordCount: number): string {
  if (wordCount === 0) {
    return '0 min'
  }

  return `${Math.max(1, Math.ceil(wordCount / 180))} min`
}

function toMarkdownName(fileName: string): string {
  if (!fileName.trim()) {
    return 'cleanmarkdown-notiz.md'
  }

  return /\.md$/i.test(fileName) ? fileName : `${fileName.replace(/\.[^.]+$/, '')}.md`
}

function toSessionName(fileName: string): string {
  return toMarkdownName(fileName).replace(/\.md$/i, '.cleanmarkdown-session-v1.json')
}

function triggerDownload(name: string, content: string, type: string): void {
  const blob = new Blob([content], { type })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = name
  document.body.append(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}

function renderMarkdown(markdown: string): string {
  const html = marked.parse(markdown, {
    breaks: true,
    gfm: true
  }) as string

  return DOMPurify.sanitize(html)
}

function formatTimestamp(value: string, dateLocale: string, unknownLabel: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return unknownLabel
  }

  return new Intl.DateTimeFormat(dateLocale, {
    dateStyle: 'medium',
    timeStyle: 'short'
  }).format(date)
}

function StatCard(props: { label: string; value: string }): ReactNode {
  return (
    <article className="stat-card">
      <span className="stat-card__label">{props.label}</span>
      <strong className="stat-card__value">{props.value}</strong>
    </article>
  )
}

function ToggleButton(props: {
  active: boolean
  children: ReactNode
  onClick: () => void
}): ReactNode {
  return (
    <button
      type="button"
      className={`toggle-button${props.active ? ' toggle-button--active' : ''}`}
      onClick={props.onClick}
    >
      {props.children}
    </button>
  )
}

function ToolbarButton(props: {
  children: ReactNode
  onClick: () => void
  variant?: 'primary' | 'secondary'
}): ReactNode {
  return (
    <button
      type="button"
      className={`toolbar-button toolbar-button--${props.variant ?? 'secondary'}`}
      onClick={props.onClick}
    >
      {props.children}
    </button>
  )
}

async function readImportedFile(
  file: File,
  errorInvalidSession: string
): Promise<CompanionSession> {
  const text = await file.text()

  if (file.name.endsWith('.json')) {
    let parsed: Partial<CompanionSession>
    try {
      parsed = JSON.parse(text) as Partial<CompanionSession>
    } catch {
      throw new Error(errorInvalidSession)
    }
    if (
      parsed.version !== 'cleanmarkdown-session-v1' ||
      typeof parsed.fileName !== 'string' ||
      typeof parsed.markdown !== 'string'
    ) {
      throw new Error(errorInvalidSession)
    }

    return {
      version: 'cleanmarkdown-session-v1',
      fileName: parsed.fileName,
      markdown: parsed.markdown,
      theme: parsed.theme === 'night' ? 'night' : 'paper',
      workspace:
        parsed.workspace === 'read' || parsed.workspace === 'write' || parsed.workspace === 'split'
          ? parsed.workspace
          : 'split',
      updatedAt: new Date().toISOString()
    }
  }

  return {
    version: 'cleanmarkdown-session-v1',
    fileName: toMarkdownName(file.name),
    markdown: text,
    theme: 'paper',
    workspace: 'split',
    updatedAt: new Date().toISOString()
  }
}

export default function App() {
  const { locale, t, setLocale } = useLocale()
  const [session, setSession] = useState<CompanionSession>(() => readStoredSession())
  const [dragActive, setDragActive] = useState(false)
  const [statusMessage, setStatusMessage] = useState(() => t.statusInitial)
  const [errorMessage, setErrorMessage] = useState('')
  const inputId = useId()
  const fileInputRef = useRef<HTMLInputElement | null>(null)
  const deferredMarkdown = useDeferredValue(session.markdown)

  const wordCount = countWords(session.markdown)
  const lineCount = countLines(session.markdown)
  const linkCount = countLinks(session.markdown)
  const renderedHtml = renderMarkdown(deferredMarkdown)

  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(session))
  }, [session])

  useEffect(() => {
    document.documentElement.dataset.theme = session.theme
  }, [session.theme])

  function patchSession(update: Partial<CompanionSession>) {
    setSession((current) => ({
      ...current,
      ...update,
      updatedAt: update.updatedAt ?? new Date().toISOString()
    }))
  }

  async function importFile(file: File) {
    try {
      const nextSession = await readImportedFile(file, t.errorInvalidSession)
      startTransition(() => {
        setSession(nextSession)
        setErrorMessage('')
        setStatusMessage(fillIn(t.statusLoaded, { file: file.name }))
      })
    } catch (error) {
      const message =
        error instanceof Error ? error.message : t.errorCannotRead
      setErrorMessage(message)
    }
  }

  async function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    if (!file) {
      return
    }

    await importFile(file)
    event.target.value = ''
  }

  async function handleDrop(event: DragEvent<HTMLElement>) {
    event.preventDefault()
    setDragActive(false)
    const file = event.dataTransfer.files?.[0]
    if (file) {
      await importFile(file)
    }
  }

  function handleDragOver(event: DragEvent<HTMLElement>) {
    event.preventDefault()
    setDragActive(true)
  }

  function handleDragLeave(event: DragEvent<HTMLElement>) {
    event.preventDefault()
    if (!event.relatedTarget || !event.currentTarget.contains(event.relatedTarget)) {
      setDragActive(false)
    }
  }

  function handleMarkdownExport() {
    triggerDownload(toMarkdownName(session.fileName), session.markdown, 'text/markdown;charset=utf-8')
    setStatusMessage(t.statusMarkdownExported)
  }

  function handleSessionExport() {
    triggerDownload(
      toSessionName(session.fileName),
      JSON.stringify(session, null, 2),
      'application/json;charset=utf-8'
    )
    setStatusMessage(t.statusSessionExported)
  }

  function handleReset() {
    const nextSession = createDefaultSession()
    startTransition(() => {
      setSession(nextSession)
      setErrorMessage('')
      setStatusMessage(t.statusDemoRestored)
    })
  }

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(session.markdown)
      setStatusMessage(t.statusCopied)
    } catch {
      setStatusMessage(t.statusCopyFailed)
    }
  }

  return (
    <main className="app-shell">
      <section className="hero-panel">
        <div className="hero-panel__copy">
          <p className="hero-panel__eyebrow">{t.heroEyebrow}</p>
          <h1>{t.heroHeadline}</h1>
          <p className="hero-panel__text">{t.heroText}</p>
        </div>

        <div className="hero-panel__actions">
          <ToolbarButton variant="primary" onClick={() => fileInputRef.current?.click()}>
            {t.btnOpen}
          </ToolbarButton>
          <ToolbarButton onClick={handleCopy}>{t.btnCopy}</ToolbarButton>
          <ToolbarButton onClick={handleMarkdownExport}>{t.btnSaveMd}</ToolbarButton>
          <ToolbarButton onClick={handleSessionExport}>{t.btnExportSession}</ToolbarButton>
          <ToolbarButton onClick={handleReset}>{t.btnDemo}</ToolbarButton>
        </div>

        <input
          id={inputId}
          ref={fileInputRef}
          className="sr-only"
          type="file"
          accept=".md,.markdown,.json,text/markdown,application/json"
          onChange={handleFileChange}
        />

        <div className="hero-panel__meta">
          <span>{statusMessage}</span>
          <span>{t.metaUpdatedPrefix}{formatTimestamp(session.updatedAt, t.dateLocale, t.timestampUnknown)}</span>
        </div>

        {errorMessage ? <p className="notice notice--error">{errorMessage}</p> : null}
      </section>

      <section className="status-grid" aria-label={t.ariaMetrics}>
        <StatCard label={t.statFile} value={session.fileName} />
        <StatCard label={t.statWords} value={String(wordCount)} />
        <StatCard label={t.statChars} value={String(session.markdown.length)} />
        <StatCard label={t.statLines} value={String(lineCount)} />
        <StatCard label={t.statLinks} value={String(linkCount)} />
        <StatCard label={t.statReadTime} value={estimateReadingMinutes(wordCount)} />
      </section>

      <section className="controls-panel">
        <div className="toggle-group" aria-label={t.ariaView}>
          <ToggleButton active={session.workspace === 'read'} onClick={() => patchSession({ workspace: 'read' })}>
            {t.toggleRead}
          </ToggleButton>
          <ToggleButton active={session.workspace === 'split'} onClick={() => patchSession({ workspace: 'split' })}>
            {t.toggleSplit}
          </ToggleButton>
          <ToggleButton active={session.workspace === 'write'} onClick={() => patchSession({ workspace: 'write' })}>
            {t.toggleWrite}
          </ToggleButton>
        </div>

        <div className="toggle-group" aria-label={t.ariaTheme}>
          <ToggleButton active={session.theme === 'paper'} onClick={() => patchSession({ theme: 'paper' })}>
            {t.togglePaper}
          </ToggleButton>
          <ToggleButton active={session.theme === 'night'} onClick={() => patchSession({ theme: 'night' })}>
            {t.toggleNight}
          </ToggleButton>
        </div>

        <div className="toggle-group" aria-label={t.ariaLanguage}>
          <ToggleButton active={locale === 'de'} onClick={() => setLocale('de')}>
            DE
          </ToggleButton>
          <ToggleButton active={locale === 'en'} onClick={() => setLocale('en')}>
            EN
          </ToggleButton>
        </div>
      </section>

      <section
        className={`workspace workspace--${session.workspace}${dragActive ? ' workspace--drag' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <article className="surface surface--reader">
          <header className="surface__header">
            <div>
              <span className="surface__label">{t.surfaceReaderLabel}</span>
              <h2>{t.surfaceReaderTitle}</h2>
            </div>
            <p>{t.surfaceReaderDesc}</p>
          </header>

          <div className="markdown-body" dangerouslySetInnerHTML={{ __html: renderedHtml }} />
        </article>

        <article className="surface surface--writer">
          <header className="surface__header">
            <div>
              <span className="surface__label">{t.surfaceWriterLabel}</span>
              <h2>{t.surfaceWriterTitle}</h2>
            </div>
            <p>{t.surfaceWriterDesc}</p>
          </header>

          <label className="field">
            <span className="field__label">{t.fieldFilename}</span>
            <input
              className="field__input"
              type="text"
              value={session.fileName}
              onChange={(event) => patchSession({ fileName: event.target.value })}
            />
          </label>

          <label className="field field--grow">
            <span className="field__label">{t.fieldContent}</span>
            <textarea
              className="editor"
              spellCheck={false}
              value={session.markdown}
              onChange={(event) => patchSession({ markdown: event.target.value })}
            />
          </label>
        </article>
      </section>

      <section className="footnotes">
        <p>{t.footnote1}</p>
        <p>{t.footnote2}</p>
        <label className="file-link" htmlFor={inputId}>
          {t.footnoteDropLabel}
        </label>
      </section>
    </main>
  )
}
