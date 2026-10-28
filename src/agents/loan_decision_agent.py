"""Loan Decision Agent - Makes final lending decisions."""

import json
import re
from typing import Any, Dict, List

from config.prompts import LOAN_DECISION_PROMPT
from config.thresholds import APPROVAL_POLICY
from src.agents.base_agent import BaseAgent, Tool
from src.mcp_servers.decision_synthesis import DecisionSynthesisServer
from src.utils.logger import get_logger

logger = get_logger(__name__)


class LoanDecisionAgent(BaseAgent):
    """Agent for synthesizing evaluations and making final lending decisions."""

    def __init__(self):
        """Initialize Loan Decision Agent."""
        self.mcp_server = DecisionSynthesisServer()

        # Register all MCP server tools
        tools = [
            Tool(
                name="retrieve_evaluations",
                description="Retrieve all evaluations from other agents for this application",
                input_schema={
                    "properties": {
                        "application_id": {"type": "string", "description": "Application ID"}
                    },
                    "required": ["application_id"],
                },
                handler=self._handle_retrieve_evaluations,
            ),
            Tool(
                name="calculate_composite_risk",
                description="Calculate composite risk score from all agent evaluations",
                input_schema={
                    "properties": {
                        "application_id": {"type": "string", "description": "Application ID"}
                    },
                    "required": ["application_id"],
                },
                handler=self._handle_calculate_composite_risk,
            ),
            Tool(
                name="resolve_conflicting_recommendations",
                description="Resolve any conflicting recommendations from agents",
                input_schema={
                    "properties": {
                        "application_id": {"type": "string", "description": "Application ID"}
                    },
                    "required": ["application_id"],
                },
                handler=self._handle_resolve_conflicting_recommendations,
            ),
            Tool(
                name="prepare_decision_summary",
                description="Prepare comprehensive decision summary for the final determination",
                input_schema={
                    "properties": {
                        "application_id": {"type": "string", "description": "Application ID"},
                        "final_decision": {"type": "string", "description": "Final decision (APPROVED/REJECTED/MANUAL_REVIEW)"},
                        "risk_score": {"type": "number", "description": "Overall risk score (0-100)"},
                        "confidence_level": {"type": "number", "description": "Confidence level (0-100)"},
                        "key_factors": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Key factors influencing decision",
                        },
                    },
                    "required": ["application_id", "final_decision", "risk_score", "confidence_level", "key_factors"],
                },
                handler=self._handle_prepare_decision_summary,
            ),
        ]

        super().__init__(
            agent_name="loan_decision_agent",
            system_prompt=LOAN_DECISION_PROMPT,
            tools=tools,
        )

    def _handle_retrieve_evaluations(self, application_id: str) -> Dict[str, Any]:
        """Handle retrieve_evaluations tool call."""
        return self.mcp_server.retrieve_evaluations(application_id)

    def _handle_calculate_composite_risk(self, application_id: str) -> Dict[str, Any]:
        """Handle calculate_composite_risk tool call."""
        return self.mcp_server.calculate_composite_risk(application_id)

    def _handle_resolve_conflicting_recommendations(self, application_id: str) -> Dict[str, Any]:
        """Handle resolve_conflicting_recommendations tool call."""
        return self.mcp_server.resolve_conflicting_recommendations(application_id)

    def _handle_prepare_decision_summary(
        self,
        application_id: str,
        final_decision: str,
        risk_score: float,
        confidence_level: float,
        key_factors: List[str],
    ) -> Dict[str, Any]:
        """Handle prepare_decision_summary tool call."""
        return self.mcp_server.prepare_decision_summary(
            application_id, final_decision, risk_score, confidence_level, key_factors
        )

    def _format_input_for_claude(self, input_data: Dict[str, Any]) -> str:
        """Format decision data into a prompt for Claude."""
        application_id = input_data.get("application_id", "")

        return f"""Make a final lending decision for the following application:

Application ID: {application_id}
Loan Amount: ${input_data.get('loan_amount', 0):,.2f}
Applicant Income: ${input_data.get('income', 0):,.2f}

Company Approval Policy:
- Minimum Credit Score: {APPROVAL_POLICY['min_credit_score']}
- Maximum DTI Ratio: {APPROVAL_POLICY['max_dti_ratio']:.0%}
- Minimum Income Stability: {APPROVAL_POLICY['min_income_stability']}/100
- Auto-Approve Risk Score: < {APPROVAL_POLICY['auto_approve_max_risk_score']}
- Auto-Reject Risk Score: > {APPROVAL_POLICY['auto_reject_min_risk_score']}

Please perform the following:
1. Retrieve all agent evaluations using retrieve_evaluations
2. Calculate composite risk score using calculate_composite_risk
3. Resolve any conflicting recommendations using resolve_conflicting_recommendations
4. Based on all information, determine the final decision:
   - APPROVED: Low risk, meets all criteria
   - REJECTED: High risk, fails key criteria
   - MANUAL_REVIEW: Borderline case requiring expert review
5. Prepare decision summary using prepare_decision_summary

Provide your analysis with:
- Final Decision (APPROVED/REJECTED/MANUAL_REVIEW)
- Risk Score (0-100)
- Confidence Level (0-100)
- Top 3 Key Factors influencing the decision
- Detailed Reasoning

Format your final response as JSON with keys: final_decision, risk_score, confidence_level, key_factors, reasoning"""

    def _extract_final_response(
        self,
        response: Any,
        messages: List[Dict[str, Any]],
        input_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Extract final response from Claude."""
        text_content = ""
        for content_block in response.content:
            if hasattr(content_block, "text"):
                text_content += content_block.text

        # Try to parse JSON from response
        try:
            json_match = re.search(r'\{.*\}', text_content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = {
                    "final_decision": "MANUAL_REVIEW",
                    "risk_score": 50,
                    "confidence_level": 50,
                    "key_factors": [],
                    "reasoning": text_content,
                }
        except json.JSONDecodeError:
            result = {
                "final_decision": "MANUAL_REVIEW",
                "risk_score": 50,
                "confidence_level": 50,
                "key_factors": [],
                "reasoning": text_content,
            }

        return {
            "success": True,
            "data": result,
            "iterations": len(messages) // 2,
        }

    def validate_output(self, output: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate agent output format and content."""
        errors = []

        if not output.get("success"):
            errors.append("Output missing success flag")

        data = output.get("data", {})

        if "final_decision" not in data:
            errors.append("Missing final_decision")
        elif data["final_decision"] not in ["APPROVED", "REJECTED", "MANUAL_REVIEW"]:
            errors.append("final_decision must be APPROVED, REJECTED, or MANUAL_REVIEW")

        if "risk_score" not in data:
            errors.append("Missing risk_score")
        elif not (0 <= data.get("risk_score", 0) <= 100):
            errors.append("risk_score must be between 0 and 100")

        if "confidence_level" not in data:
            errors.append("Missing confidence_level")
        elif not (0 <= data.get("confidence_level", 0) <= 100):
            errors.append("confidence_level must be between 0 and 100")

        if "key_factors" not in data:
            errors.append("Missing key_factors")
        elif not isinstance(data["key_factors"], list):
            errors.append("key_factors must be a list")

        return len(errors) == 0, errors
