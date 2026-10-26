import { useState } from 'react';
import { errorMessage, postAPI } from '../api';
import { useAuth } from '../hooks/useAuth';
import { formatRelativeTime, plural } from '../lib/format';
import CommentSection from './CommentSection';

export default function PostCard({ post, onDeleted }) {
  const { user } = useAuth();
  const [liked, setLiked] = useState(post.is_liked);
  const [likes, setLikes] = useState(post.likes_count);
  const [busy, setBusy] = useState(false);
  const [showComments, setShowComments] = useState(false);
  const [error, setError] = useState('');
  const isOwner = user?.id === post.author.id;

  async function toggleLike() {
    setBusy(true);
    setError('');
    const next = !liked;
    setLiked(next);
    setLikes((count) => count + (next ? 1 : -1));
    try {
      await (next ? postAPI.like(post.id) : postAPI.unlike(post.id));
    } catch (err) {
      setLiked(!next);
      setLikes((count) => count + (next ? -1 : 1));
      setError(errorMessage(err, 'Could not update your like.'));
    } finally {
      setBusy(false);
    }
  }

  async function deletePost() {
    if (!window.confirm('Delete this post?')) return;
    try {
      await postAPI.remove(post.id);
      onDeleted(post.id);
    } catch (err) {
      setError(errorMessage(err, 'Could not delete the post.'));
    }
  }

  return (
    <article className="print" aria-labelledby={`post-${post.id}-title`}>
      <header className="print-head">
        <span className="avatar" aria-hidden="true">
          {post.author.username[0].toUpperCase()}
        </span>
        <div>
          <p className="print-author">{post.author.username}</p>
          <p className="muted small">
            <time dateTime={post.created_at}>{formatRelativeTime(post.created_at)}</time>
          </p>
        </div>
        {isOwner && (
          <button type="button" className="btn btn-quiet btn-danger" onClick={deletePost}>
            Delete
          </button>
        )}
      </header>

      {post.image && (
        <img className="print-photo" src={post.image} alt={post.caption || post.title} loading="lazy" />
      )}

      <div className="print-body">
        <h3 id={`post-${post.id}-title`} className="print-title">
          {post.title}
        </h3>
        {post.caption && <p>{post.caption}</p>}

        <div className="print-actions">
          <button
            type="button"
            className={`btn btn-like${liked ? ' is-liked' : ''}`}
            aria-pressed={liked}
            onClick={toggleLike}
            disabled={busy}
          >
            {liked ? 'Liked' : 'Like'}
          </button>
          <span className="muted small">{plural(likes, 'like')}</span>
          <button
            type="button"
            className="btn btn-quiet"
            aria-expanded={showComments}
            onClick={() => setShowComments((open) => !open)}
          >
            {plural(post.comments_count, 'comment')}
          </button>
        </div>
        {error && (
          <p className="form-error" role="alert">
            {error}
          </p>
        )}
        {showComments && <CommentSection postId={post.id} />}
      </div>
    </article>
  );
}
