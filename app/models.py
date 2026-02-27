from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from .db import Base
import datetime

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, index=True)
    type = Column(String, index=True)
    how = Column(String)
    time = Column(String)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    raw_xml = Column(Text)
    received_at = Column(DateTime, default=datetime.datetime.utcnow)