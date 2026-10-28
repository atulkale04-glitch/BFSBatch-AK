"""FastAPI routes for loan approval system."""

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from src.models.schemas import ApplicationStatusResponse, ApplicationSubmissionResponse, LoanApplicationRequest
from src.utils.constants import (
    STATUS_PENDING,
    STATUS_PROCESSING,
    generate_application_id,
)
from src.utils.validators import validate_application_data

router = APIRouter(prefix="/applications", tags=["Loan Applications"])
logger = logging.getLogger(__name__)

# In-memory storage for this phase (will be replaced with database in later phases)
applications_store = {}


@router.post(
    "",
    response_model=ApplicationSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit Loan Application",
    description="Submit a new loan application for processing",
)
async def submit_application(application: LoanApplicationRequest) -> ApplicationSubmissionResponse:
    """
    Submit a new loan application.

    **Request Body:**
    - applicant_id: Unique applicant identifier
    - age: Applicant age (18-100)
    - income: Annual income
    - employment_type: Type of employment
    - credit_score: Credit score (300-850)
    - loan_amount: Requested loan amount
    - loan_tenure_months: Loan duration in months
    - existing_liabilities: Total existing liabilities
    - location: Applicant location

    **Returns:**
    - application_id: Unique identifier for tracking
    - status: Current processing status
    - created_at: Application submission timestamp
    """
    try:
        # Validate input data
        is_valid, errors = validate_application_data(application)
        if not is_valid:
            logger.warning(f"Application validation failed: {errors}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "Application validation failed", "errors": errors},
            )

        # Generate application ID
        application_id = generate_application_id()

        # Store application data
        applications_store[application_id] = {
            "id": application_id,
            "applicant_id": application.applicant_id,
            "status": STATUS_PROCESSING,
            "data": application.model_dump(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        logger.info(f"Application submitted: {application_id} for applicant: {application.applicant_id}")

        return ApplicationSubmissionResponse(
            application_id=application_id,
            status=STATUS_PROCESSING,
            created_at=datetime.utcnow(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting application: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit application",
        )


@router.get(
    "/{application_id}",
    response_model=ApplicationStatusResponse,
    summary="Get Application Status",
    description="Retrieve the current status of a loan application",
)
async def get_application_status(application_id: str) -> ApplicationStatusResponse:
    """
    Get the current status of a loan application.

    **Parameters:**
    - application_id: The application ID to look up

    **Returns:**
    - application_id: Application identifier
    - status: Current status (pending/processing/completed/failed)
    - created_at: Creation timestamp
    - updated_at: Last update timestamp
    - decision: Final decision (if completed)
    """
    try:
        # Retrieve from storage
        if application_id not in applications_store:
            logger.warning(f"Application not found: {application_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application {application_id} not found",
            )

        app_data = applications_store[application_id]

        return ApplicationStatusResponse(
            application_id=app_data["id"],
            status=app_data["status"],
            created_at=app_data["created_at"],
            updated_at=app_data["updated_at"],
            decision=app_data.get("decision"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving application status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve application status",
        )


@router.get(
    "/{application_id}/decision",
    summary="Get Loan Decision",
    description="Retrieve the final loan decision (available when status is completed)",
)
async def get_decision(application_id: str):
    """
    Get the final loan decision for an application.

    **Parameters:**
    - application_id: The application ID to look up

    **Returns:**
    - decision: Final decision (APPROVED/REJECTED/MANUAL_REVIEW)
    - risk_score: Risk score (0-100)
    - confidence_level: Confidence level (0-100%)
    - key_factors: Key factors influencing decision
    - explanation: Detailed explanation
    - case_id: Unique case identifier
    - timestamp: Decision timestamp
    """
    try:
        # Retrieve from storage
        if application_id not in applications_store:
            logger.warning(f"Application not found: {application_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application {application_id} not found",
            )

        app_data = applications_store[application_id]

        # Check if decision is available
        if not app_data.get("decision_result"):
            raise HTTPException(
                status_code=status.HTTP_202_ACCEPTED,
                detail="Decision not yet available. Application is still processing.",
            )

        return app_data["decision_result"]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving decision: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve decision",
        )


@router.get(
    "",
    summary="List Applications",
    description="Retrieve a list of all applications (for this phase, development only)",
)
async def list_applications(skip: int = 0, limit: int = 10):
    """
    List all applications (development endpoint).

    **Parameters:**
    - skip: Number of applications to skip
    - limit: Maximum number of applications to return

    **Returns:**
    List of application summaries
    """
    applications_list = list(applications_store.values())
    return {
        "total": len(applications_list),
        "applications": applications_list[skip : skip + limit],
    }
