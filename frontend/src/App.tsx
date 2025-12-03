import { type CSSProperties } from 'react';
import { BrowserRouter, NavLink, Route, Routes } from 'react-router-dom';
import OverviewPage from './pages/OverviewPage';
import ComparisonPage from './pages/ComparisonPage';
import RecommendationsPage from './pages/RecommendationsPage';
import { API_BASE_URL } from './config/api';

const navLinks = [
  { path: '/', label: 'Overview' },
  { path: '/comparison', label: 'Comparison' },
  { path: '/recommendations', label: 'Recommendations' },
];

const navStyle: CSSProperties = {
  display: 'flex',
  gap: '0.75rem',
  flexWrap: 'wrap',
  marginTop: '1rem',
};

const pillStyle = (isActive: boolean): CSSProperties => ({
  padding: '0.4rem 0.85rem',
  borderRadius: '999px',
  border: '1px solid',
  borderColor: isActive ? '#0b5ed7' : '#d0d7de',
  textDecoration: 'none',
  color: isActive ? '#0b5ed7' : '#24292f',
  backgroundColor: isActive ? 'rgba(11, 94, 215, 0.08)' : 'transparent',
  fontWeight: isActive ? 600 : 500,
});

const App = () => {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <header>
          <h1>Cloud Optimization Dashboard</h1>
          <p className="env-hint">
            API Base URL: {API_BASE_URL || 'not configured'}
          </p>
          <nav aria-label="Primary navigation" style={navStyle}>
            {navLinks.map((link) => (
              <NavLink
                key={link.path}
                to={link.path}
                className="nav-link"
                style={({ isActive }) => pillStyle(isActive)}
                end={link.path === '/'}
              >
                {link.label}
              </NavLink>
            ))}
          </nav>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<OverviewPage />} />
            <Route path="/comparison" element={<ComparisonPage />} />
            <Route path="/recommendations" element={<RecommendationsPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
};

export default App;
