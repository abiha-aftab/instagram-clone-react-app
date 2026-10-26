import { useState } from 'react';
import { postAPI } from '../api';
import { formatRelativeTime, getImageUrl } from '../utils/helpers';
import { useAuth } from '../context/AuthContext';
import CommentSection from './CommentSection';
import './PostCard.css';

const PostCard = ({ post, onUpdate }) => {
  const { user: currentUser } = useAuth();
  const [isLiked, setIsLiked] = useState(post.is_liked);
  const [likeCount, setLikeCount] = useState(post.like_count);
  const [showComments, setShowComments] = useState(false);

  const handleLike = async () => {
    try {
      if (isLiked) {
        await postAPI.unlikePost(post.id);
        setIsLiked(false);
        setLikeCount(prev => prev - 1);
      } else {
        await postAPI.likePost(post.id);
        setIsLiked(true);
        setLikeCount(prev => prev + 1);
      }
    } catch (error) {
      console.error('Error toggling like:', error);
    }
  };

  return (
    <div className="post-card">
      <div className="post-header">
        <div className="post-user-info">
          <img 
            src={getImageUrl(post.user.profile_picture) || '/default-avatar.png'}
            alt={post.user.username}
            className="post-avatar"
          />
          <span className="post-username">{post.user.username}</span>
        </div>
        <div className="post-time">{formatRelativeTime(post.created_at)}</div>
      </div>

      <div className="post-image-container">
        <img 
          src={getImageUrl(post.image)}
          alt="Post"
          className="post-image"
        />
      </div>

      <div className="post-actions">
        <button 
          className={`action-button ${isLiked ? 'liked' : ''}`}
          onClick={handleLike}
        >
          {isLiked ? '❤️' : '🤍'} {likeCount}
        </button>
        
        <button 
          className="action-button"
          onClick={() => setShowComments(!showComments)}
        >
          💬 {post.comment_count}
        </button>
      </div>

      {post.caption && (
        <div className="post-caption">
          <span className="caption-username">{post.user.username}</span>
          <span className="caption-text">{post.caption}</span>
        </div>
      )}

      {showComments && (
        <CommentSection postId={post.id} />
      )}
    </div>
  );
};

export default PostCard;
