import { useEffect, useRef, useState } from 'react';
import { errorMessage, postAPI } from '../api';
import { validateImage } from '../lib/upload';

export default function CreatePost({ onClose, onCreated }) {
  const dialogRef = useRef(null);
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [title, setTitle] = useState('');
  const [caption, setCaption] = useState('');
  const [scheduledFor, setScheduledFor] = useState('');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (dialog && !dialog.open) dialog.showModal?.();
  }, []);

  useEffect(() => () => preview && URL.revokeObjectURL(preview), [preview]);

  function chooseFile(event) {
    const chosen = event.target.files[0];
    const problem = validateImage(chosen);
    setError(problem ?? '');
    setFile(problem ? null : chosen);
    setPreview(problem ? null : URL.createObjectURL(chosen));
  }

  async function submit(event) {
    event.preventDefault();
    const problem = validateImage(file);
    if (problem) {
      setError(problem);
      return;
    }
    const form = new FormData();
    form.append('image', file);
    form.append('title', title.trim());
    form.append('caption', caption.trim());
    if (scheduledFor) form.append('scheduled_for', new Date(scheduledFor).toISOString());

    setSaving(true);
    setError('');
    try {
      const { data } = await postAPI.create(form);
      onCreated(data);
    } catch (err) {
      setError(errorMessage(err, 'Could not publish the post.'));
    } finally {
      setSaving(false);
    }
  }

  return (
    <dialog ref={dialogRef} className="sheet" aria-labelledby="create-post-title" onClose={onClose}>
      <form onSubmit={submit} className="stack">
        <h2 id="create-post-title">New post</h2>

        <label className="field">
          <span>Photo</span>
          <input type="file" accept="image/jpeg,image/png,image/webp,image/gif" onChange={chooseFile} />
        </label>
        {preview && <img src={preview} alt="Preview of the chosen photo" className="sheet-preview" />}

        <label className="field">
          <span>Title</span>
          <input value={title} onChange={(event) => setTitle(event.target.value)} required minLength={2} maxLength={255} />
        </label>
        <label className="field">
          <span>Caption</span>
          <textarea value={caption} onChange={(event) => setCaption(event.target.value)} rows={3} required />
        </label>
        <label className="field">
          <span>Publish later (optional)</span>
          <input type="datetime-local" value={scheduledFor} onChange={(event) => setScheduledFor(event.target.value)} />
        </label>

        {error && (
          <p className="form-error" role="alert">
            {error}
          </p>
        )}
        <div className="row-end">
          <button type="button" className="btn btn-quiet" onClick={onClose}>
            Cancel
          </button>
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? 'Publishing…' : scheduledFor ? 'Schedule' : 'Publish'}
          </button>
        </div>
      </form>
    </dialog>
  );
}
