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
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 px-4 py-3">
      <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">{label}</p>
      <p className="text-xl font-semibold text-slate-100">{value.toLocaleString()}</p>
    </div>
  )
}

export default async function AdminPage({
  params,
}: {
  params: Promise<{ locale: string }>
}) {
  const { locale } = await params
  const t = await getTranslations({ locale, namespace: 'admin' })
  const ta = await getTranslations({ locale, namespace: 'admin_analytics' })

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
    if (res.status === 401 || res.status === 403) {
      redirect(`/${locale}/login`)
    }
    if (!res.ok) {
      redirect(`/${locale}`)
    }
    ;({ role } = (await res.json()) as { role: string })
  } catch (err) {
    if ((err as { digest?: string }).digest?.startsWith('NEXT_REDIRECT')) throw err
    redirect(`/${locale}`)
  }

  if (!ADMIN_ROLES.has(role)) {
    redirect(`/${locale}`)
  }

  // ── Fetch summary stats ──────────────────────────────────────────────────────
  let summary: Summary | null = null
  try {
    const res = await fetch(`${BACKEND}/api/v1/admin/analytics/summary`, {
      headers: { Cookie: `access_token=${token}` },
      cache: 'no-store',
    })
    if (res.ok) summary = (await res.json()) as Summary
  } catch {
    // non-blocking — page still renders without stats
  }

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-xl mx-auto space-y-6">

        <div className="space-y-1">
          <h1 className="text-xl font-semibold text-slate-100">{t('title')}</h1>
          <p className="text-slate-400 text-sm">{t('subtitle')}</p>
        </div>

        {/* Read-only MVP notice */}
        <div className="rounded-lg border border-amber-800/50 bg-amber-950/30 px-4 py-3">
          <p className="text-xs text-amber-400">{t('notice')}</p>
        </div>

        {/* Summary stats */}
        {summary && (
          <div className="grid grid-cols-2 gap-3">
            <StatCard label={ta('summary.total_users')} value={summary.total_users} />
            <StatCard label={ta('summary.total_sites')} value={summary.total_sites} />
            <StatCard label={ta('summary.verified_sites')} value={summary.verified_sites} />
            <StatCard label={ta('summary.total_scans')} value={summary.total_scans} />
          </div>
        )}

        {/* Navigation */}
        <nav className="space-y-2">
          <Link
            href="/admin/leads"
            className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900 px-4 py-3 hover:bg-slate-800 transition-colors"
          >
            <span className="text-sm text-slate-200">{t('view_leads')}</span>
            <span className="text-slate-500 text-sm">→</span>
          </Link>
          <Link
            href="/admin/analytics"
            className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900 px-4 py-3 hover:bg-slate-800 transition-colors"
          >
            <span className="text-sm text-slate-200">{t('view_analytics')}</span>
            <span className="text-slate-500 text-sm">→</span>
          </Link>
        </nav>

      </div>
    </div>
  )
}
