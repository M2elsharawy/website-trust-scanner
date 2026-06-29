'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useTranslations, useLocale } from 'next-intl'
import { Link } from '@/i18n/navigation'
import FixPlan, { type FixPlanChecks } from '@/components/FixPlan'
import BrandLogo from '@/components/BrandLogo'
import LogoutButton from '@/components/LogoutButton'

const BACKEND = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

type TrustLevel = 'low' | 'medium' | 'good' | 'high'
type LoadStatus = 'loading' | 'ok' | 'unauthorized' | 'not_found' | 'error'

interface ScanDetail {
  trust_score: number
  result_json: {
    trust_level: TrustLevel
    checks: FixPlanChecks
  }
}

const LEVEL_COLORS: Record<TrustLevel, { ring: string; text: string; bg: string; badge: string }> = {
  high:   { ring: 'ring-emerald-500', text: 'text-emerald-400', bg: 'bg-emerald-500/10', badge: 'bg-emerald-950/50 text-emerald-400 border-emerald-800/60' },
  good:   { ring: 'ring-blue-500',    text: 'text-blue-400',    bg: 'bg-blue-500/10',    badge: 'bg-blue-950/50 text-blue-400 border-blue-800/60'          },
  medium: { ring: 'ring-amber-500',   text: 'text-amber-400',   bg: 'bg-amber-500/10',   badge: 'bg-amber-950/50 text-amber-400 border-amber-800/60'       },
  low:    { ring: 'ring-red-500',     text: 'text-red-400',     bg: 'bg-red-500/10',     badge: 'bg-red-950/50 text-red-400 border-red-800/60'             },
}

export default function ScanDetailPage() {
  const params = useParams()
  const router = useRouter()
  const locale = useLocale()
  const siteId = params.siteId as string
  const scanId = params.scanId as string
  const t = useTranslations()

  const [scan, setScan] = useState<ScanDetail | null>(null)
  const [status, setStatus] = useState<LoadStatus>('loading')

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch(
          `${BACKEND}/api/v1/sites/${encodeURIComponent(siteId)}/scans/${encodeURIComponent(scanId)}`,
          { credentials: 'include' },
        )
        if (res.status === 401 || res.status === 403) { setStatus('unauthorized'); return }
        if (res.status === 404) { setStatus('not_found'); return }
        if (!res.ok) { setStatus('error'); return }
        setScan(await res.json() as ScanDetail)
        setStatus('ok')
      } catch {
        setStatus('error')
      }
    }
    load()
  }, [siteId, scanId])

  if (status === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (status !== 'ok' || scan === null) {
    const msgKey =
      status === 'unauthorized' ? 'owner_scan.unauthorized' :
      status === 'not_found'    ? 'owner_scan.not_found'    :
                                  'owner_scan.error'
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <p className="text-slate-400 text-sm text-center">
          {t(msgKey as Parameters<typeof t>[0])}
        </p>
      </div>
    )
  }

  const { trust_level, checks } = scan.result_json
  const colors = LEVEL_COLORS[trust_level] ?? LEVEL_COLORS['medium']

  return (
    <div className="min-h-screen flex flex-col">
      <header className="flex justify-between items-center px-6 py-4 border-b border-slate-800">
        <BrandLogo href="/sites" />
        <LogoutButton />
      </header>

      <main className="flex-1 flex flex-col items-center justify-start p-6 pt-8">
        <div className="w-full max-w-xl space-y-4">
          {/* Back link */}
          <button
            onClick={() => router.push(`/${locale}/sites/${siteId}/scans`)}
            className="text-sm text-slate-400 hover:text-slate-200 transition-colors flex items-center gap-1.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 rounded"
          >
            ← {t('owner_scan.back_to_scans')}
          </button>

          {/* Score card */}
          <div className="bg-slate-900 border border-slate-700/80 rounded-2xl p-6 flex flex-col items-center gap-4 shadow-2xl shadow-black/30">
            <div dir="ltr" className="flex flex-col items-center gap-3">
              <div
                className={`w-28 h-28 rounded-full ring-4 ring-offset-2 ring-offset-slate-900 ${colors.ring} ${colors.bg}
                            flex flex-col items-center justify-center`}
              >
                <span className={`text-4xl font-bold tabular-nums ${colors.text}`}>{scan.trust_score}</span>
                <span className="text-slate-500 text-xs mt-0.5">/100</span>
              </div>
              <span className={`inline-flex items-center px-3 py-1 rounded-full border text-sm font-semibold ${colors.badge}`}>
                {t(`home.trust_levels.${trust_level}` as Parameters<typeof t>[0])}
              </span>
            </div>
          </div>

          {/* Disclaimer */}
          <p className="text-slate-600 text-xs text-center leading-relaxed px-2">
            {t('owner_scan.disclaimer')}
          </p>

          <FixPlan checks={checks} />
        </div>
      </main>
    </div>
  )
}
