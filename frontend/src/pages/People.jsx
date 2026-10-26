import { useCallback, useState } from 'react';
import { errorMessage, userAPI } from '../api';
import { useAuth } from '../hooks/useAuth';
import { usePagedList } from '../hooks/usePagedList';

export default function People() {
  const { user: me, refreshUser } = useAuth();
  const [search, setSearch] = useState('');
  const fetchPage = useCallback((page) => userAPI.list({ page, search: search || undefined }), [search]);
  const { items, setItems, hasMore, status, loadMore } = usePagedList(fetchPage);
  const [error, setError] = useState('');

  async function toggleFollow(person) {
    setError('');
    try {
      await (person.is_following ? userAPI.unfollow(person.id) : userAPI.follow(person.id));
      const delta = person.is_following ? -1 : 1;
      setItems((current) =>
        current.map((p) =>
          p.id === person.id
            ? { ...p, is_following: !p.is_following, followers_count: p.followers_count + delta }
            : p,
        ),
      );
      refreshUser();
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  return (
    <>
      <h1>People</h1>
      <p className="muted">
        You follow {me.following_count} and have {me.followers_count} followers.
      </p>
      <label className="field">
        <span>Search by username</span>
        <input type="search" value={search} onChange={(event) => setSearch(event.target.value)} />
      </label>
      {error && (
        <p className="form-error" role="alert">
          {error}
        </p>
      )}
      {status === 'error' && <p className="form-error">People could not be loaded.</p>}
      {status === 'ready' && items.length === 0 && <p className="muted">No one matches that name.</p>}
      <ul className="people">
        {items
          .filter((person) => person.id !== me.id)
          .map((person) => (
            <li key={person.id} className="person">
              <span className="avatar" aria-hidden="true">
                {person.username[0].toUpperCase()}
              </span>
              <div>
                <p className="print-author">{person.username}</p>
                <p className="muted small">
                  {person.followers_count} followers · {person.following_count} following
                </p>
                {person.bio && <p className="small">{person.bio}</p>}
              </div>
              <button
                type="button"
                className={`btn ${person.is_following ? 'btn-quiet' : 'btn-primary'}`}
                onClick={() => toggleFollow(person)}
                aria-label={`${person.is_following ? 'Unfollow' : 'Follow'} ${person.username}`}
              >
                {person.is_following ? 'Following' : 'Follow'}
              </button>
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
