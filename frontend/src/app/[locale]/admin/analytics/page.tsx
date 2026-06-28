import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import { getTranslations } from 'next-intl/server'
import { Link } from '@/i18n/navigation'

const BACKEND = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'
const ADMIN_ROLES = new Set(['admin', 'super_admin'])

interface Summary {
  total_users: number
  total_sites: number
  verified_sites: number
  total_scans: number
  risk_distribution: { critical: number; high: number; medium: number; low: number }
}

interface AuditEntry {
  id: number
  action: string
  outcome: string
  actor_role: string | null
  resource_type: string | null
  resource_id: string | null
  created_at: string | null
}

interface TrendDay {
  date: string | null
  scan_count: number
  avg_trust_score: number | null
}

interface ScanTrends {
  days: number
  trend: TrendDay[]
}

function isoToDate(iso: string | null): string {
  if (!iso) return '—'
  return iso.slice(0, 10)
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 px-5 py-4">
      <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">{label}</p>
      <p className="text-2xl font-semibold text-slate-100">{value.toLocaleString()}</p>
    </div>
  )
}

function RiskBadge({ level }: { level: string }) {
  const cls: Record<string, string> = {
    critical: 'bg-red-900/40 text-red-400 border-red-800/50',
    high: 'bg-orange-900/40 text-orange-400 border-orange-800/50',
    medium: 'bg-amber-900/40 text-amber-400 border-amber-800/50',
    low: 'bg-emerald-900/40 text-emerald-400 border-emerald-800/50',
  }
  return (
    <span className={`inline-block rounded px-2 py-0.5 text-xs border ${cls[level] ?? 'text-slate-400'}`}>
      {level}
    </span>
  )
}

export default async function AdminAnalyticsPage({
  params,
}: {
  params: Promise<{ locale: string }>
}) {
  const { locale } = await params
  const t = await getTranslations({ locale, namespace: 'admin_analytics' })
  const ta = await getTranslations({ locale, namespace: 'admin' })

  const cookieStore = await cookies()
  const token = cookieStore.get('access_token')?.value

  if (!token) {
    redirect(`/${locale}/login`)
  }

  let role = ''
  try {
    const res = await fetch(`${BACKEND}/api/v1/auth/me`, {
      headers: { Cookie: `access_token=${token}` },
      cache: 'no-store',
    })
    if (res.status === 401 || res.status === 403) redirect(`/${locale}/login`)
    if (!res.ok) redirect(`/${locale}`)
    ;({ role } = (await res.json()) as { role: string })
  } catch (err) {
    if ((err as { digest?: string }).digest?.startsWith('NEXT_REDIRECT')) throw err
    redirect(`/${locale}`)
  }

  if (!ADMIN_ROLES.has(role)) redirect(`/${locale}`)

  // ── Fetch analytics data ─────────────────────────────────────────────────────
  let summary: Summary | null = null
  let auditLog: AuditEntry[] = []
  let trends: ScanTrends | null = null
  let fetchError = false

  const headers = { Cookie: `access_token=${token}` }

  try {
    const [summaryRes, auditRes, trendsRes] = await Promise.all([
      fetch(`${BACKEND}/api/v1/admin/analytics/summary`, { headers, cache: 'no-store' }),
      fetch(`${BACKEND}/api/v1/admin/analytics/audit-log?limit=20`, { headers, cache: 'no-store' }),
      fetch(`${BACKEND}/api/v1/admin/analytics/scan-trends?days=30`, { headers, cache: 'no-store' }),
    ])

    if (summaryRes.ok) summary = (await summaryRes.json()) as Summary
    if (auditRes.ok) auditLog = (await auditRes.json()) as AuditEntry[]
    if (trendsRes.ok) trends = (await trendsRes.json()) as ScanTrends

    if (!summaryRes.ok && !auditRes.ok && !trendsRes.ok) fetchError = true
  } catch (err) {
    if ((err as { digest?: string }).digest?.startsWith('NEXT_REDIRECT')) throw err
    fetchError = true
  }

  const riskOrder = ['critical', 'high', 'medium', 'low'] as const

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-4xl mx-auto space-y-8">

        {/* Breadcrumb */}
        <div className="flex items-center gap-2 text-sm flex-wrap">
          <Link href="/admin" className="text-slate-400 hover:text-slate-200 transition-colors">
            {ta('title')}
          </Link>
          <span className="text-slate-600">/</span>
          <span className="text-slate-200">{t('title')}</span>
        </div>

        {/* Header */}
        <div className="space-y-1">
          <h1 className="text-xl font-semibold text-slate-100">{t('title')}</h1>
          <p className="text-slate-400 text-sm">{t('subtitle')}</p>
        </div>

        {fetchError && (
          <p className="text-slate-400 text-sm">{t('error')}</p>
        )}

        {/* Summary cards */}
        {summary && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <StatCard label={t('summary.total_users')} value={summary.total_users} />
            <StatCard label={t('summary.total_sites')} value={summary.total_sites} />
            <StatCard label={t('summary.verified_sites')} value={summary.verified_sites} />
            <StatCard label={t('summary.total_scans')} value={summary.total_scans} />
          </div>
        )}

        {/* Risk distribution */}
        {summary && (
          <div className="space-y-3">
            <div>
              <h2 className="text-sm font-medium text-slate-200">{t('risk.title')}</h2>
              <p className="text-xs text-slate-500 mt-0.5">{t('risk.subtitle')}</p>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {riskOrder.map((level) => (
                <div key={level} className="rounded-xl border border-slate-800 bg-slate-900 px-4 py-3 flex items-center justify-between">
                  <RiskBadge level={level} />
                  <span className="text-lg font-semibold text-slate-100">
                    {summary!.risk_distribution[level]}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Scan trends */}
        {trends && (
          <div className="space-y-3">
            <h2 className="text-sm font-medium text-slate-200">{t('trends.title')}</h2>
            {trends.trend.length === 0 ? (
              <p className="text-slate-500 text-sm">{t('trends.empty')}</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm border-collapse">
                  <thead>
                    <tr className="text-left text-xs text-slate-500 uppercase tracking-wide border-b border-slate-800">
                      <th className="pb-2 pr-4">{t('trends.columns.date')}</th>
                      <th className="pb-2 pr-4 text-right">{t('trends.columns.count')}</th>
                      <th className="pb-2 text-right">{t('trends.columns.avg_score')}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/50">
                    {[...trends.trend].reverse().slice(0, 14).map((row, i) => (
                      <tr key={i} className="text-slate-300">
                        <td className="py-2 pr-4 font-mono text-xs">{row.date ?? '—'}</td>
                        <td className="py-2 pr-4 text-right">{row.scan_count}</td>
                        <td className="py-2 text-right">
                          {row.avg_trust_score !== null ? row.avg_trust_score : '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Audit log */}
        <div className="space-y-3">
          <h2 className="text-sm font-medium text-slate-200">{t('audit.title')}</h2>
          {auditLog.length === 0 ? (
            <p className="text-slate-500 text-sm">{t('audit.empty')}</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm border-collapse">
                <thead>
                  <tr className="text-left text-xs text-slate-500 uppercase tracking-wide border-b border-slate-800">
                    <th className="pb-2 pr-4">{t('audit.columns.action')}</th>
                    <th className="pb-2 pr-4">{t('audit.columns.outcome')}</th>
                    <th className="pb-2 pr-4">{t('audit.columns.role')}</th>
                    <th className="pb-2 pr-4">{t('audit.columns.resource')}</th>
                    <th className="pb-2">{t('audit.columns.time')}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/50">
                  {auditLog.map((entry) => (
                    <tr key={entry.id} className="text-slate-300">
                      <td className="py-2 pr-4 font-mono text-xs">{entry.action}</td>
                      <td className="py-2 pr-4">
                        <span className={entry.outcome === 'success' ? 'text-emerald-400' : 'text-red-400'}>
                          {entry.outcome}
                        </span>
                      </td>
                      <td className="py-2 pr-4 text-slate-400 text-xs">{entry.actor_role ?? '—'}</td>
                      <td className="py-2 pr-4 text-xs font-mono text-slate-400">
                        {entry.resource_type ? `${entry.resource_type}` : '—'}
                      </td>
                      <td className="py-2 text-xs font-mono text-slate-500">
                        {isoToDate(entry.created_at)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

      </div>
    </div>
  )
}
