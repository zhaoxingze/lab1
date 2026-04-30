from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()
engine = create_engine('sqlite:///devops_metrics.db', connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(bind=engine)

class BuildRecord(Base):
    __tablename__ = 'build_records'
    id = Column(Integer, primary_key=True)
    service_name = Column(String(100))
    build_time = Column(DateTime, default=datetime.utcnow)
    duration_seconds = Column(Integer)
    status = Column(String(20))  # success/failed
    commit_hash = Column(String(50))

class DeploymentRecord(Base):
    __tablename__ = 'deployment_records'
    id = Column(Integer, primary_key=True)
    service_name = Column(String(100))
    deploy_time = Column(DateTime, default=datetime.utcnow)
    deploy_duration = Column(Integer)
    success = Column(Integer)  # 0/1
    environment = Column(String(20))  # dev/staging/prod

class ServiceHealth(Base):
    __tablename__ = 'service_health'
    id = Column(Integer, primary_key=True)
    service_name = Column(String(100))
    timestamp = Column(DateTime, default=datetime.utcnow)
    response_time_ms = Column(Float)
    error_rate = Column(Float)
    cpu_usage = Column(Float)
    memory_usage = Column(Float)

class CodeStats(Base):
    __tablename__ = 'code_stats'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow)
    lines_of_code = Column(Integer)
    commits_count = Column(Integer)
    bug_count = Column(Integer)

def init_db():
    Base.metadata.create_all(engine)
    print("Database initialized")

if __name__ == "__main__":
    init_db()
