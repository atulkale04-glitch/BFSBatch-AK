"""MCP Server: RiskRulesDB - Financial risk analysis and calculations."""

import json
import logging
from typing import Any, Dict, List

from config.thresholds import CREDIT_SCORE_THRESHOLDS, DTI_RATIO_THRESHOLDS, LOAN_AMOUNT_RISK_THRESHOLDS
from src.utils.logger import get_logger
from src.utils.validators import calculate_dti_ratio

logger = get_logger(__name__)


class RiskRulesDBServer:
    """MCP Server for financial risk analysis and rule-based calculations."""

    def __init__(self):
        """Initialize RiskRulesDB MCP Server."""
        self.logger = get_logger("mcp_servers.risk_rules_db")
        self.logger.info("RiskRulesDB MCP Server initialized")

    def calculate_dti_ratio(
        self,
        income: float,
        existing_liabilities: float,
        loan_amount: float,
        tenure_months: int,
    ) -> Dict[str, Any]:
        """
        Calculate Debt-to-Income ratio.

        Args:
            income: Annual income
            existing_liabilities: Total existing monthly debt
            loan_amount: Requested loan amount
            tenure_months: Loan tenure in months

        Returns:
            DTI ratio with risk classification
        """
        self.logger.debug(f"Calculating DTI: income={income}, liabilities={existing_liabilities}, loan={loan_amount}")

        try:
            dti = calculate_dti_ratio(income, existing_liabilities, loan_amount, tenure_months)

            # Classify DTI risk
            risk_level = "low"
            if dti >= DTI_RATIO_THRESHOLDS["high_risk"][0]:
                risk_level = "high"
            elif dti >= DTI_RATIO_THRESHOLDS["medium_risk"][0]:
                risk_level = "medium"

            return {
                "success": True,
                "data": {
                    "dti_ratio": dti,
                    "dti_risk_level": risk_level,
                    "dti_percentage": round(dti * 100, 2),
                    "thresholds": {
                        "low_risk": f"< {DTI_RATIO_THRESHOLDS['low_risk'][1]:.2%}",
                        "medium_risk": f"{DTI_RATIO_THRESHOLDS['medium_risk'][0]:.2%} - {DTI_RATIO_THRESHOLDS['medium_risk'][1]:.2%}",
                        "high_risk": f"> {DTI_RATIO_THRESHOLDS['high_risk'][0]:.2%}",
                    },
                },
            }
        except Exception as e:
            self.logger.error(f"Error calculating DTI: {e}")
            return {"error": str(e), "success": False}

    def analyze_credit_score_risk(self, credit_score: int) -> Dict[str, Any]:
        """
        Analyze credit score and determine risk level.

        Args:
            credit_score: Applicant credit score (300-850)

        Returns:
            Credit risk classification
        """
        self.logger.debug(f"Analyzing credit score: {credit_score}")

        if credit_score < 300 or credit_score > 850:
            return {"error": "Credit score must be between 300 and 850", "success": False}

        # Determine credit rating
        credit_rating = None
        for rating, (min_score, max_score) in CREDIT_SCORE_THRESHOLDS.items():
            if min_score <= credit_score <= max_score:
                credit_rating = rating
                break

        # Map to risk level
        risk_map = {
            "poor": ("high", 85),
            "fair": ("medium", 60),
            "good": ("low", 30),
            "very_good": ("low", 15),
            "excellent": ("low", 5),
        }

        risk_level, risk_score = risk_map.get(credit_rating, ("unknown", 50))

        return {
            "success": True,
            "data": {
                "credit_score": credit_score,
                "credit_rating": credit_rating,
                "credit_score_risk_level": risk_level,
                "credit_risk_score": risk_score,
                "interpretation": f"{credit_rating.replace('_', ' ').title()} credit rating indicates {risk_level} risk",
            },
        }

    def assess_loan_amount_risk(self, loan_amount: float, annual_income: float) -> Dict[str, Any]:
        """
        Assess loan amount risk based on loan-to-income ratio.

        Args:
            loan_amount: Requested loan amount
            annual_income: Applicant annual income

        Returns:
            Loan amount risk assessment
        """
        self.logger.debug(f"Assessing loan risk: amount={loan_amount}, income={annual_income}")

        if annual_income <= 0:
            return {"error": "Annual income must be positive", "success": False}

        # Calculate loan-to-income ratio
        loan_to_income = loan_amount / annual_income

        # Determine risk level
        risk_level = "low"
        risk_score = 20

        if loan_to_income >= LOAN_AMOUNT_RISK_THRESHOLDS["high_risk"][0]:
            risk_level = "high"
            risk_score = 75
        elif loan_to_income >= LOAN_AMOUNT_RISK_THRESHOLDS["medium_risk"][0]:
            risk_level = "medium"
            risk_score = 50

        return {
            "success": True,
            "data": {
                "loan_amount": loan_amount,
                "annual_income": annual_income,
                "loan_to_income_ratio": round(loan_to_income, 2),
                "loan_amount_risk": risk_level,
                "loan_risk_score": risk_score,
                "interpretation": f"Loan amount is {round(loan_to_income, 1)}x annual income",
            },
        }

    def detect_financial_anomalies(
        self,
        credit_score: int,
        dti_ratio: float,
        income: float,
        existing_liabilities: float,
        loan_amount: float,
    ) -> Dict[str, Any]:
        """
        Detect financial anomalies and red flags.

        Args:
            credit_score: Credit score
            dti_ratio: Debt-to-income ratio
            income: Annual income
            existing_liabilities: Total liabilities
            loan_amount: Requested loan amount

        Returns:
            List of detected anomalies
        """
        self.logger.debug("Detecting financial anomalies")

        anomalies = []

        # Check credit score anomalies
        if credit_score < 500:
            anomalies.append("Very low credit score (<500)")
        if credit_score < 620:
            anomalies.append("Poor credit score (< 620) - subprime range")

        # Check DTI anomalies
        if dti_ratio > 0.60:
            anomalies.append("Very high DTI ratio (>60%)")
        if dti_ratio > 0.50:
            anomalies.append("High DTI ratio (>50%)")

        # Check income vs liabilities
        if existing_liabilities > income:
            anomalies.append("Total liabilities exceed annual income")

        # Check loan vs income anomalies
        if loan_amount > income * 5:
            anomalies.append("Loan amount exceeds 5x annual income")

        # Check for suspicious patterns
        if existing_liabilities > 0 and dti_ratio > 0.45:
            anomalies.append("High existing debt burden combined with high DTI")

        return {
            "success": True,
            "data": {
                "anomalies_detected": len(anomalies),
                "anomalies": anomalies,
                "risk_level": "high" if len(anomalies) > 2 else "medium" if len(anomalies) > 0 else "low",
                "requires_manual_review": len(anomalies) > 1,
            },
        }

    def apply_risk_rules(
        self,
        credit_score: int,
        dti_ratio: float,
        income_stability: float,
        loan_amount: float,
        annual_income: float,
    ) -> Dict[str, Any]:
        """
        Apply company risk rules and policies.

        Args:
            credit_score: Credit score
            dti_ratio: DTI ratio
            income_stability: Income stability score (0-100)
            loan_amount: Loan amount
            annual_income: Annual income

        Returns:
            Risk assessment with policy check
        """
        self.logger.debug("Applying risk rules and policies")

        from config.thresholds import APPROVAL_POLICY, RISK_SCORE_WEIGHTS

        violations = []
        policy_compliance = {}

        # Check credit score policy
        if credit_score < APPROVAL_POLICY["min_credit_score"]:
            violations.append(f"Credit score below minimum ({credit_score} < {APPROVAL_POLICY['min_credit_score']})")
            policy_compliance["credit_score"] = False
        else:
            policy_compliance["credit_score"] = True

        # Check DTI policy
        if dti_ratio > APPROVAL_POLICY["max_dti_ratio"]:
            violations.append(f"DTI ratio exceeds maximum ({dti_ratio:.2%} > {APPROVAL_POLICY['max_dti_ratio']:.2%})")
            policy_compliance["dti_ratio"] = False
        else:
            policy_compliance["dti_ratio"] = True

        # Check income stability policy
        if income_stability < APPROVAL_POLICY["min_income_stability"]:
            violations.append(f"Income stability below minimum ({income_stability:.0f} < {APPROVAL_POLICY['min_income_stability']})")
            policy_compliance["income_stability"] = False
        else:
            policy_compliance["income_stability"] = True

        # Calculate composite risk score
        credit_risk = 100 - min(((credit_score - 300) / 550) * 100, 100)
        dti_risk = min(dti_ratio / APPROVAL_POLICY["max_dti_ratio"] * 100, 100)
        stability_risk = 100 - income_stability
        loan_risk = min((loan_amount / annual_income / 5) * 100, 100)

        composite_risk = (
            credit_risk * RISK_SCORE_WEIGHTS["credit_score"]
            + dti_risk * RISK_SCORE_WEIGHTS["dti_ratio"]
            + stability_risk * RISK_SCORE_WEIGHTS["income_stability"]
            + loan_risk * RISK_SCORE_WEIGHTS["loan_amount_risk"]
        )

        return {
            "success": True,
            "data": {
                "policy_compliance": policy_compliance,
                "violations": violations,
                "compliant_with_policy": len(violations) == 0,
                "composite_risk_score": round(composite_risk, 1),
                "risk_components": {
                    "credit_risk": round(credit_risk, 1),
                    "dti_risk": round(dti_risk, 1),
                    "stability_risk": round(stability_risk, 1),
                    "loan_risk": round(loan_risk, 1),
                },
            },
        }

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools for Claude."""
        return [
            {
                "name": "calculate_dti_ratio",
                "description": "Calculate Debt-to-Income ratio and classify risk level",
                "input_schema": {
                    "properties": {
                        "income": {"type": "number", "description": "Annual income"},
                        "existing_liabilities": {"type": "number", "description": "Total existing monthly debt obligations"},
                        "loan_amount": {"type": "number", "description": "Requested loan amount"},
                        "tenure_months": {"type": "integer", "description": "Loan tenure in months"},
                    },
                    "required": ["income", "existing_liabilities", "loan_amount", "tenure_months"],
                },
            },
            {
                "name": "analyze_credit_score_risk",
                "description": "Analyze credit score and determine risk level",
                "input_schema": {
                    "properties": {"credit_score": {"type": "integer", "description": "Credit score (300-850)"}},
                    "required": ["credit_score"],
                },
            },
            {
                "name": "assess_loan_amount_risk",
                "description": "Assess loan amount risk based on loan-to-income ratio",
                "input_schema": {
                    "properties": {
                        "loan_amount": {"type": "number", "description": "Requested loan amount"},
                        "annual_income": {"type": "number", "description": "Annual income"},
                    },
                    "required": ["loan_amount", "annual_income"],
                },
            },
            {
                "name": "detect_financial_anomalies",
                "description": "Detect financial anomalies and red flags",
                "input_schema": {
                    "properties": {
                        "credit_score": {"type": "integer", "description": "Credit score"},
                        "dti_ratio": {"type": "number", "description": "DTI ratio"},
                        "income": {"type": "number", "description": "Annual income"},
                        "existing_liabilities": {"type": "number", "description": "Total liabilities"},
                        "loan_amount": {"type": "number", "description": "Loan amount"},
                    },
                    "required": ["credit_score", "dti_ratio", "income", "existing_liabilities", "loan_amount"],
                },
            },
            {
                "name": "apply_risk_rules",
                "description": "Apply company risk rules and policies",
                "input_schema": {
                    "properties": {
                        "credit_score": {"type": "integer", "description": "Credit score"},
                        "dti_ratio": {"type": "number", "description": "DTI ratio"},
                        "income_stability": {"type": "number", "description": "Income stability score (0-100)"},
                        "loan_amount": {"type": "number", "description": "Loan amount"},
                        "annual_income": {"type": "number", "description": "Annual income"},
                    },
                    "required": ["credit_score", "dti_ratio", "income_stability", "loan_amount", "annual_income"],
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

        if tool_name == "calculate_dti_ratio":
            result = self.calculate_dti_ratio(
                tool_input.get("income", 0),
                tool_input.get("existing_liabilities", 0),
                tool_input.get("loan_amount", 0),
                tool_input.get("tenure_months", 0),
            )
        elif tool_name == "analyze_credit_score_risk":
            result = self.analyze_credit_score_risk(tool_input.get("credit_score", 0))
        elif tool_name == "assess_loan_amount_risk":
            result = self.assess_loan_amount_risk(
                tool_input.get("loan_amount", 0),
                tool_input.get("annual_income", 0),
            )
        elif tool_name == "detect_financial_anomalies":
            result = self.detect_financial_anomalies(
                tool_input.get("credit_score", 0),
                tool_input.get("dti_ratio", 0),
                tool_input.get("income", 0),
                tool_input.get("existing_liabilities", 0),
                tool_input.get("loan_amount", 0),
            )
        elif tool_name == "apply_risk_rules":
            result = self.apply_risk_rules(
                tool_input.get("credit_score", 0),
                tool_input.get("dti_ratio", 0),
                tool_input.get("income_stability", 0),
                tool_input.get("loan_amount", 0),
                tool_input.get("annual_income", 0),
            )
        else:
            result = {"error": f"Unknown tool: {tool_name}"}

        return json.dumps(result)
