'use client'

import { useTranslations } from 'next-intl'
import { Link } from '@/i18n/navigation'

export default function AppFooter() {
  const t = useTranslations('footer')

  return (
    <footer className="border-t border-slate-800/60 py-7 px-6">
      <div className="max-w-4xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
        <p className="text-slate-500 text-xs">{t('tagline')}</p>
        <nav className="flex items-center gap-5 text-xs text-slate-500" aria-label="Footer navigation">
          <Link
            href="/roadmap"
            className="hover:text-slate-300 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 rounded"
          >
            {t('roadmap_link')}
          </Link>
          <Link
            href="/terms"
            className="hover:text-slate-300 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 rounded"
          >
            {t('terms_link')}
          </Link>
          <Link
            href="/privacy"
            className="hover:text-slate-300 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 rounded"
          >
            {t('privacy_link')}
          </Link>
        </nav>
      </div>
    </footer>
  )
}
