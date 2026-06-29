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
  const t = await getTranslations({ locale, namespace: 'roadmap' })
  return { title: t('page_title') }
}

// ── Sub-components ────────────────────────────────────────────────────────────

function FlowStep({ text, index }: { text: string; index: number }) {
  return (
    <div className="flex items-start gap-3">
      <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-700 text-white text-xs flex items-center justify-center font-bold mt-0.5">
        {index + 1}
      </div>
      <span className="text-slate-300 text-sm leading-relaxed">{text}</span>
    </div>
  )
}

function CheckItem({ text, done }: { text: string; done: boolean }) {
  return (
    <li className="flex items-start gap-2 text-sm">
      <span className={done ? 'text-emerald-400 mt-0.5' : 'text-slate-600 mt-0.5'}>
        {done ? '✓' : '○'}
      </span>
      <span className={done ? 'text-slate-200' : 'text-slate-400'}>{text}</span>
    </li>
  )
}

function ProgressBar({ pct, label }: { pct: number; label: string }) {
  return (
    <div className="space-y-1.5">
      <div className="flex justify-between text-xs text-slate-400">
        <span>{label}</span>
        <span className="font-mono text-slate-300">{pct}%</span>
      </div>
      <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
        <div
          className="h-full bg-blue-600 rounded-full"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}

interface PathCardProps {
  title: string
  status: string
  statusColor: string
  flow: readonly string[]
  done: readonly string[]
  remaining: readonly string[]
  doneLabel: string
  remainingLabel: string
}

function PathCard({
  title,
  status,
  statusColor,
  flow,
  done,
  remaining,
  doneLabel,
  remainingLabel,
}: PathCardProps) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-lg font-semibold text-slate-100">{title}</h2>
        <span className={`text-xs px-2.5 py-1 rounded-full border ${statusColor}`}>
          {status}
        </span>
      </div>

      <div className="space-y-2.5">
        {flow.map((step, i) => (
          <FlowStep key={i} text={step} index={i} />
        ))}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 border-t border-slate-800">
        <div>
          <p className="text-xs font-medium text-emerald-400 mb-2 uppercase tracking-wide">
            {doneLabel}
          </p>
          <ul className="space-y-1.5">
            {done.map((item, i) => (
              <CheckItem key={i} text={item} done />
            ))}
          </ul>
        </div>
        <div>
          <p className="text-xs font-medium text-amber-400 mb-2 uppercase tracking-wide">
            {remainingLabel}
          </p>
          <ul className="space-y-1.5">
            {remaining.map((item, i) => (
              <CheckItem key={i} text={item} done={false} />
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function RoadmapPage(_: {
  params: Promise<{ locale: string }>
}) {
  const t = useTranslations('roadmap')

  const progress: Array<{ key: string; pct: number }> = [
    { key: 'security_arch', pct: 95 },
    { key: 'public_trust_mvp', pct: 100 },
    { key: 'owner_mvp', pct: 85 },
    { key: 'admin_lead_mvp', pct: 80 },
    { key: 'fix_experience', pct: 70 },
    { key: 'beta_ready', pct: 75 },
  ]

  return (
    <div className="min-h-screen flex flex-col">
      <header className="flex justify-between items-center px-6 py-4 border-b border-slate-800">
        <BrandLogo />
        <LanguageToggle />
      </header>

      <main className="flex-1 max-w-4xl mx-auto w-full px-4 py-12 space-y-10">
        {/* Plain-language intro for visitors */}
        <div className="bg-slate-900/60 border border-slate-800/60 rounded-xl p-5 space-y-2">
          <p className="text-sm font-semibold text-slate-300">{t('visitor_intro.title')}</p>
          <p className="text-slate-400 text-sm leading-relaxed">{t('visitor_intro.body')}</p>
        </div>

        {/* Hero */}
        <div className="space-y-3">
          <h1 className="text-3xl font-bold text-slate-100">{t('headline')}</h1>
          <p className="text-slate-400 leading-relaxed max-w-2xl">{t('intro')}</p>
        </div>

        {/* Current position */}
        <div className="bg-blue-950/40 border border-blue-800/50 rounded-xl p-5 space-y-3">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
            <span className="text-sm font-medium text-blue-300 uppercase tracking-wide">
              {t('where_now_label')}
            </span>
          </div>
          <p className="text-slate-200">{t('where_now_value')}</p>
          <div className="pt-1 border-t border-blue-800/40 grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
            <div>
              <span className="text-slate-500">{t('next_step_label')}: </span>
              <span className="text-slate-300">{t('next_step_value')}</span>
            </div>
            <div>
              <span className="text-slate-500">{t('after_next_label')}: </span>
              <span className="text-slate-300">{t('after_next_value')}</span>
            </div>
          </div>
        </div>

        <PathCard
          title={t('visitor_path.title')}
          status={t('visitor_path.status')}
          statusColor="text-emerald-400 border-emerald-800/50 bg-emerald-950/30"
          flow={t.raw('visitor_path.flow') as string[]}
          done={t.raw('visitor_path.done') as string[]}
          remaining={t.raw('visitor_path.remaining') as string[]}
          doneLabel={t('status_done')}
          remainingLabel={t('status_remaining')}
        />

        <PathCard
          title={t('owner_path.title')}
          status={t('owner_path.status')}
          statusColor="text-amber-400 border-amber-800/50 bg-amber-950/20"
          flow={t.raw('owner_path.flow') as string[]}
          done={t.raw('owner_path.done') as string[]}
          remaining={t.raw('owner_path.remaining') as string[]}
          doneLabel={t('status_done')}
          remainingLabel={t('status_remaining')}
        />

        <PathCard
          title={t('admin_path.title')}
          status={t('admin_path.status')}
          statusColor="text-slate-400 border-slate-700 bg-slate-800/20"
          flow={t.raw('admin_path.flow') as string[]}
          done={t.raw('admin_path.done') as string[]}
          remaining={t.raw('admin_path.remaining') as string[]}
          doneLabel={t('status_done')}
          remainingLabel={t('status_remaining')}
        />

        {/* Progress bars */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-base font-semibold text-slate-100">
            {t('progress.title')}
          </h2>
          <div className="space-y-4">
            {progress.map(({ key, pct }) => (
              <ProgressBar
                key={key}
                pct={pct}
                label={t(`progress.${key}` as Parameters<typeof t>[0])}
              />
            ))}
          </div>
          <p className="text-xs text-slate-600 pt-2 border-t border-slate-800">
            {t('note_estimates')}
          </p>
        </div>
      </main>

      <AppFooter />
    </div>
  )
}
