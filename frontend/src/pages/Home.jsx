import { useCallback, useState } from 'react';
import { postAPI } from '../api';
import CreatePost from '../components/CreatePost';
import PostCard from '../components/PostCard';
import StoryBar from '../components/StoryBar';
import { usePagedList } from '../hooks/usePagedList';

export default function Home() {
  const fetchPage = useCallback((page) => postAPI.feed(page), []);
  const { items: posts, setItems, hasMore, status, loadMore, reload } = usePagedList(fetchPage);
  const [composing, setComposing] = useState(false);
  const [notice, setNotice] = useState('');

  function handleCreated(post) {
    setComposing(false);
    setNotice(post.is_published ? '' : 'Scheduled. It will appear in the feed at the time you picked.');
    reload();
  }

  const removePost = (id) => setItems((current) => current.filter((post) => post.id !== id));

  return (
    <>
      <StoryBar />

      <div className="feed-head">
        <h1>Your feed</h1>
        <button type="button" className="btn btn-primary" onClick={() => setComposing(true)}>
          New post
        </button>
      </div>
      {notice && (
        <p className="notice" role="status">
          {notice}
        </p>
      )}

      {status === 'error' && (
        <div className="empty" role="alert">
          <p>The feed could not be loaded.</p>
          <button type="button" className="btn" onClick={reload}>
            Try again
          </button>
        </div>
      )}
      {status === 'ready' && posts.length === 0 && (
        <div className="empty">
          <p>Nothing here yet. Share a photo, or find people to follow.</p>
        </div>
      )}

      <div className="feed">
        {posts.map((post) => (
          <PostCard key={post.id} post={post} onDeleted={removePost} />
        ))}
      </div>

      {status === 'loading' && (
        <p className="page-status" role="status">
          Loading posts…
        </p>
      )}
      {hasMore && status === 'ready' && (
        <button type="button" className="btn btn-wide" onClick={loadMore}>
          Load more
        </button>
      )}

      {composing && <CreatePost onClose={() => setComposing(false)} onCreated={handleCreated} />}
    </>
  );
}
