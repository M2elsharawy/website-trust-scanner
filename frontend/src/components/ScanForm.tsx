'use client'

import { useState } from 'react'
import { useTranslations } from 'next-intl'
import TrustResult from './TrustResult'

interface TrustReport {
  domain: string
  trust_score: number
  trust_level: 'low' | 'medium' | 'good' | 'high'
  checks: {
    https: boolean
    ssl_valid: boolean
    ssl_expiry_warning: boolean
    hsts: boolean
    headers_score: number
    headers_max: number
    reputation: 'clean' | 'flagged' | 'unknown'
  }
  recommendations: {
    safe_to_browse: boolean
    safe_for_email: boolean
    safe_for_account: boolean
    safe_for_payment: boolean
  }
  warnings: string[]
}

const ERROR_CODE_TO_KEY: Record<string, string> = {
  INVALID_URL: 'errors.invalid_url',
  SSRF_BLOCKED: 'errors.ssrf_blocked',
  URL_NOT_SAFE: 'errors.ssrf_blocked',
  DOMAIN_BLOCKED: 'errors.domain_blocked',
  RATE_LIMIT_EXCEEDED: 'errors.rate_limit',
}

function GlobeIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <circle cx="8" cy="8" r="6.5" stroke="currentColor" strokeWidth="1.25"/>
      <ellipse cx="8" cy="8" rx="3" ry="6.5" stroke="currentColor" strokeWidth="1.25"/>
      <line x1="1.5" y1="8" x2="14.5" y2="8" stroke="currentColor" strokeWidth="1.25"/>
      <line x1="1.5" y1="5" x2="14.5" y2="5" stroke="currentColor" strokeWidth="1"/>
      <line x1="1.5" y1="11" x2="14.5" y2="11" stroke="currentColor" strokeWidth="1"/>
    </svg>
  )
}

function EnvelopeIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <rect x="1.5" y="3.5" width="13" height="9" rx="1.25" stroke="currentColor" strokeWidth="1.25"/>
      <path d="M1.5 5L8 9.5L14.5 5" stroke="currentColor" strokeWidth="1.25" strokeLinecap="round"/>
    </svg>
  )
}

function UserIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <circle cx="8" cy="5.5" r="2.75" stroke="currentColor" strokeWidth="1.25"/>
      <path d="M2 14.5c0-3.31 2.69-6 6-6s6 2.69 6 6" stroke="currentColor" strokeWidth="1.25" strokeLinecap="round"/>
    </svg>
  )
}

function LockIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <rect x="3" y="7.5" width="10" height="7" rx="1.25" stroke="currentColor" strokeWidth="1.25"/>
      <path d="M5.5 7.5V5a2.5 2.5 0 0 1 5 0v2.5" stroke="currentColor" strokeWidth="1.25" strokeLinecap="round"/>
      <circle cx="8" cy="11" r="1" fill="currentColor"/>
    </svg>
  )
}

const PREVIEW_ICONS = {
  safe_to_browse: GlobeIcon,
  safe_for_email: EnvelopeIcon,
  safe_for_account: UserIcon,
  safe_for_payment: LockIcon,
} as const

function ScanningOverlay({ label }: { label: string }) {
  return (
    <div className="flex flex-col items-center gap-3 py-4">
      <div className="relative w-8 h-8">
        <div className="absolute inset-0 border-2 border-blue-500/30 rounded-full" />
        <div className="absolute inset-0 border-2 border-transparent border-t-blue-500 rounded-full animate-spin" />
      </div>
      <span className="text-slate-400 text-sm">{label}</span>
    </div>
  )
}

export default function ScanForm({ apiUrl }: { apiUrl: string }) {
  const t = useTranslations()
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<TrustReport | null>(null)
  const [error, setError] = useState<string | null>(null)

  function reset() {
    setResult(null)
    setError(null)
    setUrl('')
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!url.trim()) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const res = await fetch(`${apiUrl}/api/v1/scans/public`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url.trim() }),
      })

      if (res.status === 429) {
        setError(t('errors.rate_limit'))
        return
      }

      const data = await res.json()

      if (!res.ok) {
        const key = data?.error ? ERROR_CODE_TO_KEY[data.error] : null
        setError(key ? t(key) : t('errors.try_again'))
        return
      }

      setResult(data as TrustReport)
    } catch {
      setError(t('errors.try_again'))
    } finally {
      setLoading(false)
    }
  }

  if (result) {
    return <TrustResult report={result} onReset={reset} />
  }

  return (
    <div className="w-full max-w-xl">
      {/* Hero text */}
      <div className="text-center mb-10">
        <h1 className="text-4xl md:text-5xl font-bold text-white mb-4 leading-tight tracking-tight">
          {t('home.title')}
        </h1>
        <p className="text-slate-400 text-lg leading-relaxed max-w-md mx-auto">
          {t('home.subtitle')}
        </p>
      </div>

      {/* URL Input Card */}
      <form
        onSubmit={handleSubmit}
        className="bg-slate-900 border border-slate-700/80 rounded-2xl p-4 shadow-2xl shadow-black/40 mb-4"
      >
        <div className="flex flex-col sm:flex-row gap-3">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder={t('home.url_placeholder')}
            disabled={loading}
            required
            className="flex-1 px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl
                       text-slate-100 placeholder:text-slate-500
                       focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                       text-sm transition-all disabled:opacity-50"
            dir="ltr"
            aria-label={t('home.url_placeholder')}
          />
          <button
            type="submit"
            disabled={loading || !url.trim()}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-500 active:bg-blue-700 text-white rounded-xl
                       font-semibold text-sm whitespace-nowrap transition-all
                       disabled:opacity-50 disabled:cursor-not-allowed
                       focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-900"
          >
            {loading ? t('home.scanning') : t('home.check_button')}
          </button>
        </div>

        {error && (
          <p className="text-red-400 text-xs mt-3 text-center" role="alert">{error}</p>
        )}

        {loading && (
          <ScanningOverlay label={t('home.scanning')} />
        )}
      </form>

      {/* Disclaimer */}
      <p className="text-slate-600 text-xs text-center leading-relaxed px-4 mb-8">
        {t('home.disclaimer')}
      </p>

      {/* Static recommendation preview */}
      <div className="grid grid-cols-2 gap-2.5">
        {(
          [
            'safe_to_browse',
            'safe_for_email',
            'safe_for_account',
            'safe_for_payment',
          ] as const
        ).map((key) => {
          const Icon = PREVIEW_ICONS[key]
          return (
            <div
              key={key}
              className="flex items-center gap-3 bg-slate-900/70 border border-slate-800 rounded-xl px-4 py-3"
            >
              <span className="text-slate-600 flex-shrink-0">
                <Icon />
              </span>
              <span className="text-slate-500 text-sm">
                {t(`home.recommendations.${key}`)}
              </span>
            </div>
          )
        })}
      </div>

      {/* How it works */}
      <div className="mt-7 space-y-3">
        <p className="text-slate-600 text-xs uppercase tracking-wider font-medium text-center">
          {t('home.how_it_works.title')}
        </p>
        <div className="flex flex-col sm:flex-row gap-2">
          {([0, 1, 2] as const).map((i) => (
            <div
              key={i}
              className="flex-1 flex items-start gap-2.5 bg-slate-900/50 border border-slate-800/60 rounded-xl px-3 py-3"
            >
              <span className="flex-shrink-0 w-5 h-5 rounded-full bg-blue-700/50 text-blue-300 text-xs flex items-center justify-center font-bold mt-0.5">
                {i + 1}
              </span>
              <span className="text-slate-500 text-xs leading-relaxed">
                {t(`home.how_it_works.steps.${i}` as Parameters<typeof t>[0])}
              </span>
            </div>
          ))}
        </div>
        <p className="text-slate-700 text-xs text-center leading-relaxed pt-1 px-2">
          {t('home.trust_signals.note')}
        </p>
      </div>
    </div>
  )
}
