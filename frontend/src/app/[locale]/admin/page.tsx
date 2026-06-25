import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import { getTranslations } from 'next-intl/server'
import { Link } from '@/i18n/navigation'

const BACKEND = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'
const ADMIN_ROLES = new Set(['admin', 'super_admin'])

export default async function AdminPage({
  params,
}: {
  params: Promise<{ locale: string }>
}) {
  const { locale } = await params
  const t = await getTranslations({ locale, namespace: 'admin' })

  const cookieStore = await cookies()
  const token = cookieStore.get('access_token')?.value

  if (!token) {
    redirect(`/${locale}/login`)
  }

  let role = ''
  try {
    const res = await fetch(`${BACKEND}/api/v1/auth/me`, {
      headers: { Cookie: `access_token=${token}` },
      cache: 'no-store',
    })
    if (res.status === 401 || res.status === 403) {
      redirect(`/${locale}/login`)
    }
    if (!res.ok) {
      redirect(`/${locale}`)
    }
    ;({ role } = (await res.json()) as { role: string })
  } catch (err) {
    if ((err as { digest?: string }).digest?.startsWith('NEXT_REDIRECT')) throw err
    redirect(`/${locale}`)
  }

  if (!ADMIN_ROLES.has(role)) {
    redirect(`/${locale}`)
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6">
      <div className="w-full max-w-xl space-y-4">
        <div className="space-y-2">
          <h1 className="text-xl font-semibold text-slate-100">{t('title')}</h1>
          <p className="text-slate-400 text-sm">{t('subtitle')}</p>
        </div>
        <nav>
          <Link
            href="/admin/leads"
            className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
          >
            {t('view_leads')} →
          </Link>
        </nav>
      </div>
    </div>
  )
}
