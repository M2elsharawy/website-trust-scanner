'use client'

import { useTranslations, useLocale } from 'next-intl'
import { usePathname, Link } from '@/i18n/navigation'

export default function LanguageToggle() {
  const locale = useLocale()
  const pathname = usePathname()
  const t = useTranslations('common')

  const otherLocale = locale === 'ar' ? 'en' : 'ar'

  return (
    <Link
      href={pathname}
      locale={otherLocale}
      className="text-sm text-slate-400 hover:text-slate-100 transition-colors px-3 py-1.5 rounded-lg hover:bg-slate-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
    >
      {t('switch_language')}
    </Link>
  )
}
