"""SQLAlchemy ORM models for F1 Race Intelligence Dashboard."""

from sqlalchemy import (
    Column, Integer, String, Float, Date, Time, ForeignKey, Index,
    PrimaryKeyConstraint,
)
from sqlalchemy.orm import relationship
from app.database import Base


class Season(Base):
    """F1 racing season."""
    __tablename__ = "seasons"

    year = Column(Integer, primary_key=True)
    url = Column(String(255), nullable=True)

    races = relationship("Race", back_populates="season", lazy="select")

    def __repr__(self):
        return f"<Season(year={self.year})>"


class Circuit(Base):
    """Racing circuit / track."""
    __tablename__ = "circuits"

    circuitId = Column(Integer, primary_key=True, autoincrement=True)
    circuitRef = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    country = Column(String(255), nullable=True, index=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    alt = Column(Float, nullable=True)
    url = Column(String(255), nullable=True)

    races = relationship("Race", back_populates="circuit", lazy="select")

    def __repr__(self):
        return f"<Circuit(circuitId={self.circuitId}, name='{self.name}')>"


class Constructor(Base):
    """Racing team / constructor."""
    __tablename__ = "constructors"

    constructorId = Column(Integer, primary_key=True, autoincrement=True)
    constructorRef = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    nationality = Column(String(255), nullable=True, index=True)
    url = Column(String(255), nullable=True)

    results = relationship("Result", back_populates="constructor", lazy="select")
    standings = relationship("ConstructorStanding", back_populates="constructor", lazy="select")
    qualifying_entries = relationship("Qualifying", back_populates="constructor", lazy="select")

    def __repr__(self):
        return f"<Constructor(constructorId={self.constructorId}, name='{self.name}')>"


class Driver(Base):
    """Racing driver."""
    __tablename__ = "drivers"

    driverId = Column(Integer, primary_key=True, autoincrement=True)
    driverRef = Column(String(255), unique=True, nullable=False, index=True)
    number = Column(Integer, nullable=True)
    code = Column(String(3), nullable=True, index=True)
    forename = Column(String(255), nullable=False)
    surname = Column(String(255), nullable=False)
    dob = Column(Date, nullable=True)
    nationality = Column(String(255), nullable=True, index=True)
    url = Column(String(255), nullable=True)

    results = relationship("Result", back_populates="driver", lazy="select")
    standings = relationship("DriverStanding", back_populates="driver", lazy="select")
    qualifying_entries = relationship("Qualifying", back_populates="driver", lazy="select")
    pit_stops = relationship("PitStop", back_populates="driver", lazy="select")
    lap_times = relationship("LapTime", back_populates="driver", lazy="select")

    def __repr__(self):
        return f"<Driver(driverId={self.driverId}, name='{self.forename} {self.surname}')>"


class Status(Base):
    """Race finish status (Finished, Accident, Engine failure, etc.)."""
    __tablename__ = "status"

    statusId = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(String(255), nullable=False)

    results = relationship("Result", back_populates="status_rel", lazy="select")

    def __repr__(self):
        return f"<Status(statusId={self.statusId}, status='{self.status}')>"


class Race(Base):
    """Individual race event within a season."""
    __tablename__ = "races"

    raceId = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer, ForeignKey("seasons.year"), nullable=False, index=True)
    round = Column(Integer, nullable=False)
    circuitId = Column(Integer, ForeignKey("circuits.circuitId"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    date = Column(Date, nullable=True)
    time = Column(String(50), nullable=True)
    url = Column(String(255), nullable=True)

    season = relationship("Season", back_populates="races", lazy="select")
    circuit = relationship("Circuit", back_populates="races", lazy="select")
    results = relationship("Result", back_populates="race", lazy="select")
    driver_standings = relationship("DriverStanding", back_populates="race", lazy="select")
    constructor_standings = relationship("ConstructorStanding", back_populates="race", lazy="select")
    qualifying_entries = relationship("Qualifying", back_populates="race", lazy="select")
    pit_stops = relationship("PitStop", back_populates="race", lazy="select")
    lap_times = relationship("LapTime", back_populates="race", lazy="select")

    __table_args__ = (
        Index("ix_races_year_round", "year", "round"),
    )

    def __repr__(self):
        return f"<Race(raceId={self.raceId}, name='{self.name}', year={self.year})>"


class Result(Base):
    """Race result for a driver in a specific race."""
    __tablename__ = "results"

    resultId = Column(Integer, primary_key=True, autoincrement=True)
    raceId = Column(Integer, ForeignKey("races.raceId"), nullable=False, index=True)
    driverId = Column(Integer, ForeignKey("drivers.driverId"), nullable=False, index=True)
    constructorId = Column(Integer, ForeignKey("constructors.constructorId"), nullable=False, index=True)
    number = Column(Integer, nullable=True)
    grid = Column(Integer, nullable=True)
    position = Column(Integer, nullable=True)
    positionText = Column(String(10), nullable=True)
    positionOrder = Column(Integer, nullable=True)
    points = Column(Float, nullable=True)
    laps = Column(Integer, nullable=True)
    time = Column(String(50), nullable=True)
    milliseconds = Column(Integer, nullable=True)
    fastestLap = Column(Integer, nullable=True)
    rank = Column(Integer, nullable=True)
    fastestLapTime = Column(String(20), nullable=True)
    fastestLapSpeed = Column(String(20), nullable=True)
    statusId = Column(Integer, ForeignKey("status.statusId"), nullable=False, index=True)

    race = relationship("Race", back_populates="results", lazy="select")
    driver = relationship("Driver", back_populates="results", lazy="select")
    constructor = relationship("Constructor", back_populates="results", lazy="select")
    status_rel = relationship("Status", back_populates="results", lazy="select")

    __table_args__ = (
        Index("ix_results_race_driver", "raceId", "driverId"),
        Index("ix_results_race_constructor", "raceId", "constructorId"),
    )

    def __repr__(self):
        return f"<Result(resultId={self.resultId}, raceId={self.raceId}, position={self.position})>"


class DriverStanding(Base):
    """Driver championship standings after each race."""
    __tablename__ = "driver_standings"

    driverStandingsId = Column(Integer, primary_key=True, autoincrement=True)
    raceId = Column(Integer, ForeignKey("races.raceId"), nullable=False, index=True)
    driverId = Column(Integer, ForeignKey("drivers.driverId"), nullable=False, index=True)
    points = Column(Float, nullable=True)
    position = Column(Integer, nullable=True)
    wins = Column(Integer, nullable=True)

    race = relationship("Race", back_populates="driver_standings", lazy="select")
    driver = relationship("Driver", back_populates="standings", lazy="select")

    __table_args__ = (
        Index("ix_driverstandings_race_driver", "raceId", "driverId"),
    )

    def __repr__(self):
        return f"<DriverStanding(id={self.driverStandingsId}, position={self.position})>"


class ConstructorStanding(Base):
    """Constructor championship standings after each race."""
    __tablename__ = "constructor_standings"

    constructorStandingsId = Column(Integer, primary_key=True, autoincrement=True)
    raceId = Column(Integer, ForeignKey("races.raceId"), nullable=False, index=True)
    constructorId = Column(Integer, ForeignKey("constructors.constructorId"), nullable=False, index=True)
    points = Column(Float, nullable=True)
    position = Column(Integer, nullable=True)
    wins = Column(Integer, nullable=True)

    race = relationship("Race", back_populates="constructor_standings", lazy="select")
    constructor = relationship("Constructor", back_populates="standings", lazy="select")

    __table_args__ = (
        Index("ix_constructorstandings_race_constructor", "raceId", "constructorId"),
    )

    def __repr__(self):
        return f"<ConstructorStanding(id={self.constructorStandingsId}, position={self.position})>"


class Qualifying(Base):
    """Qualifying session results."""
    __tablename__ = "qualifying"

    qualifyId = Column(Integer, primary_key=True, autoincrement=True)
    raceId = Column(Integer, ForeignKey("races.raceId"), nullable=False, index=True)
    driverId = Column(Integer, ForeignKey("drivers.driverId"), nullable=False, index=True)
    constructorId = Column(Integer, ForeignKey("constructors.constructorId"), nullable=False, index=True)
    number = Column(Integer, nullable=True)
    position = Column(Integer, nullable=True)
    q1 = Column(String(20), nullable=True)
    q2 = Column(String(20), nullable=True)
    q3 = Column(String(20), nullable=True)

    race = relationship("Race", back_populates="qualifying_entries", lazy="select")
    driver = relationship("Driver", back_populates="qualifying_entries", lazy="select")
    constructor = relationship("Constructor", back_populates="qualifying_entries", lazy="select")

    __table_args__ = (
        Index("ix_qualifying_race_driver", "raceId", "driverId"),
    )

    def __repr__(self):
        return f"<Qualifying(qualifyId={self.qualifyId}, position={self.position})>"


class PitStop(Base):
    """Pit stop data for a driver during a race."""
    __tablename__ = "pitStops"

    raceId = Column(Integer, ForeignKey("races.raceId"), nullable=False, index=True)
    driverId = Column(Integer, ForeignKey("drivers.driverId"), nullable=False, index=True)
    stop = Column(Integer, nullable=False)
    lap = Column(Integer, nullable=True)
    time = Column(String(50), nullable=True)
    duration = Column(String(20), nullable=True)
    milliseconds = Column(Integer, nullable=True)

    race = relationship("Race", back_populates="pit_stops", lazy="select")
    driver = relationship("Driver", back_populates="pit_stops", lazy="select")

    __table_args__ = (
        PrimaryKeyConstraint("raceId", "driverId", "stop"),
        Index("ix_pitstops_race_driver", "raceId", "driverId"),
    )

    def __repr__(self):
        return f"<PitStop(raceId={self.raceId}, driverId={self.driverId}, stop={self.stop})>"


class LapTime(Base):
    """Individual lap time for a driver during a race."""
    __tablename__ = "lapTimes"

    raceId = Column(Integer, ForeignKey("races.raceId"), nullable=False, index=True)
    driverId = Column(Integer, ForeignKey("drivers.driverId"), nullable=False, index=True)
    lap = Column(Integer, nullable=False)
    position = Column(Integer, nullable=True)
    time = Column(String(20), nullable=True)
    milliseconds = Column(Integer, nullable=True)

    race = relationship("Race", back_populates="lap_times", lazy="select")
    driver = relationship("Driver", back_populates="lap_times", lazy="select")

    __table_args__ = (
        PrimaryKeyConstraint("raceId", "driverId", "lap"),
        Index("ix_laptimes_race_driver", "raceId", "driverId"),
    )

    def __repr__(self):
        return f"<LapTime(raceId={self.raceId}, driverId={self.driverId}, lap={self.lap})>"
