from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False, index=True)
    round = Column(Integer, nullable=False, index=True)
    driver_code = Column(String, nullable=False, index=True)
    grid = Column(Integer, nullable=True)
    score = Column(Float, nullable=False)
    predicted_rank = Column(Integer, nullable=False)
    group_key = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("year", "round", "driver_code", name="uq_prediction_yrrd_driver"),
    )


class Result(Base):
    __tablename__ = "results"
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False, index=True)
    round = Column(Integer, nullable=False, index=True)
    driver_code = Column(String, nullable=False, index=True)
    position = Column(Integer, nullable=True)
    points = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("year", "round", "driver_code", name="uq_result_yrrd_driver"),
    )



