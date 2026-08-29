import './Header.css';

export default function Header() {
  return (
    <header className="layout__header" id="main-header">
      <div className="header__left">
        <div className="header__brand" style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <img
            src="/images/vaapsi-logo.png"
            alt="Vaapsi (वापसी) Emblem"
            style={{
              width: '64px',
              height: '64px',
              borderRadius: '50%',
              objectFit: 'cover',
              boxShadow: '0 0 24px rgba(255, 176, 102, 0.65)',
              border: '2.5px solid rgba(255, 176, 102, 0.7)',
            }}
          />
          <span className="header__title" style={{ display: 'flex', alignItems: 'baseline', gap: '8px', fontSize: '1.65rem' }}>
            Vaapsi <span style={{ fontSize: '1rem', opacity: 0.85, fontWeight: 600, fontFamily: 'var(--font-body)' }}>(वापसी)</span>
          </span>
        </div>

        {/* Live System Status Pill */}
        <div className="header__status-pill">
          <span className="header__status-dot" />
          <span className="text-mono" style={{ fontSize: '0.6875rem', letterSpacing: '0.05em' }}>
            LIVE · TEST MODE API
          </span>
        </div>
      </div>

      <nav className="header__nav">
        <span className="text-body-sm header__nav-item header__nav-item--active">
          Dashboard
        </span>
        <a
          href="http://localhost:8000/docs"
          target="_blank"
          rel="noopener noreferrer"
          className="text-body-sm header__nav-item"
        >
          API Docs
        </a>
        <a
          href="http://localhost:8000/health"
          target="_blank"
          rel="noopener noreferrer"
          className="text-body-sm header__nav-item"
        >
          System Health
        </a>
      </nav>
    </header>
  );
}
