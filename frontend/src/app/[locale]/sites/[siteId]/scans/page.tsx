'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { useTranslations, useLocale } from 'next-intl'
import { Link } from '@/i18n/navigation'
import BrandLogo from '@/components/BrandLogo'
import LogoutButton from '@/components/LogoutButton'

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

function scoreBadgeBg(score: number): string {
  if (score >= 80) return 'bg-emerald-950/30 ring-1 ring-emerald-800/40'
  if (score >= 60) return 'bg-blue-950/30 ring-1 ring-blue-800/40'
  if (score >= 40) return 'bg-amber-950/30 ring-1 ring-amber-800/40'
  return 'bg-red-950/30 ring-1 ring-red-800/40'
}

export default function SiteScansListPage() {
  const params = useParams()
  const locale = useLocale()
  const siteId = params.siteId as string
  const t = useTranslations('owner_scans_list')

  const [scans, setScans] = useState<ScanSummary[]>([])
  const [loadStatus, setLoadStatus] = useState<LoadStatus>('loading')
  const [retryKey, setRetryKey] = useState(0)

  useEffect(() => {
    setLoadStatus('loading')
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
  }, [siteId, retryKey])

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
    const canRetry = loadStatus === 'error'
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <div className="text-center space-y-3">
          <p className="text-slate-400 text-sm">
            {t(msgKey as Parameters<typeof t>[0])}
          </p>
          {canRetry && (
            <button
              onClick={() => setRetryKey((k) => k + 1)}
              className="text-sm text-blue-400 hover:text-blue-300 transition-colors px-4 py-1.5 rounded-lg border border-blue-800/50 hover:bg-blue-950/20"
            >
              {t('retry')}
            </button>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex flex-col">
      <header className="flex justify-between items-center px-6 py-4 border-b border-slate-800">
        <BrandLogo href="/sites" />
        <LogoutButton />
      </header>

      <main className="flex-1 flex flex-col items-center justify-start p-6 pt-8">
        <div className="w-full max-w-xl space-y-4">
          <Link
            href="/sites"
            className="inline-flex items-center gap-1.5 text-sm text-slate-400 hover:text-slate-200 transition-colors"
          >
            ← {t('back_to_sites')}
          </Link>
          <h1 className="text-xl font-semibold text-slate-100">{t('title')}</h1>

          {scans.length === 0 ? (
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 text-center space-y-2">
              <p className="text-slate-400 text-sm">{t('empty')}</p>
              <p className="text-slate-600 text-xs leading-relaxed">{t('empty_hint')}</p>
            </div>
          ) : (
            <ul className="space-y-3">
              {scans.map((scan) => (
                <li
                  key={scan.id}
                  className="bg-slate-900 border border-slate-700/80 rounded-2xl p-4 flex items-center justify-between gap-4"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-12 h-12 rounded-xl flex flex-col items-center justify-center ${scoreBadgeBg(scan.trust_score)}`}>
                      <span className={`text-lg font-bold tabular-nums ${scoreColor(scan.trust_score)}`}>
                        {scan.trust_score}
                      </span>
                    </div>
                    <span className="text-slate-400 text-xs">
                      {new Date(scan.scanned_at).toLocaleString(locale)}
                    </span>
                  </div>
                  <Link
                    href={`/sites/${encodeURIComponent(siteId)}/scans/${encodeURIComponent(scan.id)}`}
                    className="shrink-0 text-xs text-blue-400 hover:text-blue-300 transition-colors
                               px-3 py-1.5 rounded-lg border border-blue-800/50 hover:border-blue-700/60
                               hover:bg-blue-950/30"
                  >
                    {t('view_details')}
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </div>
      </main>
    </div>
  )
}
