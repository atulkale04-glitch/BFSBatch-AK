"""SQLAlchemy database models for loan approval system."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, JSON, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class LoanApplication(Base):
    """Loan application record."""

    __tablename__ = "loan_applications"

    id = Column(String, primary_key=True, index=True)
    applicant_id = Column(String, index=True, nullable=False)
    status = Column(String, nullable=False, default="pending")
    decision = Column(String, nullable=True)
    risk_score = Column(Float, nullable=True)
    case_id = Column(String, unique=True, nullable=True, index=True)

    # Application data
    age = Column(Integer, nullable=False)
    income = Column(Float, nullable=False)
    employment_type = Column(String, nullable=False)
    credit_score = Column(Integer, nullable=False)
    loan_amount = Column(Float, nullable=False)
    loan_tenure_months = Column(Integer, nullable=False)
    existing_liabilities = Column(Float, nullable=False)
    location = Column(String, nullable=False)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class AgentEvaluation(Base):
    """Agent evaluation results."""

    __tablename__ = "agent_evaluations"

    id = Column(String, primary_key=True, index=True)
    application_id = Column(String, index=True, nullable=False)
    agent_name = Column(String, nullable=False)
    evaluation_result = Column(JSON, nullable=False)
    confidence_score = Column(Float, nullable=True)
    status = Column(String, nullable=False, default="pending")

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class DecisionRecord(Base):
    """Final decision record."""

    __tablename__ = "decision_records"

    id = Column(String, primary_key=True, index=True)
    application_id = Column(String, unique=True, index=True, nullable=False)
    final_decision = Column(String, nullable=False)
    risk_score = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    reasoning = Column(JSON, nullable=False)
    key_factors = Column(JSON, nullable=False)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLog(Base):
    """Audit trail for all actions."""

    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, index=True)
    application_id = Column(String, index=True, nullable=False)
    action = Column(String, nullable=False)
    details = Column(JSON, nullable=True)
    case_id = Column(String, nullable=True, index=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)


def get_database_session_maker(database_url: str):
    """Create database session maker with given URL."""
    engine = create_engine(
        database_url,
        pool_size=10,
        max_overflow=20,
        echo=False,
    )
    return sessionmaker(autocommit=False, autoflush=False, bind=engine), engine
