"""Deterministic insights engine for F1 Race Intelligence Dashboard.

Generates insights from computed statistics — never hardcoded values.
Each insight is derived from real database queries and comparisons.
"""

import re
from typing import List, Optional

import pandas as pd
from sqlalchemy import func, desc, and_
from sqlalchemy.orm import Session

from app.models import (
    Race, Result, Driver, Constructor, Status, Circuit,
    ConstructorStanding, DriverStanding,
)
from app.schemas import InsightItem


_FINISHED_PATTERN = re.compile(r"^(Finished|\+\d+ Lap(s)?)$", re.IGNORECASE)


def _is_classified(status_text: str) -> bool:
    return bool(_FINISHED_PATTERN.match(status_text))


def generate_insights(
    db: Session,
    start_season: Optional[int] = None,
    end_season: Optional[int] = None,
) -> List[InsightItem]:
    """Generate all deterministic insights for the given season range."""
    effective_start = start_season or 2010
    effective_end = end_season or 2026

    insights: List[InsightItem] = []
    season_range_label = f"{effective_start}-{effective_end}"

    insights.extend(_constructor_yoy_trends(db, effective_start, effective_end, season_range_label))
    insights.extend(_driver_podium_trends(db, effective_start, effective_end, season_range_label))
    insights.extend(_circuit_dnf_insights(db, effective_start, effective_end, season_range_label))
    insights.extend(_consistency_insights(db, effective_start, effective_end, season_range_label))
    insights.extend(_top_performers_insights(db, effective_start, effective_end, season_range_label))

    return insights


def _constructor_yoy_trends(
    db: Session, start: int, end: int, season_range: str,
) -> List[InsightItem]:
    """Compare constructor points year-over-year."""
    insights: List[InsightItem] = []

    # Get final standings per season: use last race of each season
    seasons_data = []
    for year in range(start, end + 1):
        last_race = (
            db.query(Race.raceId)
            .filter(Race.year == year)
            .order_by(desc(Race.round))
            .first()
        )
        if not last_race:
            continue
        standings = (
            db.query(ConstructorStanding, Constructor)
            .join(Constructor, ConstructorStanding.constructorId == Constructor.constructorId)
            .filter(ConstructorStanding.raceId == last_race[0])
            .all()
        )
        for standing, constructor in standings:
            seasons_data.append({
                "year": year,
                "constructor_id": constructor.constructorId,
                "constructor_name": constructor.name,
                "points": float(standing.points or 0),
                "position": standing.position,
            })

    if not seasons_data:
        return insights

    df = pd.DataFrame(seasons_data)

    # For each constructor, compare consecutive seasons
    for cid, grp in df.groupby("constructor_id"):
        grp = grp.sort_values("year")
        if len(grp) < 2:
            continue

        name = grp.iloc[0]["constructor_name"]
        for i in range(1, len(grp)):
            prev = grp.iloc[i - 1]
            curr = grp.iloc[i]

            if prev["year"] + 1 != curr["year"]:
                continue  # skip non-consecutive seasons

            prev_pts = prev["points"]
            curr_pts = curr["points"]
            if prev_pts == 0:
                continue

            pct_change = ((curr_pts - prev_pts) / prev_pts) * 100

            if pct_change > 30:
                insights.append(InsightItem(
                    category="trend",
                    title=f"{name} surged in {int(curr['year'])}",
                    description=(
                        f"{name} increased their points from {prev_pts:.0f} "
                        f"({int(prev['year'])}) to {curr_pts:.0f} ({int(curr['year'])}), "
                        f"a {pct_change:.1f}% improvement."
                    ),
                    metric_value=round(curr_pts, 1),
                    comparison_value=round(prev_pts, 1),
                    season_range=f"{int(prev['year'])}-{int(curr['year'])}",
                    severity="positive",
                ))
            elif pct_change < -30:
                insights.append(InsightItem(
                    category="trend",
                    title=f"{name} declined in {int(curr['year'])}",
                    description=(
                        f"{name} dropped from {prev_pts:.0f} points "
                        f"({int(prev['year'])}) to {curr_pts:.0f} ({int(curr['year'])}), "
                        f"a {abs(pct_change):.1f}% decrease."
                    ),
                    metric_value=round(curr_pts, 1),
                    comparison_value=round(prev_pts, 1),
                    season_range=f"{int(prev['year'])}-{int(curr['year'])}",
                    severity="negative",
                ))

    return insights


def _driver_podium_trends(
    db: Session, start: int, end: int, season_range: str,
) -> List[InsightItem]:
    """Identify drivers with improving or declining podium rates."""
    insights: List[InsightItem] = []

    # Get podium data per driver per season
    rows = (
        db.query(
            Result.driverId,
            Driver.forename,
            Driver.surname,
            Race.year,
            Result.position,
        )
        .join(Driver, Result.driverId == Driver.driverId)
        .join(Race, Result.raceId == Race.raceId)
        .filter(Race.year >= start, Race.year <= end)
        .all()
    )

    if not rows:
        return insights

    df = pd.DataFrame(rows, columns=["driver_id", "forename", "surname", "year", "position"])
    df["is_podium"] = df["position"].isin([1, 2, 3])

    for did, grp in df.groupby("driver_id"):
        season_stats = (
            grp.groupby("year")
            .agg(
                races=("position", "count"),
                podiums=("is_podium", "sum"),
            )
            .reset_index()
            .sort_values("year")
        )
        season_stats["podium_rate"] = season_stats["podiums"] / season_stats["races"] * 100

        if len(season_stats) < 2:
            continue

        name = f"{grp.iloc[0]['forename']} {grp.iloc[0]['surname']}"

        # Compare first half vs second half
        mid = len(season_stats) // 2
        first_half_rate = season_stats.iloc[:mid]["podium_rate"].mean()
        second_half_rate = season_stats.iloc[mid:]["podium_rate"].mean()

        if first_half_rate == 0 and second_half_rate == 0:
            continue

        if second_half_rate > first_half_rate + 15:
            insights.append(InsightItem(
                category="performance",
                title=f"{name}: Rising podium trend",
                description=(
                    f"{name}'s podium rate improved from "
                    f"{first_half_rate:.1f}% in earlier seasons to "
                    f"{second_half_rate:.1f}% in recent seasons."
                ),
                metric_value=round(second_half_rate, 1),
                comparison_value=round(first_half_rate, 1),
                season_range=season_range,
                severity="positive",
            ))
        elif second_half_rate < first_half_rate - 15:
            insights.append(InsightItem(
                category="performance",
                title=f"{name}: Declining podium trend",
                description=(
                    f"{name}'s podium rate fell from "
                    f"{first_half_rate:.1f}% in earlier seasons to "
                    f"{second_half_rate:.1f}% in recent seasons."
                ),
                metric_value=round(second_half_rate, 1),
                comparison_value=round(first_half_rate, 1),
                season_range=season_range,
                severity="negative",
            ))

    return insights


def _circuit_dnf_insights(
    db: Session, start: int, end: int, season_range: str,
) -> List[InsightItem]:
    """Flag circuits with above-average DNF rates."""
    insights: List[InsightItem] = []

    rows = (
        db.query(
            Circuit.circuitId,
            Circuit.name,
            Status.status,
        )
        .join(Race, Circuit.circuitId == Race.circuitId)
        .join(Result, Race.raceId == Result.raceId)
        .join(Status, Result.statusId == Status.statusId)
        .filter(Race.year >= start, Race.year <= end)
        .all()
    )

    if not rows:
        return insights

    df = pd.DataFrame(rows, columns=["circuit_id", "circuit_name", "status"])
    df["is_dnf"] = ~df["status"].apply(_is_classified)

    circuit_stats = (
        df.groupby(["circuit_id", "circuit_name"])
        .agg(
            total=("status", "count"),
            dnfs=("is_dnf", "sum"),
        )
        .reset_index()
    )
    circuit_stats["dnf_rate"] = circuit_stats["dnfs"] / circuit_stats["total"] * 100

    overall_dnf_rate = float(df["is_dnf"].mean() * 100)

    # Flag circuits with DNF rate significantly above average
    threshold = overall_dnf_rate + 10
    high_dnf = circuit_stats[
        (circuit_stats["dnf_rate"] > threshold) & (circuit_stats["total"] >= 10)
    ].sort_values("dnf_rate", ascending=False)

    for _, row in high_dnf.head(5).iterrows():
        insights.append(InsightItem(
            category="reliability",
            title=f"High DNF rate at {row['circuit_name']}",
            description=(
                f"{row['circuit_name']} has a {row['dnf_rate']:.1f}% DNF rate "
                f"({int(row['dnfs'])} DNFs in {int(row['total'])} entries), "
                f"which is above the overall average of {overall_dnf_rate:.1f}%."
            ),
            metric_value=round(row["dnf_rate"], 1),
            comparison_value=round(overall_dnf_rate, 1),
            season_range=season_range,
            severity="warning",
        ))

    return insights


def _consistency_insights(
    db: Session, start: int, end: int, season_range: str,
) -> List[InsightItem]:
    """Note consistency patterns — drivers with high finish rates."""
    insights: List[InsightItem] = []

    rows = (
        db.query(
            Result.driverId,
            Driver.forename,
            Driver.surname,
            Status.status,
        )
        .join(Driver, Result.driverId == Driver.driverId)
        .join(Race, Result.raceId == Race.raceId)
        .join(Status, Result.statusId == Status.statusId)
        .filter(Race.year >= start, Race.year <= end)
        .all()
    )

    if not rows:
        return insights

    df = pd.DataFrame(rows, columns=["driver_id", "forename", "surname", "status"])
    df["classified"] = df["status"].apply(_is_classified)

    driver_stats = (
        df.groupby(["driver_id", "forename", "surname"])
        .agg(
            total=("status", "count"),
            classified=("classified", "sum"),
        )
        .reset_index()
    )
    driver_stats["finish_rate"] = driver_stats["classified"] / driver_stats["total"] * 100

    # Only consider drivers with meaningful sample sizes
    significant = driver_stats[driver_stats["total"] >= 20].sort_values(
        "finish_rate", ascending=False
    )

    for _, row in significant.head(3).iterrows():
        if row["finish_rate"] >= 90:
            insights.append(InsightItem(
                category="consistency",
                title=f"{row['forename']} {row['surname']}: Exceptionally consistent",
                description=(
                    f"{row['forename']} {row['surname']} finished "
                    f"{int(row['classified'])} of {int(row['total'])} races "
                    f"({row['finish_rate']:.1f}% finish rate) in the {season_range} period."
                ),
                metric_value=round(row["finish_rate"], 1),
                comparison_value=None,
                season_range=season_range,
                severity="positive",
            ))

    return insights


def _top_performers_insights(
    db: Session, start: int, end: int, season_range: str,
) -> List[InsightItem]:
    """Highlight top performers by wins and podiums."""
    insights: List[InsightItem] = []

    rows = (
        db.query(
            Result.driverId,
            Driver.forename,
            Driver.surname,
            Result.position,
        )
        .join(Driver, Result.driverId == Driver.driverId)
        .join(Race, Result.raceId == Race.raceId)
        .filter(Race.year >= start, Race.year <= end)
        .filter(Result.position == 1)
        .all()
    )

    if not rows:
        return insights

    df = pd.DataFrame(rows, columns=["driver_id", "forename", "surname", "position"])
    win_counts = (
        df.groupby(["driver_id", "forename", "surname"])
        .size()
        .reset_index(name="wins")
        .sort_values("wins", ascending=False)
    )

    if len(win_counts) >= 1:
        top = win_counts.iloc[0]
        insights.append(InsightItem(
            category="performance",
            title=f"{top['forename']} {top['surname']}: Most wins",
            description=(
                f"{top['forename']} {top['surname']} leads with "
                f"{int(top['wins'])} race wins in the {season_range} period."
            ),
            metric_value=float(top["wins"]),
            comparison_value=(
                float(win_counts.iloc[1]["wins"]) if len(win_counts) > 1 else None
            ),
            season_range=season_range,
            severity="info",
        ))

    return insights
