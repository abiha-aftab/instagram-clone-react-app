import { useState, useEffect } from 'react';
import { postAPI } from '../api';
import PostCard from '../components/PostCard';
import CreatePost from '../components/CreatePost';
import StoryBar from '../components/StoryBar';
import './Home.css';

const Home = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreatePost, setShowCreatePost] = useState(false);

  useEffect(() => {
    fetchFeed();
  }, []);

  const fetchFeed = async () => {
    try {
      setLoading(true);
      const response = await postAPI.getFeed();
      setPosts(response.data.results || response.data);
      setError('');
    } catch (err) {
      setError('Failed to load feed');
      console.error('Error fetching feed:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePostCreated = () => {
    setShowCreatePost(false);
    fetchFeed();
  };

  if (loading) {
    return (
      <div className="home-container">
        <div className="loading">Loading feed...</div>
      </div>
    );
  }

  return (
    <div className="home-container">
      <div className="feed-content">
        <StoryBar />
        
        <div className="create-post-trigger">
          <button 
            onClick={() => setShowCreatePost(true)}
            className="create-post-button"
          >
            + Create New Post
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        <div className="posts-list">
          {posts.length === 0 ? (
            <div className="no-posts">
              <p>No posts yet. Follow people to see their posts!</p>
            </div>
          ) : (
            posts.map((post) => (
              <PostCard key={post.id} post={post} onUpdate={fetchFeed} />
            ))
          )}
        </div>
      </div>

      {showCreatePost && (
        <CreatePost 
          onClose={() => setShowCreatePost(false)}
          onSuccess={handlePostCreated}
        />
      )}
    </div>
  );
};

export default Home;
