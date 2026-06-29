import ScanForm from '@/components/ScanForm'
import BrandLogo from '@/components/BrandLogo'
import AppFooter from '@/components/AppFooter'
import LanguageToggle from '@/components/LanguageToggle'

export default function HomePage() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

  return (
    <div className="min-h-screen flex flex-col">
      <header className="flex justify-between items-center px-6 py-4 border-b border-slate-800/60">
        <BrandLogo />
        <LanguageToggle />
      </header>

      <main className="flex-1 flex items-center justify-center px-4 py-12">
        <ScanForm apiUrl={apiUrl} />
      </main>

      <AppFooter />
    </div>
  )
}
