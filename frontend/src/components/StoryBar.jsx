import { useEffect, useState } from 'react';
import { storyAPI } from '../api';

export default function StoryBar() {
  const [stories, setStories] = useState([]);
  const [status, setStatus] = useState('loading');

  useEffect(() => {
    storyAPI
      .list()
      .then(({ data }) => {
        setStories(data.results);
        setStatus('ready');
      })
      .catch(() => setStatus('error'));
  }, []);

  if (status === 'error') return null;

  return (
    <section className="story-strip" aria-label="Stories from the last 24 hours">
      <h2 className="eyebrow">Last 24 hours</h2>
      {status === 'loading' && <p className="muted">Loading stories…</p>}
      {status === 'ready' && stories.length === 0 && (
        <p className="muted">No stories right now. Follow a few people to fill this strip.</p>
      )}
      <ol className="frames">
        {stories.map((story, index) => (
          <li key={story.id} className="frame">
            <span className="frame-number" aria-hidden="true">
              {String(index + 1).padStart(2, '0')}A
            </span>
            {story.media ? (
              <img src={story.media} alt={`${story.username}: ${story.title}`} loading="lazy" />
            ) : (
              <span className="frame-text">{story.title}</span>
            )}
            <span className="frame-caption">{story.username}</span>
          </li>
        ))}
      </ol>
    </section>
  );
}
