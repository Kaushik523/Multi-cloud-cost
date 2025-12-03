const resolveViteBaseUrl = (): string | undefined => {
  if (typeof import.meta !== 'undefined' && import.meta.env) {
    return import.meta.env.VITE_API_BASE_URL as string | undefined;
  }
  return undefined;
};

const resolveCraBaseUrl = (): string | undefined => {
  const globalProcess = (globalThis as { process?: { env?: Record<string, string | undefined> } }).process;
  return globalProcess?.env?.REACT_APP_API_BASE_URL;
};

export const API_BASE_URL = resolveViteBaseUrl() ?? resolveCraBaseUrl() ?? '';
