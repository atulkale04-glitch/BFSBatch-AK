"""Financial Risk Analysis Agent - Evaluates financial risk metrics."""

import json
import re
from typing import Any, Dict, List

from config.prompts import FINANCIAL_RISK_PROMPT
from src.agents.base_agent import BaseAgent, Tool
from src.mcp_servers.risk_rules_db import RiskRulesDBServer
from src.utils.logger import get_logger

logger = get_logger(__name__)


class FinancialRiskAgent(BaseAgent):
    """Agent for analyzing financial risk and calculating risk metrics."""

    def __init__(self):
        """Initialize Financial Risk Analysis Agent."""
        self.mcp_server = RiskRulesDBServer()

        # Register all MCP server tools
        tools = [
            Tool(
                name="calculate_dti_ratio",
                description="Calculate Debt-to-Income ratio and classify risk level",
                input_schema={
                    "properties": {
                        "income": {"type": "number", "description": "Annual income"},
                        "existing_liabilities": {"type": "number", "description": "Total existing monthly debt"},
                        "loan_amount": {"type": "number", "description": "Requested loan amount"},
                        "tenure_months": {"type": "integer", "description": "Loan tenure in months"},
                    },
                    "required": ["income", "existing_liabilities", "loan_amount", "tenure_months"],
                },
                handler=self._handle_calculate_dti_ratio,
            ),
            Tool(
                name="analyze_credit_score_risk",
                description="Analyze credit score and determine risk level",
                input_schema={
                    "properties": {
                        "credit_score": {"type": "integer", "description": "Credit score (300-850)"}
                    },
                    "required": ["credit_score"],
                },
                handler=self._handle_analyze_credit_score_risk,
            ),
            Tool(
                name="assess_loan_amount_risk",
                description="Assess loan amount risk based on loan-to-income ratio",
                input_schema={
                    "properties": {
                        "loan_amount": {"type": "number", "description": "Requested loan amount"},
                        "annual_income": {"type": "number", "description": "Annual income"},
                    },
                    "required": ["loan_amount", "annual_income"],
                },
                handler=self._handle_assess_loan_amount_risk,
            ),
            Tool(
                name="detect_financial_anomalies",
                description="Detect financial anomalies and red flags",
                input_schema={
                    "properties": {
                        "credit_score": {"type": "integer", "description": "Credit score"},
                        "dti_ratio": {"type": "number", "description": "DTI ratio"},
                        "income": {"type": "number", "description": "Annual income"},
                        "existing_liabilities": {"type": "number", "description": "Total liabilities"},
                        "loan_amount": {"type": "number", "description": "Loan amount"},
                    },
                    "required": ["credit_score", "dti_ratio", "income", "existing_liabilities", "loan_amount"],
                },
                handler=self._handle_detect_financial_anomalies,
            ),
            Tool(
                name="apply_risk_rules",
                description="Apply company risk rules and policies to generate composite risk score",
                input_schema={
                    "properties": {
                        "credit_score": {"type": "integer", "description": "Credit score"},
                        "dti_ratio": {"type": "number", "description": "DTI ratio"},
                        "income_stability": {"type": "number", "description": "Income stability score (0-100)"},
                        "loan_amount": {"type": "number", "description": "Loan amount"},
                        "annual_income": {"type": "number", "description": "Annual income"},
                    },
                    "required": ["credit_score", "dti_ratio", "income_stability", "loan_amount", "annual_income"],
                },
                handler=self._handle_apply_risk_rules,
            ),
        ]

        super().__init__(
            agent_name="financial_risk_agent",
            system_prompt=FINANCIAL_RISK_PROMPT,
            tools=tools,
        )

    def _handle_calculate_dti_ratio(
        self,
        income: float,
        existing_liabilities: float,
        loan_amount: float,
        tenure_months: int,
    ) -> Dict[str, Any]:
        """Handle calculate_dti_ratio tool call."""
        return self.mcp_server.calculate_dti_ratio(income, existing_liabilities, loan_amount, tenure_months)

    def _handle_analyze_credit_score_risk(self, credit_score: int) -> Dict[str, Any]:
        """Handle analyze_credit_score_risk tool call."""
        return self.mcp_server.analyze_credit_score_risk(credit_score)

    def _handle_assess_loan_amount_risk(self, loan_amount: float, annual_income: float) -> Dict[str, Any]:
        """Handle assess_loan_amount_risk tool call."""
        return self.mcp_server.assess_loan_amount_risk(loan_amount, annual_income)

    def _handle_detect_financial_anomalies(
        self,
        credit_score: int,
        dti_ratio: float,
        income: float,
        existing_liabilities: float,
        loan_amount: float,
    ) -> Dict[str, Any]:
        """Handle detect_financial_anomalies tool call."""
        return self.mcp_server.detect_financial_anomalies(
            credit_score, dti_ratio, income, existing_liabilities, loan_amount
        )

    def _handle_apply_risk_rules(
        self,
        credit_score: int,
        dti_ratio: float,
        income_stability: float,
        loan_amount: float,
        annual_income: float,
    ) -> Dict[str, Any]:
        """Handle apply_risk_rules tool call."""
        return self.mcp_server.apply_risk_rules(credit_score, dti_ratio, income_stability, loan_amount, annual_income)

    def _format_input_for_claude(self, input_data: Dict[str, Any]) -> str:
        """Format financial data into a prompt for Claude."""
        return f"""Perform comprehensive financial risk analysis for the following applicant:

Application Details:
- Applicant ID: {input_data.get('applicant_id', '')}
- Age: {input_data.get('age', 0)}
- Income: ${input_data.get('income', 0):,.2f} per year
- Credit Score: {input_data.get('credit_score', 0)}
- Loan Amount Requested: ${input_data.get('loan_amount', 0):,.2f}
- Loan Tenure: {input_data.get('loan_tenure_months', 0)} months
- Existing Liabilities: ${input_data.get('existing_liabilities', 0):,.2f}

Please perform the following analysis:
1. Calculate DTI ratio using calculate_dti_ratio
2. Analyze credit score risk using analyze_credit_score_risk
3. Assess loan amount risk using assess_loan_amount_risk
4. Detect any financial anomalies using detect_financial_anomalies
5. Apply company risk rules using apply_risk_rules

Based on these analyses, provide:
- Debt-to-Income Ratio (as percentage)
- Credit Score Risk Level (low/medium/high)
- Loan Amount Risk Assessment
- Detected Anomalies (list)
- Composite Risk Score (0-100)
- Overall Risk Assessment and Reasoning

Format your final response as JSON with keys: dti_ratio, credit_score_risk, loan_amount_risk, anomalies, composite_risk_score, reasoning"""

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
                    "dti_ratio": 0,
                    "credit_score_risk": "unknown",
                    "loan_amount_risk": "unknown",
                    "anomalies": [],
                    "composite_risk_score": 50,
                    "reasoning": text_content,
                }
        except json.JSONDecodeError:
            result = {
                "dti_ratio": 0,
                "credit_score_risk": "unknown",
                "loan_amount_risk": "unknown",
                "anomalies": [],
                "composite_risk_score": 50,
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

        if "dti_ratio" not in data:
            errors.append("Missing dti_ratio")
        elif not (0 <= data.get("dti_ratio", 0) <= 1.0):
            errors.append("dti_ratio must be between 0 and 1.0")

        if "credit_score_risk" not in data:
            errors.append("Missing credit_score_risk")

        if "loan_amount_risk" not in data:
            errors.append("Missing loan_amount_risk")

        if "composite_risk_score" not in data:
            errors.append("Missing composite_risk_score")
        elif not (0 <= data.get("composite_risk_score", 0) <= 100):
            errors.append("composite_risk_score must be between 0 and 100")

        if "anomalies" not in data:
            errors.append("Missing anomalies")
        elif not isinstance(data["anomalies"], list):
            errors.append("anomalies must be a list")

        return len(errors) == 0, errors
