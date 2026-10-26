export default function AuthLayout({ title, children, footer }) {
  return (
    <main className="auth">
      <div className="auth-card">
        <p className="wordmark" aria-hidden="true">
          Insta<span>Cham</span>
        </p>
        <h1>{title}</h1>
        {children}
        <p className="auth-footer">{footer}</p>
      </div>
    </main>
  );
}
