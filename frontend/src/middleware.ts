import createMiddleware from 'next-intl/middleware'
import { type NextRequest, NextResponse } from 'next/server'

import { routing } from './i18n/routing'

const intlMiddleware = createMiddleware(routing)

// All paths under /sites require an authenticated session.
const PROTECTED_PREFIXES = ['/sites', '/admin']

export default function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  const isProtected = routing.locales.some(locale =>
    PROTECTED_PREFIXES.some(
      prefix =>
        pathname === `/${locale}${prefix}` ||
        pathname.startsWith(`/${locale}${prefix}/`),
    ),
  )

  if (isProtected && !request.cookies.get('access_token')) {
    const locale =
      routing.locales.find(
        l => pathname.startsWith(`/${l}/`) || pathname === `/${l}`,
      ) ?? routing.defaultLocale
    return NextResponse.redirect(new URL(`/${locale}/login`, request.url))
  }

  return intlMiddleware(request)
}

export const config = {
  matcher: ['/((?!api|_next|_vercel|.*\\..*).*)'],
}
