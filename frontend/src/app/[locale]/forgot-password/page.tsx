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
  const t = await getTranslations({ locale, namespace: 'auth' })
  return { title: t('forgot_password') }
}

export default function ForgotPasswordPage() {
  const t = useTranslations('auth')

  return (
    <div className="min-h-screen flex flex-col">
      <header className="flex justify-between items-center px-6 py-4 border-b border-slate-800">
        <BrandLogo />
        <LanguageToggle />
      </header>

      <main className="flex-1 flex items-center justify-center px-4 py-16">
        <div className="max-w-md w-full space-y-4 text-center">
          <h1 className="text-2xl font-bold text-slate-100">{t('forgot_password')}</h1>
          <p className="text-slate-400 leading-relaxed">{t('forgot_password_coming_soon')}</p>
        </div>
      </main>

      <AppFooter />
    </div>
  )
}
