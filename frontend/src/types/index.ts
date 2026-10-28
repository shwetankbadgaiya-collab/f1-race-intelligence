// ── Core Domain Types ──

export interface Season {
  year: number;
  url?: string;
}

export interface Circuit {
  circuitId: string;
  circuitName: string;
  locality: string;
  country: string;
  lat?: number;
  lng?: number;
  url?: string;
  totalRaces?: number;
}

export interface Driver {
  driverId: string;
  givenName: string;
  familyName: string;
  fullName?: string;
  dateOfBirth?: string;
  nationality: string;
  code?: string;
  number?: string;
  url?: string;
  constructorId?: string;
  constructorName?: string;
}

export interface Constructor {
  constructorId: string;
  name: string;
  nationality: string;
  url?: string;
}

export interface Race {
  season: number;
  round: number;
  raceName: string;
  circuitId: string;
  circuitName: string;
  locality: string;
  country: string;
  date: string;
  time?: string;
  url?: string;
}

export interface Result {
  season: number;
  round: number;
  raceName: string;
  circuitId: string;
  circuitName: string;
  driverId: string;
  driverName: string;
  constructorId: string;
  constructorName: string;
  grid: number;
  position: number | null;
  positionText: string;
  points: number;
  laps: number;
  status: string;
  time?: string;
  fastestLap?: string;
  fastestLapTime?: string;
  fastestLapSpeed?: string;
}

export interface Status {
  statusId: string;
  status: string;
  count: number;
}

// ── Analytics / Aggregated Types ──

export interface OverviewData {
  totalRaces: number;
  totalDrivers: number;
  totalConstructors: number;
  totalCircuits: number;
  totalPodiums: number;
  classifiedFinishes: number;
  dnfCount: number;
  seasonRange: string;
  avgDriversPerSeason: number;
  avgRacesPerSeason: number;
}

export interface ChampionshipTrend {
  season: number;
  [constructorName: string]: number | string;
}

export interface DriverStats {
  driverId: string;
  driverName: string;
  nationality: string;
  constructorId?: string;
  constructorName?: string;
  totalRaces: number;
  totalWins: number;
  totalPodiums: number;
  totalPoints: number;
  totalPoles?: number;
  totalDNFs: number;
  bestFinish: number;
  avgFinishPosition: number;
  winPercentage: number;
  podiumPercentage: number;
  dnfPercentage: number;
  seasons: number[];
  pointsBySeason?: Record<string, number>;
  winsBySeason?: Record<string, number>;
}

export interface ConstructorStats {
  constructorId: string;
  constructorName: string;
  nationality: string;
  totalRaces: number;
  totalWins: number;
  totalPodiums: number;
  totalPoints: number;
  totalDNFs: number;
  championships?: number;
  avgFinishPosition: number;
  winPercentage: number;
  podiumPercentage: number;
  dnfPercentage: number;
  seasons: number[];
  drivers?: string[];
  pointsBySeason?: Record<string, number>;
}

export interface ReliabilityData {
  season: number;
  totalDNFs: number;
  mechanicalDNFs: number;
  crashDNFs: number;
  otherDNFs: number;
  totalRaces: number;
  dnfRate: number;
}

export interface DNFReasonBreakdown {
  reason: string;
  count: number;
  percentage: number;
  category: string;
}

export interface PodiumData {
  driverId: string;
  driverName: string;
  nationality: string;
  constructorName?: string;
  wins: number;
  seconds: number;
  thirds: number;
  totalPodiums: number;
}

export interface TyreData {
  compound: string;
  count: number;
  avgLaps: number;
}

export interface DataQuality {
  dataset: string;
  totalRecords: number;
  completeness: number;
  missingFields: string[];
  coverage: string;
  lastUpdated?: string;
}

export interface Insight {
  id: string;
  title: string;
  description: string;
  type: 'trend' | 'anomaly' | 'record' | 'comparison';
  importance: 'high' | 'medium' | 'low';
  relatedData?: string;
}

// ── Filter & Pagination ──

export interface FilterState {
  season?: number;
  seasonFrom?: number;
  seasonTo?: number;
  driverId?: string;
  constructorId?: string;
  circuitId?: string;
  country?: string;
  status?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// ── Chart Data Types ──

export interface ChartDataPoint {
  name: string;
  value: number;
  color?: string;
}

export interface MultiSeriesDataPoint {
  name: string;
  [key: string]: string | number;
}

export interface FinishingPositionData {
  position: number;
  count: number;
  percentage: number;
}

export interface CircuitStats {
  circuitId: string;
  circuitName: string;
  country: string;
  locality: string;
  totalRaces: number;
  uniqueWinners: number;
  avgDNFRate: number;
  mostWins?: { driverName: string; wins: number };
}

export interface SeasonHeatmapEntry {
  season: number;
  constructorId: string;
  constructorName: string;
  position: number;
  points: number;
}

export interface DriverComparison {
  driverId: string;
  driverName: string;
  stats: DriverStats;
}

export interface NationalityPodiums {
  nationality: string;
  totalPodiums: number;
  wins: number;
  driverCount: number;
}

// ── API Response wrappers ──

export interface ApiResponse<T> {
  data: T;
  status: 'success' | 'error';
  message?: string;
}

export interface ApiError {
  status: number;
  message: string;
  detail?: string;
}
