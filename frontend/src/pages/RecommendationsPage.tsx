import { useCallback, useEffect, useState } from 'react';
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
    <section className="page-section recommendations-page">
      <header>
        <h2>Recommendations</h2>
        <p>Actionable workload moves that lower spend while keeping CPU usage steady.</p>
      </header>

      {loading && <p className="inline-status">Loading recommendation results…</p>}

      {error && (
        <div role="alert" className="feedback">
          <p>We couldn't load the recommendations: {error}</p>
          <button type="button" onClick={refetch}>
            Retry
          </button>
        </div>
      )}

      {!loading && !error && (
        <>
          {hasRecommendations ? (
            <div className="surface-card table-wrapper">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Workload ID</th>
                    <th>Current provider</th>
                    <th>Recommended provider</th>
                    <th>Estimated savings (%)</th>
                    <th>Explanation</th>
                  </tr>
                </thead>
                <tbody>
                  {data.map((item) => (
                    <tr key={item.workload_id}>
                      <td>{item.workload_id}</td>
                      <td>{item.current_provider}</td>
                      <td>{item.recommended_provider}</td>
                      <td>{item.estimated_savings_percent.toFixed(1)}%</td>
                      <td>{item.explanation}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="surface-card empty-state">
              <h3>No recommendations yet</h3>
              <p>
                All monitored workloads look optimized right now. Check back later or adjust your API
                filters to surface new opportunities.
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
