import { CSSProperties, useMemo } from 'react';
import { DEFAULT_PROVIDERS, useOverviewSummary } from '../hooks/useOverviewSummary';

const currencyFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 0,
});

const gridStyle: CSSProperties = {
  display: 'grid',
  gap: '1rem',
  gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
  marginBlock: '1.5rem',
};

const cardStyle: CSSProperties = {
  border: '1px solid #e1e4e8',
  borderRadius: '0.5rem',
  padding: '1rem',
  background: '#fff',
  boxShadow: '0 1px 2px rgba(0,0,0,0.06)',
};

const chartContainerStyle: CSSProperties = {
  border: '1px solid #e1e4e8',
  borderRadius: '0.5rem',
  padding: '1.5rem',
  background: '#fff',
  boxShadow: '0 1px 2px rgba(0,0,0,0.06)',
};

const barChartStyle: CSSProperties = {
  display: 'flex',
  gap: '1rem',
  alignItems: 'flex-end',
  minHeight: '200px',
};

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

  return (
    <section className="overview-page">
      <header>
        <h2>Overview</h2>
        <p>
          High-level summary of cloud spend for the last{' '}
          {data?.time_window_days ?? 30} days.
        </p>
      </header>

      {loading && <p>Loading overview data…</p>}

      {error && (
        <div role="alert" style={{ color: '#d93025', marginBlock: '1rem' }}>
          <p>Failed to load overview data: {error}</p>
          <button type="button" onClick={refetch}>
            Try again
          </button>
        </div>
      )}

      {!loading && !error && data && (
        <>
          <div style={gridStyle}>
            {providerCosts.map((entry) => (
              <article key={entry.provider} style={cardStyle}>
                <h3>{entry.provider}</h3>
                <p style={{ fontSize: '1.75rem', margin: '0.5rem 0 0' }}>
                  {currencyFormatter.format(entry.cost)}
                </p>
              </article>
            ))}
          </div>

          <div style={chartContainerStyle}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
              <h3 style={{ margin: 0 }}>Total cost by provider</h3>
              <span style={{ color: '#6a737d' }}>
                Time window: last {data.time_window_days} days
              </span>
            </div>

            {totalCost === 0 ? (
              <p style={{ marginTop: '1rem' }}>No cost data available for this period.</p>
            ) : (
              <div
                style={{ ...barChartStyle, marginTop: '1.5rem' }}
                role="img"
                aria-label="Bar chart of total cost per cloud provider"
              >
                {providerCosts.map((entry) => {
                  const heightPercent = maxValue ? (entry.cost / maxValue) * 100 : 0;
                  return (
                    <div
                      key={entry.provider}
                      style={{ flex: 1, textAlign: 'center', minWidth: '80px' }}
                    >
                      <div
                        style={{
                          background: '#e5f0ff',
                          borderRadius: '0.25rem 0.25rem 0 0',
                          height: `${heightPercent}%`,
                          position: 'relative',
                        }}
                      >
                        <div
                          style={{
                            position: 'absolute',
                            top: '-1.75rem',
                            width: '100%',
                            fontSize: '0.9rem',
                            fontWeight: 600,
                          }}
                        >
                          {currencyFormatter.format(entry.cost)}
                        </div>
                      </div>
                      <div style={{ marginTop: '0.5rem', fontWeight: 600 }}>{entry.provider}</div>
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
