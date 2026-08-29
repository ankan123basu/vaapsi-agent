import './Header.css';

export default function Header() {
  return (
    <header className="layout__header" id="main-header">
      <div className="header__left">
        <div className="header__brand" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <img
            src="/images/vaapsi-logo.png"
            alt="Vaapsi (वापसी) Emblem"
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '50%',
              objectFit: 'cover',
              boxShadow: '0 0 14px rgba(255, 176, 102, 0.5)',
              border: '1.5px solid rgba(255, 176, 102, 0.4)',
            }}
          />
          <span className="header__title" style={{ display: 'flex', alignItems: 'baseline', gap: '6px' }}>
            Vaapsi <span style={{ fontSize: '0.85rem', opacity: 0.8, fontWeight: 500, fontFamily: 'var(--font-body)' }}>(वापसी)</span>
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
