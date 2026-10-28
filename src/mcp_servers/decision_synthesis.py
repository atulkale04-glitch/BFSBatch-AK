"""MCP Server: DecisionSynthesis - Decision aggregation and synthesis."""

import json
import logging
from typing import Any, Dict, List

from src.utils.logger import get_logger

logger = get_logger(__name__)


class DecisionSynthesisServer:
    """MCP Server for aggregating agent evaluations and synthesizing decisions."""

    def __init__(self):
        """Initialize DecisionSynthesis MCP Server."""
        self.logger = get_logger("mcp_servers.decision_synthesis")
        self.evaluation_store = {}
        self.logger.info("DecisionSynthesis MCP Server initialized")

    def store_evaluation(
        self,
        application_id: str,
        agent_name: str,
        evaluation_result: Dict[str, Any],
        confidence_score: float = None,
    ) -> Dict[str, Any]:
        """
        Store evaluation result from an agent.

        Args:
            application_id: Application ID
            agent_name: Name of agent providing evaluation
            evaluation_result: Evaluation data
            confidence_score: Confidence score (0-100)

        Returns:
            Confirmation of storage
        """
        self.logger.debug(f"Storing evaluation for {application_id} from {agent_name}")

        if application_id not in self.evaluation_store:
            self.evaluation_store[application_id] = {}

        self.evaluation_store[application_id][agent_name] = {
            "result": evaluation_result,
            "confidence": confidence_score or 0.0,
            "timestamp": str(__import__("datetime").datetime.utcnow()),
        }

        return {
            "success": True,
            "data": {
                "message": f"Evaluation stored for {agent_name}",
                "application_id": application_id,
                "agent_name": agent_name,
            },
        }

    def retrieve_evaluations(self, application_id: str) -> Dict[str, Any]:
        """
        Retrieve all evaluations for an application.

        Args:
            application_id: Application ID

        Returns:
            All stored evaluations
        """
        self.logger.debug(f"Retrieving evaluations for {application_id}")

        if application_id not in self.evaluation_store:
            return {
                "success": False,
                "data": {"message": f"No evaluations found for {application_id}"},
            }

        return {
            "success": True,
            "data": {
                "application_id": application_id,
                "evaluations": self.evaluation_store[application_id],
                "agent_count": len(self.evaluation_store[application_id]),
            },
        }

    def calculate_composite_risk(self, application_id: str) -> Dict[str, Any]:
        """
        Calculate composite risk score from all evaluations.

        Args:
            application_id: Application ID

        Returns:
            Composite risk score
        """
        self.logger.debug(f"Calculating composite risk for {application_id}")

        if application_id not in self.evaluation_store:
            return {"error": f"No evaluations found for {application_id}", "success": False}

        evaluations = self.evaluation_store[application_id]

        # Extract individual risk scores
        risk_scores = []

        for agent_name, eval_data in evaluations.items():
            if "risk_score" in eval_data["result"]:
                risk_scores.append(eval_data["result"]["risk_score"])
            elif "dti_risk_score" in eval_data["result"]:
                risk_scores.append(eval_data["result"].get("dti_risk_score", 50))
            elif "loan_risk_score" in eval_data["result"]:
                risk_scores.append(eval_data["result"].get("loan_risk_score", 50))

        if not risk_scores:
            composite_risk = 50
        else:
            composite_risk = sum(risk_scores) / len(risk_scores)

        # Determine risk level
        if composite_risk < 30:
            risk_level = "low"
        elif composite_risk < 70:
            risk_level = "medium"
        else:
            risk_level = "high"

        return {
            "success": True,
            "data": {
                "application_id": application_id,
                "composite_risk_score": round(composite_risk, 1),
                "risk_level": risk_level,
                "individual_scores": risk_scores,
                "agent_count": len(evaluations),
            },
        }

    def resolve_conflicting_recommendations(self, application_id: str) -> Dict[str, Any]:
        """
        Identify and attempt to resolve conflicting agent recommendations.

        Args:
            application_id: Application ID

        Returns:
            Conflict analysis and resolution
        """
        self.logger.debug(f"Resolving conflicts for {application_id}")

        if application_id not in self.evaluation_store:
            return {"error": f"No evaluations found for {application_id}", "success": False}

        evaluations = self.evaluation_store[application_id]
        conflicts = []

        # Extract recommendations
        recommendations = {}
        for agent_name, eval_data in evaluations.items():
            if "recommendation" in eval_data["result"]:
                recommendations[agent_name] = eval_data["result"]["recommendation"]
            elif "risk_level" in eval_data["result"]:
                recommendations[agent_name] = eval_data["result"]["risk_level"]

        # Detect conflicts
        unique_recommendations = set(recommendations.values())
        if len(unique_recommendations) > 1:
            conflicts = [f"Conflicting recommendations: {', '.join(unique_recommendations)}"]

        resolution = "Use composite risk score for tiebreaker" if conflicts else "All agents align"

        return {
            "success": True,
            "data": {
                "application_id": application_id,
                "recommendations": recommendations,
                "conflicts": conflicts,
                "resolution_strategy": resolution,
                "conflict_count": len(conflicts),
            },
        }

    def prepare_decision_summary(
        self,
        application_id: str,
        final_decision: str,
        risk_score: float,
        confidence_level: float,
        key_factors: List[str],
    ) -> Dict[str, Any]:
        """
        Prepare comprehensive decision summary.

        Args:
            application_id: Application ID
            final_decision: Final decision (APPROVED/REJECTED/MANUAL_REVIEW)
            risk_score: Overall risk score
            confidence_level: Decision confidence
            key_factors: Key factors influencing decision

        Returns:
            Decision summary
        """
        self.logger.debug(f"Preparing decision summary for {application_id}")

        summary = {
            "application_id": application_id,
            "decision": final_decision,
            "risk_score": round(risk_score, 1),
            "confidence_level": round(confidence_level, 1),
            "key_factors": key_factors,
            "decision_reasoning": self._generate_reasoning(final_decision, risk_score),
            "timestamp": str(__import__("datetime").datetime.utcnow()),
        }

        return {
            "success": True,
            "data": summary,
        }

    def _generate_reasoning(self, decision: str, risk_score: float) -> str:
        """Generate decision reasoning."""
        if decision == "APPROVED":
            return f"Application approved based on low risk profile (Risk Score: {risk_score:.1f}/100)"
        elif decision == "REJECTED":
            return f"Application rejected due to high risk factors (Risk Score: {risk_score:.1f}/100)"
        else:
            return f"Application requires manual review due to borderline risk assessment (Risk Score: {risk_score:.1f}/100)"

    def validate_decision_consistency(self, application_id: str) -> Dict[str, Any]:
        """
        Validate consistency of decision across agent evaluations.

        Args:
            application_id: Application ID

        Returns:
            Consistency check results
        """
        self.logger.debug(f"Validating decision consistency for {application_id}")

        if application_id not in self.evaluation_store:
            return {"error": f"No evaluations found for {application_id}", "success": False}

        # Check if all required evaluations exist
        required_agents = ["applicant_profile_agent", "financial_risk_agent"]
        existing_agents = set(self.evaluation_store[application_id].keys())
        missing_agents = [a for a in required_agents if a not in existing_agents]

        is_consistent = len(missing_agents) == 0

        return {
            "success": True,
            "data": {
                "application_id": application_id,
                "is_consistent": is_consistent,
                "existing_agents": list(existing_agents),
                "missing_agents": missing_agents,
                "ready_for_decision": is_consistent,
            },
        }

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools for Claude."""
        return [
            {
                "name": "store_evaluation",
                "description": "Store evaluation result from an agent",
                "input_schema": {
                    "properties": {
                        "application_id": {"type": "string", "description": "Application ID"},
                        "agent_name": {"type": "string", "description": "Name of agent providing evaluation"},
                        "evaluation_result": {"type": "object", "description": "Evaluation data"},
                        "confidence_score": {"type": "number", "description": "Confidence score (0-100)"},
                    },
                    "required": ["application_id", "agent_name", "evaluation_result"],
                },
            },
            {
                "name": "retrieve_evaluations",
                "description": "Retrieve all evaluations for an application",
                "input_schema": {
                    "properties": {"application_id": {"type": "string", "description": "Application ID"}},
                    "required": ["application_id"],
                },
            },
            {
                "name": "calculate_composite_risk",
                "description": "Calculate composite risk score from all evaluations",
                "input_schema": {
                    "properties": {"application_id": {"type": "string", "description": "Application ID"}},
                    "required": ["application_id"],
                },
            },
            {
                "name": "resolve_conflicting_recommendations",
                "description": "Identify and resolve conflicting agent recommendations",
                "input_schema": {
                    "properties": {"application_id": {"type": "string", "description": "Application ID"}},
                    "required": ["application_id"],
                },
            },
            {
                "name": "prepare_decision_summary",
                "description": "Prepare comprehensive decision summary",
                "input_schema": {
                    "properties": {
                        "application_id": {"type": "string", "description": "Application ID"},
                        "final_decision": {"type": "string", "description": "Final decision"},
                        "risk_score": {"type": "number", "description": "Risk score"},
                        "confidence_level": {"type": "number", "description": "Confidence level"},
                        "key_factors": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Key factors",
                        },
                    },
                    "required": [
                        "application_id",
                        "final_decision",
                        "risk_score",
                        "confidence_level",
                        "key_factors",
                    ],
                },
            },
            {
                "name": "validate_decision_consistency",
                "description": "Validate consistency of decision across agent evaluations",
                "input_schema": {
                    "properties": {"application_id": {"type": "string", "description": "Application ID"}},
                    "required": ["application_id"],
                },
            },
        ]

    def handle_tool_call(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """
        Handle tool call from Claude.

        Args:
            tool_name: Name of tool to execute
            tool_input: Tool input parameters

        Returns:
            JSON string result
        """
        self.logger.debug(f"Handling tool call: {tool_name}")

        if tool_name == "store_evaluation":
            result = self.store_evaluation(
                tool_input.get("application_id", ""),
                tool_input.get("agent_name", ""),
                tool_input.get("evaluation_result", {}),
                tool_input.get("confidence_score"),
            )
        elif tool_name == "retrieve_evaluations":
            result = self.retrieve_evaluations(tool_input.get("application_id", ""))
        elif tool_name == "calculate_composite_risk":
            result = self.calculate_composite_risk(tool_input.get("application_id", ""))
        elif tool_name == "resolve_conflicting_recommendations":
            result = self.resolve_conflicting_recommendations(tool_input.get("application_id", ""))
        elif tool_name == "prepare_decision_summary":
            result = self.prepare_decision_summary(
                tool_input.get("application_id", ""),
                tool_input.get("final_decision", ""),
                tool_input.get("risk_score", 0),
                tool_input.get("confidence_level", 0),
                tool_input.get("key_factors", []),
            )
        elif tool_name == "validate_decision_consistency":
            result = self.validate_decision_consistency(tool_input.get("application_id", ""))
        else:
            result = {"error": f"Unknown tool: {tool_name}"}

        return json.dumps(result)
