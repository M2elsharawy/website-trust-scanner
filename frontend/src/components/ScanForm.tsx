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

// Map backend error codes to translation keys
const ERROR_CODE_TO_KEY: Record<string, string> = {
  INVALID_URL: 'errors.invalid_url',
  SSRF_BLOCKED: 'errors.ssrf_blocked',
  URL_NOT_SAFE: 'errors.ssrf_blocked',
  DOMAIN_BLOCKED: 'errors.domain_blocked',
  RATE_LIMIT_EXCEEDED: 'errors.rate_limit',
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
      {/* Title */}
      <div className="text-center mb-10">
        <h1 className="text-4xl md:text-5xl font-bold text-white mb-4 leading-tight">
          {t('home.title')}
        </h1>
        <p className="text-slate-400 text-lg leading-relaxed">
          {t('home.subtitle')}
        </p>
      </div>

      {/* URL Input Card */}
      <form
        onSubmit={handleSubmit}
        className="bg-slate-900 border border-slate-700 rounded-2xl p-4 shadow-2xl mb-4"
      >
        <div className="flex flex-col sm:flex-row gap-3">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder={t('home.url_placeholder')}
            disabled={loading}
            required
            className="flex-1 px-4 py-3 bg-slate-800 border border-slate-600 rounded-xl
                       text-slate-100 placeholder:text-slate-500
                       focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                       text-sm transition-all disabled:opacity-50"
            dir="ltr"
            aria-label={t('home.url_placeholder')}
          />
          <button
            type="submit"
            disabled={loading || !url.trim()}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-semibold
                       text-sm whitespace-nowrap transition-all
                       disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? t('home.scanning') : t('home.check_button')}
          </button>
        </div>

        {error && (
          <p className="text-red-400 text-xs mt-3 text-center">{error}</p>
        )}

        {loading && (
          <div className="flex justify-center mt-3">
            <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          </div>
        )}
      </form>

      {/* Disclaimer */}
      <p className="text-slate-600 text-xs text-center leading-relaxed px-4 mb-10">
        {t('home.disclaimer')}
      </p>

      {/* Static recommendation preview */}
      <div className="grid grid-cols-2 gap-3">
        {(
          [
            'safe_to_browse',
            'safe_for_email',
            'safe_for_account',
            'safe_for_payment',
          ] as const
        ).map((key) => (
          <div
            key={key}
            className="flex items-center gap-2 bg-slate-900 border border-slate-800 rounded-xl px-4 py-3"
          >
            <div className="w-2 h-2 rounded-full bg-slate-600 flex-shrink-0" />
            <span className="text-slate-500 text-sm">
              {t(`home.recommendations.${key}`)}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
