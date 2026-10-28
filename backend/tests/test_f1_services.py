"""Comprehensive test suite for F1 Race Intelligence service and analytics layer."""

import pytest
from app.database import SessionLocal
from app.services import data_service
from app.analytics.insights import generate_insights


@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    yield session
    session.close()


def test_seasons_query(db):
    seasons = data_service.get_seasons(db)
    assert len(seasons) >= 15
    years = [s.year for s in seasons]
    assert 2010 in years
    assert 2024 in years


def test_overview_metrics(db):
    ov = data_service.get_overview(db)
    assert ov.total_races == 299
    assert ov.total_drivers >= 40
    assert ov.total_constructors >= 20
    assert ov.total_podiums == 897
    assert ov.classified_finishes > 5000
    assert ov.unclassified_finishes > 800
    assert ov.classified_finishes + ov.unclassified_finishes == 5945


def test_championship_trends(db):
    trends = data_service.get_championship_trends(db, start_season=2010, end_season=2024)
    assert len(trends) > 0
    constructors = {t.constructor for t in trends}
    assert any("Red Bull" in c or "Mercedes" in c or "Ferrari" in c for c in constructors)
    for t in trends:
        assert t.points >= 0


def test_drivers_list(db):
    drivers = data_service.get_drivers(db)
    assert len(drivers) >= 40
    driver_refs = [d.driverRef for d in drivers]
    assert "hamilton" in driver_refs or "verstappen" in driver_refs or "vettel" in driver_refs


def test_driver_profile(db):
    # Search for Hamilton
    ham = data_service.get_drivers(db, search="Hamilton")
    assert len(ham) > 0
    hid = ham[0].driverId
    profile = data_service.get_driver_detail(db, driver_id=hid)
    assert profile is not None
    assert profile.driver.driverId == hid
    assert profile.race_starts > 100
    assert profile.podiums > 0
    assert profile.finish_rate > 50.0


def test_driver_comparison(db):
    drivers = data_service.get_drivers(db)
    d1 = drivers[0].driverId
    d2 = drivers[1].driverId
    comp = data_service.get_driver_comparison(db, driver_ids=[d1, d2])
    assert len(comp.drivers) == 2
    assert comp.drivers[0].driver.driverId == d1
    assert comp.drivers[1].driver.driverId == d2


def test_constructors_list(db):
    constructors = data_service.get_constructors(db)
    assert len(constructors) >= 10
    names = [c.name for c in constructors]
    assert any("Ferrari" in n or "Red Bull" in n or "Mercedes" in n for n in names)


def test_constructor_profile(db):
    ferrari = data_service.get_constructors(db, search="Ferrari")
    assert len(ferrari) > 0
    cid = ferrari[0].constructorId
    profile = data_service.get_constructor_detail(db, constructor_id=cid)
    assert profile is not None
    assert profile.total_points > 0
    assert profile.race_entries > 0


def test_circuits_list(db):
    circuits = data_service.get_circuits(db)
    assert len(circuits) >= 30
    names = [c.name for c in circuits]
    assert any("Monza" in n or "Silverstone" in n or "Spa" in n for n in names)


def test_circuit_detail(db):
    circuits = data_service.get_circuits(db)
    cid = circuits[0].circuitId
    detail = data_service.get_circuit_detail(db, circuit_id=cid)
    assert detail is not None
    assert "circuit" in detail
    assert "total_races" in detail


def test_reliability_stats(db):
    rel = data_service.get_reliability(db)
    assert len(rel.data) > 0
    item = rel.data[0]
    assert item.total_entries > 0
    assert 0.0 <= item.finish_rate <= 100.0


def test_podiums_stats(db):
    podiums = data_service.get_podiums(db)
    assert len(podiums.data) > 0
    top = podiums.data[0]
    assert top.total_podiums >= podiums.data[-1].total_podiums


def test_data_quality_report(db):
    dq = data_service.get_data_quality(db)
    assert len(dq.tables) >= 5
    assert dq.total_records > 10000
    assert dq.overall_completeness > 80.0


def test_data_explorer(db):
    page = data_service.get_data_explorer(db, dataset="races", page=1, per_page=15)
    assert len(page.data) == 15
    assert page.total == 299


def test_export_data(db):
    df = data_service.get_export_data(db, dataset="circuits")
    assert df is not None
    assert len(df) >= 30
    assert "circuitId" in df.columns
    assert "name" in df.columns


def test_insights_generation(db):
    insights = generate_insights(db, start_season=2010, end_season=2024)
    assert len(insights) > 0
    for ins in insights:
        assert ins.title
        assert ins.description
        assert ins.category in ["performance", "reliability", "consistency", "trend"]
        assert ins.severity in ["info", "positive", "negative", "warning"]
