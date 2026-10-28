"""FastAPI routes for loan approval application with orchestrator integration."""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from src.models.schemas import (
    LoanApplicationRequest,
    ApplicationSubmissionResponse,
    LoanDecisionResponse,
)
from src.models.database import LoanApplication, DecisionRecord, AuditLog
from src.database.connection import get_db_session
from src.orchestration.orchestrator import ApplicationOrchestrator
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1", tags=["applications"])

orchestrator = ApplicationOrchestrator()


@router.post("/applications", response_model=ApplicationSubmissionResponse)
async def submit_application(
    request: LoanApplicationRequest, db: Session = Depends(get_db_session)
):
    """
    Submit a new loan application for processing.

    Args:
        request: Loan application data
        db: Database session

    Returns:
        ApplicationSubmissionResponse with application_id and status
    """
    logger.info(f"Received application submission from {request.applicant_id}")

    try:
        application_data = request.dict()

        application_record = LoanApplication(
            application_id=str(uuid.uuid4()),
            applicant_id=request.applicant_id,
            age=request.age,
            income=request.income,
            employment_type=request.employment_type,
            credit_score=request.credit_score,
            loan_amount=request.loan_amount,
            loan_tenure_months=request.loan_tenure_months,
            existing_liabilities=request.existing_liabilities,
            location=request.location,
            applicant_email=request.applicant_email,
            status="submitted",
        )
        db.add(application_record)
        db.commit()
        db.refresh(application_record)

        result = await orchestrator.process_application(application_data)

        if result.get("success"):
            application_record.status = result.get("status", "completed")
            application_record.decision = result.get("decision")
            application_record.risk_score = result.get("risk_score")
            application_record.confidence_level = result.get("confidence_level")
            db.commit()

            if result.get("status") == "completed":
                decision_record = DecisionRecord(
                    application_id=application_record.application_id,
                    final_decision=result.get("decision"),
                    risk_score=result.get("risk_score"),
                    confidence_level=result.get("confidence_level"),
                    key_factors=",".join(result.get("key_factors", [])),
                    reasoning=result.get("reasoning"),
                    case_id=result.get("case_id"),
                )
                db.add(decision_record)
                db.commit()

        return ApplicationSubmissionResponse(
            application_id=application_record.application_id,
            status=application_record.status,
            message=f"Application {application_record.application_id} submitted successfully",
        )

    except Exception as e:
        logger.error(f"Error submitting application: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/applications/{application_id}")
async def get_application_status(
    application_id: str, db: Session = Depends(get_db_session)
):
    """
    Get application status by ID.

    Args:
        application_id: Application ID
        db: Database session

    Returns:
        Application record with current status
    """
    logger.info(f"Fetching application status: {application_id}")

    try:
        application = db.query(LoanApplication).filter(
            LoanApplication.application_id == application_id
        ).first()

        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        return {
            "application_id": application.application_id,
            "applicant_id": application.applicant_id,
            "status": application.status,
            "decision": application.decision,
            "risk_score": application.risk_score,
            "confidence_level": application.confidence_level,
            "created_at": application.created_at.isoformat(),
            "updated_at": application.updated_at.isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching application status: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/applications/{application_id}/decision", response_model=LoanDecisionResponse)
async def get_application_decision(
    application_id: str, db: Session = Depends(get_db_session)
):
    """
    Get loan decision for an application.

    Args:
        application_id: Application ID
        db: Database session

    Returns:
        Detailed loan decision with reasoning
    """
    logger.info(f"Fetching decision for application: {application_id}")

    try:
        decision = db.query(DecisionRecord).filter(
            DecisionRecord.application_id == application_id
        ).first()

        if not decision:
            raise HTTPException(status_code=404, detail="Decision not found")

        key_factors = decision.key_factors.split(",") if decision.key_factors else []

        return LoanDecisionResponse(
            application_id=decision.application_id,
            final_decision=decision.final_decision,
            risk_score=decision.risk_score,
            confidence_level=decision.confidence_level,
            key_factors=key_factors,
            reasoning=decision.reasoning,
            case_id=decision.case_id,
            created_at=decision.created_at.isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching decision: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/applications/{application_id}/audit-trail")
async def get_audit_trail(
    application_id: str, db: Session = Depends(get_db_session)
):
    """
    Get audit trail for an application.

    Args:
        application_id: Application ID
        db: Database session

    Returns:
        List of audit log entries
    """
    logger.info(f"Fetching audit trail for application: {application_id}")

    try:
        audit_logs = db.query(AuditLog).filter(
            AuditLog.application_id == application_id
        ).order_by(AuditLog.created_at).all()

        return {
            "application_id": application_id,
            "audit_entries": [
                {
                    "timestamp": log.created_at.isoformat(),
                    "action": log.action,
                    "details": log.details,
                }
                for log in audit_logs
            ],
        }

    except Exception as e:
        logger.error(f"Error fetching audit trail: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
