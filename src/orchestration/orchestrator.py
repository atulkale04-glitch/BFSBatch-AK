"""Application Orchestrator - Executes complete loan approval workflow."""

import asyncio
from typing import Any, Dict, Optional

from src.orchestration.state import WorkflowState, create_initial_state
from src.orchestration.workflow import create_workflow_graph
from src.utils.constants import generate_application_id
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ApplicationOrchestrator:
    """Orchestrates complete loan application processing workflow."""

    def __init__(self):
        """Initialize orchestrator with workflow graph."""
        self.graph = create_workflow_graph()
        self.app = self.graph.compile()
        logger.info("ApplicationOrchestrator initialized")

    async def process_application(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a complete loan application through all agents.

        Args:
            application_data: Complete application data including:
                - applicant_id: Unique applicant ID
                - age, income, employment_type, credit_score
                - loan_amount, loan_tenure_months, existing_liabilities
                - location, applicant_email

        Returns:
            Complete workflow state with all decisions and audit trail
        """
        try:
            # Generate unique application ID
            application_id = generate_application_id()
            applicant_id = application_data.get("applicant_id", "unknown")

            logger.info(f"Starting application processing: {application_id}")

            # Create initial state
            state = create_initial_state(application_id, applicant_id, application_data)

            # Execute workflow
            logger.info("Invoking workflow graph")
            result = self.app.invoke(state)

            logger.info(f"Application processing completed: {application_id}")
            logger.info(f"Final decision: {result.get('final_decision')}")
            logger.info(f"Risk score: {result.get('risk_score')}")

            return {
                "success": True,
                "application_id": result.get("application_id"),
                "case_id": result.get("case_id"),
                "status": result.get("status"),
                "decision": result.get("final_decision"),
                "risk_score": result.get("risk_score"),
                "confidence_level": result.get("confidence_level"),
                "key_factors": result.get("key_factors", []),
                "reasoning": result.get("reasoning"),
                "audit_trail": result.get("audit_entries", []),
                "full_state": result,
            }

        except Exception as e:
            logger.error(f"Error processing application: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "application_id": application_id,
            }

    async def process_application_async(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process application asynchronously (for background task queues).

        Args:
            application_data: Application data

        Returns:
            Processing result
        """
        return await self.process_application(application_data)

    def process_application_sync(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process application synchronously (blocking).

        Args:
            application_data: Application data

        Returns:
            Processing result
        """
        # Run async function in sync context
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.process_application(application_data))

    async def validate_application_data(self, application_data: Dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate application data before processing.

        Args:
            application_data: Application data to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check required fields
        required_fields = [
            "applicant_id",
            "age",
            "income",
            "employment_type",
            "credit_score",
            "loan_amount",
            "loan_tenure_months",
            "existing_liabilities",
            "location",
        ]

        for field in required_fields:
            if field not in application_data:
                errors.append(f"Missing required field: {field}")

        # Validate ranges
        if application_data.get("age", 0) < 18:
            errors.append("Applicant must be at least 18 years old")

        if application_data.get("credit_score", 0) < 300 or application_data.get("credit_score", 0) > 850:
            errors.append("Credit score must be between 300 and 850")

        if application_data.get("income", 0) <= 0:
            errors.append("Income must be positive")

        if application_data.get("loan_amount", 0) <= 0:
            errors.append("Loan amount must be positive")

        return len(errors) == 0, errors

    def get_workflow_stats(self) -> Dict[str, Any]:
        """Get workflow statistics."""
        return {
            "graph_compiled": True,
            "nodes": len(self.graph.nodes),
            "edges": len(self.graph.edges),
        }
