/**
 * Zeigt Lerntexte im Markdown-Format an.
 *
 * Rohes HTML im Text wird nicht ausgeführt (`skipHtml`), Links öffnen sich in einem
 * neuen Tab ohne Zugriff auf diese Seite.
 */
import ReactMarkdown, { type Components } from 'react-markdown'

/** Gestaltung der Markdown-Elemente mit den Design-Tokens. */
const ELEMENTE: Components = {
  h2: ({ children }) => <h3 className="mt-6 mb-2 text-xl font-bold">{children}</h3>,
  h3: ({ children }) => <h4 className="mt-4 mb-2 text-lg font-semibold">{children}</h4>,
  p: ({ children }) => <p className="my-3 leading-relaxed">{children}</p>,
  ul: ({ children }) => <ul className="my-3 list-disc space-y-1 pl-6">{children}</ul>,
  ol: ({ children }) => <ol className="my-3 list-decimal space-y-1 pl-6">{children}</ol>,
  a: ({ children, href }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-accent-cyan underline underline-offset-2"
    >
      {children}
    </a>
  ),
  code: ({ children }) => (
    <code className="rounded bg-surface-raised px-1.5 py-0.5 font-mono text-sm text-accent-violet">
      {children}
    </code>
  ),
  pre: ({ children }) => (
    // Codeblöcke: Die Inline-Code-Hervorhebung wird innerhalb von <pre> zurückgesetzt.
    <pre className="my-4 overflow-x-auto rounded-card border border-border bg-bg p-4 text-sm [&_code]:bg-transparent [&_code]:p-0">
      {children}
    </pre>
  ),
}

/**
 * Rendert einen Markdown-Text.
 *
 * @param props.text - Der Lerntext.
 * @returns Den formatierten Text.
 */
export function Markdown({ text }: { text: string }) {
  return (
    <ReactMarkdown skipHtml components={ELEMENTE}>
      {text}
    </ReactMarkdown>
  )
}
