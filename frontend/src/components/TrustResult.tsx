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

type Verdict = 'suitable' | 'caution' | 'not_recommended'
type DecisionKey = 'browse' | 'account' | 'payment' | 'personal_data'

const LEVEL_COLORS = {
  high:   { ring: 'ring-emerald-500', text: 'text-emerald-400', bg: 'bg-emerald-500/10' },
  good:   { ring: 'ring-blue-500',    text: 'text-blue-400',    bg: 'bg-blue-500/10'    },
  medium: { ring: 'ring-amber-500',   text: 'text-amber-400',   bg: 'bg-amber-500/10'   },
  low:    { ring: 'ring-red-500',     text: 'text-red-400',     bg: 'bg-red-500/10'     },
}

const VERDICT_STYLES: Record<Verdict, { border: string; bg: string; dot: string; text: string }> = {
  suitable:        { border: 'border-emerald-800/50', bg: 'bg-emerald-950/30', dot: 'bg-emerald-400', text: 'text-emerald-400' },
  caution:         { border: 'border-amber-800/50',   bg: 'bg-amber-950/20',   dot: 'bg-amber-400',   text: 'text-amber-400'   },
  not_recommended: { border: 'border-red-800/50',     bg: 'bg-red-950/20',     dot: 'bg-red-500',     text: 'text-red-400'     },
}

function getVerdict(
  isSafe: boolean,
  level: TrustReport['trust_level'],
  reputation: TrustReport['checks']['reputation'],
): Verdict {
  if (reputation === 'flagged') return 'not_recommended'
  if (isSafe && (level === 'high' || level === 'good')) return 'suitable'
  if (isSafe && level === 'medium') return 'caution'
  if (!isSafe && level === 'low') return 'not_recommended'
  return 'caution'
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

function DecisionCard({
  decisionKey,
  verdict,
  t,
}: {
  decisionKey: DecisionKey
  verdict: Verdict
  t: ReturnType<typeof useTranslations>
}) {
  const styles = VERDICT_STYLES[verdict]

  return (
    <div className={`rounded-xl border p-4 space-y-2 ${styles.border} ${styles.bg}`}>
      <div className="flex items-center gap-2">
        <span className={`w-2 h-2 rounded-full flex-shrink-0 ${styles.dot}`} />
        <span className="text-slate-200 text-sm font-medium">
          {t(`results.decision.${decisionKey}.label` as Parameters<typeof t>[0])}
        </span>
      </div>
      <p className={`text-xs font-semibold ${styles.text}`}>
        {t(`results.decision.verdict.${verdict}` as Parameters<typeof t>[0])}
      </p>
      <p className="text-slate-400 text-xs leading-relaxed">
        {t(`results.decision.${decisionKey}.${verdict}` as Parameters<typeof t>[0])}
      </p>
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
  const { trust_level, checks } = report

  const decisions: { key: DecisionKey; verdict: Verdict }[] = [
    { key: 'browse',        verdict: getVerdict(report.recommendations.safe_to_browse,  trust_level, checks.reputation) },
    { key: 'account',       verdict: getVerdict(report.recommendations.safe_for_account, trust_level, checks.reputation) },
    { key: 'payment',       verdict: getVerdict(report.recommendations.safe_for_payment, trust_level, checks.reputation) },
    { key: 'personal_data', verdict: getVerdict(report.recommendations.safe_for_payment, trust_level, checks.reputation) },
  ]

  const headersLabel = t('results.headers_score', {
    score: report.checks.headers_score,
    max: report.checks.headers_max,
  })

  const reputationLabel = t(`results.reputation.${report.checks.reputation}` as Parameters<typeof t>[0])

  return (
    <div className="w-full max-w-xl space-y-4">
      {/* Score card */}
      <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 shadow-2xl">
        <p className="text-slate-400 text-sm text-center mb-4 truncate" dir="ltr">
          {report.domain}
        </p>

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
            {t(`home.trust_levels.${report.trust_level}` as Parameters<typeof t>[0])}
          </span>
          <p className="text-slate-500 text-xs text-center mt-1 max-w-xs leading-relaxed">
            {t('results.score_based_on', {
              https: report.checks.https ? '✓' : '✗',
              ssl: report.checks.ssl_valid ? '✓' : '✗',
              headers: `${report.checks.headers_score}/${report.checks.headers_max}`,
              reputation: reputationLabel,
            })}
          </p>
        </div>

        {report.warnings.length > 0 && (
          <div className="mb-4 bg-amber-500/10 border border-amber-500/30 rounded-xl px-4 py-2">
            {report.warnings.map((w) => (
              <p key={w} className="text-amber-400 text-xs text-center">
                ⚠ {t(`results.warnings.${w}` as Parameters<typeof t>[0])}
              </p>
            ))}
          </div>
        )}
      </div>

      {/* Usage Decision */}
      <div className="bg-slate-900 border border-slate-700 rounded-2xl p-5 shadow-xl space-y-3">
        <p className="text-slate-400 text-xs uppercase tracking-wider">
          {t('results.decision.title')}
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {decisions.map(({ key, verdict }) => (
            <DecisionCard key={key} decisionKey={key} verdict={verdict} t={t} />
          ))}
        </div>
      </div>

      {/* Security indicators */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow">
        <div className="px-5 py-3 border-b border-slate-800">
          <p className="text-slate-400 text-xs uppercase tracking-wider">
            {t('results.checks_title')}
          </p>
        </div>
        <div className="px-5 py-2 pb-4">
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

      <p className="text-slate-600 text-xs text-center leading-relaxed px-4">
        {t('home.disclaimer')}
      </p>
    </div>
  )
}
