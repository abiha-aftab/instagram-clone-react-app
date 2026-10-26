import { useState } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import { errorMessage } from '../api';
import { useAuth } from '../hooks/useAuth';
import AuthLayout from './AuthLayout';

export default function Register() {
  const { user, register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', username: '', password: '', confirm: '' });
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  if (user) return <Navigate to="/" replace />;

  const update = (event) => setForm({ ...form, [event.target.name]: event.target.value });

  async function submit(event) {
    event.preventDefault();
    if (form.password !== form.confirm) {
      setError('The passwords do not match.');
      return;
    }
    setBusy(true);
    setError('');
    try {
      await register(form);
      navigate('/');
    } catch (err) {
      setError(errorMessage(err, 'Registration failed.'));
      setBusy(false);
    }
  }

  return (
    <AuthLayout
      title="Create an account"
      footer={
        <>
          Already registered? <Link to="/login">Log in</Link>
        </>
      }
    >
      <form className="stack" onSubmit={submit}>
        <label className="field">
          <span>Email</span>
          <input type="email" name="email" autoComplete="email" value={form.email} onChange={update} required />
        </label>
        <label className="field">
          <span>Username</span>
          <input name="username" autoComplete="username" value={form.username} onChange={update} required />
        </label>
        <label className="field">
          <span>Password</span>
          <input
            type="password"
            name="password"
            autoComplete="new-password"
            aria-describedby="password-rules"
            value={form.password}
            onChange={update}
            required
            minLength={8}
          />
        </label>
        <p id="password-rules" className="muted small">
          At least 8 characters with upper and lower case, a digit and a symbol.
        </p>
        <label className="field">
          <span>Confirm password</span>
          <input
            type="password"
            name="confirm"
            autoComplete="new-password"
            value={form.confirm}
            onChange={update}
            required
          />
        </label>
        {error && (
          <p className="form-error" role="alert">
            {error}
          </p>
        )}
        <button type="submit" className="btn btn-primary btn-wide" disabled={busy}>
          {busy ? 'Creating account…' : 'Create account'}
        </button>
      </form>
    </AuthLayout>
  );
}
