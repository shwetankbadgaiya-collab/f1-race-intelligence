"""Core data access service for F1 Race Intelligence Dashboard.

All statistics are computed from the database using SQLAlchemy queries
and Pandas for complex aggregations. Nothing is hard-coded.
"""

import re
import os
from datetime import date
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from sqlalchemy import func, case, distinct, or_, and_, desc, asc, text, inspect
from sqlalchemy.orm import Session, joinedload

from app.models import (
    Season, Circuit, Constructor, Driver, Race, Result, Status,
    DriverStanding, ConstructorStanding, Qualifying, PitStop, LapTime,
)
from app.schemas import (
    SeasonSchema, CircuitSchema, DriverSchema, ConstructorSchema,
    RaceSchema, ResultSchema, OverviewResponse, ChampionshipTrendItem,
    SeasonSummary, DriverStatsResponse, DriverComparisonItem,
    DriverComparisonResponse, ConstructorStatsResponse,
    ConstructorComparisonItem, ConstructorComparisonResponse,
    ReliabilityItem, ReliabilityResponse, PodiumItem, PodiumResponse,
    DataQualityItem, DataQualityResponse, PaginatedResponse,
)


# ─── Helpers ───────────────────────────────────────────────────────

# Statuses that count as classified (finished the race)
_FINISHED_PATTERN = re.compile(r"^(Finished|\+\d+ Lap(s)?)$", re.IGNORECASE)


def _is_classified(status_text: str) -> bool:
    """Return True if the status means the driver was classified."""
    return bool(_FINISHED_PATTERN.match(status_text))


def _classified_status_filter():
    """SQLAlchemy filter expression for classified finishes.

    Classified = status is 'Finished' OR matches '+N Lap(s)' pattern.
    """
    return or_(
        Status.status == "Finished",
        Status.status.like("+% Lap%"),
    )


def _dnf_status_filter():
    """SQLAlchemy filter for DNF (not classified) results."""
    return and_(
        Status.status != "Finished",
        ~Status.status.like("+% Lap%"),
    )


def _season_range_filter(query, start: Optional[int], end: Optional[int]):
    """Apply optional season range filters using Race.year."""
    if start is not None:
        query = query.filter(Race.year >= start)
    if end is not None:
        query = query.filter(Race.year <= end)
    return query


# ─── Seasons ───────────────────────────────────────────────────────

def get_seasons(
    db: Session,
    start: Optional[int] = None,
    end: Optional[int] = None,
) -> List[SeasonSchema]:
    """Return seasons optionally filtered by range."""
    q = db.query(Season)
    if start is not None:
        q = q.filter(Season.year >= start)
    if end is not None:
        q = q.filter(Season.year <= end)
    rows = q.order_by(Season.year).all()
    return [SeasonSchema.model_validate(r) for r in rows]


# ─── Overview ──────────────────────────────────────────────────────

def get_overview(
    db: Session,
    season: Optional[int] = None,
    start_season: Optional[int] = None,
    end_season: Optional[int] = None,
) -> OverviewResponse:
    """Compute dashboard overview statistics from the database."""
    # Base query for races
    race_q = db.query(Race.raceId)
    if season is not None:
        race_q = race_q.filter(Race.year == season)
    else:
        race_q = _season_range_filter(race_q, start_season, end_season)
    race_ids = [r[0] for r in race_q.all()]

    if not race_ids:
        return OverviewResponse()

    # Total distinct races
    total_races = len(race_ids)

    # Total distinct drivers in those races
    total_drivers = (
        db.query(func.count(distinct(Result.driverId)))
        .filter(Result.raceId.in_(race_ids))
        .scalar() or 0
    )

    # Total distinct constructors
    total_constructors = (
        db.query(func.count(distinct(Result.constructorId)))
        .filter(Result.raceId.in_(race_ids))
        .scalar() or 0
    )

    # Total distinct circuits
    total_circuits = (
        db.query(func.count(distinct(Race.circuitId)))
        .filter(Race.raceId.in_(race_ids))
        .scalar() or 0
    )

    # Total podiums (position 1, 2, or 3)
    total_podiums = (
        db.query(func.count(Result.resultId))
        .filter(Result.raceId.in_(race_ids))
        .filter(Result.position.in_([1, 2, 3]))
        .scalar() or 0
    )

    # Classified finishes
    classified = (
        db.query(func.count(Result.resultId))
        .join(Status, Result.statusId == Status.statusId)
        .filter(Result.raceId.in_(race_ids))
        .filter(_classified_status_filter())
        .scalar() or 0
    )

    # Unclassified finishes (DNFs)
    total_results = (
        db.query(func.count(Result.resultId))
        .filter(Result.raceId.in_(race_ids))
        .scalar() or 0
    )
    unclassified = total_results - classified

    # Season range label
    if season is not None:
        season_range = str(season)
    else:
        years = (
            db.query(func.min(Race.year), func.max(Race.year))
            .filter(Race.raceId.in_(race_ids))
            .one()
        )
        season_range = f"{years[0]}-{years[1]}" if years[0] else None

    return OverviewResponse(
        total_races=total_races,
        total_drivers=total_drivers,
        total_constructors=total_constructors,
        total_circuits=total_circuits,
        total_podiums=total_podiums,
        classified_finishes=classified,
        unclassified_finishes=unclassified,
        season_range=season_range,
    )


# ─── Drivers ──────────────────────────────────────────────────────

def get_drivers(
    db: Session,
    season: Optional[int] = None,
    constructor_id: Optional[int] = None,
    search: Optional[str] = None,
) -> List[DriverSchema]:
    """Return drivers with optional filters."""
    q = db.query(Driver)

    if season is not None or constructor_id is not None:
        q = q.join(Result, Driver.driverId == Result.driverId)
        if season is not None:
            q = q.join(Race, Result.raceId == Race.raceId).filter(Race.year == season)
        if constructor_id is not None:
            q = q.filter(Result.constructorId == constructor_id)
        q = q.distinct()

    if search:
        term = f"%{search}%"
        q = q.filter(
            or_(
                Driver.forename.ilike(term),
                Driver.surname.ilike(term),
                Driver.code.ilike(term),
                Driver.driverRef.ilike(term),
            )
        )

    rows = q.order_by(Driver.surname, Driver.forename).all()
    return [DriverSchema.model_validate(r) for r in rows]


def get_driver_detail(
    db: Session,
    driver_id: int,
    season: Optional[int] = None,
) -> Optional[DriverStatsResponse]:
    """Return detailed stats for a single driver."""
    driver = db.query(Driver).filter(Driver.driverId == driver_id).first()
    if not driver:
        return None

    # Build results query
    results_q = (
        db.query(Result, Race, Status)
        .join(Race, Result.raceId == Race.raceId)
        .join(Status, Result.statusId == Status.statusId)
        .filter(Result.driverId == driver_id)
    )
    if season is not None:
        results_q = results_q.filter(Race.year == season)

    rows = results_q.all()
    if not rows:
        return DriverStatsResponse(driver=DriverSchema.model_validate(driver))

    # Use Pandas for aggregation
    data = []
    for result, race, status in rows:
        data.append({
            "year": race.year,
            "position": result.position,
            "positionOrder": result.positionOrder,
            "points": result.points or 0,
            "grid": result.grid,
            "status": status.status,
            "rank": result.rank,
            "constructorId": result.constructorId,
        })
    df = pd.DataFrame(data)

    race_starts = len(df)
    total_points = float(df["points"].sum())
    wins = int((df["position"] == 1).sum())
    podiums = int(df["position"].isin([1, 2, 3]).sum())
    poles = int((df["grid"] == 1).sum())
    fastest_laps = int((df["rank"] == 1).sum())
    classified = int(df["status"].apply(_is_classified).sum())
    dnf_count = race_starts - classified
    finish_rate = round(classified / race_starts * 100, 2) if race_starts > 0 else 0.0

    # Average finish position (only classified)
    classified_positions = df.loc[
        df["status"].apply(_is_classified) & df["positionOrder"].notna(),
        "positionOrder",
    ]
    avg_finish = round(float(classified_positions.mean()), 2) if len(classified_positions) > 0 else None

    # Per-season breakdown
    season_groups = df.groupby("year")
    seasons_list: List[SeasonSummary] = []
    for yr, grp in season_groups:
        # Get final standing position for that season
        last_race = (
            db.query(DriverStanding.position)
            .join(Race, DriverStanding.raceId == Race.raceId)
            .filter(DriverStanding.driverId == driver_id, Race.year == yr)
            .order_by(desc(Race.round))
            .first()
        )
        seasons_list.append(SeasonSummary(
            season=int(yr),
            points=float(grp["points"].sum()),
            wins=int((grp["position"] == 1).sum()),
            podiums=int(grp["position"].isin([1, 2, 3]).sum()),
            races=len(grp),
            position=last_race[0] if last_race else None,
        ))
    seasons_list.sort(key=lambda s: s.season)

    # Constructors the driver raced for
    constructor_ids = df["constructorId"].unique().tolist()
    constructors = (
        db.query(Constructor)
        .filter(Constructor.constructorId.in_(constructor_ids))
        .all()
    )

    return DriverStatsResponse(
        driver=DriverSchema.model_validate(driver),
        season_points=total_points,
        wins=wins,
        podiums=podiums,
        poles=poles,
        fastest_laps=fastest_laps,
        race_starts=race_starts,
        finish_rate=finish_rate,
        dnf_count=dnf_count,
        avg_finish_position=avg_finish,
        seasons=seasons_list,
        constructors=[ConstructorSchema.model_validate(c) for c in constructors],
    )


def get_driver_comparison(
    db: Session,
    driver_ids: List[int],
    start_season: Optional[int] = None,
    end_season: Optional[int] = None,
) -> DriverComparisonResponse:
    """Compare multiple drivers across a season range."""
    effective_start = start_season or 2010
    effective_end = end_season or 2026

    items: List[DriverComparisonItem] = []
    for did in driver_ids:
        driver = db.query(Driver).filter(Driver.driverId == did).first()
        if not driver:
            continue

        results_q = (
            db.query(Result, Race, Status)
            .join(Race, Result.raceId == Race.raceId)
            .join(Status, Result.statusId == Status.statusId)
            .filter(Result.driverId == did)
            .filter(Race.year >= effective_start, Race.year <= effective_end)
        )
        rows = results_q.all()
        if not rows:
            items.append(DriverComparisonItem(
                driver=DriverSchema.model_validate(driver),
            ))
            continue

        data = []
        for result, race, status in rows:
            data.append({
                "year": race.year,
                "position": result.position,
                "positionOrder": result.positionOrder,
                "points": result.points or 0,
                "grid": result.grid,
                "status": status.status,
                "rank": result.rank,
            })
        df = pd.DataFrame(data)

        race_starts = len(df)
        classified = int(df["status"].apply(_is_classified).sum())
        dnf_count = race_starts - classified
        finish_rate = round(classified / race_starts * 100, 2) if race_starts > 0 else 0.0
        classified_positions = df.loc[
            df["status"].apply(_is_classified) & df["positionOrder"].notna(),
            "positionOrder",
        ]
        avg_finish = round(float(classified_positions.mean()), 2) if len(classified_positions) > 0 else None

        # Per-season data
        season_data: List[SeasonSummary] = []
        for yr, grp in df.groupby("year"):
            last_race = (
                db.query(DriverStanding.position)
                .join(Race, DriverStanding.raceId == Race.raceId)
                .filter(DriverStanding.driverId == did, Race.year == yr)
                .order_by(desc(Race.round))
                .first()
            )
            season_data.append(SeasonSummary(
                season=int(yr),
                points=float(grp["points"].sum()),
                wins=int((grp["position"] == 1).sum()),
                podiums=int(grp["position"].isin([1, 2, 3]).sum()),
                races=len(grp),
                position=last_race[0] if last_race else None,
            ))
        season_data.sort(key=lambda s: s.season)

        items.append(DriverComparisonItem(
            driver=DriverSchema.model_validate(driver),
            total_points=float(df["points"].sum()),
            wins=int((df["position"] == 1).sum()),
            podiums=int(df["position"].isin([1, 2, 3]).sum()),
            poles=int((df["grid"] == 1).sum()),
            fastest_laps=int((df["rank"] == 1).sum()),
            race_starts=race_starts,
            finish_rate=finish_rate,
            dnf_count=dnf_count,
            avg_finish_position=avg_finish,
            season_data=season_data,
        ))

    return DriverComparisonResponse(
        drivers=items,
        start_season=effective_start,
        end_season=effective_end,
    )


# ─── Constructors ─────────────────────────────────────────────────

def get_constructors(
    db: Session,
    season: Optional[int] = None,
    search: Optional[str] = None,
) -> List[ConstructorSchema]:
    """Return constructors with optional filters."""
    q = db.query(Constructor)

    if season is not None:
        q = (
            q.join(Result, Constructor.constructorId == Result.constructorId)
            .join(Race, Result.raceId == Race.raceId)
            .filter(Race.year == season)
            .distinct()
        )

    if search:
        term = f"%{search}%"
        q = q.filter(
            or_(
                Constructor.name.ilike(term),
                Constructor.constructorRef.ilike(term),
                Constructor.nationality.ilike(term),
            )
        )

    rows = q.order_by(Constructor.name).all()
    return [ConstructorSchema.model_validate(r) for r in rows]


def get_constructor_detail(
    db: Session,
    constructor_id: int,
    season: Optional[int] = None,
) -> Optional[ConstructorStatsResponse]:
    """Return detailed stats for a single constructor."""
    constructor = db.query(Constructor).filter(Constructor.constructorId == constructor_id).first()
    if not constructor:
        return None

    results_q = (
        db.query(Result, Race, Status)
        .join(Race, Result.raceId == Race.raceId)
        .join(Status, Result.statusId == Status.statusId)
        .filter(Result.constructorId == constructor_id)
    )
    if season is not None:
        results_q = results_q.filter(Race.year == season)

    rows = results_q.all()
    if not rows:
        return ConstructorStatsResponse(
            constructor=ConstructorSchema.model_validate(constructor)
        )

    data = []
    for result, race, status in rows:
        data.append({
            "year": race.year,
            "position": result.position,
            "positionOrder": result.positionOrder,
            "points": result.points or 0,
            "grid": result.grid,
            "status": status.status,
            "driverId": result.driverId,
        })
    df = pd.DataFrame(data)

    race_entries = len(df)
    total_points = float(df["points"].sum())
    wins = int((df["position"] == 1).sum())
    podiums = int(df["position"].isin([1, 2, 3]).sum())
    poles = int((df["grid"] == 1).sum())
    classified = int(df["status"].apply(_is_classified).sum())
    dnf_count = race_entries - classified
    finish_rate = round(classified / race_entries * 100, 2) if race_entries > 0 else 0.0

    # Count constructor championships (position == 1 in final standing)
    championships = 0
    for yr in df["year"].unique():
        last_race = (
            db.query(ConstructorStanding)
            .join(Race, ConstructorStanding.raceId == Race.raceId)
            .filter(
                ConstructorStanding.constructorId == constructor_id,
                Race.year == yr,
            )
            .order_by(desc(Race.round))
            .first()
        )
        if last_race and last_race.position == 1:
            championships += 1

    # Per-season breakdown
    seasons_list: List[SeasonSummary] = []
    for yr, grp in df.groupby("year"):
        last_standing = (
            db.query(ConstructorStanding.position)
            .join(Race, ConstructorStanding.raceId == Race.raceId)
            .filter(ConstructorStanding.constructorId == constructor_id, Race.year == yr)
            .order_by(desc(Race.round))
            .first()
        )
        seasons_list.append(SeasonSummary(
            season=int(yr),
            points=float(grp["points"].sum()),
            wins=int((grp["position"] == 1).sum()),
            podiums=int(grp["position"].isin([1, 2, 3]).sum()),
            races=int(grp["year"].count()),
            position=last_standing[0] if last_standing else None,
        ))
    seasons_list.sort(key=lambda s: s.season)

    # Drivers who raced for this constructor
    driver_ids = df["driverId"].unique().tolist()
    drivers = db.query(Driver).filter(Driver.driverId.in_(driver_ids)).all()

    return ConstructorStatsResponse(
        constructor=ConstructorSchema.model_validate(constructor),
        total_points=total_points,
        wins=wins,
        podiums=podiums,
        poles=poles,
        race_entries=race_entries,
        finish_rate=finish_rate,
        dnf_count=dnf_count,
        championships=championships,
        seasons=seasons_list,
        drivers=[DriverSchema.model_validate(d) for d in drivers],
    )


def get_constructor_comparison(
    db: Session,
    constructor_ids: List[int],
    start_season: Optional[int] = None,
    end_season: Optional[int] = None,
) -> ConstructorComparisonResponse:
    """Compare multiple constructors across a season range."""
    effective_start = start_season or 2010
    effective_end = end_season or 2026

    items: List[ConstructorComparisonItem] = []
    for cid in constructor_ids:
        constructor = db.query(Constructor).filter(Constructor.constructorId == cid).first()
        if not constructor:
            continue

        results_q = (
            db.query(Result, Race, Status)
            .join(Race, Result.raceId == Race.raceId)
            .join(Status, Result.statusId == Status.statusId)
            .filter(Result.constructorId == cid)
            .filter(Race.year >= effective_start, Race.year <= effective_end)
        )
        rows = results_q.all()
        if not rows:
            items.append(ConstructorComparisonItem(
                constructor=ConstructorSchema.model_validate(constructor),
            ))
            continue

        data = []
        for result, race, status in rows:
            data.append({
                "year": race.year,
                "position": result.position,
                "points": result.points or 0,
                "status": status.status,
            })
        df = pd.DataFrame(data)

        race_entries = len(df)
        classified = int(df["status"].apply(_is_classified).sum())
        dnf_count = race_entries - classified
        finish_rate = round(classified / race_entries * 100, 2) if race_entries > 0 else 0.0

        season_data: List[SeasonSummary] = []
        for yr, grp in df.groupby("year"):
            last_standing = (
                db.query(ConstructorStanding.position)
                .join(Race, ConstructorStanding.raceId == Race.raceId)
                .filter(ConstructorStanding.constructorId == cid, Race.year == yr)
                .order_by(desc(Race.round))
                .first()
            )
            season_data.append(SeasonSummary(
                season=int(yr),
                points=float(grp["points"].sum()),
                wins=int((grp["position"] == 1).sum()),
                podiums=int(grp["position"].isin([1, 2, 3]).sum()),
                races=len(grp),
                position=last_standing[0] if last_standing else None,
            ))
        season_data.sort(key=lambda s: s.season)

        items.append(ConstructorComparisonItem(
            constructor=ConstructorSchema.model_validate(constructor),
            total_points=float(df["points"].sum()),
            wins=int((df["position"] == 1).sum()),
            podiums=int(df["position"].isin([1, 2, 3]).sum()),
            race_entries=race_entries,
            finish_rate=finish_rate,
            dnf_count=dnf_count,
            season_data=season_data,
        ))

    return ConstructorComparisonResponse(
        constructors=items,
        start_season=effective_start,
        end_season=effective_end,
    )


# ─── Races & Circuits ─────────────────────────────────────────────

def get_races(
    db: Session,
    season: Optional[int] = None,
    circuit_id: Optional[int] = None,
) -> List[RaceSchema]:
    """Return races with optional filters."""
    q = db.query(Race).options(joinedload(Race.circuit))
    if season is not None:
        q = q.filter(Race.year == season)
    if circuit_id is not None:
        q = q.filter(Race.circuitId == circuit_id)
    rows = q.order_by(Race.year.desc(), Race.round).all()
    return [RaceSchema.model_validate(r) for r in rows]


def get_circuits(
    db: Session,
    country: Optional[str] = None,
    search: Optional[str] = None,
) -> List[CircuitSchema]:
    """Return circuits with optional filters."""
    q = db.query(Circuit)
    if country:
        q = q.filter(Circuit.country.ilike(f"%{country}%"))
    if search:
        term = f"%{search}%"
        q = q.filter(
            or_(
                Circuit.name.ilike(term),
                Circuit.location.ilike(term),
                Circuit.country.ilike(term),
                Circuit.circuitRef.ilike(term),
            )
        )
    rows = q.order_by(Circuit.name).all()
    return [CircuitSchema.model_validate(r) for r in rows]


def get_circuit_detail(
    db: Session,
    circuit_id: int,
) -> Optional[Dict[str, Any]]:
    """Return circuit info with race history."""
    circuit = db.query(Circuit).filter(Circuit.circuitId == circuit_id).first()
    if not circuit:
        return None

    races = (
        db.query(Race)
        .filter(Race.circuitId == circuit_id)
        .order_by(Race.year.desc())
        .all()
    )

    return {
        "circuit": CircuitSchema.model_validate(circuit),
        "total_races": len(races),
        "races": [RaceSchema.model_validate(r) for r in races],
    }


# ─── Championship Trends ──────────────────────────────────────────

def get_championship_trends(
    db: Session,
    start_season: Optional[int] = None,
    end_season: Optional[int] = None,
    constructor_ids: Optional[List[int]] = None,
) -> List[ChampionshipTrendItem]:
    """Compute constructor championship trends over a season range.

    For each season, get the final constructor standings (last race of the season).
    """
    effective_start = start_season or 2010
    effective_end = end_season or 2026

    # Subquery: last race per season in the range
    last_race_sq = (
        db.query(
            Race.year,
            func.max(Race.round).label("max_round"),
        )
        .filter(Race.year >= effective_start, Race.year <= effective_end)
        .group_by(Race.year)
        .subquery()
    )

    # Get the raceId for each season's last race
    last_race_ids = (
        db.query(Race.raceId, Race.year)
        .join(
            last_race_sq,
            and_(Race.year == last_race_sq.c.year, Race.round == last_race_sq.c.max_round),
        )
        .all()
    )

    if not last_race_ids:
        return []

    race_id_to_year = {r.raceId: r.year for r in last_race_ids}
    race_ids = list(race_id_to_year.keys())

    # Get constructor standings for those races
    q = (
        db.query(ConstructorStanding, Constructor)
        .join(Constructor, ConstructorStanding.constructorId == Constructor.constructorId)
        .filter(ConstructorStanding.raceId.in_(race_ids))
    )
    if constructor_ids:
        q = q.filter(ConstructorStanding.constructorId.in_(constructor_ids))

    rows = q.all()

    results: List[ChampionshipTrendItem] = []
    for standing, constructor in rows:
        year = race_id_to_year.get(standing.raceId)
        if year is None:
            continue
        results.append(ChampionshipTrendItem(
            season=year,
            constructor=constructor.name,
            constructor_id=constructor.constructorId,
            points=float(standing.points or 0),
            position=standing.position,
            wins=standing.wins or 0,
        ))

    results.sort(key=lambda x: (x.season, x.position or 999))
    return results


# ─── Reliability ───────────────────────────────────────────────────

def get_reliability(
    db: Session,
    season: Optional[int] = None,
    driver_id: Optional[int] = None,
    constructor_id: Optional[int] = None,
    circuit_id: Optional[int] = None,
) -> ReliabilityResponse:
    """Compute reliability stats (finish rates, DNF breakdown)."""
    # Determine grouping
    if driver_id:
        entity_type = "driver"
    elif constructor_id:
        entity_type = "constructor"
    elif circuit_id:
        entity_type = "circuit"
    else:
        entity_type = "driver"

    # Build base query
    q = (
        db.query(Result, Status, Race)
        .join(Status, Result.statusId == Status.statusId)
        .join(Race, Result.raceId == Race.raceId)
    )
    if season is not None:
        q = q.filter(Race.year == season)
    if driver_id is not None:
        q = q.filter(Result.driverId == driver_id)
    if constructor_id is not None:
        q = q.filter(Result.constructorId == constructor_id)
    if circuit_id is not None:
        q = q.filter(Race.circuitId == circuit_id)

    rows = q.all()
    if not rows:
        return ReliabilityResponse(
            data=[],
            season=season,
            filters={
                "driver_id": driver_id,
                "constructor_id": constructor_id,
                "circuit_id": circuit_id,
            },
        )

    # Build dataframe
    data = []
    for result, status, race in rows:
        is_classified = _is_classified(status.status)
        # Classify DNF reasons
        dnf_type = None
        if not is_classified:
            status_lower = status.status.lower()
            if any(k in status_lower for k in [
                "engine", "gearbox", "hydraulic", "electrical", "power unit",
                "turbo", "transmission", "oil", "fuel", "water", "exhaust",
                "radiator", "suspension", "brake", "clutch", "drivetrain",
                "overheating", "mechanical",
            ]):
                dnf_type = "mechanical"
            elif any(k in status_lower for k in [
                "accident", "collision", "spun off", "crash",
            ]):
                dnf_type = "accident"
            else:
                dnf_type = "other"

        if entity_type == "driver":
            eid = result.driverId
        elif entity_type == "constructor":
            eid = result.constructorId
        else:
            eid = race.circuitId

        data.append({
            "entity_id": eid,
            "classified": is_classified,
            "dnf_type": dnf_type,
            "status": status.status,
        })

    df = pd.DataFrame(data)

    items: List[ReliabilityItem] = []
    for eid, grp in df.groupby("entity_id"):
        total = len(grp)
        classified_count = int(grp["classified"].sum())
        dnf = total - classified_count
        finish_rate = round(classified_count / total * 100, 2) if total > 0 else 0.0

        dnf_df = grp[~grp["classified"]]
        mechanical = int((dnf_df["dnf_type"] == "mechanical").sum())
        accident = int((dnf_df["dnf_type"] == "accident").sum())
        other = int((dnf_df["dnf_type"] == "other").sum())

        # DNF reasons breakdown
        dnf_reasons = []
        if len(dnf_df) > 0:
            for status_text, count in dnf_df["status"].value_counts().items():
                dnf_reasons.append({"status": status_text, "count": int(count)})

        # Get entity name
        if entity_type == "driver":
            entity = db.query(Driver).filter(Driver.driverId == eid).first()
            name = f"{entity.forename} {entity.surname}" if entity else str(eid)
        elif entity_type == "constructor":
            entity = db.query(Constructor).filter(Constructor.constructorId == eid).first()
            name = entity.name if entity else str(eid)
        else:
            entity = db.query(Circuit).filter(Circuit.circuitId == eid).first()
            name = entity.name if entity else str(eid)

        items.append(ReliabilityItem(
            entity_id=int(eid),
            entity_name=name,
            entity_type=entity_type,
            total_entries=total,
            classified_finishes=classified_count,
            dnf_count=dnf,
            finish_rate=finish_rate,
            mechanical_dnf=mechanical,
            accident_dnf=accident,
            other_dnf=other,
            dnf_reasons=dnf_reasons,
        ))

    items.sort(key=lambda x: x.finish_rate, reverse=True)

    return ReliabilityResponse(
        data=items,
        season=season,
        filters={
            "driver_id": driver_id,
            "constructor_id": constructor_id,
            "circuit_id": circuit_id,
        },
    )


# ─── Podiums ──────────────────────────────────────────────────────

def get_podiums(
    db: Session,
    driver_id: Optional[int] = None,
    constructor_id: Optional[int] = None,
    nationality: Optional[str] = None,
    season: Optional[int] = None,
) -> PodiumResponse:
    """Compute podium statistics."""
    q = (
        db.query(Result, Driver, Constructor, Race)
        .join(Driver, Result.driverId == Driver.driverId)
        .join(Constructor, Result.constructorId == Constructor.constructorId)
        .join(Race, Result.raceId == Race.raceId)
        .filter(Result.position.in_([1, 2, 3]))
    )
    if driver_id is not None:
        q = q.filter(Result.driverId == driver_id)
    if constructor_id is not None:
        q = q.filter(Result.constructorId == constructor_id)
    if nationality is not None:
        q = q.filter(Driver.nationality.ilike(f"%{nationality}%"))
    if season is not None:
        q = q.filter(Race.year == season)

    rows = q.all()

    if not rows:
        return PodiumResponse(
            data=[], total=0,
            filters={
                "driver_id": driver_id,
                "constructor_id": constructor_id,
                "nationality": nationality,
                "season": season,
            },
        )

    data = []
    for result, driver_obj, constructor_obj, race in rows:
        data.append({
            "driver_id": driver_obj.driverId,
            "driver_name": f"{driver_obj.forename} {driver_obj.surname}",
            "constructor_name": constructor_obj.name,
            "nationality": driver_obj.nationality,
            "position": result.position,
        })
    df = pd.DataFrame(data)

    # Also compute race starts for podium rate
    start_counts: Dict[int, int] = {}
    for did in df["driver_id"].unique():
        start_q = db.query(func.count(Result.resultId)).filter(Result.driverId == did)
        if season is not None:
            start_q = start_q.join(Race, Result.raceId == Race.raceId).filter(Race.year == season)
        start_counts[int(did)] = start_q.scalar() or 0

    items: List[PodiumItem] = []
    for (did, dname, cname, nat), grp in df.groupby(
        ["driver_id", "driver_name", "constructor_name", "nationality"]
    ):
        wins = int((grp["position"] == 1).sum())
        seconds = int((grp["position"] == 2).sum())
        thirds = int((grp["position"] == 3).sum())
        total_podiums = wins + seconds + thirds
        race_starts = start_counts.get(int(did), 0)
        podium_rate = round(total_podiums / race_starts * 100, 2) if race_starts > 0 else None

        items.append(PodiumItem(
            driver_id=int(did),
            driver_name=dname,
            constructor_name=cname,
            nationality=nat,
            wins=wins,
            seconds=seconds,
            thirds=thirds,
            total_podiums=total_podiums,
            podium_rate=podium_rate,
            race_starts=race_starts,
        ))

    items.sort(key=lambda x: x.total_podiums, reverse=True)

    return PodiumResponse(
        data=items,
        total=len(items),
        filters={
            "driver_id": driver_id,
            "constructor_id": constructor_id,
            "nationality": nationality,
            "season": season,
        },
    )


# ─── Data Quality ─────────────────────────────────────────────────

def get_data_quality(db: Session) -> DataQualityResponse:
    """Assess data quality across all tables."""
    insp = inspect(db.bind)
    table_names = insp.get_table_names()

    tables: List[DataQualityItem] = []
    total_records = 0

    model_map = {
        "seasons": Season,
        "circuits": Circuit,
        "constructors": Constructor,
        "drivers": Driver,
        "races": Race,
        "results": Result,
        "status": Status,
        "driverStandings": DriverStanding,
        "constructorStandings": ConstructorStanding,
        "qualifying": Qualifying,
        "pitStops": PitStop,
        "lapTimes": LapTime,
    }

    for tbl_name in table_names:
        model = model_map.get(tbl_name)
        if model is None:
            continue

        total_rows = db.query(func.count()).select_from(model).scalar() or 0
        total_records += total_rows

        if total_rows == 0:
            tables.append(DataQualityItem(
                table_name=tbl_name,
                total_rows=0,
                null_counts={},
                completeness=100.0,
            ))
            continue

        # Check null counts for each column
        columns = insp.get_columns(tbl_name)
        null_counts = {}
        total_cells = 0
        non_null_cells = 0

        for col_info in columns:
            col_name = col_info["name"]
            col_attr = getattr(model, col_name, None)
            if col_attr is None:
                continue
            null_count = (
                db.query(func.count())
                .select_from(model)
                .filter(col_attr.is_(None))
                .scalar() or 0
            )
            if null_count > 0:
                null_counts[col_name] = null_count
            total_cells += total_rows
            non_null_cells += (total_rows - null_count)

        completeness = round(non_null_cells / total_cells * 100, 2) if total_cells > 0 else 100.0

        # Date range for time-based tables
        date_range = None
        if hasattr(model, "year"):
            min_max = db.query(
                func.min(model.year), func.max(model.year)
            ).one()
            if min_max[0] is not None:
                date_range = f"{min_max[0]}-{min_max[1]}"
        elif hasattr(model, "date"):
            min_max = db.query(
                func.min(model.date), func.max(model.date)
            ).one()
            if min_max[0] is not None:
                date_range = f"{min_max[0]} to {min_max[1]}"

        tables.append(DataQualityItem(
            table_name=tbl_name,
            total_rows=total_rows,
            null_counts=null_counts,
            completeness=completeness,
            date_range=date_range,
        ))

    overall = (
        sum(t.completeness * t.total_rows for t in tables) /
        max(sum(t.total_rows for t in tables), 1)
    )

    # Database file size
    db_size = None
    db_url = str(db.bind.url)
    if db_url.startswith("sqlite"):
        db_path = db_url.replace("sqlite:///", "")
        if os.path.exists(db_path):
            db_size = round(os.path.getsize(db_path) / (1024 * 1024), 2)

    return DataQualityResponse(
        tables=tables,
        overall_completeness=round(overall, 2),
        total_records=total_records,
        database_size_mb=db_size,
    )


# ─── Data Explorer ─────────────────────────────────────────────────

_EXPLORER_MODELS = {
    "seasons": Season,
    "circuits": Circuit,
    "constructors": Constructor,
    "drivers": Driver,
    "races": Race,
    "results": Result,
    "status": Status,
    "driverStandings": DriverStanding,
    "constructorStandings": ConstructorStanding,
    "qualifying": Qualifying,
    "pitStops": PitStop,
    "lapTimes": LapTime,
}


def get_data_explorer(
    db: Session,
    dataset: str,
    page: int = 1,
    per_page: int = 25,
    sort_by: Optional[str] = None,
    order: str = "asc",
    search: Optional[str] = None,
) -> PaginatedResponse:
    """Generic paginated data explorer for any dataset table."""
    model = _EXPLORER_MODELS.get(dataset)
    if model is None:
        return PaginatedResponse(data=[], total=0, page=page, per_page=per_page)

    q = db.query(model)

    # Apply search across string columns
    if search:
        insp = inspect(model)
        string_cols = [
            getattr(model, c.key)
            for c in insp.mapper.column_attrs
            if hasattr(c.columns[0].type, "length") or str(c.columns[0].type) == "VARCHAR"
            or str(c.columns[0].type).startswith("VARCHAR")
            or isinstance(c.columns[0].type, (type(String()),))
        ]
        # Fallback: search all string-type columns
        from sqlalchemy import String as SAString
        string_cols = []
        for c in insp.mapper.column_attrs:
            col = c.columns[0]
            if isinstance(col.type, SAString):
                string_cols.append(getattr(model, c.key))
        if string_cols:
            term = f"%{search}%"
            q = q.filter(or_(*[col.ilike(term) for col in string_cols]))

    # Total count before pagination
    total = q.count()

    # Sorting
    if sort_by and hasattr(model, sort_by):
        col = getattr(model, sort_by)
        q = q.order_by(desc(col) if order == "desc" else asc(col))

    # Pagination
    offset = (page - 1) * per_page
    rows = q.offset(offset).limit(per_page).all()

    # Serialize rows to dicts
    insp_model = inspect(model)
    result_data = []
    for row in rows:
        row_dict = {}
        for c in insp_model.mapper.column_attrs:
            val = getattr(row, c.key)
            if isinstance(val, date):
                val = val.isoformat()
            row_dict[c.key] = val
        result_data.append(row_dict)

    return PaginatedResponse(
        data=result_data,
        total=total,
        page=page,
        per_page=per_page,
    )


def get_export_data(
    db: Session,
    dataset: str,
    season: Optional[int] = None,
) -> Optional[pd.DataFrame]:
    """Return a DataFrame for CSV export of a given dataset."""
    model = _EXPLORER_MODELS.get(dataset)
    if model is None:
        return None

    q = db.query(model)

    # Apply season filter if the model has a year column or join through Race
    if season is not None:
        if hasattr(model, "year"):
            q = q.filter(model.year == season)
        elif hasattr(model, "raceId"):
            q = q.join(Race, model.raceId == Race.raceId).filter(Race.year == season)

    rows = q.all()

    if not rows:
        return pd.DataFrame()

    insp_model = inspect(model)
    data = []
    for row in rows:
        row_dict = {}
        for c in insp_model.mapper.column_attrs:
            val = getattr(row, c.key)
            row_dict[c.key] = val
        data.append(row_dict)

    return pd.DataFrame(data)
