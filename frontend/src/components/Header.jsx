import { Link, useLocation } from 'react-router-dom';
import './Header.css';

function Header() {
  const location = useLocation();

  return (
    <header className="header">
      <div className="container">
        <div className="header-content">
          <Link to="/" className="logo">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
              <rect width="32" height="32" rx="6" fill="currentColor"/>
              <path d="M16 8L20 14H12L16 8Z" fill="white"/>
              <path d="M10 16H22V24H10V16Z" fill="white"/>
            </svg>
            <span>AI Paper Reviewer</span>
          </Link>
          
          <nav className="nav">
            <Link 
              to="/" 
              className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
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
