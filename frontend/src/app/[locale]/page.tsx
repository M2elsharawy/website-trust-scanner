import { useTranslations } from 'next-intl'
import { Link } from '@/i18n/navigation'

export default function HomePage({
  params: { locale },
}: {
  params: { locale: string }
}) {
  const t = useTranslations()

  const otherLocale = locale === 'ar' ? 'en' : 'ar'
  const otherLocaleLabel = t('common.switch_language')

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

      {/* Hero */}
      <main className="flex-1 flex items-center justify-center px-4 py-16">
        <div className="w-full max-w-xl">
          {/* Title */}
          <div className="text-center mb-10">
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4 leading-tight">
              {t('home.title')}
            </h1>
            <p className="text-slate-400 text-lg leading-relaxed">
              {t('home.subtitle')}
            </p>
          </div>

          {/* URL Input Card */}
          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-4 shadow-2xl mb-4">
            <div className="flex flex-col sm:flex-row gap-3">
              <input
                type="url"
                placeholder={t('home.url_placeholder')}
                className="flex-1 px-4 py-3 bg-slate-800 border border-slate-600 rounded-xl
                           text-slate-100 placeholder:text-slate-500
                           focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                           text-sm transition-all"
                dir="ltr"
                aria-label={t('home.url_placeholder')}
              />
              <button
                type="button"
                disabled
                title={t('home.coming_soon')}
                className="px-6 py-3 bg-blue-600 text-white rounded-xl font-semibold
                           text-sm whitespace-nowrap
                           opacity-60 cursor-not-allowed
                           transition-all"
              >
                {t('home.check_button')}
              </button>
            </div>

            {/* Coming soon notice */}
            <p className="text-slate-500 text-xs mt-3 text-center">
              {t('home.coming_soon')}
            </p>
          </div>

          {/* Disclaimer */}
          <p className="text-slate-600 text-xs text-center leading-relaxed px-4">
            {t('home.disclaimer')}
          </p>

          {/* Recommendation badges (static preview) */}
          <div className="mt-10 grid grid-cols-2 gap-3">
            {(
              [
                'safe_to_browse',
                'safe_for_email',
                'safe_for_account',
                'safe_for_payment',
              ] as const
            ).map((key) => (
              <div
                key={key}
                className="flex items-center gap-2 bg-slate-900 border border-slate-800 rounded-xl px-4 py-3"
              >
                <div className="w-2 h-2 rounded-full bg-slate-600 flex-shrink-0" />
                <span className="text-slate-500 text-sm">
                  {t(`home.recommendations.${key}`)}
                </span>
              </div>
            ))}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="text-center py-6 border-t border-slate-900">
        <p className="text-slate-700 text-xs">{t('footer.tagline')}</p>
      </footer>
    </div>
  )
}
