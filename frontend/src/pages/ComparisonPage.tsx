import { useCallback, useEffect, useMemo, useState } from 'react';
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
    <section className="page-section comparison-page">
      <header>
        <h2>Provider comparison</h2>
        <p>Monitor spend, CPU efficiency, and workload volume by provider in one view.</p>
      </header>

      {loading && <p className="inline-status">Loading provider comparison data…</p>}

      {error && (
        <div role="alert" className="feedback">
          <p>We couldn't load the comparison data: {error}</p>
          <button type="button" onClick={refetch}>
            Retry
          </button>
        </div>
      )}

      {!loading && !error && (
        <>
          {hasRows ? (
            <div className="surface-card table-wrapper">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Provider</th>
                    <th>Total cost</th>
                    <th>Avg CPU utilization</th>
                    <th>Workloads tracked</th>
                  </tr>
                </thead>
                <tbody>
                  {sortedRows.map((row) => (
                    <tr key={row.provider}>
                      <td>{row.provider}</td>
                      <td>{currencyFormatter.format(row.total_cost)}</td>
                      <td>
                        {row.avg_cpu_utilization !== null
                          ? `${cpuFormatter.format(row.avg_cpu_utilization)}%`
                          : '—'}
                      </td>
                      <td>{integerFormatter.format(row.workload_count)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="surface-card empty-state">
              <h3>No provider metrics yet</h3>
              <p>
                We didn't receive any comparison data for this time window. Refresh the feed or adjust
                the API filters.
              </p>
              <button type="button" onClick={refetch}>
                Refresh data
              </button>
            </div>
          )}
        </>
      )}
    </section>
  );
};

export default ComparisonPage;
