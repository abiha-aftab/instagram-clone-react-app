import { useCallback, useEffect, useState } from 'react';

// Loads a DRF page-number list and appends further pages on demand.
export function usePagedList(fetchPage) {
  const [items, setItems] = useState([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);
  const [status, setStatus] = useState('loading');
  const [reloadKey, setReloadKey] = useState(0);
  const [source, setSource] = useState(() => fetchPage);

  // A new fetcher (e.g. a changed search) starts again from page 1.
  if (source !== fetchPage) {
    setSource(() => fetchPage);
    setPage(1);
    setStatus('loading');
  }

  useEffect(() => {
    let cancelled = false;
    fetchPage(page)
      .then(({ data }) => {
        if (cancelled) return;
        setItems((current) => (page === 1 ? data.results : [...current, ...data.results]));
        setHasMore(Boolean(data.next));
        setStatus('ready');
      })
      .catch(() => {
        if (!cancelled) setStatus('error');
      });
    return () => {
      cancelled = true;
    };
  }, [fetchPage, page, reloadKey]);

  const loadMore = useCallback(() => {
    setStatus('loading');
    setPage((current) => current + 1);
  }, []);

  const reload = useCallback(() => {
    setStatus('loading');
    setPage(1);
    setReloadKey((key) => key + 1);
  }, []);

  return { items, setItems, hasMore, status, loadMore, reload };
}
