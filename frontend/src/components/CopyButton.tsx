'use client'

import { useState } from 'react'

function CheckIcon() {
  return (
    <svg width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden="true">
      <path d="M2 6L4.5 8.5L10 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  )
}

function CopyIcon() {
  return (
    <svg width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden="true">
      <rect x="4" y="1" width="7" height="8" rx="1" stroke="currentColor" strokeWidth="1.25"/>
      <rect x="1" y="3" width="7" height="8" rx="1" stroke="currentColor" strokeWidth="1.25" fill="none"/>
    </svg>
  )
}

export default function CopyButton({
  text,
  label,
  copiedLabel,
}: {
  text: string
  label: string
  copiedLabel: string
}) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // Clipboard not available — silently ignore
    }
  }

  return (
    <button
      onClick={handleCopy}
      className={`
        inline-flex items-center gap-1.5
        text-xs px-3 py-1.5 rounded-lg border transition-all duration-200
        focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500
        ${copied
          ? 'border-emerald-700/60 bg-emerald-950/40 text-emerald-400 scale-95'
          : 'border-slate-700 bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-slate-100 hover:border-slate-600'
        }
      `}
      aria-label={copied ? copiedLabel : label}
    >
      {copied ? <CheckIcon /> : <CopyIcon />}
      {copied ? copiedLabel : label}
    </button>
  )
}
