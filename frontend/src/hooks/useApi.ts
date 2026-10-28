import { useState, useEffect, useCallback, useRef } from 'react';

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

interface UseApiReturn<T> extends UseApiState<T> {
  refetch: () => void;
}

export function useApi<T>(
  fetcher: (signal: AbortSignal) => Promise<T>,
  deps: unknown[] = []
): UseApiReturn<T> {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: true,
    error: null,
  });
  const mountedRef = useRef(true);

  const fetchData = useCallback(() => {
    const controller = new AbortController();
    setState((prev) => ({ ...prev, loading: true, error: null }));

    fetcher(controller.signal)
      .then((data) => {
        if (mountedRef.current) {
          setState({ data, loading: false, error: null });
        }
      })
      .catch((err) => {
        if (err.name === 'AbortError') return;
        if (mountedRef.current) {
          setState({ data: null, loading: false, error: err.message || 'An error occurred' });
        }
      });

    return () => {
      controller.abort();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => {
    mountedRef.current = true;
    const cleanup = fetchData();
    return () => {
      mountedRef.current = false;
      cleanup();
    };
  }, [fetchData]);

  return { ...state, refetch: fetchData };
}

export function useApiLazy<T>(): {
  data: T | null;
  loading: boolean;
  error: string | null;
  execute: (fetcher: () => Promise<T>) => Promise<T | null>;
  reset: () => void;
} {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const execute = useCallback(async (fetcher: () => Promise<T>) => {
    setState({ data: null, loading: true, error: null });
    try {
      const data = await fetcher();
      setState({ data, loading: false, error: null });
      return data;
    } catch (err) {
      setState({ data: null, loading: false, error: (err as Error).message || 'An error occurred' });
      return null;
    }
  }, []);

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  return { ...state, execute, reset };
}
