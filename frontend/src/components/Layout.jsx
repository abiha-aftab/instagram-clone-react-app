import { NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export default function Layout() {
  const { user, logout } = useAuth();

  return (
    <div className="shell">
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <header className="masthead">
        <NavLink to="/" className="wordmark" aria-label="InstaCham home">
          Insta<span>Cham</span>
        </NavLink>
        <nav aria-label="Main">
          <ul className="nav-list">
            <li>
              <NavLink to="/" end>
                Feed
              </NavLink>
            </li>
            <li>
              <NavLink to="/people">People</NavLink>
            </li>
            <li>
              <NavLink to="/notifications">Notifications</NavLink>
            </li>
          </ul>
        </nav>
        <div className="masthead-user">
          <span className="handle">@{user.username}</span>
          <button type="button" className="btn btn-quiet" onClick={logout}>
            Log out
          </button>
        </div>
      </header>
      <main id="main" className="page">
        <Outlet />
      </main>
    </div>
  );
}
