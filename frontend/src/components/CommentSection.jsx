import { useCallback, useState } from 'react';
import { commentAPI, errorMessage, postAPI } from '../api';
import { useAuth } from '../hooks/useAuth';
import { usePagedList } from '../hooks/usePagedList';
import { formatRelativeTime } from '../lib/format';

function Comment({ comment, canDelete, onDelete, onReply }) {
  return (
    <div className="comment">
      <p>
        <strong>{comment.username}</strong> {comment.text}
      </p>
      <p className="muted small comment-meta">
        <time dateTime={comment.created_at}>{formatRelativeTime(comment.created_at)}</time>
        {onReply && (
          <button type="button" className="link-button" onClick={() => onReply(comment)}>
            Reply
          </button>
        )}
        {canDelete && (
          <button type="button" className="link-button" onClick={() => onDelete(comment.id)}>
            Delete
          </button>
        )}
      </p>
    </div>
  );
}

export default function CommentSection({ postId }) {
  const { user } = useAuth();
  const fetchPage = useCallback((page) => postAPI.comments(postId, page), [postId]);
  const { items, hasMore, status, loadMore, reload } = usePagedList(fetchPage);
  const [text, setText] = useState('');
  const [replyTo, setReplyTo] = useState(null);
  const [error, setError] = useState('');
  const [sending, setSending] = useState(false);

  async function submit(event) {
    event.preventDefault();
    if (!text.trim()) return;
    setSending(true);
    setError('');
    try {
      await commentAPI.create({ post: postId, text: text.trim(), parent: replyTo?.id ?? null });
      setText('');
      setReplyTo(null);
      reload();
    } catch (err) {
      setError(errorMessage(err, 'Could not post your comment.'));
    } finally {
      setSending(false);
    }
  }

  async function remove(id) {
    try {
      await commentAPI.remove(id);
      reload();
    } catch (err) {
      setError(errorMessage(err, 'Could not delete the comment.'));
    }
  }

  const ownsComment = (comment) => comment.user === user?.id;

  return (
    <section className="comments" aria-label="Comments">
      {status === 'error' && <p className="form-error">Comments could not be loaded.</p>}
      {status === 'ready' && items.length === 0 && <p className="muted small">No comments yet.</p>}
      <ul className="comment-list">
        {items.map((comment) => (
          <li key={comment.id}>
            <Comment
              comment={comment}
              canDelete={ownsComment(comment)}
              onDelete={remove}
              onReply={setReplyTo}
            />
            {comment.replies.length > 0 && (
              <ul className="reply-list">
                {comment.replies.map((reply) => (
                  <li key={reply.id}>
                    <Comment comment={reply} canDelete={ownsComment(reply)} onDelete={remove} />
                  </li>
                ))}
              </ul>
            )}
          </li>
        ))}
      </ul>
      {hasMore && (
        <button type="button" className="link-button" onClick={loadMore} disabled={status === 'loading'}>
          Older comments
        </button>
      )}

      <form className="comment-form" onSubmit={submit}>
        {replyTo && (
          <p className="muted small">
            Replying to {replyTo.username}{' '}
            <button type="button" className="link-button" onClick={() => setReplyTo(null)}>
              Cancel
            </button>
          </p>
        )}
        <label className="visually-hidden" htmlFor={`comment-${postId}`}>
          Add a comment
        </label>
        <input
          id={`comment-${postId}`}
          value={text}
          onChange={(event) => setText(event.target.value)}
          placeholder="Add a comment…"
          maxLength={1000}
        />
        <button type="submit" className="btn" disabled={sending || !text.trim()}>
          Post
        </button>
        {error && (
          <p className="form-error" role="alert">
            {error}
          </p>
        )}
      </form>
    </section>
  );
}
