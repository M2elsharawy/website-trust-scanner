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
  high:   { ring: 'ring-emerald-500', text: 'text-emerald-400', bg: 'bg-emerald-500/10', badge: 'bg-emerald-950/50 text-emerald-400 border-emerald-800/60' },
  good:   { ring: 'ring-blue-500',    text: 'text-blue-400',    bg: 'bg-blue-500/10',    badge: 'bg-blue-950/50 text-blue-400 border-blue-800/60'          },
  medium: { ring: 'ring-amber-500',   text: 'text-amber-400',   bg: 'bg-amber-500/10',   badge: 'bg-amber-950/50 text-amber-400 border-amber-800/60'       },
  low:    { ring: 'ring-red-500',     text: 'text-red-400',     bg: 'bg-red-500/10',     badge: 'bg-red-950/50 text-red-400 border-red-800/60'             },
}

const VERDICT_STYLES: Record<Verdict, { border: string; bg: string; indicator: string; text: string }> = {
  suitable:        { border: 'border-emerald-800/40', bg: 'bg-emerald-950/20', indicator: 'bg-emerald-400', text: 'text-emerald-400' },
  caution:         { border: 'border-amber-800/40',   bg: 'bg-amber-950/15',   indicator: 'bg-amber-400',   text: 'text-amber-400'   },
  not_recommended: { border: 'border-red-800/40',     bg: 'bg-red-950/15',     indicator: 'bg-red-500',     text: 'text-red-400'     },
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

function PassIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
      <path d="M2.5 7L5.5 10L11.5 4" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  )
}

function FailIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
      <path d="M4 4L10 10M10 4L4 10" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round"/>
    </svg>
  )
}

function CheckRow({ label, passed }: { label: string; passed: boolean }) {
  return (
    <div className="flex items-center justify-between py-2.5 border-b border-slate-800/60 last:border-0">
      <span className="text-slate-300 text-sm">{label}</span>
      <span className={`flex items-center gap-1 text-sm font-medium ${passed ? 'text-emerald-400' : 'text-red-400'}`}>
        {passed ? <PassIcon /> : <FailIcon />}
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
    <div className={`rounded-xl border p-4 space-y-1.5 ${styles.border} ${styles.bg}`}>
      <div className="flex items-center gap-2">
        <span className={`w-2 h-2 rounded-full flex-shrink-0 ${styles.indicator}`} />
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

function DangerBanner({ t }: { t: ReturnType<typeof useTranslations> }) {
  const checklist = t.raw('results.danger_banner.checklist') as string[]
  return (
    <div className="bg-red-950/40 border border-red-800/60 rounded-2xl p-5 space-y-4">
      <div className="flex items-start gap-3.5">
        <div className="flex-shrink-0 w-9 h-9 rounded-full bg-red-500/20 flex items-center justify-center mt-0.5">
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
            <path d="M9 3L16.5 15H1.5L9 3Z" stroke="#f87171" strokeWidth="1.5" strokeLinejoin="round"/>
            <path d="M9 8V11" stroke="#f87171" strokeWidth="1.75" strokeLinecap="round"/>
            <circle cx="9" cy="13.5" r="0.75" fill="#f87171"/>
          </svg>
        </div>
        <div className="space-y-1">
          <p className="text-red-400 font-semibold text-sm">{t('results.danger_banner.title')}</p>
          <p className="text-slate-400 text-xs leading-relaxed">{t('results.danger_banner.body')}</p>
        </div>
      </div>
      <ul className="space-y-2 ps-2">
        {checklist.map((item, i) => (
          <li key={i} className="flex items-center gap-2.5 text-xs text-slate-300">
            <span className="w-1.5 h-1.5 rounded-full bg-red-500/70 flex-shrink-0" aria-hidden="true" />
            {item}
          </li>
        ))}
      </ul>
    </div>
  )
}

function GuidanceSection({
  trustLevel,
  isDangerous,
  t,
}: {
  trustLevel: TrustReport['trust_level']
  isDangerous: boolean
  t: ReturnType<typeof useTranslations>
}) {
  const meansKey = `results.what_this_means.${trustLevel}` as Parameters<typeof t>[0]
  const doKey = (isDangerous ? 'results.what_to_do.danger' : `results.what_to_do.${trustLevel}`) as Parameters<typeof t>[0]

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4">
      <div className="space-y-1.5">
        <p className="text-slate-400 text-xs uppercase tracking-wider font-medium">
          {t('results.what_this_means.title')}
        </p>
        <p className="text-slate-300 text-sm leading-relaxed">{t(meansKey)}</p>
      </div>
      <div className="space-y-1.5 pt-3 border-t border-slate-800">
        <p className="text-slate-400 text-xs uppercase tracking-wider font-medium">
          {t('results.what_to_do.title')}
        </p>
        <p className="text-slate-300 text-sm leading-relaxed">{t(doKey)}</p>
      </div>
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

  const isDangerous = trust_level === 'low' || checks.reputation === 'flagged'

  const headersLabel = t('results.headers_score', {
    score: report.checks.headers_score,
    max: report.checks.headers_max,
  })

  const reputationLabel = t(`results.reputation.${report.checks.reputation}` as Parameters<typeof t>[0])

  return (
    <div className="w-full max-w-xl space-y-4">
      {/* Score card */}
      <div className="bg-slate-900 border border-slate-700/80 rounded-2xl p-6 shadow-2xl shadow-black/30">
        {/* Domain */}
        <p className="text-slate-500 text-xs text-center mb-5 font-mono truncate" dir="ltr">
          {report.domain}
        </p>

        {/* Score ring */}
        <div className="flex flex-col items-center mb-6" dir="ltr">
          <div
            className={`w-32 h-32 rounded-full ring-4 ring-offset-2 ring-offset-slate-900 ${colors.ring} ${colors.bg}
                        flex flex-col items-center justify-center mb-3`}
          >
            <span className={`text-5xl font-bold tabular-nums ${colors.text}`}>
              {report.trust_score}
            </span>
            <span className="text-slate-500 text-xs mt-0.5">/100</span>
          </div>
          <span className={`inline-flex items-center px-3 py-1 rounded-full border text-sm font-semibold ${colors.badge}`}>
            {t(`home.trust_levels.${report.trust_level}` as Parameters<typeof t>[0])}
          </span>
        </div>

        {/* Score basis summary */}
        <p className="text-slate-600 text-xs text-center leading-relaxed max-w-xs mx-auto" dir="ltr">
          {t('results.score_based_on', {
            https: report.checks.https ? '✓' : '✗',
            ssl: report.checks.ssl_valid ? '✓' : '✗',
            headers: `${report.checks.headers_score}/${report.checks.headers_max}`,
            reputation: reputationLabel,
          })}
        </p>

        {/* Warnings */}
        {report.warnings.length > 0 && (
          <div className="mt-4 bg-amber-500/8 border border-amber-500/25 rounded-xl px-4 py-2.5">
            {report.warnings.map((w) => (
              <p key={w} className="text-amber-400 text-xs text-center">
                ⚠ {t(`results.warnings.${w}` as Parameters<typeof t>[0])}
              </p>
            ))}
          </div>
        )}
      </div>

      {/* Danger banner */}
      {isDangerous && <DangerBanner t={t} />}

      {/* Usage Decision */}
      <div className="bg-slate-900 border border-slate-700/80 rounded-2xl p-5 shadow-xl space-y-3">
        <p className="text-slate-400 text-xs uppercase tracking-wider font-medium">
          {t('results.decision.title')}
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {decisions.map(({ key, verdict }) => (
            <DecisionCard key={key} decisionKey={key} verdict={verdict} t={t} />
          ))}
        </div>
      </div>

      {/* Guidance — what this means + what to do — all trust levels */}
      <GuidanceSection trustLevel={trust_level} isDangerous={isDangerous} t={t} />

      {/* Security Checks */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl">
        <div className="px-5 py-3.5 border-b border-slate-800">
          <p className="text-slate-400 text-xs uppercase tracking-wider font-medium">
            {t('results.checks_title')}
          </p>
        </div>
        <div className="px-5 py-1 pb-3">
          <CheckRow label={t('results.checks.https')} passed={report.checks.https} />
          <CheckRow label={t('results.checks.ssl')} passed={report.checks.ssl_valid} />
          <div className="flex items-center justify-between py-2.5 border-b border-slate-800/60">
            <span className="text-slate-300 text-sm">{t('results.checks.headers')}</span>
            <span className="text-slate-400 text-sm tabular-nums">{headersLabel}</span>
          </div>
          <div className="flex items-center justify-between py-2.5">
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
      <div className="text-center pt-2">
        <button
          onClick={onReset}
          className="text-sm text-slate-400 hover:text-slate-100 transition-colors
                     px-5 py-2.5 rounded-xl hover:bg-slate-800 border border-transparent
                     hover:border-slate-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
        >
          {t('results.new_scan')}
        </button>
      </div>

      <p className="text-slate-600 text-xs text-center leading-relaxed px-4 pb-2">
        {t('results.advisor_note')}
      </p>
    </div>
  )
}
