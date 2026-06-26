'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useTranslations, useLocale } from 'next-intl'
import FixPlan, { type FixPlanChecks } from '@/components/FixPlan'

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

const LEVEL_COLORS: Record<TrustLevel, { ring: string; text: string; bg: string }> = {
  high:   { ring: 'ring-emerald-500', text: 'text-emerald-400', bg: 'bg-emerald-500/10' },
  good:   { ring: 'ring-blue-500',    text: 'text-blue-400',    bg: 'bg-blue-500/10'    },
  medium: { ring: 'ring-amber-500',   text: 'text-amber-400',   bg: 'bg-amber-500/10'   },
  low:    { ring: 'ring-red-500',     text: 'text-red-400',     bg: 'bg-red-500/10'     },
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
    <div className="min-h-screen flex flex-col items-center justify-start p-6 pt-10">
      <div className="w-full max-w-xl space-y-4">

        {/* Back link */}
        <button
          onClick={() => router.push(`/${locale}/sites/${siteId}/scans`)}
          className="text-sm text-slate-400 hover:text-slate-200 transition-colors flex items-center gap-1"
        >
          ← {t('owner_scan.back_to_scans')}
        </button>

        {/* Score card */}
        <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 flex flex-col items-center gap-3">
          <div
            className={`w-24 h-24 rounded-full ring-4 ${colors.ring} ${colors.bg}
                        flex flex-col items-center justify-center`}
          >
            <span className={`text-4xl font-bold ${colors.text}`}>{scan.trust_score}</span>
            <span className="text-slate-500 text-xs">/100</span>
          </div>
          <span className={`text-lg font-semibold ${colors.text}`}>
            {t(`home.trust_levels.${trust_level}` as Parameters<typeof t>[0])}
          </span>
        </div>

        {/* Disclaimer */}
        <p className="text-slate-600 text-xs text-center leading-relaxed px-2">
          {t('owner_scan.disclaimer')}
        </p>

        <FixPlan checks={checks} />
      </div>
    </div>
  )
}
