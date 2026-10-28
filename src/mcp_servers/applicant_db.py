"""MCP Server: ApplicantDB - Applicant information data source."""

import json
import logging
from typing import Any, Dict, List

from src.utils.logger import get_logger

logger = get_logger(__name__)


class ApplicantDBServer:
    """MCP Server for accessing applicant profile information."""

    # Mock applicant database (Phase 2 - will be replaced with real DB queries)
    MOCK_APPLICANTS = {
        "APP-001": {
            "applicant_id": "APP-001",
            "name": "John Smith",
            "age": 35,
            "email": "john.smith@example.com",
            "employment_type": "Full-time",
            "employer": "Tech Corp",
            "employment_tenure_years": 5,
            "previous_employers": ["StartUp Inc", "Other Co"],
            "credit_history": {
                "accounts": 8,
                "average_age_months": 84,
                "inquiries_6m": 1,
                "delinquencies": 0,
                "late_payments_24m": 0,
            },
            "income_history": {
                "current_annual": 75000,
                "previous_annual": 72000,
                "years_reported": 5,
                "stable": True,
            },
            "location": "New York",
            "risk_profile": "low",
        },
        "APP-002": {
            "applicant_id": "APP-002",
            "name": "Jane Doe",
            "age": 28,
            "email": "jane.doe@example.com",
            "employment_type": "Self-employed",
            "employer": "Personal Business",
            "employment_tenure_years": 2,
            "previous_employers": ["Finance Corp"],
            "credit_history": {
                "accounts": 5,
                "average_age_months": 48,
                "inquiries_6m": 3,
                "delinquencies": 0,
                "late_payments_24m": 1,
            },
            "income_history": {
                "current_annual": 85000,
                "previous_annual": 65000,
                "years_reported": 3,
                "stable": False,
            },
            "location": "California",
            "risk_profile": "medium",
        },
    }

    def __init__(self):
        """Initialize ApplicantDB MCP Server."""
        self.logger = get_logger("mcp_servers.applicant_db")
        self.logger.info("ApplicantDB MCP Server initialized")

    def get_applicant_profile(self, applicant_id: str) -> Dict[str, Any]:
        """
        Retrieve complete applicant profile.

        Args:
            applicant_id: Unique applicant identifier

        Returns:
            Applicant profile data
        """
        self.logger.debug(f"Fetching applicant profile: {applicant_id}")

        if applicant_id not in self.MOCK_APPLICANTS:
            return {"error": f"Applicant {applicant_id} not found", "success": False}

        return {
            "success": True,
            "data": self.MOCK_APPLICANTS[applicant_id],
        }

    def get_employment_history(self, applicant_id: str) -> Dict[str, Any]:
        """
        Retrieve employment history and verification.

        Args:
            applicant_id: Unique applicant identifier

        Returns:
            Employment history data
        """
        self.logger.debug(f"Fetching employment history: {applicant_id}")

        if applicant_id not in self.MOCK_APPLICANTS:
            return {"error": f"Applicant {applicant_id} not found", "success": False}

        applicant = self.MOCK_APPLICANTS[applicant_id]
        return {
            "success": True,
            "data": {
                "applicant_id": applicant_id,
                "current_employment": {
                    "employer": applicant["employer"],
                    "tenure_years": applicant["employment_tenure_years"],
                    "employment_type": applicant["employment_type"],
                },
                "previous_employers": applicant.get("previous_employers", []),
                "employment_gaps": [],
                "verified": True,
            },
        }

    def get_credit_history(self, applicant_id: str) -> Dict[str, Any]:
        """
        Retrieve credit history summary.

        Args:
            applicant_id: Unique applicant identifier

        Returns:
            Credit history data
        """
        self.logger.debug(f"Fetching credit history: {applicant_id}")

        if applicant_id not in self.MOCK_APPLICANTS:
            return {"error": f"Applicant {applicant_id} not found", "success": False}

        applicant = self.MOCK_APPLICANTS[applicant_id]
        return {
            "success": True,
            "data": {
                "applicant_id": applicant_id,
                "credit_history": applicant["credit_history"],
                "summary": {
                    "total_accounts": applicant["credit_history"]["accounts"],
                    "recent_inquiries": applicant["credit_history"]["inquiries_6m"],
                    "delinquencies": applicant["credit_history"]["delinquencies"],
                    "late_payments_24m": applicant["credit_history"]["late_payments_24m"],
                },
            },
        }

    def calculate_income_stability(self, applicant_id: str) -> Dict[str, Any]:
        """
        Calculate income stability score (0-100).

        Args:
            applicant_id: Unique applicant identifier

        Returns:
            Income stability score
        """
        self.logger.debug(f"Calculating income stability: {applicant_id}")

        if applicant_id not in self.MOCK_APPLICANTS:
            return {"error": f"Applicant {applicant_id} not found", "success": False}

        applicant = self.MOCK_APPLICANTS[applicant_id]
        income_hist = applicant["income_history"]

        # Calculate stability score based on:
        # 1. Years of reported income history (30%)
        # 2. Employment tenure (30%)
        # 3. Income growth consistency (25%)
        # 4. Current employment type (15%)

        years_score = min(income_hist["years_reported"] / 5 * 30, 30)
        tenure_score = min(applicant["employment_tenure_years"] / 5 * 30, 30)

        # Income growth score
        if income_hist["years_reported"] > 1:
            annual_growth = (
                (income_hist["current_annual"] - income_hist["previous_annual"])
                / income_hist["previous_annual"]
                * 100
            )
            growth_score = min(abs(annual_growth) / 10 * 25, 25)
        else:
            growth_score = 12.5

        # Employment type score
        employment_type_scores = {
            "Full-time": 15,
            "Part-time": 10,
            "Self-employed": 7,
            "Retired": 8,
            "Student": 0,
            "Unemployed": 0,
        }
        employment_score = employment_type_scores.get(applicant["employment_type"], 5)

        total_score = years_score + tenure_score + growth_score + employment_score
        return {
            "success": True,
            "data": {
                "applicant_id": applicant_id,
                "income_stability_score": round(total_score, 2),
                "score_components": {
                    "years_history": years_score,
                    "employment_tenure": tenure_score,
                    "income_growth": growth_score,
                    "employment_type": employment_score,
                },
                "interpretation": "High stability" if total_score > 75 else "Medium stability" if total_score > 50 else "Low stability",
            },
        }

    def get_employment_risk(self, applicant_id: str) -> Dict[str, Any]:
        """
        Assess employment risk level.

        Args:
            applicant_id: Unique applicant identifier

        Returns:
            Employment risk assessment
        """
        self.logger.debug(f"Assessing employment risk: {applicant_id}")

        if applicant_id not in self.MOCK_APPLICANTS:
            return {"error": f"Applicant {applicant_id} not found", "success": False}

        applicant = self.MOCK_APPLICANTS[applicant_id]

        # Determine risk based on:
        # 1. Employment tenure
        # 2. Employment type
        # 3. Previous employment gaps
        # 4. Industry

        tenure = applicant["employment_tenure_years"]
        emp_type = applicant["employment_type"]

        if tenure < 1:
            risk_level = "high"
            risk_score = 80
        elif tenure < 2:
            risk_level = "medium"
            risk_score = 60
        elif emp_type == "Self-employed":
            risk_level = "medium"
            risk_score = 55
        else:
            risk_level = "low"
            risk_score = 25

        return {
            "success": True,
            "data": {
                "applicant_id": applicant_id,
                "employment_risk_level": risk_level,
                "risk_score": risk_score,
                "tenure_years": tenure,
                "employment_type": emp_type,
                "factors": {
                    "tenure": "Low" if tenure > 3 else "Medium" if tenure > 1 else "High",
                    "employment_type": "Self-employed" if emp_type == "Self-employed" else "Stable",
                    "employment_gaps": "None detected",
                },
            },
        }

    def verify_applicant_data_completeness(self, applicant_id: str) -> Dict[str, Any]:
        """
        Check completeness of applicant data.

        Args:
            applicant_id: Unique applicant identifier

        Returns:
            Data completeness assessment
        """
        self.logger.debug(f"Verifying applicant data completeness: {applicant_id}")

        if applicant_id not in self.MOCK_APPLICANTS:
            return {"error": f"Applicant {applicant_id} not found", "success": False}

        applicant = self.MOCK_APPLICANTS[applicant_id]

        required_fields = [
            "applicant_id",
            "name",
            "age",
            "employment_type",
            "employment_tenure_years",
            "credit_history",
            "income_history",
            "location",
        ]

        missing_fields = [f for f in required_fields if f not in applicant or not applicant[f]]
        completeness_percentage = ((len(required_fields) - len(missing_fields)) / len(required_fields)) * 100

        return {
            "success": True,
            "data": {
                "applicant_id": applicant_id,
                "completeness_percentage": completeness_percentage,
                "complete": len(missing_fields) == 0,
                "missing_fields": missing_fields,
                "warnings": [] if completeness_percentage > 80 else ["Incomplete profile data"],
            },
        }

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools for Claude."""
        return [
            {
                "name": "get_applicant_profile",
                "description": "Retrieve complete applicant profile with all personal and employment information",
                "input_schema": {
                    "properties": {"applicant_id": {"type": "string", "description": "Unique applicant identifier"}},
                    "required": ["applicant_id"],
                },
            },
            {
                "name": "get_employment_history",
                "description": "Retrieve employment history and current employment verification",
                "input_schema": {
                    "properties": {"applicant_id": {"type": "string", "description": "Unique applicant identifier"}},
                    "required": ["applicant_id"],
                },
            },
            {
                "name": "get_credit_history",
                "description": "Retrieve credit history summary and credit account information",
                "input_schema": {
                    "properties": {"applicant_id": {"type": "string", "description": "Unique applicant identifier"}},
                    "required": ["applicant_id"],
                },
            },
            {
                "name": "calculate_income_stability",
                "description": "Calculate income stability score (0-100) based on income history and employment tenure",
                "input_schema": {
                    "properties": {"applicant_id": {"type": "string", "description": "Unique applicant identifier"}},
                    "required": ["applicant_id"],
                },
            },
            {
                "name": "get_employment_risk",
                "description": "Assess employment risk level (low/medium/high)",
                "input_schema": {
                    "properties": {"applicant_id": {"type": "string", "description": "Unique applicant identifier"}},
                    "required": ["applicant_id"],
                },
            },
            {
                "name": "verify_applicant_data_completeness",
                "description": "Check completeness of applicant data and identify missing information",
                "input_schema": {
                    "properties": {"applicant_id": {"type": "string", "description": "Unique applicant identifier"}},
                    "required": ["applicant_id"],
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
        self.logger.debug(f"Handling tool call: {tool_name} with input: {tool_input}")

        if tool_name == "get_applicant_profile":
            result = self.get_applicant_profile(tool_input.get("applicant_id", ""))
        elif tool_name == "get_employment_history":
            result = self.get_employment_history(tool_input.get("applicant_id", ""))
        elif tool_name == "get_credit_history":
            result = self.get_credit_history(tool_input.get("applicant_id", ""))
        elif tool_name == "calculate_income_stability":
            result = self.calculate_income_stability(tool_input.get("applicant_id", ""))
        elif tool_name == "get_employment_risk":
            result = self.get_employment_risk(tool_input.get("applicant_id", ""))
        elif tool_name == "verify_applicant_data_completeness":
            result = self.verify_applicant_data_completeness(tool_input.get("applicant_id", ""))
        else:
            result = {"error": f"Unknown tool: {tool_name}"}

        return json.dumps(result)
