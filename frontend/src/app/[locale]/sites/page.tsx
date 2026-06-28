'use client'

import { useEffect, useState } from 'react'
import { useTranslations, useLocale } from 'next-intl'
import { Link } from '@/i18n/navigation'
import BrandLogo from '@/components/BrandLogo'
import LogoutButton from '@/components/LogoutButton'

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

function StatusDot({ status }: { status: SiteStatus }) {
  const colors: Record<SiteStatus, string> = {
    active:    'bg-emerald-400',
    pending:   'bg-amber-400',
    suspended: 'bg-red-400',
  }
  return <span className={`inline-block w-1.5 h-1.5 rounded-full ${colors[status]} me-1.5`} />
}

export default function SitesListPage() {
  const t = useTranslations('owner_sites')
  const ta = useTranslations('auth')
  const locale = useLocale()

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
        <div className="text-center space-y-3">
          <p className="text-slate-400 text-sm">{t('unauthorized')}</p>
          <Link
            href={`/login?next=/${locale}/sites`}
            className="inline-block text-sm text-blue-400 hover:text-blue-300 hover:underline"
          >
            {ta('login')}
          </Link>
        </div>
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
    <div className="min-h-screen flex flex-col">
      <header className="flex justify-between items-center px-6 py-4 border-b border-slate-800">
        <BrandLogo href="/sites" />
        <LogoutButton />
      </header>

      <main className="flex-1 flex flex-col items-center justify-center p-6">
        <div className="w-full max-w-xl space-y-4">
          <h1 className="text-xl font-semibold text-slate-100">{t('title')}</h1>

          {sites.length === 0 ? (
            <p className="text-slate-400 text-sm">{t('empty')}</p>
          ) : (
            <ul className="space-y-3">
              {sites.map((site) => (
                <li
                  key={site.id}
                  className="bg-slate-900 border border-slate-700/80 rounded-2xl p-4 flex items-center justify-between gap-4"
                >
                  <div className="flex flex-col gap-1 min-w-0">
                    <span className="text-slate-100 font-medium truncate">{site.domain}</span>
                    <span className={`text-xs flex items-center ${STATUS_STYLES[site.status] ?? 'text-slate-400'}`}>
                      <StatusDot status={site.status} />
                      {t(`status_${site.status}` as 'status_active' | 'status_pending' | 'status_suspended')}
                    </span>
                    {site.status === 'pending' && (
                      <span className="text-xs text-slate-500 mt-0.5">
                        {t('pending_hint')}
                      </span>
                    )}
                  </div>
                  {site.status === 'active' && (
                    <Link
                      href={`/sites/${encodeURIComponent(site.id)}/scans`}
                      className="shrink-0 text-xs text-blue-400 hover:text-blue-300 transition-colors
                                 px-3 py-1.5 rounded-lg border border-blue-800/50 hover:border-blue-700/60
                                 hover:bg-blue-950/30"
                    >
                      {t('view_scans')}
                    </Link>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      </main>
    </div>
  )
}
