import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Auth.css';

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: '',
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    // Clear error for this field
    if (errors[e.target.name]) {
      setErrors({ ...errors, [e.target.name]: '' });
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (formData.password !== formData.password_confirm) {
      newErrors.password_confirm = 'Passwords do not match';
    }

    if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setErrors({});

    const result = await register(formData);
    
    if (result.success) {
      navigate('/');
    } else {
      setErrors(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="auth-container">
      <div className="auth-box">
        <h1 className="auth-title">InstaCham</h1>
        <p className="auth-subtitle">Sign up to see photos from your friends</p>
        
        <form onSubmit={handleSubmit} className="auth-form">
          <input
            type="email"
            name="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleChange}
            required
            className="auth-input"
          />
          {errors.email && <div className="auth-error">{errors.email}</div>}

          <input
            type="text"
            name="username"
            placeholder="Username"
            value={formData.username}
            onChange={handleChange}
            required
            className="auth-input"
          />
          {errors.username && <div className="auth-error">{errors.username}</div>}

          <input
            type="text"
            name="first_name"
            placeholder="First Name (optional)"
            value={formData.first_name}
            onChange={handleChange}
            className="auth-input"
          />

          <input
            type="text"
            name="last_name"
            placeholder="Last Name (optional)"
            value={formData.last_name}
            onChange={handleChange}
            className="auth-input"
          />

          <input
            type="password"
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
            required
            className="auth-input"
          />
          {errors.password && <div className="auth-error">{errors.password}</div>}

          <input
            type="password"
            name="password_confirm"
            placeholder="Confirm Password"
            value={formData.password_confirm}
            onChange={handleChange}
            required
            className="auth-input"
          />
          {errors.password_confirm && (
            <div className="auth-error">{errors.password_confirm}</div>
          )}

          <button 
            type="submit" 
            disabled={loading}
            className="auth-button"
          >
            {loading ? 'Signing up...' : 'Sign Up'}
          </button>
        </form>

        <div className="auth-divider">
          <span>OR</span>
        </div>

        <div className="auth-signup">
          Have an account? <Link to="/login">Log in</Link>
        </div>
      </div>
    </div>
  );
};

export default Register;
