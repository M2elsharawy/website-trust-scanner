'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { Link } from '@/i18n/navigation'

const BACKEND = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

type LoadStatus = 'loading' | 'ok' | 'unauthorized' | 'not_found' | 'error'

interface ScanSummary {
  id: string
  trust_score: number
  scanned_at: string
}

function scoreColor(score: number): string {
  if (score >= 80) return 'text-emerald-400'
  if (score >= 60) return 'text-blue-400'
  if (score >= 40) return 'text-amber-400'
  return 'text-red-400'
}

export default function SiteScansListPage() {
  const params = useParams()
  const locale = params.locale as string
  const siteId = params.siteId as string
  const t = useTranslations('owner_scans_list')

  const [scans, setScans] = useState<ScanSummary[]>([])
  const [loadStatus, setLoadStatus] = useState<LoadStatus>('loading')

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch(
          `${BACKEND}/api/v1/sites/${encodeURIComponent(siteId)}/scans`,
          { credentials: 'include' },
        )
        if (res.status === 401 || res.status === 403) { setLoadStatus('unauthorized'); return }
        if (res.status === 404) { setLoadStatus('not_found'); return }
        if (!res.ok) { setLoadStatus('error'); return }
        setScans(await res.json() as ScanSummary[])
        setLoadStatus('ok')
      } catch {
        setLoadStatus('error')
      }
    }
    load()
  }, [siteId])

  if (loadStatus === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (loadStatus !== 'ok') {
    const msgKey =
      loadStatus === 'unauthorized' ? 'unauthorized' :
      loadStatus === 'not_found'    ? 'not_found'    :
                                      'error'
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <p className="text-slate-400 text-sm text-center">
          {t(msgKey as Parameters<typeof t>[0])}
        </p>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6">
      <div className="w-full max-w-xl space-y-4">
        <h1 className="text-xl font-semibold text-slate-100">{t('title')}</h1>

        {scans.length === 0 ? (
          <p className="text-slate-400 text-sm">{t('empty')}</p>
        ) : (
          <ul className="space-y-3">
            {scans.map((scan) => (
              <li
                key={scan.id}
                className="bg-slate-900 border border-slate-700 rounded-2xl p-4 flex items-center justify-between gap-4"
              >
                <div className="flex flex-col gap-1">
                  <span className={`text-2xl font-bold ${scoreColor(scan.trust_score)}`}>
                    {scan.trust_score}
                    <span className="text-slate-500 text-xs font-normal">/100</span>
                  </span>
                  <span className="text-slate-400 text-xs">
                    {new Date(scan.scanned_at).toLocaleString(locale)}
                  </span>
                </div>
                <Link
                  href={`/sites/${encodeURIComponent(siteId)}/scans/${encodeURIComponent(scan.id)}`}
                  className="shrink-0 text-xs text-blue-400 hover:text-blue-300 underline underline-offset-2"
                >
                  {t('view_details')}
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
