"""Pydantic response schemas for F1 Race Intelligence Dashboard API."""

from pydantic import BaseModel, Field
from typing import Any, Generic, List, Optional, TypeVar, Union
from datetime import date as dt_date


# ─── Base entity schemas ───────────────────────────────────────────

class SeasonSchema(BaseModel):
    """Schema for an F1 season."""
    year: int
    url: Optional[str] = None

    model_config = {"from_attributes": True}


class CircuitSchema(BaseModel):
    """Schema for a racing circuit."""
    circuitId: int
    circuitRef: str
    name: str
    location: Optional[str] = None
    country: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    alt: Optional[float] = None
    url: Optional[str] = None

    model_config = {"from_attributes": True}


class DriverSchema(BaseModel):
    """Schema for a driver."""
    driverId: int
    driverRef: str
    number: Optional[int] = None
    code: Optional[str] = None
    forename: str
    surname: str
    dob: Optional[dt_date] = None
    nationality: Optional[str] = None
    url: Optional[str] = None

    model_config = {"from_attributes": True}


class ConstructorSchema(BaseModel):
    """Schema for a constructor / team."""
    constructorId: int
    constructorRef: str
    name: str
    nationality: Optional[str] = None
    url: Optional[str] = None

    model_config = {"from_attributes": True}


class StatusSchema(BaseModel):
    """Schema for a race finish status."""
    statusId: int
    status: str

    model_config = {"from_attributes": True}


class RaceSchema(BaseModel):
    """Schema for a race event."""
    raceId: int
    year: int
    round: int
    circuitId: int
    name: str
    date: Optional[Union[dt_date, str]] = None
    time: Optional[str] = None
    url: Optional[str] = None
    circuit: Optional[CircuitSchema] = None

    model_config = {"from_attributes": True}


class ResultSchema(BaseModel):
    """Schema for a race result."""
    resultId: int
    raceId: int
    driverId: int
    constructorId: int
    number: Optional[int] = None
    grid: Optional[int] = None
    position: Optional[int] = None
    positionText: Optional[str] = None
    positionOrder: Optional[int] = None
    points: Optional[float] = None
    laps: Optional[int] = None
    time: Optional[str] = None
    milliseconds: Optional[int] = None
    fastestLap: Optional[int] = None
    rank: Optional[int] = None
    fastestLapTime: Optional[str] = None
    fastestLapSpeed: Optional[str] = None
    statusId: int

    model_config = {"from_attributes": True}


# ─── Composite / analytics response schemas ────────────────────────

class OverviewResponse(BaseModel):
    """Dashboard overview statistics."""
    total_races: int = 0
    total_drivers: int = 0
    total_constructors: int = 0
    total_circuits: int = 0
    total_podiums: int = 0
    classified_finishes: int = 0
    unclassified_finishes: int = 0
    season_range: Optional[str] = None


class ChampionshipTrendItem(BaseModel):
    """Single data point in championship trend analysis."""
    season: int
    constructor: str
    constructor_id: int
    points: float
    position: Optional[int] = None
    wins: int = 0


class SeasonSummary(BaseModel):
    """Per-season summary for a driver or constructor."""
    season: int
    points: float = 0.0
    wins: int = 0
    podiums: int = 0
    races: int = 0
    position: Optional[int] = None


class DriverStatsResponse(BaseModel):
    """Detailed statistics for a single driver."""
    driver: DriverSchema
    season_points: float = 0.0
    wins: int = 0
    podiums: int = 0
    poles: int = 0
    fastest_laps: int = 0
    race_starts: int = 0
    finish_rate: float = 0.0
    dnf_count: int = 0
    avg_finish_position: Optional[float] = None
    seasons: List[SeasonSummary] = []
    constructors: List[ConstructorSchema] = []


class DriverComparisonItem(BaseModel):
    """Comparison data for a single driver."""
    driver: DriverSchema
    total_points: float = 0.0
    wins: int = 0
    podiums: int = 0
    poles: int = 0
    fastest_laps: int = 0
    race_starts: int = 0
    finish_rate: float = 0.0
    dnf_count: int = 0
    avg_finish_position: Optional[float] = None
    season_data: List[SeasonSummary] = []


class DriverComparisonResponse(BaseModel):
    """Response for driver comparison endpoint."""
    drivers: List[DriverComparisonItem] = []
    start_season: int
    end_season: int


class ConstructorStatsResponse(BaseModel):
    """Detailed statistics for a single constructor."""
    constructor: ConstructorSchema
    total_points: float = 0.0
    wins: int = 0
    podiums: int = 0
    poles: int = 0
    race_entries: int = 0
    finish_rate: float = 0.0
    dnf_count: int = 0
    championships: int = 0
    seasons: List[SeasonSummary] = []
    drivers: List[DriverSchema] = []


class ConstructorComparisonItem(BaseModel):
    """Comparison data for a single constructor."""
    constructor: ConstructorSchema
    total_points: float = 0.0
    wins: int = 0
    podiums: int = 0
    race_entries: int = 0
    finish_rate: float = 0.0
    dnf_count: int = 0
    season_data: List[SeasonSummary] = []


class ConstructorComparisonResponse(BaseModel):
    """Response for constructor comparison endpoint."""
    constructors: List[ConstructorComparisonItem] = []
    start_season: int
    end_season: int


class ReliabilityItem(BaseModel):
    """Reliability data for a single entity (driver, constructor, or circuit)."""
    entity_id: int
    entity_name: str
    entity_type: str  # "driver", "constructor", or "circuit"
    total_entries: int = 0
    classified_finishes: int = 0
    dnf_count: int = 0
    finish_rate: float = 0.0
    mechanical_dnf: int = 0
    accident_dnf: int = 0
    other_dnf: int = 0
    dnf_reasons: List[dict] = []


class ReliabilityResponse(BaseModel):
    """Response for reliability endpoint."""
    data: List[ReliabilityItem] = []
    season: Optional[int] = None
    filters: dict = {}


class PodiumItem(BaseModel):
    """Podium appearance data."""
    driver_id: int
    driver_name: str
    constructor_name: str
    nationality: Optional[str] = None
    wins: int = 0
    seconds: int = 0
    thirds: int = 0
    total_podiums: int = 0
    podium_rate: Optional[float] = None
    race_starts: int = 0


class PodiumResponse(BaseModel):
    """Response for podiums endpoint."""
    data: List[PodiumItem] = []
    total: int = 0
    filters: dict = {}


class TyreAnalysisResponse(BaseModel):
    """Response for tyre analysis endpoint.

    Tyre compound data requires stint-level data not available in the
    base Ergast dataset, so this response indicates data unavailability.
    """
    data_available: bool = False
    message: str = (
        "Detailed tyre compound analysis requires stint-level data "
        "(tyre compound per stint) which is not available in the base Ergast "
        "dataset. To enable this feature, integrate a data source that "
        "provides stint-level tyre compound information, such as the "
        "FastF1 Python library or the FIA timing data."
    )
    data: List[Any] = []


class DataQualityItem(BaseModel):
    """Data quality metric for a single table."""
    table_name: str
    total_rows: int = 0
    null_counts: dict = {}
    completeness: float = 0.0
    date_range: Optional[str] = None


class DataQualityResponse(BaseModel):
    """Response for data quality endpoint."""
    tables: List[DataQualityItem] = []
    overall_completeness: float = 0.0
    total_records: int = 0
    database_size_mb: Optional[float] = None


class InsightItem(BaseModel):
    """A single computed insight."""
    category: str  # "performance", "reliability", "consistency", "trend"
    title: str
    description: str
    metric_value: Optional[float] = None
    comparison_value: Optional[float] = None
    season_range: Optional[str] = None
    severity: str = "info"  # "info", "positive", "negative", "warning"


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""
    data: List[T] = []
    total: int = 0
    page: int = 1
    per_page: int = 25
