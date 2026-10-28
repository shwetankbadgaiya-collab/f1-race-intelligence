import { useState, useEffect } from 'react';
import {
  Database,
  Search,
  Download,
  Upload,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
  AlertCircle,
  FileText,
} from 'lucide-react';
import KPICard from '../components/KPICard';
import ChartCard from '../components/ChartCard';
import { fetchWithFallback, API_BASE_URL, fallbackData } from '../services/api';

const DATASETS = [
  { id: 'results', name: 'Race Results', desc: 'Finishing positions, points, laps, and finish status' },
  { id: 'races', name: 'Grand Prix Calendar', desc: 'Rounds, circuits, official event dates, and seasons' },
  { id: 'drivers', name: 'Driver Master Table', desc: 'Names, permanent numbers, codes, and nationalities' },
  { id: 'constructors', name: 'Constructor Master Table', desc: 'Team names, historical references, and nationalities' },
  { id: 'circuits', name: 'Circuit Venues', desc: 'Coordinates, altitudes, track locations, and host nations' },
  { id: 'driver_standings', name: 'Driver Standings', desc: 'Championship points and positions after each race' },
  { id: 'constructor_standings', name: 'Constructor Standings', desc: 'Constructor title points after each round' },
  { id: 'qualifying', name: 'Qualifying Sessions', desc: 'Grid orders, Q1, Q2, and Q3 session lap times' },
  { id: 'status', name: 'Status Classifications', desc: 'Catalog of 139+ official completion & failure statuses' },
];

export default function DataExplorer() {
  const [selectedDataset, setSelectedDataset] = useState<string>('results');
  const [dataRows, setDataRows] = useState<any[]>([]);
  const [dataQuality, setDataQuality] = useState<any[]>([]);
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(25);
  const [search, setSearch] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  // Upload State
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadResult, setUploadResult] = useState<any>(null);
  const [uploading, setUploading] = useState<boolean>(false);

  // Fetch Data Quality Report
  useEffect(() => {
    async function loadQuality() {
      try {
        const data = await fetchWithFallback<any[]>('/data-quality', 'data_quality');
        setDataQuality(data);
      } catch (err) {
        console.error(err);
      }
    }
    loadQuality();
  }, []);

  // Fetch Dataset Rows
  useEffect(() => {
    async function loadDataset() {
      setLoading(true);
      try {
        const params = new URLSearchParams({
          page: String(page),
          page_size: String(pageSize),
        });
        if (search) params.set('search', search);

        const data = await fetchWithFallback<any[]>(`/data-explorer/${selectedDataset}?${params.toString()}`).catch(() => {
          if (selectedDataset === 'results' && fallbackData.results) return fallbackData.results;
          if (selectedDataset === 'races' && fallbackData.races) return fallbackData.races;
          if (selectedDataset === 'drivers' && fallbackData.drivers) return fallbackData.drivers;
          if (selectedDataset === 'constructors' && fallbackData.constructors) return fallbackData.constructors;
          if (selectedDataset === 'circuits' && fallbackData.circuits_leaderboard) return fallbackData.circuits_leaderboard;
          return [];
        });
        setDataRows(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadDataset();
  }, [selectedDataset, page, pageSize, search]);

  const handleExportCsv = () => {
    window.open(`${API_BASE_URL}/export/${selectedDataset}`, '_blank');
  };

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) return;

    setUploading(true);
    setUploadResult(null);
    try {
      const formData = new FormData();
      formData.append('file', uploadFile);

      const res = await fetch(`${API_BASE_URL}/data-explorer/upload`, {
        method: 'POST',
        body: formData,
      });

      const json = await res.json();
      if (res.ok) {
        setUploadResult({ success: true, data: json });
      } else {
        setUploadResult({ success: false, error: json.detail || 'Upload failed validation' });
      }
    } catch (err: any) {
      setUploadResult({ success: false, error: err.message });
    } finally {
      setUploading(false);
    }
  };

  const columns = dataRows.length > 0 ? Object.keys(dataRows[0]) : [];
  const currentQuality = dataQuality.find((q) => q.table_name.toLowerCase() === selectedDataset.toLowerCase().replace('_', ''));

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="border-b border-[#222] pb-4">
        <h1 className="text-xl md:text-2xl font-black text-white tracking-tight flex items-center gap-2">
          RAW DATA EXPLORER & SCHEMA AUDIT
          <span className="text-xs px-2.5 py-0.5 rounded-full bg-[#E10600]/20 text-[#E10600] font-mono font-bold">
            RELATIONAL TABLES & EXPORTS
          </span>
        </h1>
        <p className="text-xs md:text-sm text-gray-400 mt-0.5">
          Inspect granular database rows, review null checks and completeness scores, and download validated CSV files.
        </p>
      </div>

      {/* Dataset Selector Tabs */}
      <div className="flex flex-wrap gap-2">
        {DATASETS.map((d) => (
          <button
            key={d.id}
            onClick={() => {
              setSelectedDataset(d.id);
              setPage(1);
            }}
            className={`px-3.5 py-2 rounded-xl text-xs font-semibold transition-all flex items-center gap-2 ${
              selectedDataset === d.id
                ? 'bg-[#E10600] text-white shadow-[0_0_12px_rgba(225,6,0,0.5)]'
                : 'bg-[#141414] text-gray-400 hover:text-white border border-[#262626]'
            }`}
          >
            <Database size={13} />
            <span>{d.name}</span>
          </button>
        ))}
      </div>

      {/* Table Quality & Export Toolbar */}
      <div className="bg-[#141414] border border-[#262626] rounded-xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="relative w-full md:w-72">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
            <input
              type="text"
              placeholder={`Search ${selectedDataset}...`}
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              className="w-full bg-[#1C1C1C] border border-[#333] rounded-lg pl-8 pr-3 py-1.5 text-xs text-white focus:outline-none focus:border-[#E10600]"
            />
          </div>

          <div className="flex items-center gap-2 text-xs text-gray-400">
            <span>Per page:</span>
            <select
              value={pageSize}
              onChange={(e) => {
                setPageSize(Number(e.target.value));
                setPage(1);
              }}
              className="bg-[#1C1C1C] border border-[#333] rounded p-1 text-xs text-white focus:outline-none"
            >
              <option value={15}>15</option>
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleExportCsv}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-medium text-white bg-[#E10600] hover:bg-[#B30500] transition-colors shadow-sm"
          >
            <Download size={13} />
            <span>Download {selectedDataset}.csv</span>
          </button>
        </div>
      </div>

      {/* Data Table */}
      <div className="bg-[#141414] border border-[#262626] rounded-xl p-4">
        <div className="overflow-x-auto min-h-[360px]">
          {loading ? (
            <div className="flex items-center justify-center h-64 text-gray-500 text-xs">
              Loading table data...
            </div>
          ) : dataRows.length === 0 ? (
            <div className="flex items-center justify-center h-64 text-gray-500 text-xs">
              No matching records found.
            </div>
          ) : (
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-[#2A2A2A] text-gray-400 bg-[#181818]">
                  {columns.map((col) => (
                    <th key={col} className="py-2.5 px-3 font-semibold uppercase tracking-wider text-[11px]">
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1F1F1F]">
                {dataRows.map((row, idx) => (
                  <tr key={idx} className="hover:bg-[#1A1A1A]">
                    {columns.map((col) => (
                      <td key={col} className="py-2 px-3 font-mono text-gray-300 whitespace-nowrap">
                        {row[col] !== null && row[col] !== undefined ? String(row[col]) : <span className="text-gray-600">null</span>}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Pagination Controls */}
        <div className="flex items-center justify-between pt-4 border-t border-[#222] mt-2">
          <span className="text-xs text-gray-400">
            Page <strong className="text-white font-mono">{page}</strong> (Showing up to {pageSize} records)
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="p-1.5 rounded-lg border border-[#333] text-gray-400 hover:text-white disabled:opacity-40"
            >
              <ChevronLeft size={16} />
            </button>
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={dataRows.length < pageSize}
              className="p-1.5 rounded-lg border border-[#333] text-gray-400 hover:text-white disabled:opacity-40"
            >
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* CSV Dataset Upload & Validation Form */}
      <div className="bg-[#141414] border border-[#262626] rounded-xl p-6">
        <div className="flex items-center gap-2 mb-3 border-b border-[#222] pb-3">
          <Upload size={18} className="text-[#3671C6]" />
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">
            CSV Ingestion & Schema Integrity Validator
          </h3>
        </div>
        <p className="text-xs text-gray-400 mb-4">
          Upload any external Formula 1 CSV file for schema parsing, duplicate detection, and null completeness validation.
        </p>

        <form onSubmit={handleUploadSubmit} className="flex flex-col md:flex-row items-center gap-4">
          <input
            type="file"
            accept=".csv"
            onChange={(e) => setUploadFile(e.target.files ? e.target.files[0] : null)}
            className="text-xs text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-[#222] file:text-white hover:file:bg-[#333]"
          />
          <button
            type="submit"
            disabled={!uploadFile || uploading}
            className="px-4 py-2 rounded-lg text-xs font-semibold text-white bg-[#3671C6] hover:bg-[#2B5CA3] disabled:opacity-50 transition-colors"
          >
            {uploading ? 'Validating Schema...' : 'Validate CSV'}
          </button>
        </form>

        {uploadResult && (
          <div className="mt-4 p-4 rounded-xl border border-[#333] bg-[#181818]">
            {uploadResult.success ? (
              <div className="space-y-2 text-xs">
                <div className="flex items-center gap-2 text-[#00D26A] font-bold">
                  <ShieldCheck size={16} />
                  <span>Validation Passed Successfully: {uploadResult.data.filename}</span>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-gray-300 pt-2 font-mono">
                  <div>Rows: {uploadResult.data.row_count}</div>
                  <div>Columns: {uploadResult.data.column_count}</div>
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-2 text-[#E10600] text-xs font-bold">
                <AlertCircle size={16} />
                <span>Validation Error: {uploadResult.error}</span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
