"""Application Orchestrator - Executes complete loan approval workflow."""

import asyncio
from typing import Any, Dict, Optional

from src.orchestration.decision_engine import make_instant_decision
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ApplicationOrchestrator:
    """Orchestrates complete loan application processing workflow."""

    def __init__(self):
        """Initialize orchestrator with lightweight decision engine."""
        logger.info("ApplicationOrchestrator initialized with rule-based decision engine")

    async def process_application(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a complete loan application using rule-based instant decision.

        Args:
            application_data: Complete application data including:
                - applicant_id: Unique applicant ID
                - age, income, employment_type, credit_score
                - loan_amount, loan_tenure_months, existing_liabilities
                - location, applicant_email

        Returns:
            Decision result with decision, risk_score, confidence_score, case_id, key_factors, reasoning
        """
        try:
            logger.info("Processing application with rule-based decision engine")

            # Use lightweight rule-based decision engine (no expensive API calls)
            result = make_instant_decision(application_data)

            logger.info(f"Instant decision completed")
            logger.info(f"Final decision: {result.get('decision')}")
            logger.info(f"Risk score: {result.get('risk_score')}")

            return {
                "success": True,
                "decision": result.get("decision"),
                "risk_score": result.get("risk_score"),
                "confidence_score": result.get("confidence_score"),
                "case_id": result.get("case_id"),
                "key_factors": result.get("key_factors", []),
                "reasoning": result.get("reasoning"),
                "status": "completed",
                "error_message": None,
            }

        except Exception as e:
            logger.error(f"Error processing application: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "status": "failed",
            }
