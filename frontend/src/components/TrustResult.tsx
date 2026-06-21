'use client'

import { useTranslations } from 'next-intl'

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

const LEVEL_COLORS = {
  high:   { ring: 'ring-emerald-500', text: 'text-emerald-400', bg: 'bg-emerald-500/10', dot: 'bg-emerald-500' },
  good:   { ring: 'ring-blue-500',    text: 'text-blue-400',    bg: 'bg-blue-500/10',    dot: 'bg-blue-500'    },
  medium: { ring: 'ring-amber-500',   text: 'text-amber-400',   bg: 'bg-amber-500/10',   dot: 'bg-amber-500'   },
  low:    { ring: 'ring-red-500',     text: 'text-red-400',     bg: 'bg-red-500/10',     dot: 'bg-red-500'     },
}

function CheckRow({ label, passed }: { label: string; passed: boolean }) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-slate-800 last:border-0">
      <span className="text-slate-300 text-sm">{label}</span>
      <span className={`text-sm font-medium ${passed ? 'text-emerald-400' : 'text-red-400'}`}>
        {passed ? '✓' : '✗'}
      </span>
    </div>
  )
}

function RecommendationBadge({ label, safe }: { label: string; safe: boolean }) {
  return (
    <div
      className={`flex items-center gap-2 rounded-xl px-4 py-3 border ${
        safe
          ? 'bg-emerald-500/10 border-emerald-500/30'
          : 'bg-slate-800 border-slate-700'
      }`}
    >
      <div
        className={`w-2 h-2 rounded-full flex-shrink-0 ${
          safe ? 'bg-emerald-500' : 'bg-slate-600'
        }`}
      />
      <span className={`text-sm ${safe ? 'text-emerald-300' : 'text-slate-500'}`}>
        {label}
      </span>
    </div>
  )
}

export default function TrustResult({
  report,
  onReset,
}: {
  report: TrustReport
  onReset: () => void
}) {
  const t = useTranslations()
  const colors = LEVEL_COLORS[report.trust_level]

  const levelLabel = t(`home.trust_levels.${report.trust_level}`)

  const headersLabel = t('results.headers_score', {
    score: report.checks.headers_score,
    max: report.checks.headers_max,
  })

  const reputationLabel = t(`results.reputation.${report.checks.reputation}`)

  return (
    <div className="w-full max-w-xl space-y-4">
      {/* Score card */}
      <div className={`bg-slate-900 border border-slate-700 rounded-2xl p-6 shadow-2xl`}>
        {/* Domain */}
        <p className="text-slate-400 text-sm text-center mb-4 truncate" dir="ltr">
          {report.domain}
        </p>

        {/* Score circle */}
        <div className="flex flex-col items-center mb-6">
          <div
            className={`w-28 h-28 rounded-full ring-4 ${colors.ring} ${colors.bg}
                        flex flex-col items-center justify-center mb-3`}
          >
            <span className={`text-4xl font-bold ${colors.text}`}>
              {report.trust_score}
            </span>
            <span className="text-slate-500 text-xs">/100</span>
          </div>
          <span className={`text-lg font-semibold ${colors.text}`}>
            {levelLabel}
          </span>
        </div>

        {/* Warnings */}
        {report.warnings.length > 0 && (
          <div className="mb-4 bg-amber-500/10 border border-amber-500/30 rounded-xl px-4 py-2">
            {report.warnings.map((w) => (
              <p key={w} className="text-amber-400 text-xs text-center">
                ⚠ {t(`results.warnings.${w}`)}
              </p>
            ))}
          </div>
        )}

        {/* Checks */}
        <div className="mb-2">
          <p className="text-slate-400 text-xs uppercase tracking-wider mb-2">
            {t('results.checks_title')}
          </p>
          <CheckRow label={t('results.checks.https')} passed={report.checks.https} />
          <CheckRow label={t('results.checks.ssl')} passed={report.checks.ssl_valid} />
          <div className="flex items-center justify-between py-2 border-b border-slate-800">
            <span className="text-slate-300 text-sm">{t('results.checks.headers')}</span>
            <span className="text-slate-400 text-sm">{headersLabel}</span>
          </div>
          <div className="flex items-center justify-between py-2">
            <span className="text-slate-300 text-sm">{t('results.checks.reputation')}</span>
            <span
              className={`text-sm font-medium ${
                report.checks.reputation === 'clean'
                  ? 'text-emerald-400'
                  : report.checks.reputation === 'flagged'
                  ? 'text-red-400'
                  : 'text-slate-400'
              }`}
            >
              {reputationLabel}
            </span>
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div className="bg-slate-900 border border-slate-700 rounded-2xl p-5 shadow-xl">
        <p className="text-slate-400 text-xs uppercase tracking-wider mb-3">
          {t('results.recommendations_title')}
        </p>
        <div className="grid grid-cols-2 gap-3">
          {(
            [
              'safe_to_browse',
              'safe_for_email',
              'safe_for_account',
              'safe_for_payment',
            ] as const
          ).map((key) => (
            <RecommendationBadge
              key={key}
              label={t(`home.recommendations.${key}`)}
              safe={report.recommendations[key]}
            />
          ))}
        </div>
      </div>

      {/* Reset */}
      <div className="text-center">
        <button
          onClick={onReset}
          className="text-sm text-slate-400 hover:text-slate-100 transition-colors
                     px-4 py-2 rounded-lg hover:bg-slate-800"
        >
          {t('results.new_scan')}
        </button>
      </div>

      {/* Disclaimer */}
      <p className="text-slate-600 text-xs text-center leading-relaxed px-4">
        {t('home.disclaimer')}
      </p>
    </div>
  )
}
