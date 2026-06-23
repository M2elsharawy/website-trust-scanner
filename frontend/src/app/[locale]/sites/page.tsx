'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { useTranslations } from 'next-intl'
import Link from 'next/link'

const BACKEND = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

type SiteStatus = 'pending' | 'active' | 'suspended'
type LoadStatus = 'loading' | 'ok' | 'unauthorized' | 'error'

interface SiteItem {
  id: string
  domain: string
  status: SiteStatus
}

const STATUS_STYLES: Record<SiteStatus, string> = {
  active:    'text-emerald-400',
  pending:   'text-amber-400',
  suspended: 'text-red-400',
}

export default function SitesListPage() {
  const params = useParams()
  const locale = params.locale as string
  const t = useTranslations('owner_sites')

  const [sites, setSites] = useState<SiteItem[]>([])
  const [loadStatus, setLoadStatus] = useState<LoadStatus>('loading')

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch(`${BACKEND}/api/v1/sites`, { credentials: 'include' })
        if (res.status === 401 || res.status === 403) { setLoadStatus('unauthorized'); return }
        if (!res.ok) { setLoadStatus('error'); return }
        setSites(await res.json() as SiteItem[])
        setLoadStatus('ok')
      } catch {
        setLoadStatus('error')
      }
    }
    load()
  }, [])

  if (loadStatus === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (loadStatus === 'unauthorized') {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <p className="text-slate-400 text-sm text-center">{t('unauthorized')}</p>
      </div>
    )
  }

  if (loadStatus === 'error') {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <p className="text-slate-400 text-sm text-center">{t('error')}</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6">
      <div className="w-full max-w-xl space-y-4">
        <h1 className="text-xl font-semibold text-slate-100">{t('title')}</h1>

        {sites.length === 0 ? (
          <p className="text-slate-400 text-sm">{t('empty')}</p>
        ) : (
          <ul className="space-y-3">
            {sites.map((site) => (
              <li
                key={site.id}
                className="bg-slate-900 border border-slate-700 rounded-2xl p-4 flex items-center justify-between gap-4"
              >
                <div className="flex flex-col gap-1 min-w-0">
                  <span className="text-slate-100 font-medium truncate">{site.domain}</span>
                  <span className={`text-xs ${STATUS_STYLES[site.status] ?? 'text-slate-400'}`}>
                    {t(`status_${site.status}` as 'status_active' | 'status_pending' | 'status_suspended')}
                  </span>
                </div>
                {site.status === 'active' && (
                  <Link
                    href={`/${locale}/sites/${encodeURIComponent(site.id)}/scans`}
                    className="shrink-0 text-xs text-blue-400 hover:text-blue-300 underline underline-offset-2"
                  >
                    {t('view_scans')}
                  </Link>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
