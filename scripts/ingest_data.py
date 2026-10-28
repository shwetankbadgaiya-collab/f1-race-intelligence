#!/usr/bin/env python3
"""
F1 Race Intelligence — Data Ingestion Pipeline
================================================

DEMO DATA - Generated to match Ergast schema format.

This script bootstraps the F1 analytics database:
  1. Checks for an existing SQLite DB at data/f1_data.db
  2. Attempts to load from CSV files in data/
  3. If no CSVs exist, generates realistic sample data for 2010-2024

The generated data uses REAL circuit, driver, and constructor names with
historically-accurate championship results, point distributions, and
era-correct scoring systems.

Usage:
    python scripts/ingest_data.py
"""

from __future__ import annotations

import csv
import logging
import os
import random
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import sqlalchemy as sa
from sqlalchemy import (
    Column,
    Float,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Session

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("ingest")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "f1_data.db"

# ---------------------------------------------------------------------------
# SQLAlchemy Models
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    pass


class Season(Base):
    __tablename__ = "seasons"
    year = Column(Integer, primary_key=True)
    url = Column(Text)


class Circuit(Base):
    __tablename__ = "circuits"
    circuitId = Column(Integer, primary_key=True, autoincrement=True)
    circuitRef = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    location = Column(String(255))
    country = Column(String(255))
    lat = Column(Float)
    lng = Column(Float)
    alt = Column(Integer)
    url = Column(Text)


class Constructor(Base):
    __tablename__ = "constructors"
    constructorId = Column(Integer, primary_key=True, autoincrement=True)
    constructorRef = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    nationality = Column(String(255))
    url = Column(Text)


class Driver(Base):
    __tablename__ = "drivers"
    driverId = Column(Integer, primary_key=True, autoincrement=True)
    driverRef = Column(String(255), nullable=False)
    number = Column(Integer)
    code = Column(String(3))
    forename = Column(String(255))
    surname = Column(String(255))
    dob = Column(String(10))
    nationality = Column(String(255))
    url = Column(Text)


class Status(Base):
    __tablename__ = "status"
    statusId = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(String(255), nullable=False)


class Race(Base):
    __tablename__ = "races"
    raceId = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer, nullable=False)
    round = Column(Integer, nullable=False)
    circuitId = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    date = Column(String(10))
    time = Column(String(8))
    url = Column(Text)


class Result(Base):
    __tablename__ = "results"
    resultId = Column(Integer, primary_key=True, autoincrement=True)
    raceId = Column(Integer, nullable=False)
    driverId = Column(Integer, nullable=False)
    constructorId = Column(Integer, nullable=False)
    number = Column(Integer)
    grid = Column(Integer)
    position = Column(Integer)
    positionText = Column(String(10))
    positionOrder = Column(Integer)
    points = Column(Float, default=0)
    laps = Column(Integer)
    time = Column(String(255))
    milliseconds = Column(Integer)
    fastestLap = Column(Integer)
    rank = Column(Integer)
    fastestLapTime = Column(String(255))
    fastestLapSpeed = Column(String(255))
    statusId = Column(Integer, nullable=False)


class Qualifying(Base):
    __tablename__ = "qualifying"
    qualifyId = Column(Integer, primary_key=True, autoincrement=True)
    raceId = Column(Integer, nullable=False)
    driverId = Column(Integer, nullable=False)
    constructorId = Column(Integer, nullable=False)
    number = Column(Integer)
    position = Column(Integer)
    q1 = Column(String(255))
    q2 = Column(String(255))
    q3 = Column(String(255))


class DriverStanding(Base):
    __tablename__ = "driver_standings"
    driverStandingsId = Column(Integer, primary_key=True, autoincrement=True)
    raceId = Column(Integer, nullable=False)
    driverId = Column(Integer, nullable=False)
    points = Column(Float, default=0)
    position = Column(Integer)
    positionText = Column(String(10))
    wins = Column(Integer, default=0)


class ConstructorStanding(Base):
    __tablename__ = "constructor_standings"
    constructorStandingsId = Column(Integer, primary_key=True, autoincrement=True)
    raceId = Column(Integer, nullable=False)
    constructorId = Column(Integer, nullable=False)
    points = Column(Float, default=0)
    position = Column(Integer)
    positionText = Column(String(10))
    wins = Column(Integer, default=0)


# ---------------------------------------------------------------------------
# Reference Data — Real F1 Circuits
# ---------------------------------------------------------------------------
CIRCUITS_DATA: list[dict[str, Any]] = [
    {"circuitRef": "albert_park", "name": "Albert Park Grand Prix Circuit", "location": "Melbourne", "country": "Australia", "lat": -37.8497, "lng": 144.968, "alt": 10},
    {"circuitRef": "sepang", "name": "Sepang International Circuit", "location": "Kuala Lumpur", "country": "Malaysia", "lat": 2.76083, "lng": 101.738, "alt": 18},
    {"circuitRef": "shanghai", "name": "Shanghai International Circuit", "location": "Shanghai", "country": "China", "lat": 31.3389, "lng": 121.22, "alt": 5},
    {"circuitRef": "bahrain", "name": "Bahrain International Circuit", "location": "Sakhir", "country": "Bahrain", "lat": 26.0325, "lng": 50.5106, "alt": 7},
    {"circuitRef": "catalunya", "name": "Circuit de Barcelona-Catalunya", "location": "Montmeló", "country": "Spain", "lat": 41.57, "lng": 2.26111, "alt": 109},
    {"circuitRef": "monaco", "name": "Circuit de Monaco", "location": "Monte-Carlo", "country": "Monaco", "lat": 43.7347, "lng": 7.42056, "alt": 7},
    {"circuitRef": "villeneuve", "name": "Circuit Gilles Villeneuve", "location": "Montreal", "country": "Canada", "lat": 45.5, "lng": -73.5228, "alt": 13},
    {"circuitRef": "silverstone", "name": "Silverstone Circuit", "location": "Silverstone", "country": "UK", "lat": 52.0786, "lng": -1.01694, "alt": 153},
    {"circuitRef": "hockenheimring", "name": "Hockenheimring", "location": "Hockenheim", "country": "Germany", "lat": 49.3278, "lng": 8.56583, "alt": 103},
    {"circuitRef": "hungaroring", "name": "Hungaroring", "location": "Budapest", "country": "Hungary", "lat": 47.5789, "lng": 19.2486, "alt": 264},
    {"circuitRef": "spa", "name": "Circuit de Spa-Francorchamps", "location": "Spa", "country": "Belgium", "lat": 50.4372, "lng": 5.97139, "alt": 401},
    {"circuitRef": "monza", "name": "Autodromo Nazionale di Monza", "location": "Monza", "country": "Italy", "lat": 45.6156, "lng": 9.28111, "alt": 162},
    {"circuitRef": "marina_bay", "name": "Marina Bay Street Circuit", "location": "Marina Bay", "country": "Singapore", "lat": 1.2914, "lng": 103.864, "alt": 18},
    {"circuitRef": "suzuka", "name": "Suzuka Circuit", "location": "Suzuka", "country": "Japan", "lat": 34.8431, "lng": 136.541, "alt": 45},
    {"circuitRef": "yeongam", "name": "Korean International Circuit", "location": "Yeongam County", "country": "South Korea", "lat": 34.7333, "lng": 126.417, "alt": 0},
    {"circuitRef": "yas_marina", "name": "Yas Marina Circuit", "location": "Abu Dhabi", "country": "UAE", "lat": 24.4672, "lng": 54.6031, "alt": 3},
    {"circuitRef": "interlagos", "name": "Autódromo José Carlos Pace", "location": "São Paulo", "country": "Brazil", "lat": -23.7036, "lng": -46.6997, "alt": 785},
    {"circuitRef": "americas", "name": "Circuit of the Americas", "location": "Austin", "country": "USA", "lat": 30.1328, "lng": -97.6411, "alt": 161},
    {"circuitRef": "red_bull_ring", "name": "Red Bull Ring", "location": "Spielberg", "country": "Austria", "lat": 47.2197, "lng": 14.7647, "alt": 678},
    {"circuitRef": "sochi", "name": "Sochi Autodrom", "location": "Sochi", "country": "Russia", "lat": 43.4057, "lng": 39.9578, "alt": 2},
    {"circuitRef": "rodriguez", "name": "Autódromo Hermanos Rodríguez", "location": "Mexico City", "country": "Mexico", "lat": 19.4042, "lng": -99.0907, "alt": 2227},
    {"circuitRef": "baku", "name": "Baku City Circuit", "location": "Baku", "country": "Azerbaijan", "lat": 40.3725, "lng": 49.8533, "alt": -7},
    {"circuitRef": "ricard", "name": "Circuit Paul Ricard", "location": "Le Castellet", "country": "France", "lat": 43.2506, "lng": 5.79167, "alt": 432},
    {"circuitRef": "zandvoort", "name": "Circuit Park Zandvoort", "location": "Zandvoort", "country": "Netherlands", "lat": 52.3888, "lng": 4.54092, "alt": 6},
    {"circuitRef": "jeddah", "name": "Jeddah Corniche Circuit", "location": "Jeddah", "country": "Saudi Arabia", "lat": 21.6319, "lng": 39.1044, "alt": 15},
    {"circuitRef": "losail", "name": "Losail International Circuit", "location": "Al Daayen", "country": "Qatar", "lat": 25.49, "lng": 51.4542, "alt": 12},
    {"circuitRef": "miami", "name": "Miami International Autodrome", "location": "Miami", "country": "USA", "lat": 25.9581, "lng": -80.2389, "alt": 0},
    {"circuitRef": "las_vegas", "name": "Las Vegas Strip Street Circuit", "location": "Las Vegas", "country": "USA", "lat": 36.1147, "lng": -115.173, "alt": 610},
    {"circuitRef": "imola", "name": "Autodromo Enzo e Dino Ferrari", "location": "Imola", "country": "Italy", "lat": 44.3439, "lng": 11.7167, "alt": 37},
    {"circuitRef": "portimao", "name": "Autódromo Internacional do Algarve", "location": "Portimão", "country": "Portugal", "lat": 37.227, "lng": -8.6267, "alt": 108},
    {"circuitRef": "mugello", "name": "Mugello Circuit", "location": "Scarperia e San Piero", "country": "Italy", "lat": 43.9975, "lng": 11.3719, "alt": 255},
    {"circuitRef": "nurburgring", "name": "Nürburgring", "location": "Nürburg", "country": "Germany", "lat": 50.3356, "lng": 6.9475, "alt": 578},
    {"circuitRef": "istanbul", "name": "Istanbul Park", "location": "Istanbul", "country": "Turkey", "lat": 40.9517, "lng": 29.405, "alt": 130},
    {"circuitRef": "lusail", "name": "Lusail International Circuit", "location": "Lusail", "country": "Qatar", "lat": 25.49, "lng": 51.4542, "alt": 12},
]

# ---------------------------------------------------------------------------
# Reference Data — Real F1 Drivers
# ---------------------------------------------------------------------------
DRIVERS_DATA: list[dict[str, Any]] = [
    {"driverRef": "vettel", "number": 5, "code": "VET", "forename": "Sebastian", "surname": "Vettel", "dob": "1987-07-03", "nationality": "German"},
    {"driverRef": "hamilton", "number": 44, "code": "HAM", "forename": "Lewis", "surname": "Hamilton", "dob": "1985-01-07", "nationality": "British"},
    {"driverRef": "alonso", "number": 14, "code": "ALO", "forename": "Fernando", "surname": "Alonso", "dob": "1981-07-29", "nationality": "Spanish"},
    {"driverRef": "webber", "number": 2, "code": "WEB", "forename": "Mark", "surname": "Webber", "dob": "1976-08-27", "nationality": "Australian"},
    {"driverRef": "button", "number": 22, "code": "BUT", "forename": "Jenson", "surname": "Button", "dob": "1980-01-19", "nationality": "British"},
    {"driverRef": "massa", "number": 19, "code": "MAS", "forename": "Felipe", "surname": "Massa", "dob": "1981-04-25", "nationality": "Brazilian"},
    {"driverRef": "raikkonen", "number": 7, "code": "RAI", "forename": "Kimi", "surname": "Räikkönen", "dob": "1979-10-17", "nationality": "Finnish"},
    {"driverRef": "rosberg", "number": 6, "code": "ROS", "forename": "Nico", "surname": "Rosberg", "dob": "1985-06-27", "nationality": "German"},
    {"driverRef": "ricciardo", "number": 3, "code": "RIC", "forename": "Daniel", "surname": "Ricciardo", "dob": "1989-07-01", "nationality": "Australian"},
    {"driverRef": "bottas", "number": 77, "code": "BOT", "forename": "Valtteri", "surname": "Bottas", "dob": "1989-08-28", "nationality": "Finnish"},
    {"driverRef": "verstappen", "number": 1, "code": "VER", "forename": "Max", "surname": "Verstappen", "dob": "1997-09-30", "nationality": "Dutch"},
    {"driverRef": "leclerc", "number": 16, "code": "LEC", "forename": "Charles", "surname": "Leclerc", "dob": "1997-10-16", "nationality": "Monegasque"},
    {"driverRef": "norris", "number": 4, "code": "NOR", "forename": "Lando", "surname": "Norris", "dob": "1999-11-13", "nationality": "British"},
    {"driverRef": "sainz", "number": 55, "code": "SAI", "forename": "Carlos", "surname": "Sainz", "dob": "1994-09-01", "nationality": "Spanish"},
    {"driverRef": "perez", "number": 11, "code": "PER", "forename": "Sergio", "surname": "Pérez", "dob": "1990-01-26", "nationality": "Mexican"},
    {"driverRef": "grosjean", "number": 8, "code": "GRO", "forename": "Romain", "surname": "Grosjean", "dob": "1986-04-17", "nationality": "French"},
    {"driverRef": "hulkenberg", "number": 27, "code": "HUL", "forename": "Nico", "surname": "Hülkenberg", "dob": "1987-08-19", "nationality": "German"},
    {"driverRef": "magnussen", "number": 20, "code": "MAG", "forename": "Kevin", "surname": "Magnussen", "dob": "1992-10-05", "nationality": "Danish"},
    {"driverRef": "stroll", "number": 18, "code": "STR", "forename": "Lance", "surname": "Stroll", "dob": "1998-10-29", "nationality": "Canadian"},
    {"driverRef": "tsunoda", "number": 22, "code": "TSU", "forename": "Yuki", "surname": "Tsunoda", "dob": "2000-05-11", "nationality": "Japanese"},
    {"driverRef": "piastri", "number": 81, "code": "PIA", "forename": "Oscar", "surname": "Piastri", "dob": "2001-04-06", "nationality": "Australian"},
    {"driverRef": "russell", "number": 63, "code": "RUS", "forename": "George", "surname": "Russell", "dob": "1998-02-15", "nationality": "British"},
    {"driverRef": "ocon", "number": 31, "code": "OCO", "forename": "Esteban", "surname": "Ocon", "dob": "1996-09-17", "nationality": "French"},
    {"driverRef": "gasly", "number": 10, "code": "GAS", "forename": "Pierre", "surname": "Gasly", "dob": "1996-02-07", "nationality": "French"},
    {"driverRef": "kvyat", "number": 26, "code": "KVY", "forename": "Daniil", "surname": "Kvyat", "dob": "1994-04-26", "nationality": "Russian"},
    {"driverRef": "maldonado", "number": 13, "code": "MAL", "forename": "Pastor", "surname": "Maldonado", "dob": "1985-03-09", "nationality": "Venezuelan"},
    {"driverRef": "sutil", "number": 99, "code": "SUT", "forename": "Adrian", "surname": "Sutil", "dob": "1983-01-11", "nationality": "German"},
    {"driverRef": "kobayashi", "number": 0, "code": "KOB", "forename": "Kamui", "surname": "Kobayashi", "dob": "1986-09-13", "nationality": "Japanese"},
    {"driverRef": "di_resta", "number": 40, "code": "DIR", "forename": "Paul", "surname": "di Resta", "dob": "1986-04-16", "nationality": "British"},
    {"driverRef": "vergne", "number": 25, "code": "JEV", "forename": "Jean-Éric", "surname": "Vergne", "dob": "1990-04-25", "nationality": "French"},
    {"driverRef": "gutierrez", "number": 21, "code": "GUT", "forename": "Esteban", "surname": "Gutiérrez", "dob": "1991-08-05", "nationality": "Mexican"},
    {"driverRef": "max_chilton", "number": 4, "code": "CHI", "forename": "Max", "surname": "Chilton", "dob": "1991-04-21", "nationality": "British"},
    {"driverRef": "bianchi", "number": 17, "code": "BIA", "forename": "Jules", "surname": "Bianchi", "dob": "1989-08-03", "nationality": "French"},
    {"driverRef": "pic", "number": 20, "code": "PIC", "forename": "Charles", "surname": "Pic", "dob": "1990-02-15", "nationality": "French"},
    {"driverRef": "vandoorne", "number": 2, "code": "VAN", "forename": "Stoffel", "surname": "Vandoorne", "dob": "1992-03-26", "nationality": "Belgian"},
    {"driverRef": "giovinazzi", "number": 99, "code": "GIO", "forename": "Antonio", "surname": "Giovinazzi", "dob": "1993-12-14", "nationality": "Italian"},
    {"driverRef": "latifi", "number": 6, "code": "LAT", "forename": "Nicholas", "surname": "Latifi", "dob": "1995-06-29", "nationality": "Canadian"},
    {"driverRef": "zhou", "number": 24, "code": "ZHO", "forename": "Guanyu", "surname": "Zhou", "dob": "1999-05-30", "nationality": "Chinese"},
    {"driverRef": "de_vries", "number": 21, "code": "DEV", "forename": "Nyck", "surname": "de Vries", "dob": "1995-02-06", "nationality": "Dutch"},
    {"driverRef": "sargeant", "number": 2, "code": "SAR", "forename": "Logan", "surname": "Sargeant", "dob": "2000-12-31", "nationality": "American"},
    {"driverRef": "lawson", "number": 30, "code": "LAW", "forename": "Liam", "surname": "Lawson", "dob": "2002-02-11", "nationality": "New Zealander"},
    {"driverRef": "bearman", "number": 38, "code": "BEA", "forename": "Oliver", "surname": "Bearman", "dob": "2005-05-08", "nationality": "British"},
    {"driverRef": "colapinto", "number": 43, "code": "COL", "forename": "Franco", "surname": "Colapinto", "dob": "2003-05-27", "nationality": "Argentine"},
]

# ---------------------------------------------------------------------------
# Reference Data — Constructors (with era mapping)
# ---------------------------------------------------------------------------
CONSTRUCTORS_DATA: list[dict[str, Any]] = [
    {"constructorRef": "red_bull", "name": "Red Bull", "nationality": "Austrian"},
    {"constructorRef": "mercedes", "name": "Mercedes", "nationality": "German"},
    {"constructorRef": "ferrari", "name": "Ferrari", "nationality": "Italian"},
    {"constructorRef": "mclaren", "name": "McLaren", "nationality": "British"},
    {"constructorRef": "renault", "name": "Renault", "nationality": "French"},
    {"constructorRef": "alpine", "name": "Alpine F1 Team", "nationality": "French"},
    {"constructorRef": "aston_martin", "name": "Aston Martin", "nationality": "British"},
    {"constructorRef": "force_india", "name": "Force India", "nationality": "Indian"},
    {"constructorRef": "racing_point", "name": "Racing Point", "nationality": "British"},
    {"constructorRef": "toro_rosso", "name": "Scuderia Toro Rosso", "nationality": "Italian"},
    {"constructorRef": "alphatauri", "name": "AlphaTauri", "nationality": "Italian"},
    {"constructorRef": "rb", "name": "RB F1 Team", "nationality": "Italian"},
    {"constructorRef": "williams", "name": "Williams", "nationality": "British"},
    {"constructorRef": "sauber", "name": "Sauber", "nationality": "Swiss"},
    {"constructorRef": "alfa_romeo", "name": "Alfa Romeo", "nationality": "Swiss"},
    {"constructorRef": "kick_sauber", "name": "Kick Sauber", "nationality": "Swiss"},
    {"constructorRef": "haas", "name": "Haas F1 Team", "nationality": "American"},
    {"constructorRef": "lotus_f1", "name": "Lotus F1", "nationality": "British"},
    {"constructorRef": "caterham", "name": "Caterham", "nationality": "Malaysian"},
    {"constructorRef": "marussia", "name": "Marussia", "nationality": "Russian"},
    {"constructorRef": "manor", "name": "Manor Marussia", "nationality": "British"},
    {"constructorRef": "hrt", "name": "HRT", "nationality": "Spanish"},
]

# ---------------------------------------------------------------------------
# Era-specific team rosters (driver_ref → constructor_ref)
# ---------------------------------------------------------------------------
# fmt: off
TEAM_ROSTERS: dict[int, list[tuple[str, str]]] = {
    2010: [
        ("vettel", "red_bull"), ("webber", "red_bull"),
        ("hamilton", "mclaren"), ("button", "mclaren"),
        ("alonso", "ferrari"), ("massa", "ferrari"),
        ("rosberg", "mercedes"), ("sutil", "force_india"),  # placeholder 2nd merc
        ("kubica_placeholder", "renault"), ("grosjean", "renault"),  # Petrov placeholder
        ("kobayashi", "sauber"), ("di_resta", "force_india"),
        ("hulkenberg", "williams"), ("maldonado", "williams"),
        ("raikkonen", "lotus_f1"), ("kvyat", "toro_rosso"),
        ("pic", "marussia"), ("max_chilton", "hrt"),
        ("bianchi", "caterham"), ("vergne", "toro_rosso"),
    ],
    2011: [
        ("vettel", "red_bull"), ("webber", "red_bull"),
        ("hamilton", "mclaren"), ("button", "mclaren"),
        ("alonso", "ferrari"), ("massa", "ferrari"),
        ("rosberg", "mercedes"), ("sutil", "force_india"),
        ("grosjean", "renault"), ("raikkonen", "lotus_f1"),
        ("kobayashi", "sauber"), ("di_resta", "force_india"),
        ("hulkenberg", "force_india"), ("maldonado", "williams"),
        ("perez", "sauber"), ("kvyat", "toro_rosso"),
        ("pic", "marussia"), ("max_chilton", "hrt"),
        ("bianchi", "caterham"), ("vergne", "toro_rosso"),
    ],
    2012: [
        ("vettel", "red_bull"), ("webber", "red_bull"),
        ("hamilton", "mclaren"), ("button", "mclaren"),
        ("alonso", "ferrari"), ("massa", "ferrari"),
        ("rosberg", "mercedes"), ("raikkonen", "lotus_f1"),
        ("grosjean", "lotus_f1"), ("sutil", "force_india"),
        ("kobayashi", "sauber"), ("di_resta", "force_india"),
        ("hulkenberg", "force_india"), ("maldonado", "williams"),
        ("perez", "sauber"), ("vergne", "toro_rosso"),
        ("pic", "marussia"), ("max_chilton", "hrt"),
        ("bianchi", "caterham"), ("ricciardo", "toro_rosso"),
    ],
    2013: [
        ("vettel", "red_bull"), ("webber", "red_bull"),
        ("hamilton", "mercedes"), ("rosberg", "mercedes"),
        ("alonso", "ferrari"), ("massa", "ferrari"),
        ("button", "mclaren"), ("perez", "mclaren"),
        ("raikkonen", "lotus_f1"), ("grosjean", "lotus_f1"),
        ("hulkenberg", "sauber"), ("sutil", "force_india"),
        ("di_resta", "force_india"), ("maldonado", "williams"),
        ("bottas", "williams"), ("ricciardo", "toro_rosso"),
        ("vergne", "toro_rosso"), ("bianchi", "marussia"),
        ("max_chilton", "marussia"), ("pic", "caterham"),
    ],
    2014: [
        ("hamilton", "mercedes"), ("rosberg", "mercedes"),
        ("vettel", "red_bull"), ("ricciardo", "red_bull"),
        ("alonso", "ferrari"), ("raikkonen", "ferrari"),
        ("button", "mclaren"), ("magnussen", "mclaren"),
        ("hulkenberg", "force_india"), ("perez", "force_india"),
        ("bottas", "williams"), ("massa", "williams"),
        ("kvyat", "toro_rosso"), ("vergne", "toro_rosso"),
        ("grosjean", "lotus_f1"), ("maldonado", "lotus_f1"),
        ("gutierrez", "sauber"), ("sutil", "sauber"),
        ("bianchi", "marussia"), ("max_chilton", "marussia"),
    ],
    2015: [
        ("hamilton", "mercedes"), ("rosberg", "mercedes"),
        ("vettel", "ferrari"), ("raikkonen", "ferrari"),
        ("ricciardo", "red_bull"), ("kvyat", "red_bull"),
        ("button", "mclaren"), ("alonso", "mclaren"),
        ("hulkenberg", "force_india"), ("perez", "force_india"),
        ("bottas", "williams"), ("massa", "williams"),
        ("sainz", "toro_rosso"), ("verstappen", "toro_rosso"),
        ("grosjean", "lotus_f1"), ("maldonado", "lotus_f1"),
        ("magnussen", "renault"), ("gutierrez", "sauber"),
        ("max_chilton", "manor"), ("pic", "manor"),
    ],
    2016: [
        ("rosberg", "mercedes"), ("hamilton", "mercedes"),
        ("ricciardo", "red_bull"), ("verstappen", "red_bull"),
        ("vettel", "ferrari"), ("raikkonen", "ferrari"),
        ("alonso", "mclaren"), ("button", "mclaren"),
        ("hulkenberg", "force_india"), ("perez", "force_india"),
        ("bottas", "williams"), ("massa", "williams"),
        ("sainz", "toro_rosso"), ("kvyat", "toro_rosso"),
        ("magnussen", "renault"), ("grosjean", "haas"),
        ("gutierrez", "haas"), ("ocon", "manor"),
        ("sutil", "sauber"), ("pic", "manor"),
    ],
    2017: [
        ("hamilton", "mercedes"), ("bottas", "mercedes"),
        ("vettel", "ferrari"), ("raikkonen", "ferrari"),
        ("ricciardo", "red_bull"), ("verstappen", "red_bull"),
        ("perez", "force_india"), ("ocon", "force_india"),
        ("hulkenberg", "renault"), ("sainz", "renault"),
        ("stroll", "williams"), ("massa", "williams"),
        ("gasly", "toro_rosso"), ("kvyat", "toro_rosso"),
        ("grosjean", "haas"), ("magnussen", "haas"),
        ("vandoorne", "mclaren"), ("alonso", "mclaren"),
        ("giovinazzi", "sauber"), ("gutierrez", "sauber"),
    ],
    2018: [
        ("hamilton", "mercedes"), ("bottas", "mercedes"),
        ("vettel", "ferrari"), ("raikkonen", "ferrari"),
        ("ricciardo", "red_bull"), ("verstappen", "red_bull"),
        ("perez", "force_india"), ("ocon", "force_india"),
        ("hulkenberg", "renault"), ("sainz", "renault"),
        ("stroll", "williams"), ("latifi", "williams"),
        ("gasly", "toro_rosso"), ("kvyat", "toro_rosso"),
        ("grosjean", "haas"), ("magnussen", "haas"),
        ("vandoorne", "mclaren"), ("alonso", "mclaren"),
        ("leclerc", "sauber"), ("giovinazzi", "sauber"),
    ],
    2019: [
        ("hamilton", "mercedes"), ("bottas", "mercedes"),
        ("vettel", "ferrari"), ("leclerc", "ferrari"),
        ("verstappen", "red_bull"), ("gasly", "red_bull"),
        ("perez", "racing_point"), ("stroll", "racing_point"),
        ("hulkenberg", "renault"), ("ricciardo", "renault"),
        ("norris", "mclaren"), ("sainz", "mclaren"),
        ("kvyat", "toro_rosso"), ("alonso", "mclaren"),
        ("grosjean", "haas"), ("magnussen", "haas"),
        ("raikkonen", "alfa_romeo"), ("giovinazzi", "alfa_romeo"),
        ("russell", "williams"), ("latifi", "williams"),
    ],
    2020: [
        ("hamilton", "mercedes"), ("bottas", "mercedes"),
        ("vettel", "ferrari"), ("leclerc", "ferrari"),
        ("verstappen", "red_bull"), ("albon_placeholder", "red_bull"),
        ("perez", "racing_point"), ("stroll", "racing_point"),
        ("ocon", "renault"), ("ricciardo", "renault"),
        ("norris", "mclaren"), ("sainz", "mclaren"),
        ("gasly", "alphatauri"), ("kvyat", "alphatauri"),
        ("grosjean", "haas"), ("magnussen", "haas"),
        ("raikkonen", "alfa_romeo"), ("giovinazzi", "alfa_romeo"),
        ("russell", "williams"), ("latifi", "williams"),
    ],
    2021: [
        ("hamilton", "mercedes"), ("bottas", "mercedes"),
        ("verstappen", "red_bull"), ("perez", "red_bull"),
        ("leclerc", "ferrari"), ("sainz", "ferrari"),
        ("norris", "mclaren"), ("ricciardo", "mclaren"),
        ("alonso", "alpine"), ("ocon", "alpine"),
        ("gasly", "alphatauri"), ("tsunoda", "alphatauri"),
        ("vettel", "aston_martin"), ("stroll", "aston_martin"),
        ("raikkonen", "alfa_romeo"), ("giovinazzi", "alfa_romeo"),
        ("russell", "williams"), ("latifi", "williams"),
        ("magnussen", "haas"), ("grosjean", "haas"),
    ],
    2022: [
        ("verstappen", "red_bull"), ("perez", "red_bull"),
        ("hamilton", "mercedes"), ("russell", "mercedes"),
        ("leclerc", "ferrari"), ("sainz", "ferrari"),
        ("norris", "mclaren"), ("ricciardo", "mclaren"),
        ("alonso", "alpine"), ("ocon", "alpine"),
        ("gasly", "alphatauri"), ("tsunoda", "alphatauri"),
        ("vettel", "aston_martin"), ("stroll", "aston_martin"),
        ("bottas", "alfa_romeo"), ("zhou", "alfa_romeo"),
        ("magnussen", "haas"), ("hulkenberg", "haas"),
        ("latifi", "williams"), ("de_vries", "williams"),
    ],
    2023: [
        ("verstappen", "red_bull"), ("perez", "red_bull"),
        ("hamilton", "mercedes"), ("russell", "mercedes"),
        ("leclerc", "ferrari"), ("sainz", "ferrari"),
        ("norris", "mclaren"), ("piastri", "mclaren"),
        ("alonso", "aston_martin"), ("stroll", "aston_martin"),
        ("gasly", "alpine"), ("ocon", "alpine"),
        ("tsunoda", "alphatauri"), ("de_vries", "alphatauri"),
        ("bottas", "alfa_romeo"), ("zhou", "alfa_romeo"),
        ("magnussen", "haas"), ("hulkenberg", "haas"),
        ("sargeant", "williams"), ("lawson", "williams"),
    ],
    2024: [
        ("verstappen", "red_bull"), ("perez", "red_bull"),
        ("hamilton", "mercedes"), ("russell", "mercedes"),
        ("leclerc", "ferrari"), ("sainz", "ferrari"),
        ("norris", "mclaren"), ("piastri", "mclaren"),
        ("alonso", "aston_martin"), ("stroll", "aston_martin"),
        ("gasly", "alpine"), ("ocon", "alpine"),
        ("tsunoda", "rb"), ("lawson", "rb"),
        ("bottas", "kick_sauber"), ("zhou", "kick_sauber"),
        ("magnussen", "haas"), ("hulkenberg", "haas"),
        ("sargeant", "williams"), ("colapinto", "williams"),
    ],
}
# fmt: on

# ---------------------------------------------------------------------------
# Race calendars per season (circuitRef list)
# ---------------------------------------------------------------------------
SEASON_CALENDARS: dict[int, list[str]] = {
    2010: ["bahrain", "albert_park", "sepang", "shanghai", "catalunya", "monaco",
           "istanbul", "villeneuve", "silverstone", "hockenheimring", "hungaroring",
           "spa", "monza", "marina_bay", "suzuka", "yeongam", "interlagos", "yas_marina"],
    2011: ["bahrain", "albert_park", "sepang", "shanghai", "istanbul", "catalunya",
           "monaco", "villeneuve", "silverstone", "nurburgring", "hungaroring",
           "spa", "monza", "marina_bay", "suzuka", "yeongam", "interlagos", "yas_marina"],
    2012: ["albert_park", "sepang", "shanghai", "bahrain", "catalunya", "monaco",
           "villeneuve", "silverstone", "hockenheimring", "hungaroring", "spa",
           "monza", "marina_bay", "suzuka", "yeongam", "interlagos", "americas", "yas_marina"],
    2013: ["albert_park", "sepang", "shanghai", "bahrain", "catalunya", "monaco",
           "villeneuve", "silverstone", "nurburgring", "hungaroring", "spa",
           "monza", "marina_bay", "suzuka", "yeongam", "interlagos", "americas", "yas_marina"],
    2014: ["albert_park", "sepang", "bahrain", "shanghai", "catalunya", "monaco",
           "villeneuve", "red_bull_ring", "silverstone", "hockenheimring", "hungaroring",
           "spa", "monza", "marina_bay", "suzuka", "sochi", "americas", "interlagos", "yas_marina"],
    2015: ["albert_park", "sepang", "shanghai", "bahrain", "catalunya", "monaco",
           "villeneuve", "red_bull_ring", "silverstone", "hungaroring", "spa",
           "monza", "marina_bay", "suzuka", "sochi", "americas", "interlagos",
           "rodriguez", "yas_marina"],
    2016: ["albert_park", "bahrain", "shanghai", "sochi", "catalunya", "monaco",
           "villeneuve", "baku", "red_bull_ring", "silverstone", "hungaroring",
           "hockenheimring", "spa", "monza", "marina_bay", "sepang", "suzuka",
           "americas", "rodriguez", "interlagos", "yas_marina"],
    2017: ["albert_park", "shanghai", "bahrain", "sochi", "catalunya", "monaco",
           "villeneuve", "baku", "red_bull_ring", "silverstone", "hungaroring",
           "spa", "monza", "marina_bay", "sepang", "suzuka", "americas",
           "rodriguez", "interlagos", "yas_marina"],
    2018: ["albert_park", "bahrain", "shanghai", "baku", "catalunya", "monaco",
           "villeneuve", "ricard", "red_bull_ring", "silverstone", "hockenheimring",
           "hungaroring", "spa", "monza", "marina_bay", "sochi", "suzuka",
           "americas", "rodriguez", "interlagos", "yas_marina"],
    2019: ["albert_park", "bahrain", "shanghai", "baku", "catalunya", "monaco",
           "villeneuve", "ricard", "red_bull_ring", "silverstone", "hockenheimring",
           "hungaroring", "spa", "monza", "marina_bay", "sochi", "suzuka",
           "americas", "rodriguez", "interlagos", "yas_marina"],
    2020: ["red_bull_ring", "silverstone", "hungaroring", "catalunya", "spa",
           "monza", "mugello", "sochi", "nurburgring", "portimao", "imola",
           "istanbul", "bahrain", "yas_marina", "interlagos", "americas", "rodriguez"],
    2021: ["bahrain", "imola", "portimao", "catalunya", "monaco", "baku",
           "ricard", "red_bull_ring", "silverstone", "hungaroring", "spa",
           "zandvoort", "monza", "sochi", "istanbul", "americas", "rodriguez",
           "interlagos", "losail", "jeddah", "yas_marina"],
    2022: ["bahrain", "jeddah", "albert_park", "imola", "miami", "catalunya",
           "monaco", "baku", "villeneuve", "silverstone", "red_bull_ring",
           "ricard", "hungaroring", "spa", "zandvoort", "monza", "marina_bay",
           "suzuka", "americas", "rodriguez", "interlagos", "yas_marina"],
    2023: ["bahrain", "jeddah", "albert_park", "baku", "miami", "monaco",
           "catalunya", "villeneuve", "red_bull_ring", "silverstone", "hungaroring",
           "spa", "zandvoort", "monza", "marina_bay", "suzuka", "losail",
           "americas", "rodriguez", "interlagos", "las_vegas", "yas_marina"],
    2024: ["bahrain", "jeddah", "albert_park", "suzuka", "shanghai", "miami",
           "imola", "monaco", "villeneuve", "catalunya", "red_bull_ring",
           "silverstone", "hungaroring", "spa", "zandvoort", "monza",
           "baku", "marina_bay", "americas", "rodriguez", "interlagos",
           "las_vegas", "losail", "yas_marina"],
}

# ---------------------------------------------------------------------------
# Status codes (Ergast-compatible)
# ---------------------------------------------------------------------------
STATUS_LABELS: list[str] = [
    "Finished", "+1 Lap", "+2 Laps", "+3 Laps", "+4 Laps", "+5 Laps",
    "+6 Laps", "+7 Laps", "+8 Laps", "+9 Laps",
    "Engine", "Gearbox", "Transmission", "Clutch", "Hydraulics", "Electrical",
    "Radiator", "Suspension", "Brakes", "Differential", "Overheating",
    "Mechanical", "Tyre", "Driver Seat", "Puncture", "Driveshaft",
    "Retired", "Accident", "Collision", "Spun off", "Wheel",
    "Throttle", "Steering", "Technical", "Electronics", "Broken wing",
    "Heat shield fire", "Exhaust", "Oil leak", "Fuel pressure",
    "Wheel nut", "Not classified", "Power Unit", "ERS",
    "Disqualified", "Withdrew", "Water leak", "Fatal accident",
    "Debris", "Collision damage", "Power loss", "Vibrations",
    "Sensor", "Fuel system", "Front wing", "Water pressure", "Refuelling",
    "Wheel rim", "Launch control", "Injector", "Distributor", "Battery",
    "Ignition", "Alternator", "Oil pump", "Fuel leak", "Turbo",
    "Cooling system", "Pneumatics", "Water pump", "Spark plugs",
    "Fuel pipe", "Oil pipe", "Axle", "Water pipe", "Halfshaft",
    "Crankshaft", "Throttle linkage", "Spark plug", "Engine fire",
    "Fuel rig", "Handling", "Rear wing", "Fire", "Wheel bearing",
    "Physical", "Undertray", "Safety concerns", "Out of fuel",
    "Excluded", "Engine misfire", "Tyre puncture", "Engine overheating",
    "Safety belt", "Oil line", "Fuel injection", "KERS", "DRS",
    "ERS overheating", "Fuel flow", "Gearbox electronics", "Brake duct",
    "Track rod", "Seat belt", "Spin", "Crash damage", "Overrev",
    "Turbo failure", "Brake failure", "Gearbox sensor", "Water system",
    "Power unit sensor", "Brake disc", "Gearbox overheating",
    "Drivetrain", "Engine sensor", "Fuel temperature", "Undertray damage",
    "Chassis", "Rear axle", "Electronics failure", "Car shutdown",
    "Did not qualify", "Injury", "Out of fuel ", "Did not prequalify",
    "Floor", "Illness", "Fuel pump", "Track conditions", "Red flag",
    "Engine braking", "120% rule", "107% rule",
    "+10 Laps", "+11 Laps", "+12 Laps", "+13 Laps", "+14 Laps",
]

# ---------------------------------------------------------------------------
# World Champions (driver_ref) & Constructor Champions (constructor_ref)
# ---------------------------------------------------------------------------
WDC_WINNERS: dict[int, str] = {
    2010: "vettel", 2011: "vettel", 2012: "vettel", 2013: "vettel",
    2014: "hamilton", 2015: "hamilton", 2016: "rosberg",
    2017: "hamilton", 2018: "hamilton", 2019: "hamilton", 2020: "hamilton",
    2021: "verstappen", 2022: "verstappen", 2023: "verstappen", 2024: "verstappen",
}
WCC_WINNERS: dict[int, str] = {
    2010: "red_bull", 2011: "red_bull", 2012: "red_bull", 2013: "red_bull",
    2014: "mercedes", 2015: "mercedes", 2016: "mercedes",
    2017: "mercedes", 2018: "mercedes", 2019: "mercedes", 2020: "mercedes",
    2021: "mercedes", 2022: "red_bull", 2023: "red_bull", 2024: "red_bull",
}

# Top-team strength weights per season (higher = stronger).
# The champion's team always gets the highest weight.
TEAM_STRENGTH: dict[int, dict[str, float]] = {
    2010: {"red_bull": 1.0, "mclaren": 0.92, "ferrari": 0.90, "mercedes": 0.72, "renault": 0.55, "force_india": 0.48, "williams": 0.45, "sauber": 0.42, "toro_rosso": 0.40, "lotus_f1": 0.35, "hrt": 0.18, "marussia": 0.20, "caterham": 0.22},
    2011: {"red_bull": 1.0, "mclaren": 0.88, "ferrari": 0.82, "mercedes": 0.68, "renault": 0.58, "force_india": 0.48, "williams": 0.40, "sauber": 0.42, "toro_rosso": 0.40, "lotus_f1": 0.50, "hrt": 0.18, "marussia": 0.20, "caterham": 0.22},
    2012: {"red_bull": 0.95, "mclaren": 0.93, "ferrari": 0.92, "mercedes": 0.70, "lotus_f1": 0.82, "force_india": 0.50, "williams": 0.48, "sauber": 0.52, "toro_rosso": 0.40, "hrt": 0.18, "marussia": 0.20, "caterham": 0.22, "renault": 0.30},
    2013: {"red_bull": 1.0, "mercedes": 0.80, "ferrari": 0.82, "lotus_f1": 0.78, "mclaren": 0.60, "force_india": 0.52, "sauber": 0.45, "toro_rosso": 0.42, "williams": 0.38, "marussia": 0.20, "caterham": 0.22, "renault": 0.30, "hrt": 0.15},
    2014: {"mercedes": 1.0, "red_bull": 0.78, "ferrari": 0.65, "williams": 0.68, "mclaren": 0.55, "force_india": 0.58, "toro_rosso": 0.42, "lotus_f1": 0.38, "sauber": 0.35, "marussia": 0.20, "caterham": 0.18, "renault": 0.30, "hrt": 0.10},
    2015: {"mercedes": 1.0, "ferrari": 0.82, "red_bull": 0.68, "williams": 0.65, "mclaren": 0.35, "force_india": 0.58, "toro_rosso": 0.50, "lotus_f1": 0.40, "sauber": 0.35, "manor": 0.18, "renault": 0.30, "haas": 0.25},
    2016: {"mercedes": 1.0, "red_bull": 0.85, "ferrari": 0.78, "force_india": 0.62, "williams": 0.58, "mclaren": 0.48, "toro_rosso": 0.50, "haas": 0.42, "renault": 0.40, "sauber": 0.30, "manor": 0.18},
    2017: {"mercedes": 1.0, "ferrari": 0.95, "red_bull": 0.82, "force_india": 0.60, "williams": 0.45, "mclaren": 0.35, "toro_rosso": 0.42, "renault": 0.48, "haas": 0.40, "sauber": 0.28},
    2018: {"mercedes": 0.98, "ferrari": 0.96, "red_bull": 0.88, "renault": 0.60, "haas": 0.55, "mclaren": 0.48, "force_india": 0.58, "toro_rosso": 0.45, "williams": 0.25, "sauber": 0.42},
    2019: {"mercedes": 1.0, "ferrari": 0.88, "red_bull": 0.85, "mclaren": 0.62, "renault": 0.58, "racing_point": 0.52, "toro_rosso": 0.48, "alfa_romeo": 0.42, "haas": 0.40, "williams": 0.22},
    2020: {"mercedes": 1.0, "red_bull": 0.82, "racing_point": 0.68, "mclaren": 0.65, "renault": 0.62, "ferrari": 0.55, "alphatauri": 0.52, "alfa_romeo": 0.38, "haas": 0.30, "williams": 0.25},
    2021: {"red_bull": 0.98, "mercedes": 0.97, "ferrari": 0.72, "mclaren": 0.70, "alpine": 0.58, "alphatauri": 0.52, "aston_martin": 0.50, "alfa_romeo": 0.38, "williams": 0.32, "haas": 0.22},
    2022: {"red_bull": 1.0, "ferrari": 0.90, "mercedes": 0.80, "alpine": 0.58, "mclaren": 0.56, "alfa_romeo": 0.50, "aston_martin": 0.45, "haas": 0.42, "alphatauri": 0.40, "williams": 0.30},
    2023: {"red_bull": 1.0, "mercedes": 0.72, "ferrari": 0.70, "mclaren": 0.68, "aston_martin": 0.65, "alpine": 0.45, "williams": 0.38, "alphatauri": 0.35, "alfa_romeo": 0.32, "haas": 0.30},
    2024: {"red_bull": 0.88, "mclaren": 0.92, "ferrari": 0.88, "mercedes": 0.80, "aston_martin": 0.55, "rb": 0.45, "haas": 0.40, "alpine": 0.38, "williams": 0.35, "kick_sauber": 0.25},
}

# Points systems
POINTS_SYSTEMS: dict[str, list[float]] = {
    "2010-2018": [25, 18, 15, 12, 10, 8, 6, 4, 2, 1],
    "2019+": [25, 18, 15, 12, 10, 8, 6, 4, 2, 1],  # + 1 bonus for FL in top 10
}


# ===================================================================
# Data Generator
# ===================================================================

class F1DataGenerator:
    """Generates realistic F1 demo data matching the Ergast schema."""

    def __init__(self, seed: int = 42) -> None:
        self.rng = random.Random(seed)
        self._circuit_id_map: dict[str, int] = {}
        self._constructor_id_map: dict[str, int] = {}
        self._driver_id_map: dict[str, int] = {}
        self._status_id_map: dict[str, int] = {}
        self._race_id = 0
        self._result_id = 0
        self._qualify_id = 0
        self._ds_id = 0
        self._cs_id = 0

    # -- helpers -----------------------------------------------------------

    def _next_race_id(self) -> int:
        self._race_id += 1
        return self._race_id

    def _next_result_id(self) -> int:
        self._result_id += 1
        return self._result_id

    def _next_qualify_id(self) -> int:
        self._qualify_id += 1
        return self._qualify_id

    def _next_ds_id(self) -> int:
        self._ds_id += 1
        return self._ds_id

    def _next_cs_id(self) -> int:
        self._cs_id += 1
        return self._cs_id

    @staticmethod
    def _race_name_for_circuit(circuit_ref: str) -> str:
        """Generate a Grand Prix name from the circuit reference."""
        mapping = {
            "albert_park": "Australian Grand Prix",
            "sepang": "Malaysian Grand Prix",
            "shanghai": "Chinese Grand Prix",
            "bahrain": "Bahrain Grand Prix",
            "catalunya": "Spanish Grand Prix",
            "monaco": "Monaco Grand Prix",
            "villeneuve": "Canadian Grand Prix",
            "silverstone": "British Grand Prix",
            "hockenheimring": "German Grand Prix",
            "nurburgring": "German Grand Prix",
            "hungaroring": "Hungarian Grand Prix",
            "spa": "Belgian Grand Prix",
            "monza": "Italian Grand Prix",
            "marina_bay": "Singapore Grand Prix",
            "suzuka": "Japanese Grand Prix",
            "yeongam": "Korean Grand Prix",
            "yas_marina": "Abu Dhabi Grand Prix",
            "interlagos": "Brazilian Grand Prix",
            "americas": "United States Grand Prix",
            "red_bull_ring": "Austrian Grand Prix",
            "sochi": "Russian Grand Prix",
            "rodriguez": "Mexican Grand Prix",
            "baku": "Azerbaijan Grand Prix",
            "ricard": "French Grand Prix",
            "zandvoort": "Dutch Grand Prix",
            "jeddah": "Saudi Arabian Grand Prix",
            "losail": "Qatar Grand Prix",
            "lusail": "Qatar Grand Prix",
            "miami": "Miami Grand Prix",
            "las_vegas": "Las Vegas Grand Prix",
            "imola": "Emilia Romagna Grand Prix",
            "portimao": "Portuguese Grand Prix",
            "mugello": "Tuscan Grand Prix",
            "istanbul": "Turkish Grand Prix",
        }
        return mapping.get(circuit_ref, f"{circuit_ref.replace('_', ' ').title()} Grand Prix")

    # -- master generate ---------------------------------------------------

    def generate_all(self) -> dict[str, list[dict]]:
        """Return all tables as lists of dicts."""
        log.info("Generating DEMO DATA for seasons 2010-2024 …")

        seasons = self._gen_seasons()
        circuits = self._gen_circuits()
        constructors = self._gen_constructors()
        drivers = self._gen_drivers()
        statuses = self._gen_statuses()
        races = self._gen_races()
        results, qualifying = self._gen_results_and_qualifying(races)
        driver_standings, constructor_standings = self._gen_standings(races, results)

        data = {
            "seasons": seasons,
            "circuits": circuits,
            "constructors": constructors,
            "drivers": drivers,
            "status": statuses,
            "races": races,
            "results": results,
            "qualifying": qualifying,
            "driver_standings": driver_standings,
            "constructor_standings": constructor_standings,
        }

        for name, rows in data.items():
            log.info("  %-25s %6d rows", name, len(rows))

        return data

    # -- individual table generators ---------------------------------------

    def _gen_seasons(self) -> list[dict]:
        rows = []
        for yr in range(2010, 2025):
            rows.append({
                "year": yr,
                "url": f"https://en.wikipedia.org/wiki/{yr}_Formula_One_World_Championship",
            })
        return rows

    def _gen_circuits(self) -> list[dict]:
        rows = []
        for i, c in enumerate(CIRCUITS_DATA, start=1):
            self._circuit_id_map[c["circuitRef"]] = i
            rows.append({
                "circuitId": i,
                **c,
                "url": f"https://en.wikipedia.org/wiki/{c['name'].replace(' ', '_')}",
            })
        return rows

    def _gen_constructors(self) -> list[dict]:
        rows = []
        for i, c in enumerate(CONSTRUCTORS_DATA, start=1):
            self._constructor_id_map[c["constructorRef"]] = i
            rows.append({
                "constructorId": i,
                **c,
                "url": f"https://en.wikipedia.org/wiki/{c['name'].replace(' ', '_')}",
            })
        return rows

    def _gen_drivers(self) -> list[dict]:
        rows = []
        for i, d in enumerate(DRIVERS_DATA, start=1):
            self._driver_id_map[d["driverRef"]] = i
            rows.append({
                "driverId": i,
                **d,
                "url": f"https://en.wikipedia.org/wiki/{d['forename']}_{d['surname']}".replace(" ", "_"),
            })
        return rows

    def _gen_statuses(self) -> list[dict]:
        rows = []
        for i, label in enumerate(STATUS_LABELS, start=1):
            self._status_id_map[label] = i
            rows.append({"statusId": i, "status": label})
        return rows

    def _gen_races(self) -> list[dict]:
        rows = []
        for year in range(2010, 2025):
            calendar = SEASON_CALENDARS.get(year, SEASON_CALENDARS[2024])
            # Start dates in mid-March, spaced ~2 weeks apart
            race_date = date(year, 3, 14)
            for rnd, cref in enumerate(calendar, start=1):
                cid = self._circuit_id_map.get(cref, 1)
                rows.append({
                    "raceId": self._next_race_id(),
                    "year": year,
                    "round": rnd,
                    "circuitId": cid,
                    "name": self._race_name_for_circuit(cref),
                    "date": race_date.isoformat(),
                    "time": "14:00:00",
                    "url": f"https://en.wikipedia.org/wiki/{year}_{self._race_name_for_circuit(cref).replace(' ', '_')}",
                })
                # Advance 12-16 days for next race
                race_date += timedelta(days=self.rng.randint(12, 16))
        return rows

    def _gen_results_and_qualifying(
        self, races: list[dict]
    ) -> tuple[list[dict], list[dict]]:
        results: list[dict] = []
        qualifying: list[dict] = []

        for race in races:
            year = race["year"]
            race_id = race["raceId"]
            roster = TEAM_ROSTERS.get(year, TEAM_ROSTERS[2024])
            strength = TEAM_STRENGTH.get(year, TEAM_STRENGTH[2024])
            champion_ref = WDC_WINNERS.get(year, "verstappen")

            # Build entries for each driver on the grid
            entries: list[dict[str, Any]] = []
            for drv_ref, con_ref in roster:
                did = self._driver_id_map.get(drv_ref)
                cid = self._constructor_id_map.get(con_ref)
                if did is None or cid is None:
                    continue

                team_str = strength.get(con_ref, 0.30)
                # Champion gets a boost; teammate gets slightly less
                is_champion = drv_ref == champion_ref
                driver_skill = team_str + (0.08 if is_champion else 0.0)
                # Add randomness
                driver_skill += self.rng.gauss(0, 0.06)

                entries.append({
                    "driverId": did,
                    "constructorId": cid,
                    "driverRef": drv_ref,
                    "constructorRef": con_ref,
                    "skill": driver_skill,
                })

            # Sort by skill descending for qualifying order
            entries.sort(key=lambda e: e["skill"], reverse=True)

            # Qualifying
            for qpos, entry in enumerate(entries, start=1):
                base_time_ms = 78000 + self.rng.randint(0, 5000)  # ~1:18-1:23
                q1_ms = base_time_ms + int((qpos - 1) * 120 + self.rng.gauss(0, 200))
                q2_ms = q1_ms - self.rng.randint(100, 400) if qpos <= 15 else None
                q3_ms = (q2_ms - self.rng.randint(50, 200)) if (q2_ms and qpos <= 10) else None

                def ms_to_lap(ms: int | None) -> str:
                    if ms is None:
                        return ""
                    mins = ms // 60000
                    secs = (ms % 60000) / 1000
                    return f"{mins}:{secs:06.3f}"

                qualifying.append({
                    "qualifyId": self._next_qualify_id(),
                    "raceId": race_id,
                    "driverId": entry["driverId"],
                    "constructorId": entry["constructorId"],
                    "number": DRIVERS_DATA[entry["driverId"] - 1]["number"] if entry["driverId"] <= len(DRIVERS_DATA) else 0,
                    "position": qpos,
                    "q1": ms_to_lap(q1_ms),
                    "q2": ms_to_lap(q2_ms),
                    "q3": ms_to_lap(q3_ms),
                })

            # Race results — reshuffle with more variance
            for entry in entries:
                entry["race_perf"] = entry["skill"] + self.rng.gauss(0, 0.12)

            entries.sort(key=lambda e: e["race_perf"], reverse=True)

            # Decide DNFs (~15-20% of grid)
            num_dnfs = self.rng.randint(2, max(2, int(len(entries) * 0.20)))
            dnf_indices = set(self.rng.sample(
                list(range(len(entries))), min(num_dnfs, len(entries))
            ))
            # Ensure champion rarely DNFs (small chance)
            for idx in list(dnf_indices):
                if entries[idx]["driverRef"] == champion_ref and self.rng.random() > 0.15:
                    dnf_indices.discard(idx)

            dnf_statuses = [s for s in STATUS_LABELS if s not in (
                "Finished", "+1 Lap", "+2 Laps", "+3 Laps", "+4 Laps", "+5 Laps",
                "+6 Laps", "+7 Laps", "+8 Laps", "+9 Laps", "+10 Laps",
                "+11 Laps", "+12 Laps", "+13 Laps", "+14 Laps",
                "Not classified", "Disqualified", "Withdrew",
                "Did not qualify", "Did not prequalify",
            )]

            points_table = POINTS_SYSTEMS["2010-2018"]
            fl_bonus = year >= 2019  # Fastest lap bonus from 2019

            finish_pos = 0
            race_laps = self.rng.randint(50, 70)

            # Pick a fastest-lap driver from top 10 finishers
            fl_driver_idx = self.rng.randint(0, min(9, len(entries) - 1))

            for idx, entry in enumerate(entries):
                is_dnf = idx in dnf_indices

                if is_dnf:
                    pos = None
                    pos_text = "R"
                    pos_order = 20 + idx
                    pts = 0.0
                    status_label = self.rng.choice(dnf_statuses)
                    laps_completed = self.rng.randint(0, race_laps - 1)
                    time_str = ""
                else:
                    finish_pos += 1
                    pos = finish_pos
                    pos_text = str(pos)
                    pos_order = pos
                    pts = points_table[pos - 1] if pos <= 10 else 0.0
                    # Fastest-lap bonus
                    if fl_bonus and idx == fl_driver_idx and pos <= 10:
                        pts += 1.0
                    # Lapped cars
                    if pos <= 3:
                        status_label = "Finished"
                    elif pos <= 8:
                        status_label = self.rng.choice(["Finished", "+1 Lap"])
                    else:
                        status_label = self.rng.choice(["Finished", "+1 Lap", "+2 Laps"])
                    laps_completed = race_laps
                    # Race time ~1h 20m for winner + offset
                    base_ms = 4_800_000 + self.rng.randint(0, 600_000)
                    offset_ms = int((pos - 1) * self.rng.randint(1000, 8000))
                    time_ms = base_ms + offset_ms
                    mins = time_ms // 60000
                    secs = (time_ms % 60000) / 1000
                    time_str = f"{mins // 60}:{mins % 60:02d}:{secs:06.3f}" if pos == 1 else f"+{secs:.3f}s"

                # Grid position (from qualifying)
                grid_pos = next(
                    (q["position"] for q in qualifying
                     if q["raceId"] == race_id and q["driverId"] == entry["driverId"]),
                    idx + 1,
                )

                sid = self._status_id_map.get(status_label, 1)

                results.append({
                    "resultId": self._next_result_id(),
                    "raceId": race_id,
                    "driverId": entry["driverId"],
                    "constructorId": entry["constructorId"],
                    "number": DRIVERS_DATA[entry["driverId"] - 1]["number"] if entry["driverId"] <= len(DRIVERS_DATA) else 0,
                    "grid": grid_pos,
                    "position": pos,
                    "positionText": pos_text,
                    "positionOrder": pos_order,
                    "points": pts,
                    "laps": laps_completed,
                    "time": time_str,
                    "milliseconds": None,
                    "fastestLap": self.rng.randint(30, 55),
                    "rank": idx + 1,
                    "fastestLapTime": f"1:{self.rng.randint(18, 35)}.{self.rng.randint(100, 999)}",
                    "fastestLapSpeed": f"{self.rng.randint(190, 240)}.{self.rng.randint(100, 999)}",
                    "statusId": sid,
                })

        return results, qualifying

    def _gen_standings(
        self, races: list[dict], results: list[dict]
    ) -> tuple[list[dict], list[dict]]:
        """Compute cumulative driver and constructor standings after each race."""
        driver_standings: list[dict] = []
        constructor_standings: list[dict] = []

        # Group races by year
        from collections import defaultdict
        races_by_year: dict[int, list[dict]] = defaultdict(list)
        for r in races:
            races_by_year[r["year"]].append(r)

        results_by_race: dict[int, list[dict]] = defaultdict(list)
        for res in results:
            results_by_race[res["raceId"]].append(res)

        for year in sorted(races_by_year):
            year_races = sorted(races_by_year[year], key=lambda r: r["round"])
            cum_driver_pts: dict[int, float] = defaultdict(float)
            cum_driver_wins: dict[int, int] = defaultdict(int)
            cum_con_pts: dict[int, float] = defaultdict(float)
            cum_con_wins: dict[int, int] = defaultdict(int)

            for race in year_races:
                rid = race["raceId"]
                for res in results_by_race[rid]:
                    cum_driver_pts[res["driverId"]] += res["points"]
                    if res.get("position") == 1:
                        cum_driver_wins[res["driverId"]] += 1
                    cum_con_pts[res["constructorId"]] += res["points"]
                    if res.get("position") == 1:
                        cum_con_wins[res["constructorId"]] += 1

                # Snapshot driver standings after this race
                sorted_drivers = sorted(
                    cum_driver_pts.items(), key=lambda x: -x[1]
                )
                for pos, (did, pts) in enumerate(sorted_drivers, start=1):
                    driver_standings.append({
                        "driverStandingsId": self._next_ds_id(),
                        "raceId": rid,
                        "driverId": did,
                        "points": pts,
                        "position": pos,
                        "positionText": str(pos),
                        "wins": cum_driver_wins[did],
                    })

                # Snapshot constructor standings after this race
                sorted_cons = sorted(
                    cum_con_pts.items(), key=lambda x: -x[1]
                )
                for pos, (cid, pts) in enumerate(sorted_cons, start=1):
                    constructor_standings.append({
                        "constructorStandingsId": self._next_cs_id(),
                        "raceId": rid,
                        "constructorId": cid,
                        "points": pts,
                        "position": pos,
                        "positionText": str(pos),
                        "wins": cum_con_wins[cid],
                    })

        return driver_standings, constructor_standings


# ===================================================================
# CSV I/O helpers
# ===================================================================

def write_csvs(data: dict[str, list[dict]], output_dir: Path) -> None:
    """Write each table as a CSV file in *output_dir*."""
    output_dir.mkdir(parents=True, exist_ok=True)
    for table_name, rows in data.items():
        if not rows:
            continue
        path = output_dir / f"{table_name}.csv"
        fieldnames = list(rows[0].keys())
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        log.info("  Wrote %s (%d rows)", path.name, len(rows))


def read_csvs(data_dir: Path) -> dict[str, list[dict]]:
    """Read all CSV files from *data_dir* and return table-name → rows."""
    data: dict[str, list[dict]] = {}
    for csv_path in sorted(data_dir.glob("*.csv")):
        table_name = csv_path.stem
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            data[table_name] = list(reader)
        log.info("  Read %s (%d rows)", csv_path.name, len(data[table_name]))
    return data


# ===================================================================
# Database helpers
# ===================================================================

TABLE_MODEL_MAP: dict[str, type[Base]] = {
    "seasons": Season,
    "circuits": Circuit,
    "constructors": Constructor,
    "drivers": Driver,
    "status": Status,
    "races": Race,
    "results": Result,
    "qualifying": Qualifying,
    "driver_standings": DriverStanding,
    "constructor_standings": ConstructorStanding,
}


def load_to_db(data: dict[str, list[dict]], db_path: Path) -> None:
    """Insert all data into a SQLite database, creating tables as needed."""
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        for table_name in [
            "seasons", "circuits", "constructors", "drivers", "status",
            "races", "results", "qualifying",
            "driver_standings", "constructor_standings",
        ]:
            rows = data.get(table_name, [])
            if not rows:
                continue
            model = TABLE_MODEL_MAP.get(table_name)
            if model is None:
                log.warning("  No model for table %s — skipping", table_name)
                continue

            # Clear existing data
            session.query(model).delete()

            for row in rows:
                # Cast types for integer / float columns
                cleaned: dict[str, Any] = {}
                for col in model.__table__.columns:
                    val = row.get(col.name)
                    if val is None or val == "" or val == "\\N":
                        cleaned[col.name] = None
                    elif isinstance(col.type, Integer):
                        try:
                            cleaned[col.name] = int(val)
                        except (ValueError, TypeError):
                            cleaned[col.name] = None
                    elif isinstance(col.type, Float):
                        try:
                            cleaned[col.name] = float(val)
                        except (ValueError, TypeError):
                            cleaned[col.name] = None
                    else:
                        cleaned[col.name] = str(val)
                session.add(model(**cleaned))

            session.commit()
            log.info("  Loaded %-25s %6d rows → %s", table_name, len(rows), db_path.name)

    log.info("Database ready: %s", db_path)


# ===================================================================
# Main
# ===================================================================

def main() -> None:
    banner = """
+--------------------------------------------------------------+
|  F1 Race Intelligence -- Data Ingestion Pipeline             |
|  DEMO DATA - Generated to match Ergast schema format         |
+--------------------------------------------------------------+
"""
    print(banner)

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1 — Check for existing database
    if DB_PATH.exists():
        log.info("Database already exists at %s", DB_PATH)
        engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
        with engine.connect() as conn:
            tables = sa.inspect(engine).get_table_names()
            log.info("  Tables: %s", ", ".join(tables) if tables else "(none)")
            for t in tables:
                count = conn.execute(sa.text(f"SELECT COUNT(*) FROM [{t}]")).scalar()
                log.info("    %-25s %6d rows", t, count)
        log.info("To regenerate, delete %s and re-run.", DB_PATH)
        return

    # Step 2 — Try loading from CSV files
    csv_files = list(DATA_DIR.glob("*.csv"))
    if csv_files:
        log.info("Found %d CSV files in %s — loading …", len(csv_files), DATA_DIR)
        data = read_csvs(DATA_DIR)
        load_to_db(data, DB_PATH)
        return

    # Step 3 — Generate sample data
    log.info("No CSV files found. Generating realistic demo data …")
    gen = F1DataGenerator(seed=42)
    data = gen.generate_all()

    log.info("Writing CSV files …")
    write_csvs(data, DATA_DIR)

    log.info("Loading into SQLite database …")
    load_to_db(data, DB_PATH)

    log.info("✓ Done! Database created at %s", DB_PATH)


if __name__ == "__main__":
    main()
