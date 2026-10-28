import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Overview from './pages/Overview';
import DriverAnalytics from './pages/DriverAnalytics';
import ConstructorAnalytics from './pages/ConstructorAnalytics';
import TyreStrategy from './pages/TyreStrategy';
import CircuitIntelligence from './pages/CircuitIntelligence';
import ReliabilityDNF from './pages/ReliabilityDNF';
import GlobalPodiums from './pages/GlobalPodiums';
import DataExplorer from './pages/DataExplorer';
import About from './pages/About';

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Overview />} />
        <Route path="/drivers" element={<DriverAnalytics />} />
        <Route path="/constructors" element={<ConstructorAnalytics />} />
        <Route path="/tyres" element={<TyreStrategy />} />
        <Route path="/circuits" element={<CircuitIntelligence />} />
        <Route path="/reliability" element={<ReliabilityDNF />} />
        <Route path="/podiums" element={<GlobalPodiums />} />
        <Route path="/data-explorer" element={<DataExplorer />} />
        <Route path="/about" element={<About />} />
        {/* Fallback route */}
        <Route path="*" element={<Overview />} />
      </Routes>
    </Layout>
  );
}
