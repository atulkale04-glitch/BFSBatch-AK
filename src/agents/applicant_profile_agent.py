"""Applicant Profile Agent - Analyzes applicant information and employment history."""

import json
from typing import Any, Dict, List

from config.prompts import APPLICANT_PROFILE_PROMPT
from src.agents.base_agent import BaseAgent, Tool
from src.mcp_servers.applicant_db import ApplicantDBServer
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ApplicantProfileAgent(BaseAgent):
    """Agent for analyzing applicant profiles and employment data."""

    def __init__(self):
        """Initialize Applicant Profile Agent."""
        self.mcp_server = ApplicantDBServer()

        # Register all MCP server tools
        tools = [
            Tool(
                name="get_applicant_profile",
                description="Retrieve complete applicant profile with personal and employment information",
                input_schema={
                    "properties": {
                        "applicant_id": {"type": "string", "description": "Unique applicant identifier"}
                    },
                    "required": ["applicant_id"],
                },
                handler=self._handle_get_applicant_profile,
            ),
            Tool(
                name="get_employment_history",
                description="Retrieve employment history and current employment verification",
                input_schema={
                    "properties": {
                        "applicant_id": {"type": "string", "description": "Unique applicant identifier"}
                    },
                    "required": ["applicant_id"],
                },
                handler=self._handle_get_employment_history,
            ),
            Tool(
                name="get_credit_history",
                description="Retrieve credit history summary and credit account information",
                input_schema={
                    "properties": {
                        "applicant_id": {"type": "string", "description": "Unique applicant identifier"}
                    },
                    "required": ["applicant_id"],
                },
                handler=self._handle_get_credit_history,
            ),
            Tool(
                name="calculate_income_stability",
                description="Calculate income stability score (0-100) based on income history and employment tenure",
                input_schema={
                    "properties": {
                        "applicant_id": {"type": "string", "description": "Unique applicant identifier"}
                    },
                    "required": ["applicant_id"],
                },
                handler=self._handle_calculate_income_stability,
            ),
            Tool(
                name="get_employment_risk",
                description="Assess employment risk level (low/medium/high) based on tenure and employment type",
                input_schema={
                    "properties": {
                        "applicant_id": {"type": "string", "description": "Unique applicant identifier"}
                    },
                    "required": ["applicant_id"],
                },
                handler=self._handle_get_employment_risk,
            ),
        ]

        super().__init__(
            agent_name="applicant_profile_agent",
            system_prompt=APPLICANT_PROFILE_PROMPT,
            tools=tools,
        )

    def _handle_get_applicant_profile(self, applicant_id: str) -> Dict[str, Any]:
        """Handle get_applicant_profile tool call."""
        return self.mcp_server.get_applicant_profile(applicant_id)

    def _handle_get_employment_history(self, applicant_id: str) -> Dict[str, Any]:
        """Handle get_employment_history tool call."""
        return self.mcp_server.get_employment_history(applicant_id)

    def _handle_get_credit_history(self, applicant_id: str) -> Dict[str, Any]:
        """Handle get_credit_history tool call."""
        return self.mcp_server.get_credit_history(applicant_id)

    def _handle_calculate_income_stability(self, applicant_id: str) -> Dict[str, Any]:
        """Handle calculate_income_stability tool call."""
        return self.mcp_server.calculate_income_stability(applicant_id)

    def _handle_get_employment_risk(self, applicant_id: str) -> Dict[str, Any]:
        """Handle get_employment_risk tool call."""
        return self.mcp_server.get_employment_risk(applicant_id)

    def _format_input_for_claude(self, input_data: Dict[str, Any]) -> str:
        """Format applicant data into a prompt for Claude."""
        applicant_id = input_data.get("applicant_id", "")

        return f"""Analyze the following applicant for profile assessment:

Applicant ID: {applicant_id}
Loan Amount: ${input_data.get('loan_amount', 0):,.2f}
Credit Score: {input_data.get('credit_score', 0)}

Please perform the following analysis:
1. Retrieve the applicant's full profile using get_applicant_profile
2. Get employment history using get_employment_history
3. Review credit history using get_credit_history
4. Calculate income stability using calculate_income_stability
5. Assess employment risk using get_employment_risk

Based on these tools, provide:
- Income Stability Score (0-100)
- Employment Risk Level (low/medium/high)
- Credit History Summary
- Any Completeness Flags for missing information
- Overall applicant profile assessment

Format your final response as JSON with keys: income_stability_score, employment_risk, credit_history_summary, completeness_flags, overall_assessment"""

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
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', text_content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = {
                    "income_stability_score": 0,
                    "employment_risk": "unknown",
                    "credit_history_summary": text_content,
                    "completeness_flags": [],
                    "overall_assessment": text_content,
                }
        except json.JSONDecodeError:
            result = {
                "income_stability_score": 0,
                "employment_risk": "unknown",
                "credit_history_summary": text_content,
                "completeness_flags": [],
                "overall_assessment": text_content,
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

        if "income_stability_score" not in data:
            errors.append("Missing income_stability_score")
        elif not (0 <= data["income_stability_score"] <= 100):
            errors.append("income_stability_score must be between 0 and 100")

        if "employment_risk" not in data:
            errors.append("Missing employment_risk")
        elif data["employment_risk"] not in ["low", "medium", "high"]:
            errors.append("employment_risk must be low, medium, or high")

        if "credit_history_summary" not in data:
            errors.append("Missing credit_history_summary")

        if "completeness_flags" not in data:
            errors.append("Missing completeness_flags")
        elif not isinstance(data["completeness_flags"], list):
            errors.append("completeness_flags must be a list")

        return len(errors) == 0, errors
