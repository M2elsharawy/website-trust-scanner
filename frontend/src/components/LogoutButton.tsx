'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useTranslations, useLocale } from 'next-intl'

const BACKEND = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

export default function LogoutButton({ className }: { className?: string }) {
  const t = useTranslations('auth')
  const locale = useLocale()
  const router = useRouter()
  const [loading, setLoading] = useState(false)

  async function handleLogout() {
    setLoading(true)
    try {
      await fetch(`${BACKEND}/api/v1/auth/logout`, {
        method: 'POST',
        credentials: 'include',
      })
    } finally {
      router.push(`/${locale}/login`)
      router.refresh()
      setLoading(false)
    }
  }

  return (
    <button
      onClick={handleLogout}
      disabled={loading}
      className={className ?? 'text-sm text-slate-400 hover:text-slate-200 transition-colors px-3 py-1.5 rounded-lg hover:bg-slate-800 disabled:opacity-50'}
    >
      {t('logout')}
    </button>
  )
}
