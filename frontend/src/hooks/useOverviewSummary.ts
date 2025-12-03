import { useCallback, useEffect, useState } from 'react';
import { API_BASE_URL } from '../config/api';

export type CloudProvider = 'AWS' | 'AZURE' | 'GCP' | (string & {});

export interface OverviewTopService {
  provider: CloudProvider;
  service: string;
  total_cost: number;
}

export interface OverviewSummaryResponse {
  time_window_days: number;
  total_cost_per_provider: Record<CloudProvider, number>;
  top_services: OverviewTopService[];
}

const UNCONFIGURED_API_ERROR = 'API base URL is not configured.';
const DEFAULT_ERROR_MESSAGE = 'Unable to load overview summary.';

export const DEFAULT_PROVIDERS: CloudProvider[] = ['AWS', 'AZURE', 'GCP'];

export const useOverviewSummary = () => {
  const [data, setData] = useState<OverviewSummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSummary = useCallback(
    async (signal?: AbortSignal) => {
      if (!API_BASE_URL) {
        setError(UNCONFIGURED_API_ERROR);
        setData(null);
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const response = await fetch(`${API_BASE_URL}/summary/overview`, { signal });
        if (!response.ok) {
          throw new Error(`Request failed with status ${response.status}`);
        }

        const payload: OverviewSummaryResponse = await response.json();
        setData(payload);
      } catch (err) {
        if (err instanceof DOMException && err.name === 'AbortError') {
          return;
        }

        const message = err instanceof Error ? err.message : DEFAULT_ERROR_MESSAGE;
        setError(message || DEFAULT_ERROR_MESSAGE);
        setData(null);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  useEffect(() => {
    const controller = new AbortController();
    fetchSummary(controller.signal);

    return () => {
      controller.abort();
    };
  }, [fetchSummary]);

  const refetch = useCallback(() => fetchSummary(), [fetchSummary]);

  return {
    data,
    loading,
    error,
    refetch,
  };
};
