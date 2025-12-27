from sqlalchemy import Column, Integer, String, JSON, DateTime, BigInteger
from sqlalchemy.sql import func
from app.database import Base
import datetime

class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    sheet_row_index = Column(Integer, unique=True, index=True, nullable=False)
    data_payload = Column(JSON, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_sync_source = Column(String(50), default="DB") # "DB" or "SHEET"
    version_ts = Column(BigInteger, default=lambda: int(datetime.datetime.now().timestamp() * 1000))
