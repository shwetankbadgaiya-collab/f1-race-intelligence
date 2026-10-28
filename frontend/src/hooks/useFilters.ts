import { useState, useCallback, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import type { FilterState } from '../types';

const FILTER_KEYS: (keyof FilterState)[] = [
  'season',
  'seasonFrom',
  'seasonTo',
  'driverId',
  'constructorId',
  'circuitId',
  'country',
  'status',
];

const paramToKey: Record<string, keyof FilterState> = {
  season: 'season',
  seasonFrom: 'seasonFrom',
  seasonTo: 'seasonTo',
  driverId: 'driverId',
  constructorId: 'constructorId',
  circuitId: 'circuitId',
  country: 'country',
  status: 'status',
};

export function useFilters() {
  const [searchParams, setSearchParams] = useSearchParams();

  const filtersFromUrl = useMemo((): FilterState => {
    const f: FilterState = {};
    for (const [param, key] of Object.entries(paramToKey)) {
      const val = searchParams.get(param);
      if (val) {
        if (key === 'season' || key === 'seasonFrom' || key === 'seasonTo') {
          f[key] = parseInt(val, 10);
        } else {
          (f as Record<string, string>)[key] = val;
        }
      }
    }
    return f;
  }, [searchParams]);

  const [filters, setFiltersState] = useState<FilterState>(filtersFromUrl);

  const setFilters = useCallback(
    (updater: FilterState | ((prev: FilterState) => FilterState)) => {
      setFiltersState((prev) => {
        const next = typeof updater === 'function' ? updater(prev) : updater;
        const params = new URLSearchParams();
        for (const key of FILTER_KEYS) {
          const val = next[key];
          if (val !== undefined && val !== null && val !== '') {
            params.set(key, String(val));
          }
        }
        setSearchParams(params, { replace: true });
        return next;
      });
    },
    [setSearchParams]
  );

  const updateFilter = useCallback(
    <K extends keyof FilterState>(key: K, value: FilterState[K]) => {
      setFilters((prev) => ({ ...prev, [key]: value }));
    },
    [setFilters]
  );

  const resetFilters = useCallback(() => {
    setFilters({});
  }, [setFilters]);

  const hasActiveFilters = useMemo(() => {
    return FILTER_KEYS.some((k) => filters[k] !== undefined && filters[k] !== null && filters[k] !== '');
  }, [filters]);

  return { filters, setFilters, updateFilter, resetFilters, hasActiveFilters };
}
