'use client'

import { useState, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useTranslations, useLocale } from 'next-intl'
import { Link } from '@/i18n/navigation'
import BrandLogo from '@/components/BrandLogo'
import LanguageToggle from '@/components/LanguageToggle'
import AppFooter from '@/components/AppFooter'

type Mode = 'login' | 'register'

const BACKEND = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

function errorKey(code: string | undefined): string {
  if (code === 'INVALID_CREDENTIALS') return 'invalid_credentials'
  if (code === 'ACCOUNT_LOCKED') return 'account_locked'
  if (code === 'EMAIL_ALREADY_REGISTERED') return 'email_taken'
  return 'generic'
}

function AuthFormInner({ mode }: { mode: Mode }) {
  const t = useTranslations('auth')
  const locale = useLocale()
  const router = useRouter()
  const searchParams = useSearchParams()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [lang, setLang] = useState(locale)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)

    const endpoint =
      mode === 'login'
        ? `${BACKEND}/api/v1/auth/login`
        : `${BACKEND}/api/v1/auth/register`

    const body =
      mode === 'login'
        ? { email, password }
        : { email, password, preferred_lang: lang }

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(body),
      })

      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        setError(t(`errors.${errorKey(data?.error)}`))
        return
      }

      const raw = searchParams.get('next')
      const next = raw && raw.startsWith('/') && !raw.startsWith('//') ? raw : null
      router.push(next ?? `/${locale}/sites`)
      router.refresh()
    } catch {
      setError(t('errors.generic'))
    } finally {
      setLoading(false)
    }
  }

  const altMode = mode === 'login' ? 'register' : 'login'

  return (
    <div className="min-h-screen flex flex-col">
      <header className="flex justify-between items-center px-6 py-4 border-b border-slate-800">
        <BrandLogo />
        <LanguageToggle />
      </header>

      <main className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <div className="bg-slate-900 border border-slate-700/80 rounded-2xl p-8 shadow-2xl shadow-black/30 space-y-6">
            <h1 className="text-xl font-semibold text-center text-slate-100">
              {mode === 'login' ? t('login_title') : t('register_title')}
            </h1>

            <form onSubmit={handleSubmit} className="space-y-4" noValidate>
              <div>
                <label className="block text-sm text-slate-400 mb-1.5">{t('email')}</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={t('email_placeholder')}
                  required
                  className="w-full rounded-xl bg-slate-800 border border-slate-700 px-4 py-2.5
                             text-slate-100 placeholder-slate-500
                             focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                             transition-all"
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="block text-sm text-slate-400">{t('password')}</label>
                  {mode === 'login' && (
                    <Link
                      href="/forgot-password"
                      className="text-xs text-slate-500 hover:text-blue-400 transition-colors"
                    >
                      {t('forgot_password')}
                    </Link>
                  )}
                </div>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder={t('password_placeholder')}
                    required
                    minLength={8}
                    className="w-full rounded-xl bg-slate-800 border border-slate-700 px-4 py-2.5
                               text-slate-100 placeholder-slate-500
                               focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                               transition-all pe-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((v) => !v)}
                    className="absolute inset-y-0 end-0 flex items-center px-3 text-slate-400 hover:text-slate-200 focus-visible:outline-none"
                    aria-label={showPassword ? t('hide_password') : t('show_password')}
                  >
                    {showPassword ? '🙈' : '👁'}
                  </button>
                </div>
              </div>

              {mode === 'register' && (
                <div>
                  <label className="block text-sm text-slate-400 mb-1.5">{t('preferred_lang')}</label>
                  <select
                    value={lang}
                    onChange={(e) => setLang(e.target.value)}
                    className="w-full rounded-xl bg-slate-800 border border-slate-700 px-4 py-2.5
                               text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500
                               focus:border-transparent transition-all"
                  >
                    <option value="ar">{t('lang_ar')}</option>
                    <option value="en">{t('lang_en')}</option>
                  </select>
                </div>
              )}

              {error && (
                <p className="text-red-400 text-sm" role="alert">
                  {error}
                </p>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-xl bg-blue-600 hover:bg-blue-500 active:bg-blue-700
                           disabled:opacity-60 py-2.5 font-semibold transition-colors
                           focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-400
                           focus-visible:ring-offset-2 focus-visible:ring-offset-slate-900"
              >
                {loading
                  ? t('submitting')
                  : mode === 'login'
                  ? t('login')
                  : t('register')}
              </button>
            </form>

            <p className="text-center text-slate-400 text-sm border-t border-slate-800 pt-5">
              {mode === 'login' ? t('no_account') : t('has_account')}{' '}
              <Link
                href={`/${altMode}`}
                className="text-blue-400 hover:text-blue-300 hover:underline transition-colors"
              >
                {altMode === 'login' ? t('login') : t('register')}
              </Link>
            </p>
          </div>
        </div>
      </main>

      <AppFooter />
    </div>
  )
}

export default function AuthForm({ mode }: { mode: Mode }) {
  return (
    <Suspense>
      <AuthFormInner mode={mode} />
    </Suspense>
  )
}
