import fallbackData from '../data/fallbackData.json';

export const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api').replace(/\/+$/, '');

export async function fetchWithFallback<T>(endpoint: string, fallbackKey?: keyof typeof fallbackData): Promise<T> {
  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;
  
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3500);
    
    const response = await fetch(url, {
      signal: controller.signal,
      headers: { Accept: 'application/json' },
    });
    clearTimeout(timeoutId);

    if (response.ok) {
      const json = await response.json();
      return json as T;
    }
  } catch (err) {
    // Backend unavailable or timed out, gracefully use fallback
    console.warn(`[F1 Race Intelligence] API request to ${url} unavailable, using verified historical dataset.`, err);
  }

  if (fallbackKey && fallbackData[fallbackKey]) {
    return fallbackData[fallbackKey] as unknown as T;
  }

  throw new Error(`Data unavailable for ${endpoint}`);
}

export { fallbackData };
