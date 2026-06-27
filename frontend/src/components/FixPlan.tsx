'use client'

import { useTranslations } from 'next-intl'
import CopyButton from './CopyButton'

export interface FixPlanChecks {
  https: boolean
  ssl_valid: boolean
  ssl_expiry_warning: boolean
  hsts: boolean
  headers_score: number
  headers_max: number
  reputation: 'clean' | 'flagged' | 'unknown'
}

type Priority = 'critical' | 'high' | 'medium' | 'warning'

interface IssueItem {
  key: 'no_https' | 'ssl_invalid' | 'ssl_expiry_soon' | 'no_hsts' | 'weak_headers' | 'bad_reputation'
  priority: Priority
}

const PRIORITY_STYLES: Record<Priority, { border: string; bg: string; badge: string }> = {
  critical: { border: 'border-red-800/50',    bg: 'bg-red-950/20',    badge: 'text-red-400 bg-red-950/40 border-red-800/60'    },
  high:     { border: 'border-orange-800/50', bg: 'bg-orange-950/20', badge: 'text-orange-400 bg-orange-950/40 border-orange-800/60' },
  medium:   { border: 'border-amber-800/50',  bg: 'bg-amber-950/20',  badge: 'text-amber-400 bg-amber-950/40 border-amber-800/60'  },
  warning:  { border: 'border-purple-800/50', bg: 'bg-purple-950/20', badge: 'text-purple-400 bg-purple-950/40 border-purple-800/60' },
}

function deriveIssues(checks: FixPlanChecks): IssueItem[] {
  const issues: IssueItem[] = []

  if (checks.reputation === 'flagged') {
    issues.push({ key: 'bad_reputation', priority: 'warning' })
  }
  if (!checks.https) {
    issues.push({ key: 'no_https', priority: 'critical' })
  }
  if (!checks.ssl_valid) {
    issues.push({ key: 'ssl_invalid', priority: 'critical' })
  }
  if (checks.ssl_expiry_warning) {
    issues.push({ key: 'ssl_expiry_soon', priority: 'high' })
  }
  if (checks.https && !checks.hsts) {
    issues.push({ key: 'no_hsts', priority: 'medium' })
  }
  if (checks.headers_score < checks.headers_max) {
    issues.push({ key: 'weak_headers', priority: 'medium' })
  }

  return issues
}

function IssueCard({
  item,
  t,
}: {
  item: IssueItem
  t: ReturnType<typeof useTranslations>
}) {
  const styles = PRIORITY_STYLES[item.priority]
  const issueKey = `fix_plan.issues.${item.key}` as const

  const developerText = t(`${issueKey}.developer_text` as Parameters<typeof t>[0])
  const copyLabel = t('fix_plan.copy_for_developer' as Parameters<typeof t>[0])
  const copiedLabel = t('fix_plan.copied' as Parameters<typeof t>[0])
  const priorityLabel = t(`fix_plan.priority.${item.priority}` as Parameters<typeof t>[0])

  return (
    <div className={`rounded-xl border p-4 space-y-3 ${styles.border} ${styles.bg}`}>
      <div className="flex items-start justify-between gap-3">
        <span className="text-slate-200 text-sm font-medium leading-snug">
          {t(`${issueKey}.title` as Parameters<typeof t>[0])}
        </span>
        <span className={`flex-shrink-0 text-xs px-2 py-0.5 rounded border font-medium ${styles.badge}`}>
          {priorityLabel}
        </span>
      </div>

      <div className="space-y-1.5">
        <p className="text-slate-500 text-xs uppercase tracking-wide font-medium">
          {t('fix_plan.why_label' as Parameters<typeof t>[0])}
        </p>
        <p className="text-slate-300 text-xs leading-relaxed">
          {t(`${issueKey}.why` as Parameters<typeof t>[0])}
        </p>
      </div>

      <div className="space-y-1.5">
        <p className="text-slate-500 text-xs uppercase tracking-wide font-medium">
          {t('fix_plan.how_label' as Parameters<typeof t>[0])}
        </p>
        <p className="text-slate-300 text-xs leading-relaxed">
          {t(`${issueKey}.how` as Parameters<typeof t>[0])}
        </p>
      </div>

      <div className="pt-1 border-t border-slate-800 flex justify-end">
        <CopyButton text={developerText} label={copyLabel} copiedLabel={copiedLabel} />
      </div>
    </div>
  )
}

export default function FixPlan({ checks }: { checks: FixPlanChecks }) {
  const t = useTranslations()
  const issues = deriveIssues(checks)

  return (
    <div className="w-full space-y-3">
      <p className="text-slate-400 text-xs uppercase tracking-wider">
        {t('fix_plan.title')}
      </p>

      {issues.length === 0 ? (
        <div className="bg-slate-900 border border-emerald-800/40 rounded-xl p-4">
          <p className="text-emerald-400 text-sm text-center">
            {t('fix_plan.no_issues')}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {issues.map((item) => (
            <IssueCard key={item.key} item={item} t={t} />
          ))}
        </div>
      )}
    </div>
  )
}
