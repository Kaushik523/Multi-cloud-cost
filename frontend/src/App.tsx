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

const App = () => {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <header>
          <h1>Cloud Optimization Dashboard</h1>
          <p className="env-hint">
            API Base URL: {API_BASE_URL || 'not configured'}
          </p>
          <nav>
            {navLinks.map((link) => (
              <NavLink
                key={link.path}
                to={link.path}
                className={({ isActive }) => (isActive ? 'active' : '')}
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
