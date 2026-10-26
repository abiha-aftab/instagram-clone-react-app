import { useCallback } from 'react';
import { notificationAPI } from '../api';
import { usePagedList } from '../hooks/usePagedList';
import { formatRelativeTime } from '../lib/format';

export default function Notifications() {
  const fetchPage = useCallback((page) => notificationAPI.list({ page }), []);
  const { items, setItems, hasMore, status, loadMore } = usePagedList(fetchPage);
  const unread = items.filter((item) => !item.is_read).length;

  async function markRead(id) {
    await notificationAPI.markRead(id);
    setItems((current) => current.map((n) => (n.id === id ? { ...n, is_read: true } : n)));
  }

  async function markAll() {
    await notificationAPI.markAllRead();
    setItems((current) => current.map((n) => ({ ...n, is_read: true })));
  }

  return (
    <>
      <div className="feed-head">
        <h1>Notifications</h1>
        <button type="button" className="btn" onClick={markAll} disabled={unread === 0}>
          Mark all read
        </button>
      </div>
      {status === 'error' && <p className="form-error">Notifications could not be loaded.</p>}
      {status === 'ready' && items.length === 0 && <p className="muted">You're all caught up.</p>}
      <ul className="notes">
        {items.map((note) => (
          <li key={note.id} className={`note${note.is_read ? '' : ' is-unread'}`}>
            <span className="note-kind">{note.notification_type}</span>
            <p>{note.message}</p>
            <time className="muted small" dateTime={note.created_at}>
              {formatRelativeTime(note.created_at)}
            </time>
            {!note.is_read && (
              <button type="button" className="link-button" onClick={() => markRead(note.id)}>
                Mark read
              </button>
            )}
          </li>
        ))}
      </ul>
      {hasMore && (
        <button type="button" className="btn btn-wide" onClick={loadMore} disabled={status === 'loading'}>
          Load more
        </button>
      )}
    </>
  );
}
