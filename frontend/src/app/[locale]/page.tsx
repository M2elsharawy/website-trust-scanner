import { use } from 'react'
import { useTranslations } from 'next-intl'
import { Link } from '@/i18n/navigation'
import ScanForm from '@/components/ScanForm'

export default function HomePage({
  params,
}: {
  params: Promise<{ locale: string }>
}) {
  const { locale } = use(params)
  const t = useTranslations()

  const otherLocale = locale === 'ar' ? 'en' : 'ar'
  const otherLocaleLabel = t('common.switch_language')

  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="flex justify-between items-center px-6 py-4 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white text-sm font-bold">T</span>
          </div>
          <span className="font-semibold text-slate-100">
            {t('common.app_name')}
          </span>
        </div>
        <Link
          href="/"
          locale={otherLocale}
          className="text-sm text-slate-400 hover:text-slate-100 transition-colors px-3 py-1.5 rounded-lg hover:bg-slate-800"
        >
          {otherLocaleLabel}
        </Link>
      </header>

      {/* Main */}
      <main className="flex-1 flex items-center justify-center px-4 py-16">
        <ScanForm apiUrl={apiUrl} />
      </main>

      {/* Footer */}
      <footer className="text-center py-6 border-t border-slate-900 space-y-1">
        <p className="text-slate-700 text-xs">{t('footer.tagline')}</p>
        <Link
          href="/roadmap"
          className="text-slate-600 hover:text-slate-400 text-xs transition-colors"
        >
          {t('footer.roadmap_link')}
        </Link>
      </footer>
    </div>
  )
}
