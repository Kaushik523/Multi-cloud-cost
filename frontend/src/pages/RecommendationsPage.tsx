import { type CSSProperties, useCallback, useEffect, useState } from 'react';
import { API_BASE_URL } from '../config/api';

interface Recommendation {
  workload_id: string;
  current_provider: string;
  recommended_provider: string;
  estimated_savings_percent: number;
  explanation: string;
}

const UNCONFIGURED_API_ERROR = 'API base URL is not configured.';
const DEFAULT_ERROR_MESSAGE = 'Unable to load recommendations.';

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
  verticalAlign: 'top',
};

const RecommendationsPage = () => {
  const [data, setData] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRecommendations = useCallback(async (signal?: AbortSignal) => {
    if (!API_BASE_URL) {
      setError(UNCONFIGURED_API_ERROR);
      setData([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/recommendations`, { signal });
      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const payload: Recommendation[] = await response.json();
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
    fetchRecommendations(controller.signal);

    return () => controller.abort();
  }, [fetchRecommendations]);

  const refetch = useCallback(() => fetchRecommendations(), [fetchRecommendations]);
  const hasRecommendations = data.length > 0;

  return (
    <section className="recommendations-page">
      <header>
        <h2>Recommendations</h2>
        <p>Actionable workload moves that lower cost while keeping CPU usage comparable.</p>
      </header>

      {loading && <p>Loading recommendations…</p>}

      {error && (
        <div role="alert" style={{ color: '#d93025', marginBlock: '1rem' }}>
          <p>Failed to load recommendations: {error}</p>
          <button type="button" onClick={refetch}>
            Try again
          </button>
        </div>
      )}

      {!loading && !error && (
        <>
          {hasRecommendations ? (
            <div style={{ overflowX: 'auto' }}>
              <table style={tableStyle}>
                <thead>
                  <tr>
                    <th style={thStyle}>Workload ID</th>
                    <th style={thStyle}>Current Provider</th>
                    <th style={thStyle}>Recommended Provider</th>
                    <th style={thStyle}>Estimated Savings (%)</th>
                    <th style={thStyle}>Explanation</th>
                  </tr>
                </thead>
                <tbody>
                  {data.map((item) => (
                    <tr key={item.workload_id}>
                      <td style={tdStyle}>{item.workload_id}</td>
                      <td style={tdStyle}>{item.current_provider}</td>
                      <td style={tdStyle}>{item.recommended_provider}</td>
                      <td style={tdStyle}>{item.estimated_savings_percent.toFixed(1)}%</td>
                      <td style={tdStyle}>{item.explanation}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div
              style={{
                border: '1px solid #e1e4e8',
                borderRadius: '0.5rem',
                padding: '1.5rem',
                marginTop: '1.5rem',
                background: '#f7f9fc',
              }}
            >
              <h3 style={{ marginTop: 0 }}>No recommendations yet</h3>
              <p style={{ marginBottom: '0.5rem' }}>
                All monitored workloads look optimized based on the latest data. Check back later or
                adjust your time window in the API to surface new opportunities.
              </p>
              <button type="button" onClick={refetch}>
                Refresh recommendations
              </button>
            </div>
          )}
        </>
      )}
    </section>
  );
};

export default RecommendationsPage;
