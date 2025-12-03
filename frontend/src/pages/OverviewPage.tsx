import { useMemo } from 'react';
import { DEFAULT_PROVIDERS, useOverviewSummary } from '../hooks/useOverviewSummary';

const currencyFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 0,
});

const OverviewPage = () => {
  const { data, loading, error, refetch } = useOverviewSummary();

  const providerCosts = useMemo(
    () =>
      DEFAULT_PROVIDERS.map((provider) => ({
        provider,
        cost: data?.total_cost_per_provider?.[provider] ?? 0,
      })),
    [data]
  );

  const maxValue = useMemo(
    () => providerCosts.reduce((acc, entry) => Math.max(acc, entry.cost), 0),
    [providerCosts]
  );

  const totalCost = useMemo(
    () => providerCosts.reduce((acc, entry) => acc + entry.cost, 0),
    [providerCosts]
  );

  const timeWindowDays = data?.time_window_days ?? 30;

  return (
    <section className="page-section overview-page">
      <header>
        <h2>Spend overview</h2>
        <p>Snapshot of multi-cloud spend across the last {timeWindowDays} days.</p>
      </header>

      {loading && <p className="inline-status">Loading overview insights…</p>}

      {error && (
        <div role="alert" className="feedback">
          <p>We couldn't load the overview data: {error}</p>
          <button type="button" onClick={refetch}>
            Retry
          </button>
        </div>
      )}

      {!loading && !error && data && (
        <>
          <div className="stat-grid">
            {providerCosts.map((entry) => (
              <article key={entry.provider} className="surface-card stat-card">
                <h3>{entry.provider}</h3>
                <p className="stat-value">{currencyFormatter.format(entry.cost)}</p>
              </article>
            ))}
          </div>

          <div className="surface-card chart-card">
            <div className="chart-header">
              <h3>Total cost by provider</h3>
              <span className="chart-subtitle">Window: last {data.time_window_days} days</span>
            </div>

            {totalCost === 0 ? (
              <p className="inline-status">We don't have cost details for this window yet.</p>
            ) : (
              <div
                className="bar-chart"
                role="img"
                aria-label="Bar chart of total cost per cloud provider"
              >
                {providerCosts.map((entry) => {
                  const heightPercent = maxValue ? (entry.cost / maxValue) * 100 : 0;
                  return (
                    <div key={entry.provider} className="bar-chart__column">
                      <div
                        className="bar-chart__bar"
                        style={{ height: `${heightPercent}%` }}
                      >
                        <div className="bar-chart__value">
                          {currencyFormatter.format(entry.cost)}
                        </div>
                      </div>
                      <div className="bar-chart__label">{entry.provider}</div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </>
      )}
    </section>
  );
};

export default OverviewPage;
