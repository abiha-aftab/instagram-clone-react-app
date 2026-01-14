import { useState, useEffect } from 'react';
import { postAPI } from '../api';
import { formatRelativeTime } from '../utils/helpers';
import './CommentSection.css';

const CommentSection = ({ postId }) => {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [replyTo, setReplyTo] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchComments();
  }, [postId]);

  const fetchComments = async () => {
    try {
      const response = await postAPI.getPostComments(postId);
      setComments(response.data.results || response.data);
    } catch (error) {
      console.error('Error fetching comments:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    setLoading(true);
    try {
      await postAPI.createComment(postId, {
        text: newComment,
        parent: replyTo,
      });
      
      setNewComment('');
      setReplyTo(null);
      fetchComments();
    } catch (error) {
      console.error('Error creating comment:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="comment-section">
      <div className="comments-list">
        {comments.map((comment) => (
          <div key={comment.id} className="comment">
            <div className="comment-header">
              <span className="comment-username">{comment.user.username}</span>
              <span className="comment-time">{formatRelativeTime(comment.created_at)}</span>
            </div>
            <p className="comment-text">{comment.text}</p>
            {comment.reply_count > 0 && (
              <button 
                className="view-replies"
                onClick={() => {/* TODO: Load replies */}}
              >
                View {comment.reply_count} {comment.reply_count === 1 ? 'reply' : 'replies'}
              </button>
            )}
            <button 
              className="reply-button"
              onClick={() => setReplyTo(comment.id)}
            >
              Reply
            </button>
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="comment-form">
        {replyTo && (
          <div className="reply-indicator">
            Replying to comment
            <button onClick={() => setReplyTo(null)}>Cancel</button>
          </div>
        )}
        <input
          type="text"
          placeholder="Add a comment..."
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          className="comment-input"
        />
        <button 
          type="submit" 
          disabled={loading || !newComment.trim()}
          className="comment-submit"
        >
          Post
        </button>
      </form>
    </div>
  );
};

export default CommentSection;
