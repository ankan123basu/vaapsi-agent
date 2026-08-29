import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import CaseDetail from './pages/CaseDetail';
import './styles/tokens.css';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/case/:caseId" element={<CaseDetail />} />
      </Routes>
    </BrowserRouter>
  );
}
