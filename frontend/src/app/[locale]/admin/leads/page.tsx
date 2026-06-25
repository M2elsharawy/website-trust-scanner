import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import { getTranslations } from 'next-intl/server'
import { Link } from '@/i18n/navigation'

const BACKEND = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'
const ADMIN_ROLES = new Set(['admin', 'super_admin'])

interface LeadSummary {
  id: string
  domain: string
  status: string
  last_lead_score: number | null
  last_audit_at: string | null
  created_at: string
}

function isoToDate(iso: string | null): string {
  if (!iso) return '—'
  return iso.slice(0, 10)
}

export default async function AdminLeadsPage({
  params,
}: {
  params: Promise<{ locale: string }>
}) {
  const { locale } = await params
  const t = await getTranslations({ locale, namespace: 'admin_leads' })
  const ta = await getTranslations({ locale, namespace: 'admin' })

  const cookieStore = await cookies()
  const token = cookieStore.get('access_token')?.value

  if (!token) {
    redirect(`/${locale}/login`)
  }

  // ── Auth check ──────────────────────────────────────────────────────────────
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

  // ── Fetch leads ─────────────────────────────────────────────────────────────
  let leads: LeadSummary[] = []
  let fetchError = false
  try {
    const res = await fetch(`${BACKEND}/api/v1/admin/leads`, {
      headers: { Cookie: `access_token=${token}` },
      cache: 'no-store',
    })
    if (res.status === 401 || res.status === 403) {
      redirect(`/${locale}/login`)
    }
    if (res.ok) {
      leads = (await res.json()) as LeadSummary[]
    } else {
      fetchError = true
    }
  } catch (err) {
    if ((err as { digest?: string }).digest?.startsWith('NEXT_REDIRECT')) throw err
    fetchError = true
  }

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-5xl mx-auto space-y-6">

        {/* Breadcrumb */}
        <div className="flex items-center gap-2 text-sm">
          <Link href="/admin" className="text-slate-400 hover:text-slate-200 transition-colors">
            {ta('title')}
          </Link>
          <span className="text-slate-600">/</span>
          <span className="text-slate-200">{t('title')}</span>
        </div>

        <h1 className="text-xl font-semibold text-slate-100">{t('title')}</h1>

        {/* Error state */}
        {fetchError && (
          <p className="text-slate-400 text-sm">{t('error')}</p>
        )}

        {/* Empty state */}
        {!fetchError && leads.length === 0 && (
          <p className="text-slate-400 text-sm">{t('empty')}</p>
        )}

        {/* Table */}
        {!fetchError && leads.length > 0 && (
          <div className="overflow-x-auto rounded-xl border border-slate-800">
            <table className="w-full text-sm text-left">
              <thead className="bg-slate-900 text-slate-400 text-xs uppercase tracking-wide">
                <tr>
                  <th className="px-4 py-3">{t('columns.domain')}</th>
                  <th className="px-4 py-3">{t('columns.status')}</th>
                  <th className="px-4 py-3">{t('columns.score')}</th>
                  <th className="px-4 py-3">{t('columns.last_audit')}</th>
                  <th className="px-4 py-3">{t('columns.created')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {leads.map((lead) => (
                  <tr key={lead.id} className="bg-slate-950 hover:bg-slate-900 transition-colors">
                    <td className="px-4 py-3 font-mono text-slate-200">{lead.domain}</td>
                    <td className="px-4 py-3 text-slate-300">
                      {t(`status.${lead.status}` as Parameters<typeof t>[0])}
                    </td>
                    <td className="px-4 py-3 text-slate-300">
                      {lead.last_lead_score !== null ? lead.last_lead_score : '—'}
                    </td>
                    <td className="px-4 py-3 text-slate-400">{isoToDate(lead.last_audit_at)}</td>
                    <td className="px-4 py-3 text-slate-400">{isoToDate(lead.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

      </div>
    </div>
  )
}
