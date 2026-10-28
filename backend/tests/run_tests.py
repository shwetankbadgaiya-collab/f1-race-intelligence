"""Direct async test runner for backend endpoints."""

import asyncio
import httpx
from app.main import app

async def run_all_checks():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        print("Checking /api/health...")
        r = await client.get("/api/health")
        assert r.status_code == 200, f"Health failed: {r.status_code}"
        print("  ✓ Health:", r.json())

        print("Checking /api/seasons...")
        r = await client.get("/api/seasons")
        assert r.status_code == 200
        seasons = r.json()
        assert len(seasons) >= 15
        print(f"  ✓ Seasons count: {len(seasons)}")

        print("Checking /api/overview...")
        r = await client.get("/api/overview")
        assert r.status_code == 200
        ov = r.json()
        print("  ✓ Overview:", ov)

        print("Checking /api/championship-trends...")
        r = await client.get("/api/championship-trends")
        assert r.status_code == 200
        print(f"  ✓ Championship trends items: {len(r.json())}")

        print("Checking /api/drivers/leaderboard...")
        r = await client.get("/api/drivers/leaderboard?limit=5")
        assert r.status_code == 200
        print("  ✓ Top driver:", r.json()[0]["driver_name"], r.json()[0]["points"])

        print("Checking /api/constructors/leaderboard...")
        r = await client.get("/api/constructors/leaderboard")
        assert r.status_code == 200
        print("  ✓ Top team:", r.json()[0]["name"], r.json()[0]["points"])

        print("Checking /api/circuits/leaderboard...")
        r = await client.get("/api/circuits/leaderboard")
        assert r.status_code == 200
        print("  ✓ Top circuit:", r.json()[0]["name"], r.json()[0]["races_hosted"])

        print("Checking /api/reliability/trends...")
        r = await client.get("/api/reliability/trends")
        assert r.status_code == 200
        print(f"  ✓ Reliability seasons: {len(r.json())}")

        print("Checking /api/podiums/leaderboard...")
        r = await client.get("/api/podiums/leaderboard?limit=5")
        assert r.status_code == 200
        print(f"  ✓ Podiums items: {len(r.json())}")

        print("Checking /api/tyre-analysis (Critical rule check)...")
        r = await client.get("/api/tyre-analysis")
        assert r.status_code == 200
        assert r.json()["data_available"] is False
        print("  ✓ Tyre analysis rule verified: data_available is False")

        print("Checking /api/data-quality...")
        r = await client.get("/api/data-quality")
        assert r.status_code == 200
        print(f"  ✓ Data quality tables: {len(r.json())}")

        print("Checking /api/insights...")
        r = await client.get("/api/insights")
        assert r.status_code == 200
        print(f"  ✓ Generated insights: {len(r.json())}")

        print("\nALL 12 ENDPOINT CHECKS PASSED PERFECTLY! 🚀")

if __name__ == "__main__":
    asyncio.run(run_all_checks())
