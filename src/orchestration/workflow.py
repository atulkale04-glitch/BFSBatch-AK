"""LangGraph workflow for orchestrating loan approval agents."""

import asyncio
from typing import Any, Dict, Optional

from langgraph.graph import END, START, StateGraph

from src.agents.applicant_profile_agent import ApplicantProfileAgent
from src.agents.compliance_orchestrator_agent import ComplianceOrchestratorAgent
from src.agents.financial_risk_agent import FinancialRiskAgent
from src.agents.loan_decision_agent import LoanDecisionAgent
from src.orchestration.state import WorkflowState, add_audit_entry, merge_evaluation, update_state_status
from src.utils.logger import get_logger

logger = get_logger(__name__)


class WorkflowNodes:
    """Node functions for LangGraph workflow."""

    def __init__(self):
        """Initialize workflow nodes with agents."""
        self.applicant_agent = ApplicantProfileAgent()
        self.risk_agent = FinancialRiskAgent()
        self.decision_agent = LoanDecisionAgent()
        self.compliance_agent = ComplianceOrchestratorAgent()

    def validate_input_node(self, state: WorkflowState) -> WorkflowState:
        """Validate input data."""
        logger.info(f"Validating input for application {state['application_id']}")
        update_state_status(state, "processing", "validation")

        # Basic validation
        errors = []
        if not state.get("applicant_id"):
            errors.append("Missing applicant_id")
        if state.get("credit_score", 0) < 300 or state.get("credit_score", 0) > 850:
            errors.append("Invalid credit score")
        if state.get("income", 0) <= 0:
            errors.append("Invalid income")
        if state.get("loan_amount", 0) <= 0:
            errors.append("Invalid loan amount")

        if errors:
            error_msg = "; ".join(errors)
            logger.error(f"Validation failed: {error_msg}")
            update_state_status(state, "failed", "validation", error_msg)
            return state

        logger.info("Validation passed")
        add_audit_entry(state, "VALIDATION_PASSED", {})
        return state

    async def applicant_profile_node(self, state: WorkflowState) -> WorkflowState:
        """Execute Applicant Profile Agent."""
        logger.info(f"Running Applicant Profile Agent for {state['applicant_id']}")
        update_state_status(state, "processing", "applicant_profile")

        try:
            input_data = {
                "applicant_id": state["applicant_id"],
                "loan_amount": state["loan_amount"],
                "credit_score": state["credit_score"],
            }

            result = await self.applicant_agent.execute(input_data)

            if not result.get("success"):
                raise Exception(f"Agent failed: {result.get('data', {}).get('error')}")

            state["applicant_profile_output"] = result["data"]
            merge_evaluation(state, "applicant_profile_agent", result["data"])
            logger.info("Applicant Profile Agent completed successfully")

        except Exception as e:
            logger.error(f"Applicant Profile Agent failed: {e}")
            update_state_status(state, "failed", "applicant_profile", str(e))

        return state

    async def financial_risk_node(self, state: WorkflowState) -> WorkflowState:
        """Execute Financial Risk Analysis Agent."""
        logger.info(f"Running Financial Risk Agent for {state['applicant_id']}")
        update_state_status(state, "processing", "financial_risk")

        try:
            input_data = {
                "applicant_id": state["applicant_id"],
                "age": state["age"],
                "income": state["income"],
                "credit_score": state["credit_score"],
                "loan_amount": state["loan_amount"],
                "loan_tenure_months": state["loan_tenure_months"],
                "existing_liabilities": state["existing_liabilities"],
            }

            result = await self.risk_agent.execute(input_data)

            if not result.get("success"):
                raise Exception(f"Agent failed: {result.get('data', {}).get('error')}")

            state["financial_risk_output"] = result["data"]
            merge_evaluation(state, "financial_risk_agent", result["data"])
            logger.info("Financial Risk Agent completed successfully")

        except Exception as e:
            logger.error(f"Financial Risk Agent failed: {e}")
            update_state_status(state, "failed", "financial_risk", str(e))

        return state

    async def loan_decision_node(self, state: WorkflowState) -> WorkflowState:
        """Execute Loan Decision Agent."""
        logger.info(f"Running Loan Decision Agent for {state['application_id']}")
        update_state_status(state, "processing", "loan_decision")

        try:
            input_data = {
                "application_id": state["application_id"],
                "loan_amount": state["loan_amount"],
                "income": state["income"],
            }

            result = await self.decision_agent.execute(input_data)

            if not result.get("success"):
                raise Exception(f"Agent failed: {result.get('data', {}).get('error')}")

            decision_data = result["data"]
            state["loan_decision_output"] = decision_data
            state["final_decision"] = decision_data.get("final_decision")
            state["risk_score"] = decision_data.get("risk_score")
            state["confidence_level"] = decision_data.get("confidence_level")
            state["key_factors"] = decision_data.get("key_factors", [])
            state["reasoning"] = decision_data.get("reasoning")

            merge_evaluation(state, "loan_decision_agent", decision_data)
            logger.info(f"Loan Decision Agent completed: {state['final_decision']}")

        except Exception as e:
            logger.error(f"Loan Decision Agent failed: {e}")
            update_state_status(state, "failed", "loan_decision", str(e))

        return state

    async def compliance_node(self, state: WorkflowState) -> WorkflowState:
        """Execute Compliance & Action Orchestrator Agent."""
        logger.info(f"Running Compliance Agent for {state['application_id']}")
        update_state_status(state, "processing", "compliance")

        try:
            input_data = {
                "application_id": state["application_id"],
                "decision": state.get("final_decision", "MANUAL_REVIEW"),
                "applicant_email": state.get("applicant_email", ""),
                "risk_score": state.get("risk_score", 0),
                "explanation": state.get("reasoning", ""),
            }

            result = await self.compliance_agent.execute(input_data)

            if not result.get("success"):
                raise Exception(f"Agent failed: {result.get('data', {}).get('error')}")

            compliance_data = result["data"]
            state["compliance_output"] = compliance_data
            state["case_id"] = compliance_data.get("case_id")
            state["notifications_sent"].append(compliance_data.get("notification_status", "unknown"))

            merge_evaluation(state, "compliance_orchestrator_agent", compliance_data)
            logger.info("Compliance Agent completed successfully")

        except Exception as e:
            logger.error(f"Compliance Agent failed: {e}")
            update_state_status(state, "failed", "compliance", str(e))

        return state

    def completion_node(self, state: WorkflowState) -> WorkflowState:
        """Finalize workflow."""
        logger.info(f"Completing workflow for {state['application_id']}")

        if state["status"] == "processing":
            update_state_status(state, "completed", "completion")

        add_audit_entry(state, "WORKFLOW_COMPLETED", {
            "final_decision": state.get("final_decision"),
            "risk_score": state.get("risk_score"),
            "case_id": state.get("case_id"),
        })

        logger.info(f"Workflow completed: {state['final_decision']}")
        return state


def create_workflow_graph() -> StateGraph:
    """Create LangGraph workflow graph."""
    logger.info("Creating LangGraph workflow graph")

    nodes = WorkflowNodes()
    graph = StateGraph(WorkflowState)

    # Add nodes
    graph.add_node("validate", nodes.validate_input_node)
    graph.add_node("applicant_profile", nodes.applicant_profile_node)
    graph.add_node("financial_risk", nodes.financial_risk_node)
    graph.add_node("loan_decision", nodes.loan_decision_node)
    graph.add_node("compliance", nodes.compliance_node)
    graph.add_node("completion", nodes.completion_node)

    # Add edges
    graph.add_edge(START, "validate")

    # Validation routes
    def validation_route(state: WorkflowState) -> str:
        if state["status"] == "failed":
            return "completion"
        return "applicant_profile"

    graph.add_conditional_edges("validate", validation_route)

    # Sequential flow after validation
    graph.add_edge("applicant_profile", "financial_risk")
    graph.add_edge("financial_risk", "loan_decision")
    graph.add_edge("loan_decision", "compliance")
    graph.add_edge("compliance", "completion")

    # End
    graph.add_edge("completion", END)

    logger.info("Workflow graph created successfully")
    return graph
