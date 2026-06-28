'use client'

import { useTranslations } from 'next-intl'
import { Link } from '@/i18n/navigation'

function ShieldCheckIcon({ size = 32 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <rect width="32" height="32" rx="7" fill="#2563eb" />
      <path
        d="M16 6L24.5 10V17C24.5 21.69 20.82 25.54 16 27.2C11.18 25.54 7.5 21.69 7.5 17V10L16 6Z"
        fill="rgba(255,255,255,0.12)"
        stroke="rgba(255,255,255,0.35)"
        strokeWidth="1"
      />
      <path
        d="M11.5 16.5L14.5 19.5L20.5 13"
        stroke="white"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

interface BrandLogoProps {
  href?: string
  showName?: boolean
}

export default function BrandLogo({ href = '/', showName = true }: BrandLogoProps) {
  const t = useTranslations('common')

  return (
    <Link
      href={href}
      className="flex items-center gap-2.5 hover:opacity-90 transition-opacity focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 rounded-lg"
    >
      <ShieldCheckIcon />
      {showName && (
        <span className="font-semibold text-slate-100 text-base leading-none">
          {t('app_name')}
        </span>
      )}
    </Link>
  )
}
