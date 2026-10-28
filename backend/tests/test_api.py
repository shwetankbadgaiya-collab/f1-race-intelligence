"""Automated unit and integration tests for F1 Race Intelligence API."""

import pytest


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_seasons(client):
    response = client.get("/api/seasons")
    assert response.status_code == 200
    seasons = response.json()
    assert len(seasons) > 0
    years = [s["year"] for s in seasons]
    assert 2010 in years
    assert 2024 in years


def test_overview(client):
    response = client.get("/api/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["total_races"] > 0
    assert data["total_drivers"] > 0
    assert data["total_constructors"] > 0
    assert data["total_circuits"] > 0
    assert data["total_podiums"] > 0
    assert data["classified_finishes"] > 0


def test_championship_trends(client):
    response = client.get("/api/championship-trends?start_season=2010&end_season=2024")
    assert response.status_code == 200
    trends = response.json()
    assert len(trends) > 0
    constructors = {t["constructor"] for t in trends}
    assert any("Red Bull" in c or "Mercedes" in c or "Ferrari" in c for c in constructors)


def test_drivers(client):
    response = client.get("/api/drivers")
    assert response.status_code == 200
    drivers = response.json()
    assert len(drivers) > 0
    driver_refs = [d["driverRef"] for d in drivers]
    assert "hamilton" in driver_refs or "vettel" in driver_refs or "verstappen" in driver_refs


def test_driver_leaderboard(client):
    response = client.get("/api/drivers/leaderboard?limit=10")
    assert response.status_code == 200
    board = response.json()
    assert len(board) > 0
    assert board[0]["points"] >= board[-1]["points"]


def test_driver_profile(client):
    # Search for verstappen or hamilton
    response = client.get("/api/drivers?search=hamilton")
    drivers = response.json()
    assert len(drivers) > 0
    did = drivers[0]["driverId"]

    profile_resp = client.get(f"/api/drivers/{did}")
    assert profile_resp.status_code == 200
    profile = profile_resp.json()
    assert "driver" in profile
    assert profile["driver"]["driverId"] == did
    assert profile["race_starts"] > 0


def test_driver_compare(client):
    drivers_resp = client.get("/api/drivers")
    d1 = drivers_resp.json()[0]["driverId"]
    d2 = drivers_resp.json()[1]["driverId"]

    compare_resp = client.get(f"/api/drivers/compare?driver_ids={d1},{d2}")
    assert compare_resp.status_code == 200
    data = compare_resp.json()
    assert len(data["drivers"]) == 2


def test_constructors(client):
    response = client.get("/api/constructors")
    assert response.status_code == 200
    teams = response.json()
    assert len(teams) > 0


def test_constructor_leaderboard(client):
    response = client.get("/api/constructors/leaderboard")
    assert response.status_code == 200
    teams = response.json()
    assert len(teams) > 0
    assert teams[0]["points"] >= teams[-1]["points"]


def test_circuits(client):
    response = client.get("/api/circuits")
    assert response.status_code == 200
    circuits = response.json()
    assert len(circuits) > 0
    names = [c["name"] for c in circuits]
    assert any("Silverstone" in n or "Monza" in n or "Spa" in n for n in names)


def test_circuit_leaderboard(client):
    response = client.get("/api/circuits/leaderboard")
    assert response.status_code == 200
    leaders = response.json()
    assert len(leaders) > 0
    assert leaders[0]["races_hosted"] >= 1


def test_reliability_trends(client):
    response = client.get("/api/reliability/trends")
    assert response.status_code == 200
    trends = response.json()
    assert len(trends) > 0
    assert "completion_rate" in trends[0]
    assert "dnf_rate" in trends[0]


def test_reliability_dnf_reasons(client):
    response = client.get("/api/reliability/dnf-reasons")
    assert response.status_code == 200
    reasons = response.json()
    assert len(reasons) > 0
    assert "category" in reasons[0]


def test_podiums(client):
    response = client.get("/api/podiums")
    assert response.status_code == 200
    podiums = response.json()
    assert len(podiums) > 0
    assert podiums[0]["total_podiums"] > 0


def test_tyre_analysis_rule(client):
    # Verifies the critical rule: do not simulate tyre compounds without stint data
    response = client.get("/api/tyre-analysis")
    assert response.status_code == 200
    data = response.json()
    assert data["data_available"] is False
    assert "stint-level" in data["message"].lower()


def test_data_quality(client):
    response = client.get("/api/data-quality")
    assert response.status_code == 200
    tables = response.json()
    assert len(tables) > 0
    table_names = [t["table_name"] for t in tables]
    assert "results" in table_names


def test_data_explorer(client):
    response = client.get("/api/data-explorer/races?page=1&per_page=10")
    assert response.status_code == 200
    races = response.json()
    assert len(races) == 10


def test_insights(client):
    response = client.get("/api/insights")
    assert response.status_code == 200
    insights = response.json()
    assert len(insights) > 0
    assert "category" in insights[0]
    assert "title" in insights[0]


def test_csv_export(client):
    response = client.get("/api/export/circuits")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "attachment" in response.headers["content-disposition"]
    text = response.text
    assert "circuitId" in text or "name" in text
