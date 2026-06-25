from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Enum, JSON, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    ministry = Column(String(255))
    category = Column(String(50), default="citizen")
    fee = Column(Float, default=0.0)
    turnaround_days = Column(Integer, default=5)
    icon = Column(String(50), default="document")
    requirements = Column(JSON, default=list)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    user_nin = Column(String(20), nullable=False, index=True)
    service_id = Column(Integer, nullable=False)
    status = Column(String(50), default="submitted")
    metadata_json = Column(JSON, default=dict)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_nin = Column(String(20), nullable=False, index=True)
    service_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    payment_channel = Column(String(50), default="mobile_money")
    status = Column(String(50), default="pending")
    prn = Column(String(50), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    prn = Column(String(50), index=True)
    amount = Column(Float, nullable=False)
    channel = Column(String(50))
    transaction_id = Column(String(100))
    status = Column(String(50), default="pending")
    paid_at = Column(DateTime, nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(64), index=True)
    method = Column(String(10))
    path = Column(String(500))
    user_nin = Column(String(20), nullable=True)
    ip_address = Column(String(50))
    user_agent = Column(String(500), nullable=True)
    status_code = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
