import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import { getTranslations } from 'next-intl/server'
import { Link } from '@/i18n/navigation'

const BACKEND = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'
const ADMIN_ROLES = new Set(['admin', 'super_admin'])

interface LeadDetail {
  id: string
  domain: string
  status: string
  last_lead_score: number | null
  last_audit_at: string | null
  created_at: string
  updated_at: string
  notes: string | null
}

function isoToDate(iso: string | null): string {
  if (!iso) return '—'
  return iso.slice(0, 10)
}

function Row({ label, value, mono = false }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="flex items-start gap-4 px-4 py-3">
      <dt className="w-32 flex-shrink-0 text-xs text-slate-500 uppercase tracking-wide pt-0.5">
        {label}
      </dt>
      <dd className={`text-sm text-slate-200 break-all ${mono ? 'font-mono' : ''}`}>{value}</dd>
    </div>
  )
}

export default async function AdminLeadDetailPage({
  params,
}: {
  params: Promise<{ locale: string; id: string }>
}) {
  const { locale, id } = await params
  const t = await getTranslations({ locale, namespace: 'admin_lead_detail' })
  const tl = await getTranslations({ locale, namespace: 'admin_leads' })
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

  // ── Fetch lead detail ────────────────────────────────────────────────────────
  let lead: LeadDetail | null = null
  let fetchError = false
  let notFound = false
  try {
    const res = await fetch(`${BACKEND}/api/v1/admin/leads/${id}`, {
      headers: { Cookie: `access_token=${token}` },
      cache: 'no-store',
    })
    if (res.status === 401 || res.status === 403) {
      redirect(`/${locale}/login`)
    }
    if (res.status === 404) {
      notFound = true
    } else if (res.ok) {
      lead = (await res.json()) as LeadDetail
    } else {
      fetchError = true
    }
  } catch (err) {
    if ((err as { digest?: string }).digest?.startsWith('NEXT_REDIRECT')) throw err
    fetchError = true
  }

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-2xl mx-auto space-y-6">

        {/* Breadcrumb */}
        <div className="flex items-center gap-2 text-sm flex-wrap">
          <Link href="/admin" className="text-slate-400 hover:text-slate-200 transition-colors">
            {ta('title')}
          </Link>
          <span className="text-slate-600">/</span>
          <Link href="/admin/leads" className="text-slate-400 hover:text-slate-200 transition-colors">
            {tl('title')}
          </Link>
          <span className="text-slate-600">/</span>
          <span className="text-slate-200 font-mono text-xs truncate max-w-[160px]">
            {lead?.domain ?? t('title')}
          </span>
        </div>

        {/* Not found */}
        {notFound && (
          <p className="text-slate-400 text-sm">{t('not_found')}</p>
        )}

        {/* Error */}
        {fetchError && (
          <p className="text-slate-400 text-sm">{t('error')}</p>
        )}

        {/* Detail card */}
        {lead && (
          <div className="space-y-4">
            <h1 className="text-xl font-semibold text-slate-100 font-mono break-all">
              {lead.domain}
            </h1>

            {/* Surface-level disclaimer */}
            <div className="rounded-lg border border-slate-700/50 bg-slate-800/30 px-4 py-3">
              <p className="text-xs text-slate-400">{t('disclaimer')}</p>
            </div>

            <dl className="bg-slate-900 border border-slate-800 rounded-xl divide-y divide-slate-800">
              <Row label={t('fields.domain')} value={lead.domain} mono />
              <Row
                label={t('fields.status')}
                value={tl(`status.${lead.status}` as Parameters<typeof tl>[0])}
              />
              <Row
                label={t('fields.score')}
                value={lead.last_lead_score !== null ? String(lead.last_lead_score) : '—'}
              />
              <Row label={t('fields.last_audit')} value={isoToDate(lead.last_audit_at)} />
              <Row label={t('fields.created')} value={isoToDate(lead.created_at)} />
              <Row label={t('fields.updated')} value={isoToDate(lead.updated_at)} />
              {lead.notes && <Row label={t('fields.notes')} value={lead.notes} />}
            </dl>
          </div>
        )}

      </div>
    </div>
  )
}
