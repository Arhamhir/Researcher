import { Link, useLocation } from 'react-router-dom';
import './Header.css';

function Header() {
  const location = useLocation();
  const onReview = location.pathname.startsWith('/review');

  return (
    <header className="header">
      <div className="container">
        <div className="header-content">
          <Link to="/" className="logo" aria-label="Researcher — go to upload">
            <span className="logo-mark" aria-hidden="true">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M4 15.5 13.5 6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
                <path d="M11 5.2 14.8 9" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
                <path d="M4 15.5h3" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
              </svg>
            </span>
            <span className="logo-text">
              <span className="logo-name">Researcher</span>
              <span className="logo-kicker">Blackline Review</span>
            </span>
          </Link>

          <nav className="nav" aria-label="Primary">
            <Link
              to="/"
              className={`nav-link ${!onReview ? 'active' : ''}`}
            >
              Upload
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}

export default Header;
