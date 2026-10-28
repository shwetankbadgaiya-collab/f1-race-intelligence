"""FastAPI route definitions for F1 Race Intelligence Dashboard.

Covers all required REST endpoints matching both the project specification
and frontend API client services.
"""

import csv
import io
import re
from typing import Any, Dict, List, Optional
from datetime import date

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import Response, StreamingResponse
from sqlalchemy import func, desc, asc, distinct, or_, and_, case
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Season, Circuit, Constructor, Driver, Race, Result, Status,
    DriverStanding, ConstructorStanding, Qualifying,
)
from app.schemas import (
    SeasonSchema, CircuitSchema, DriverSchema, ConstructorSchema,
    RaceSchema, ResultSchema, OverviewResponse, ChampionshipTrendItem,
    DriverStatsResponse, DriverComparisonResponse, ConstructorStatsResponse,
    ConstructorComparisonResponse, ReliabilityResponse, PodiumResponse,
    TyreAnalysisResponse, DataQualityResponse, InsightItem, PaginatedResponse,
)
from app.services import data_service
from app.analytics.insights import generate_insights

router = APIRouter(prefix="/api", tags=["F1 Analytics"])


# ─── System / Health ─────────────────────────────────────────────────────────

@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "f1-race-intelligence-api", "version": "1.0.0"}


# ─── Seasons ─────────────────────────────────────────────────────────────────

@router.get("/seasons", response_model=List[SeasonSchema])
def list_seasons(
    start: Optional[int] = Query(None, description="Start year filter"),
    end: Optional[int] = Query(None, description="End year filter"),
    db: Session = Depends(get_db),
):
    """List available F1 seasons (2010-2026)."""
    return data_service.get_seasons(db, start=start, end=end)


# ─── Overview ────────────────────────────────────────────────────────────────

@router.get("/overview")
def get_dashboard_overview(
    season: Optional[int] = Query(None, description="Specific season"),
    season_from: Optional[int] = Query(None, description="Start season"),
    season_to: Optional[int] = Query(None, description="End season"),
    start_season: Optional[int] = Query(None, description="Alias for start season"),
    end_season: Optional[int] = Query(None, description="Alias for end season"),
    db: Session = Depends(get_db),
):
    """Get high-level KPI card metrics and summary statistics."""
    start = season_from if season_from is not None else start_season
    end = season_to if season_to is not None else end_season
    overview = data_service.get_overview(db, season=season, start_season=start, end_season=end)
    return overview.model_dump()


# ─── Championship Trends ─────────────────────────────────────────────────────

@router.get("/championship-trends", response_model=List[ChampionshipTrendItem])
@router.get("/championship/trends", response_model=List[ChampionshipTrendItem])
def get_championship_trends(
    season: Optional[int] = Query(None),
    season_from: Optional[int] = Query(None),
    season_to: Optional[int] = Query(None),
    start_season: Optional[int] = Query(None),
    end_season: Optional[int] = Query(None),
    constructor_ids: Optional[str] = Query(None, description="Comma-separated constructor IDs"),
    db: Session = Depends(get_db),
):
    """Championship points progression over time for constructors."""
    start = season if season is not None else (season_from if season_from is not None else start_season)
    end = season if season is not None else (season_to if season_to is not None else end_season)

    cid_list = None
    if constructor_ids:
        try:
            cid_list = [int(x.strip()) for x in constructor_ids.split(",") if x.strip()]
        except ValueError:
            pass

    return data_service.get_championship_trends(db, start_season=start, end_season=end, constructor_ids=cid_list)


# ─── Drivers ─────────────────────────────────────────────────────────────────

@router.get("/drivers")
def list_drivers(
    season: Optional[int] = Query(None),
    constructor_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """List drivers with optional filtering."""
    drivers = data_service.get_drivers(db, season=season, constructor_id=constructor_id, search=search)
    return [d.model_dump() for d in drivers]


@router.get("/drivers/leaderboard")
def get_driver_leaderboard(
    season: Optional[int] = Query(None),
    season_from: Optional[int] = Query(None),
    season_to: Optional[int] = Query(None),
    limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Rank drivers by championship points and podiums."""
    start = season if season is not None else season_from
    end = season if season is not None else season_to

    q = (
        db.query(
            Driver.driverId,
            Driver.driverRef,
            Driver.code,
            Driver.forename,
            Driver.surname,
            Driver.nationality,
            Constructor.name.label("constructor_name"),
            Constructor.constructorRef.label("constructor_ref"),
            func.sum(Result.points).label("points"),
            func.sum(case((Result.position == 1, 1), else_=0)).label("wins"),
            func.sum(case((Result.position <= 3, 1), else_=0)).label("podiums"),
            func.count(Result.resultId).label("race_starts"),
            func.sum(case((Result.grid == 1, 1), else_=0)).label("poles"),
            func.avg(Result.position).label("avg_finish"),
        )
        .join(Result, Driver.driverId == Result.driverId)
        .join(Race, Result.raceId == Race.raceId)
        .join(Constructor, Result.constructorId == Constructor.constructorId)
    )

    if start is not None:
        q = q.filter(Race.year >= start)
    if end is not None:
        q = q.filter(Race.year <= end)

    rows = (
        q.group_by(Driver.driverId, Constructor.name, Constructor.constructorRef)
        .order_by(desc("points"))
        .limit(limit)
        .all()
    )

    result = []
    for r in rows:
        result.append({
            "driver_id": str(r.driverId),
            "driver_name": f"{r.forename} {r.surname}",
            "code": r.code or r.surname[:3].upper(),
            "nationality": r.nationality,
            "constructor_name": r.constructor_name,
            "constructor_ref": r.constructor_ref,
            "points": float(r.points or 0),
            "wins": int(r.wins or 0),
            "podiums": int(r.podiums or 0),
            "poles": int(r.poles or 0),
            "race_starts": int(r.race_starts or 0),
            "avg_finish_position": round(float(r.avg_finish), 2) if r.avg_finish else None,
        })
    return result


@router.get("/drivers/compare")
def compare_drivers(
    driver_ids: str = Query(..., description="Comma-separated driver IDs"),
    start_season: Optional[int] = Query(None),
    end_season: Optional[int] = Query(None),
    season_from: Optional[int] = Query(None),
    season_to: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """Side-by-side performance comparison of multiple drivers."""
    try:
        dids = [int(x.strip()) for x in driver_ids.split(",") if x.strip()]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid driver_ids format. Must be integers.")

    start = season_from if season_from is not None else start_season
    end = season_to if season_to is not None else end_season

    return data_service.get_driver_comparison(db, driver_ids=dids, start_season=start, end_season=end)


@router.get("/drivers/{driver_id}")
@router.get("/drivers/{driver_id}/stats")
def get_driver_profile(
    driver_id: str,
    season: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """Detailed driver profile, metrics, and season breakdowns."""
    # Lookup by id or driverRef
    did: Optional[int] = None
    if driver_id.isdigit():
        did = int(driver_id)
    else:
        d = db.query(Driver.driverId).filter(Driver.driverRef == driver_id.lower()).first()
        if d:
            did = d[0]

    if not did:
        raise HTTPException(status_code=404, detail=f"Driver '{driver_id}' not found")

    stats = data_service.get_driver_detail(db, driver_id=did, season=season)
    if not stats:
        raise HTTPException(status_code=404, detail="Driver not found")
    return stats.model_dump()


@router.get("/drivers/{driver_id}/finishing-positions")
def get_driver_finishing_positions(
    driver_id: str,
    season: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """Distribution of finishing positions (P1, P2, P3... DNF) for a driver."""
    did = int(driver_id) if driver_id.isdigit() else None
    if not did:
        d = db.query(Driver.driverId).filter(Driver.driverRef == driver_id.lower()).first()
        if d:
            did = d[0]
    if not did:
        raise HTTPException(status_code=404, detail="Driver not found")

    q = (
        db.query(Result.position, func.count(Result.resultId).label("count"))
        .join(Race, Result.raceId == Race.raceId)
        .filter(Result.driverId == did)
    )
    if season:
        q = q.filter(Race.year == season)

    rows = q.group_by(Result.position).order_by(Result.position).all()
    
    positions = []
    for r in rows:
        positions.append({
            "position": r.position if r.position else "DNF",
            "count": r.count
        })
    return positions


# ─── Constructors ────────────────────────────────────────────────────────────

@router.get("/constructors")
def list_constructors(
    season: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """List constructors with optional season or search filtering."""
    constructors = data_service.get_constructors(db, season=season, search=search)
    return [c.model_dump() for c in constructors]


@router.get("/constructors/leaderboard")
def get_constructor_leaderboard(
    season: Optional[int] = Query(None),
    season_from: Optional[int] = Query(None),
    season_to: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """Constructor leaderboard ranked by points and victories."""
    start = season if season is not None else season_from
    end = season if season is not None else season_to

    q = (
        db.query(
            Constructor.constructorId,
            Constructor.constructorRef,
            Constructor.name,
            Constructor.nationality,
            func.sum(Result.points).label("points"),
            func.sum(case((Result.position == 1, 1), else_=0)).label("wins"),
            func.sum(case((Result.position <= 3, 1), else_=0)).label("podiums"),
            func.count(Result.resultId).label("race_entries"),
            func.sum(case((Result.position.is_(None), 1), (Result.position > 20, 1), else_=0)).label("dnf_count"),
        )
        .join(Result, Constructor.constructorId == Result.constructorId)
        .join(Race, Result.raceId == Race.raceId)
    )

    if start:
        q = q.filter(Race.year >= start)
    if end:
        q = q.filter(Race.year <= end)

    rows = q.group_by(Constructor.constructorId).order_by(desc("points")).all()

    result = []
    for r in rows:
        entries = r.race_entries or 1
        dnf = r.dnf_count or 0
        finish_rate = round(max(0.0, min(100.0, ((entries - dnf) / entries) * 100)), 1)
        result.append({
            "constructor_id": str(r.constructorId),
            "constructor_ref": r.constructorRef,
            "name": r.name,
            "nationality": r.nationality,
            "points": float(r.points or 0),
            "wins": int(r.wins or 0),
            "podiums": int(r.podiums or 0),
            "race_entries": int(entries),
            "finish_rate": finish_rate,
            "dnf_count": int(dnf),
        })
    return result


@router.get("/constructors/heatmap")
def get_constructor_heatmap(
    start_season: Optional[int] = Query(2010),
    end_season: Optional[int] = Query(2024),
    db: Session = Depends(get_db),
):
    """Season-by-season championship finishing position matrix."""
    q = (
        db.query(
            Race.year.label("season"),
            Constructor.name.label("constructor_name"),
            Constructor.constructorRef.label("constructor_ref"),
            ConstructorStanding.position,
            ConstructorStanding.points,
        )
        .join(Race, ConstructorStanding.raceId == Race.raceId)
        .join(Constructor, ConstructorStanding.constructorId == Constructor.constructorId)
        .filter(Race.year >= start_season, Race.year <= end_season)
    )

    # Subquery for maximum round per season to get final standings
    max_rounds = (
        db.query(Race.year, func.max(Race.round).label("max_round"))
        .group_by(Race.year)
        .subquery()
    )
    q = q.join(max_rounds, and_(Race.year == max_rounds.c.year, Race.round == max_rounds.c.max_round))

    rows = q.all()
    return [
        {
            "season": r.season,
            "constructor_name": r.constructor_name,
            "constructor_ref": r.constructor_ref,
            "position": r.position,
            "points": float(r.points or 0),
        }
        for r in rows
    ]


@router.get("/constructors/compare")
def compare_constructors(
    constructor_ids: str = Query(..., description="Comma-separated constructor IDs"),
    start_season: Optional[int] = Query(None),
    end_season: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """Side-by-side performance comparison of multiple constructors."""
    try:
        cids = [int(x.strip()) for x in constructor_ids.split(",") if x.strip()]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid constructor_ids format")

    return data_service.get_constructor_comparison(db, constructor_ids=cids, start_season=start_season, end_season=end_season)


@router.get("/constructors/{constructor_id}")
@router.get("/constructors/{constructor_id}/stats")
def get_constructor_profile(
    constructor_id: str,
    season: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """Detailed constructor profile, points history, and team drivers."""
    cid: Optional[int] = None
    if constructor_id.isdigit():
        cid = int(constructor_id)
    else:
        c = db.query(Constructor.constructorId).filter(Constructor.constructorRef == constructor_id.lower()).first()
        if c:
            cid = c[0]

    if not cid:
        raise HTTPException(status_code=404, detail=f"Constructor '{constructor_id}' not found")

    stats = data_service.get_constructor_detail(db, constructor_id=cid, season=season)
    if not stats:
        raise HTTPException(status_code=404, detail="Constructor not found")
    return stats.model_dump()


# ─── Circuits ────────────────────────────────────────────────────────────────

@router.get("/circuits")
def list_circuits(
    country: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """List circuits with geographical details."""
    circuits = data_service.get_circuits(db, country=country, search=search)
    return [c.model_dump() for c in circuits]


@router.get("/circuits/leaderboard")
def get_circuit_leaderboard(
    db: Session = Depends(get_db),
):
    """Circuits ranked by total Grands Prix hosted and DNF rate."""
    q = (
        db.query(
            Circuit.circuitId,
            Circuit.circuitRef,
            Circuit.name,
            Circuit.location,
            Circuit.country,
            Circuit.lat,
            Circuit.lng,
            func.count(distinct(Race.raceId)).label("races_hosted"),
            func.count(Result.resultId).label("total_entries"),
            func.sum(case((Result.position.is_(None), 1), (Result.position > 20, 1), else_=0)).label("dnfs"),
        )
        .join(Race, Circuit.circuitId == Race.circuitId)
        .outerjoin(Result, Race.raceId == Result.raceId)
        .group_by(Circuit.circuitId)
        .order_by(desc("races_hosted"))
    )

    rows = q.all()
    result = []
    for r in rows:
        total = r.total_entries or 0
        dnf = r.dnfs or 0
        dnf_rate = round((dnf / total * 100), 1) if total > 0 else 0.0
        result.append({
            "circuit_id": str(r.circuitId),
            "circuit_ref": r.circuitRef,
            "name": r.name,
            "location": r.location,
            "country": r.country,
            "lat": r.lat,
            "lng": r.lng,
            "races_hosted": r.races_hosted,
            "total_entries": total,
            "dnfs": dnf,
            "dnf_rate": dnf_rate,
        })
    return result


@router.get("/circuits/{circuit_id}")
@router.get("/circuits/{circuit_id}/stats")
def get_circuit_profile(
    circuit_id: str,
    db: Session = Depends(get_db),
):
    """Circuit details, winners, and host history."""
    cid: Optional[int] = None
    if circuit_id.isdigit():
        cid = int(circuit_id)
    else:
        c = db.query(Circuit.circuitId).filter(Circuit.circuitRef == circuit_id.lower()).first()
        if c:
            cid = c[0]

    if not cid:
        raise HTTPException(status_code=404, detail="Circuit not found")

    detail = data_service.get_circuit_detail(db, circuit_id=cid)
    if not detail:
        raise HTTPException(status_code=404, detail="Circuit not found")
    return detail


# ─── Races & Results ─────────────────────────────────────────────────────────

@router.get("/races", response_model=List[RaceSchema])
def list_races(
    season: Optional[int] = Query(None),
    circuit_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """List race events."""
    return data_service.get_races(db, season=season, circuit_id=circuit_id)


@router.get("/results")
def list_results(
    race_id: Optional[int] = Query(None),
    season: Optional[int] = Query(None),
    driver_id: Optional[int] = Query(None),
    constructor_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Detailed race results with pagination and filtering."""
    q = (
        db.query(
            Result.resultId,
            Race.name.label("race_name"),
            Race.year.label("season"),
            Race.round,
            Driver.forename,
            Driver.surname,
            Driver.code,
            Constructor.name.label("constructor_name"),
            Result.grid,
            Result.position,
            Result.positionText,
            Result.points,
            Result.laps,
            Result.time,
            Status.status.label("status"),
        )
        .join(Race, Result.raceId == Race.raceId)
        .join(Driver, Result.driverId == Driver.driverId)
        .join(Constructor, Result.constructorId == Constructor.constructorId)
        .join(Status, Result.statusId == Status.statusId)
    )

    if race_id:
        q = q.filter(Result.raceId == race_id)
    if season:
        q = q.filter(Race.year == season)
    if driver_id:
        q = q.filter(Result.driverId == driver_id)
    if constructor_id:
        q = q.filter(Result.constructorId == constructor_id)

    total = q.count()
    rows = q.order_by(desc(Race.year), desc(Race.round), Result.positionOrder).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for r in rows:
        items.append({
            "result_id": r.resultId,
            "race_name": r.race_name,
            "season": r.season,
            "round": r.round,
            "driver_name": f"{r.forename} {r.surname}",
            "driver_code": r.code,
            "constructor_name": r.constructor_name,
            "grid": r.grid,
            "position": r.position,
            "position_text": r.positionText,
            "points": float(r.points or 0),
            "laps": r.laps,
            "time": r.time,
            "status": r.status,
        })
    return items


# ─── Reliability & DNF ───────────────────────────────────────────────────────

@router.get("/reliability")
@router.get("/reliability/trends")
def get_reliability_trends(
    season: Optional[int] = Query(None),
    season_from: Optional[int] = Query(None),
    season_to: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """DNF and finish rate trends over seasons."""
    start = season if season is not None else season_from
    end = season if season is not None else season_to

    q = (
        db.query(
            Race.year.label("season"),
            func.count(Result.resultId).label("total_entries"),
            func.sum(
                case(
                    (or_(Status.status == "Finished", Status.status.like("+% Lap%")), 1),
                    else_=0,
                )
            ).label("classified"),
            func.sum(
                case(
                    (and_(Status.status != "Finished", ~Status.status.like("+% Lap%")), 1),
                    else_=0,
                )
            ).label("dnfs"),
        )
        .join(Result, Race.raceId == Result.raceId)
        .join(Status, Result.statusId == Status.statusId)
    )

    if start:
        q = q.filter(Race.year >= start)
    if end:
        q = q.filter(Race.year <= end)

    rows = q.group_by(Race.year).order_by(Race.year).all()

    trends = []
    for r in rows:
        total = r.total_entries or 1
        classified = r.classified or 0
        dnfs = r.dnfs or 0
        rate = round((classified / total) * 100, 1)
        trends.append({
            "season": r.season,
            "total_entries": total,
            "classified": classified,
            "dnfs": dnfs,
            "completion_rate": rate,
            "dnf_rate": round(100.0 - rate, 1),
        })
    return trends


@router.get("/reliability/dnf-reasons")
def get_dnf_reasons(
    season: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """Categorized breakdown of mechanical, collision, and other failure reasons."""
    q = (
        db.query(Status.status, func.count(Result.resultId).label("count"))
        .join(Result, Status.statusId == Result.statusId)
        .join(Race, Result.raceId == Race.raceId)
        .filter(Status.status != "Finished", ~Status.status.like("+% Lap%"))
    )
    if season:
        q = q.filter(Race.year == season)

    rows = q.group_by(Status.status).order_by(desc("count")).limit(15).all()

    # Categorize
    categories = {
        "Engine/Power Unit": ["Engine", "Power Unit", "Turbo", "Exhaust"],
        "Transmission/Gearbox": ["Gearbox", "Clutch", "Transmission", "Driveshaft"],
        "Collision/Accident": ["Collision", "Accident", "Damage", "Collision damage", "Spun off"],
        "Brakes/Hydraulics": ["Brakes", "Hydraulics", "Brake duct"],
        "Electrical/Electronics": ["Electrical", "Battery", "ERS"],
        "Suspension/Steering": ["Suspension", "Steering", "Wheel", "Tyre"],
    }

    reasons = []
    for r in rows:
        cat = "Other / Mechanical"
        for cname, keywords in categories.items():
            if any(k.lower() in r.status.lower() for k in keywords):
                cat = cname
                break
        reasons.append({
            "reason": r.status,
            "count": r.count,
            "category": cat,
        })
    return reasons


@router.get("/reliability/constructors")
def get_reliability_constructors(
    season: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """Constructor ranking by reliability and race completion rate."""
    q = (
        db.query(
            Constructor.constructorId,
            Constructor.name,
            func.count(Result.resultId).label("total"),
            func.sum(
                case(
                    (or_(Status.status == "Finished", Status.status.like("+% Lap%")), 1),
                    else_=0,
                )
            ).label("classified"),
            func.sum(
                case(
                    (and_(Status.status != "Finished", ~Status.status.like("+% Lap%")), 1),
                    else_=0,
                )
            ).label("dnfs"),
        )
        .join(Result, Constructor.constructorId == Result.constructorId)
        .join(Race, Result.raceId == Race.raceId)
        .join(Status, Result.statusId == Status.statusId)
    )
    if season:
        q = q.filter(Race.year == season)

    rows = q.group_by(Constructor.constructorId).order_by(desc("classified")).all()

    result = []
    for r in rows:
        total = r.total or 1
        classified = r.classified or 0
        dnf = r.dnfs or 0
        finish_rate = round((classified / total) * 100, 1)
        result.append({
            "constructor_id": str(r.constructorId),
            "name": r.name,
            "total_entries": total,
            "classified": classified,
            "dnf_count": dnf,
            "finish_rate": finish_rate,
        })
    return result


# ─── Podiums ─────────────────────────────────────────────────────────────────

@router.get("/podiums")
@router.get("/podiums/leaderboard")
def get_podiums_leaderboard(
    season: Optional[int] = Query(None),
    nationality: Optional[str] = Query(None),
    limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Driver podium finishes breakdown (P1, P2, P3)."""
    podiums = data_service.get_podiums(db, nationality=nationality, season=season)
    items = [p.model_dump() for p in podiums.data[:limit]]
    return items


@router.get("/podiums/constructors")
def get_constructor_podiums(
    season: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """Constructor podium distribution."""
    q = (
        db.query(
            Constructor.name,
            Constructor.constructorRef,
            func.sum(case((Result.position == 1, 1), else_=0)).label("p1"),
            func.sum(case((Result.position == 2, 1), else_=0)).label("p2"),
            func.sum(case((Result.position == 3, 1), else_=0)).label("p3"),
            func.sum(case((Result.position <= 3, 1), else_=0)).label("total_podiums"),
        )
        .join(Result, Constructor.constructorId == Result.constructorId)
        .join(Race, Result.raceId == Race.raceId)
        .filter(Result.position <= 3)
    )
    if season:
        q = q.filter(Race.year == season)

    rows = q.group_by(Constructor.constructorId).order_by(desc("total_podiums")).all()
    return [
        {
            "name": r.name,
            "constructor_ref": r.constructorRef,
            "p1": int(r.p1 or 0),
            "p2": int(r.p2 or 0),
            "p3": int(r.p3 or 0),
            "total_podiums": int(r.total_podiums or 0),
        }
        for r in rows
    ]


@router.get("/podiums/nationalities")
def get_nationality_podiums(
    season: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """Podium achievements grouped by driver nationality."""
    q = (
        db.query(
            Driver.nationality,
            func.sum(case((Result.position == 1, 1), else_=0)).label("wins"),
            func.sum(case((Result.position <= 3, 1), else_=0)).label("podiums"),
        )
        .join(Result, Driver.driverId == Result.driverId)
        .join(Race, Result.raceId == Race.raceId)
        .filter(Result.position <= 3)
    )
    if season:
        q = q.filter(Race.year == season)

    rows = q.group_by(Driver.nationality).order_by(desc("podiums")).all()
    return [
        {
            "nationality": r.nationality,
            "wins": int(r.wins or 0),
            "podiums": int(r.podiums or 0),
        }
        for r in rows
    ]


# ─── Tyre Strategy ───────────────────────────────────────────────────────────

@router.get("/tyre-analysis", response_model=TyreAnalysisResponse)
def get_tyre_analysis():
    """Tyre strategy and compound analysis.
    
    CRITICAL RULE:
    Do not infer tyre compound usage without stint data.
    The Ergast dataset does not contain stint-level tyre compounds.
    Returns explicit data unavailability notice.
    """
    return TyreAnalysisResponse(
        data_available=False,
        message=(
            "Detailed tyre compound data (Soft, Medium, Hard, Intermediate, Wet) "
            "requires stint-level telemetry and pit strategy records not included in "
            "the standard Ergast/Jolpica database. Stint analysis is disabled to prevent "
            "simulating or fabricating unverified historical tyre usage."
        ),
        data=[],
    )


# ─── Data Quality & Explorer ─────────────────────────────────────────────────

@router.get("/data-quality")
@router.get("/data/quality")
def get_data_quality_report(db: Session = Depends(get_db)):
    """Summary of database table sizes, record counts, and data completeness."""
    quality = data_service.get_data_quality(db)
    return quality.tables


@router.get("/data-explorer/{dataset}")
@router.get("/data/{dataset}")
def explore_dataset(
    dataset: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    per_page: Optional[int] = Query(None),
    sort_by: Optional[str] = Query(None),
    order: str = Query("asc", pattern="^(asc|desc)$"),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Generic table data explorer with pagination, search, and sorting."""
    effective_per_page = per_page or page_size
    res = data_service.get_data_explorer(
        db,
        dataset=dataset,
        page=page,
        per_page=effective_per_page,
        sort_by=sort_by,
        order=order,
        search=search,
    )
    return res.data


@router.post("/data-explorer/upload")
async def upload_csv_file(file: UploadFile = File(...)):
    """Upload and validate a CSV dataset file."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # 10 MB limit
        raise HTTPException(status_code=400, detail="File exceeds 10MB limit")

    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")

    return {
        "status": "validated",
        "filename": file.filename,
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": list(df.columns),
        "null_counts": df.isnull().sum().to_dict(),
        "sample_preview": df.head(5).to_dict(orient="records"),
    }


# ─── Export ──────────────────────────────────────────────────────────────────

@router.get("/export/{dataset}")
def export_dataset_csv(
    dataset: str,
    season: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """Download filtered dataset records as a CSV file."""
    df = data_service.get_export_data(db, dataset=dataset, season=season)
    if df is None:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset}' not found for export")

    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    filename = f"f1_{dataset}_{season if season else 'all'}.csv"
    return StreamingResponse(
        iter([csv_buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ─── Insights ────────────────────────────────────────────────────────────────

@router.get("/insights", response_model=List[InsightItem])
def get_analytical_insights(
    start_season: Optional[int] = Query(2010),
    end_season: Optional[int] = Query(2024),
    db: Session = Depends(get_db),
):
    """Deterministic, computed insights from the historical dataset."""
    return generate_insights(db, start_season=start_season, end_season=end_season)
