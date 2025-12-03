import { type CSSProperties, useCallback, useEffect, useMemo, useState } from 'react';
import { API_BASE_URL } from '../config/api';

interface ComparisonSummary {
  provider: string;
  total_cost: number;
  avg_cpu_utilization: number | null;
  workload_count: number;
}

const UNCONFIGURED_API_ERROR = 'API base URL is not configured.';
const DEFAULT_ERROR_MESSAGE = 'Unable to load comparison summary.';

const currencyFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 0,
});

const cpuFormatter = new Intl.NumberFormat('en-US', {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});

const integerFormatter = new Intl.NumberFormat('en-US', {
  maximumFractionDigits: 0,
});

const tableStyle: CSSProperties = {
  width: '100%',
  borderCollapse: 'collapse',
  marginTop: '1.5rem',
};

const thStyle: CSSProperties = {
  textAlign: 'left',
  padding: '0.75rem 1rem',
  borderBottom: '2px solid #e1e4e8',
  fontSize: '0.9rem',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
  color: '#6a737d',
};

const tdStyle: CSSProperties = {
  padding: '0.75rem 1rem',
  borderBottom: '1px solid #e1e4e8',
};

const ComparisonPage = () => {
  const [data, setData] = useState<ComparisonSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchComparison = useCallback(async (signal?: AbortSignal) => {
    if (!API_BASE_URL) {
      setError(UNCONFIGURED_API_ERROR);
      setData([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/summary/comparison`, { signal });
      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const payload: ComparisonSummary[] = await response.json();
      setData(payload);
    } catch (err) {
      if (err instanceof DOMException && err.name === 'AbortError') {
        return;
      }

      const message = err instanceof Error ? err.message : DEFAULT_ERROR_MESSAGE;
      setError(message || DEFAULT_ERROR_MESSAGE);
      setData([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    fetchComparison(controller.signal);

    return () => controller.abort();
  }, [fetchComparison]);

  const refetch = useCallback(() => fetchComparison(), [fetchComparison]);

  const sortedRows = useMemo(
    () => [...data].sort((a, b) => b.total_cost - a.total_cost),
    [data]
  );

  const hasRows = sortedRows.length > 0;

  return (
    <section className="comparison-page">
      <header>
        <h2>Provider Comparison</h2>
        <p>
          Track how each cloud provider is performing across spend, CPU utilization, and workload
          counts.
        </p>
      </header>

      {loading && <p>Loading provider comparison…</p>}

      {error && (
        <div role="alert" style={{ color: '#d93025', marginBlock: '1rem' }}>
          <p>Failed to load comparison data: {error}</p>
          <button type="button" onClick={refetch}>
            Try again
          </button>
        </div>
      )}

      {!loading && !error && (
        <>
          {hasRows ? (
            <div style={{ overflowX: 'auto' }}>
              <table style={tableStyle}>
                <thead>
                  <tr>
                    <th style={thStyle}>Provider</th>
                    <th style={thStyle}>Total Cost</th>
                    <th style={thStyle}>Avg CPU Utilization</th>
                    <th style={thStyle}>Number of Workloads</th>
                  </tr>
                </thead>
                <tbody>
                  {sortedRows.map((row) => (
                    <tr key={row.provider}>
                      <td style={tdStyle}>{row.provider}</td>
                      <td style={tdStyle}>{currencyFormatter.format(row.total_cost)}</td>
                      <td style={tdStyle}>
                        {row.avg_cpu_utilization !== null
                          ? `${cpuFormatter.format(row.avg_cpu_utilization)}%`
                          : '—'}
                      </td>
                      <td style={tdStyle}>{integerFormatter.format(row.workload_count)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p style={{ marginTop: '1rem' }}>
              No provider metrics are available for the selected time window.
            </p>
          )}
        </>
      )}
    </section>
  );
};

export default ComparisonPage;
