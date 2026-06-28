import type { Metadata } from 'next'
import { useTranslations } from 'next-intl'
import { getTranslations } from 'next-intl/server'
import BrandLogo from '@/components/BrandLogo'
import AppFooter from '@/components/AppFooter'
import LanguageToggle from '@/components/LanguageToggle'

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>
}): Promise<Metadata> {
  const { locale } = await params
  const t = await getTranslations({ locale, namespace: 'terms' })
  return { title: t('page_title') }
}

export default function TermsPage() {
  const t = useTranslations('terms')

  return (
    <div className="min-h-screen flex flex-col">
      <header className="flex justify-between items-center px-6 py-4 border-b border-slate-800">
        <BrandLogo />
        <LanguageToggle />
      </header>

      <main className="flex-1 flex items-center justify-center px-4 py-16">
        <div className="max-w-2xl w-full space-y-4">
          <h1 className="text-2xl font-bold text-slate-100">{t('page_title')}</h1>
          <p className="text-slate-400 leading-relaxed">{t('coming_soon')}</p>
        </div>
      </main>

      <AppFooter />
    </div>
  )
}
