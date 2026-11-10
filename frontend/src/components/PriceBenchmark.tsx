import { Link } from 'react-router-dom'
import { Icon } from '@/components/ui/Icon'
import { Badge, Skeleton } from '@/components/ui'
import { cn, formatPrice } from '@/lib/utils'
import { useClinicBenchmark } from '@/hooks/queries'
import { api } from '@/api/client'
import { useI18n } from '@/lib/i18n'
import type { BenchmarkItem } from '@/api/types'

const POSITION: Record<BenchmarkItem['position'], { label: string; tone: 'success' | 'warning' | 'error' | 'neutral' | 'primary' }> = {
  cheapest: { label: 'Cheapest in city', tone: 'success' },
  below_median: { label: 'Below median', tone: 'success' },
  at_median: { label: 'At median', tone: 'primary' },
  above_median: { label: 'Above median', tone: 'warning' },
  most_expensive: { label: 'Most expensive in city', tone: 'error' },
  no_competitors: { label: 'No competitors', tone: 'neutral' },
}

/** CR-01: where each of this clinic's prices sits within its city's market. */
export function PriceBenchmark({ clinicId }: { clinicId: string }) {
  const { t } = useI18n()
  const { data, isLoading, isError } = useClinicBenchmark(clinicId)

  return (
    <section className="bg-surface-container-lowest border border-outline-variant rounded-xl p-6 mb-8" aria-labelledby="benchmark-title">
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 mb-5">
        <div>
          <h2 id="benchmark-title" className="font-headline-md text-headline-md text-text-main flex items-center gap-2">
            <Icon name="query_stats" className="text-primary" />
            {t('Price benchmark')}
          </h2>
          <p className="text-body-sm text-text-subtle mt-1">
            {t('How each price compares with the same service in other clinics of')} {data?.city ?? '…'}.
          </p>
        </div>
        <a
          href={api.clinicBenchmarkCsvUrl(clinicId)}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-outline-variant font-label-bold text-primary hover:bg-surface-container-low"
        >
          <Icon name="download" />
          {t('Download CSV')}
        </a>
      </div>

      {isLoading && <Skeleton className="h-40 w-full" />}
      {isError && <p className="text-error font-body-sm">{t("Couldn't load the benchmark.")}</p>}

      {data && (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-5">
            <Stat value={data.summary.services_compared} label={t('services compared')} />
            <Stat value={data.summary.cheapest_count} label={t('cheapest in city')} tone="good" />
            <Stat value={data.summary.above_median_count} label={t('above city median')} tone="bad" />
            <Stat
              value={`${data.summary.avg_diff_vs_median_pct > 0 ? '+' : ''}${data.summary.avg_diff_vs_median_pct}%`}
              label={t('average vs median')}
              tone={data.summary.avg_diff_vs_median_pct > 0 ? 'bad' : 'good'}
            />
          </div>

          {data.items.length === 0 ? (
            <p className="text-body-sm text-text-subtle">{t('No normalized services to compare yet.')}</p>
          ) : (
            <div className="overflow-x-auto max-h-[420px] overflow-y-auto border border-outline-variant/60 rounded-lg">
              <table className="w-full text-left font-body-sm">
                <thead className="bg-surface-container-low sticky top-0">
                  <tr className="text-text-subtle whitespace-nowrap">
                    <th className="px-3 py-2 font-label-bold">{t('Service')}</th>
                    <th className="px-3 py-2 font-label-bold text-right">{t('Our price')}</th>
                    <th className="px-3 py-2 font-label-bold text-right">{t('City min')}</th>
                    <th className="px-3 py-2 font-label-bold text-right">{t('Median')}</th>
                    <th className="px-3 py-2 font-label-bold text-right">{t('City max')}</th>
                    <th className="px-3 py-2 font-label-bold text-right">{t('vs median')}</th>
                    <th className="px-3 py-2 font-label-bold">{t('Rank')}</th>
                    <th className="px-3 py-2 font-label-bold">{t('Position')}</th>
                  </tr>
                </thead>
                <tbody>
                  {data.items.map((i) => (
                    <tr key={i.service_id} className="border-t border-outline-variant/60">
                      <td className="px-3 py-2">
                        <Link to={`/service/${i.service_id}`} className="text-primary hover:underline">
                          {i.service_name_norm}
                        </Link>
                      </td>
                      <td className="px-3 py-2 text-right font-label-bold">{formatPrice(i.price_kzt)}</td>
                      <td className="px-3 py-2 text-right">{formatPrice(i.city_min)}</td>
                      <td className="px-3 py-2 text-right">{formatPrice(i.city_median)}</td>
                      <td className="px-3 py-2 text-right">{formatPrice(i.city_max)}</td>
                      <td
                        className={cn(
                          'px-3 py-2 text-right font-label-bold',
                          i.diff_vs_median_pct > 0.5 && 'text-error',
                          i.diff_vs_median_pct < -0.5 && 'text-success-green',
                        )}
                      >
                        {i.clinics_compared > 1 ? `${i.diff_vs_median_pct > 0 ? '+' : ''}${i.diff_vs_median_pct}%` : '—'}
                      </td>
                      <td className="px-3 py-2 whitespace-nowrap">
                        {i.rank} / {i.clinics_compared}
                      </td>
                      <td className="px-3 py-2">
                        <Badge tone={POSITION[i.position].tone}>{t(POSITION[i.position].label)}</Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </section>
  )
}

function Stat({ value, label, tone }: { value: number | string; label: string; tone?: 'good' | 'bad' }) {
  return (
    <div className="bg-surface-container-low rounded-lg p-3">
      <div
        className={cn(
          'font-headline-md text-headline-md text-text-main',
          tone === 'good' && 'text-success-green',
          tone === 'bad' && 'text-error',
        )}
      >
        {value}
      </div>
      <div className="text-body-sm text-text-subtle">{label}</div>
    </div>
  )
}
