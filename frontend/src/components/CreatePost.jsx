import { useState } from 'react';
import { postAPI } from '../api';
import './CreatePost.css';

const CreatePost = ({ onClose, onSuccess }) => {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [caption, setCaption] = useState('');
  const [isScheduled, setIsScheduled] = useState(false);
  const [scheduledTime, setScheduledTime] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(file);
      setPreview(URL.createObjectURL(file));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!image) {
      setError('Please select an image');
      return;
    }

    if (isScheduled && !scheduledTime) {
      setError('Please select a scheduled time');
      return;
    }

    setLoading(true);
    setError('');

    const formData = new FormData();
    formData.append('image', image);
    formData.append('caption', caption);
    formData.append('is_scheduled', isScheduled);
    if (isScheduled && scheduledTime) {
      formData.append('scheduled_time', new Date(scheduledTime).toISOString());
    }

    try {
      await postAPI.createPost(formData);
      onSuccess();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create post');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Create New Post</h2>
          <button onClick={onClose} className="close-button">×</button>
        </div>

        <form onSubmit={handleSubmit} className="create-post-form">
          <div className="image-upload">
            {preview ? (
              <img src={preview} alt="Preview" className="image-preview" />
            ) : (
              <label className="upload-label">
                <span>📷 Choose Image</span>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleImageChange}
                  hidden
                />
              </label>
            )}
          </div>

          <textarea
            placeholder="Write a caption..."
            value={caption}
            onChange={(e) => setCaption(e.target.value)}
            className="caption-input"
            rows="4"
          />

          <div className="schedule-section">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={isScheduled}
                onChange={(e) => setIsScheduled(e.target.checked)}
              />
              Schedule post
            </label>

            {isScheduled && (
              <input
                type="datetime-local"
                value={scheduledTime}
                onChange={(e) => setScheduledTime(e.target.value)}
                className="datetime-input"
              />
            )}
          </div>

          {error && <div className="error-text">{error}</div>}

          <div className="form-actions">
            <button
              type="button"
              onClick={onClose}
              className="cancel-button"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || !image}
              className="submit-button"
            >
              {loading ? 'Posting...' : 'Post'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreatePost;
