"""Test MCP server implementations."""

import json

import pytest

from src.mcp_servers.applicant_db import ApplicantDBServer
from src.mcp_servers.decision_synthesis import DecisionSynthesisServer
from src.mcp_servers.notification_system import NotificationSystemServer
from src.mcp_servers.risk_rules_db import RiskRulesDBServer


class TestApplicantDBServer:
    """Test ApplicantDB MCP Server."""

    def setup_method(self):
        """Set up test fixtures."""
        self.server = ApplicantDBServer()

    def test_get_applicant_profile(self):
        """Test retrieving applicant profile."""
        result = self.server.get_applicant_profile("APP-001")
        assert result["success"] is True
        assert result["data"]["applicant_id"] == "APP-001"
        assert "name" in result["data"]

    def test_get_applicant_profile_not_found(self):
        """Test retrieving non-existent applicant."""
        result = self.server.get_applicant_profile("APP-999")
        assert result["success"] is False

    def test_get_employment_history(self):
        """Test retrieving employment history."""
        result = self.server.get_employment_history("APP-001")
        assert result["success"] is True
        assert "current_employment" in result["data"]

    def test_get_credit_history(self):
        """Test retrieving credit history."""
        result = self.server.get_credit_history("APP-001")
        assert result["success"] is True
        assert "credit_history" in result["data"]

    def test_calculate_income_stability(self):
        """Test income stability calculation."""
        result = self.server.calculate_income_stability("APP-001")
        assert result["success"] is True
        assert "income_stability_score" in result["data"]
        assert 0 <= result["data"]["income_stability_score"] <= 100

    def test_get_employment_risk(self):
        """Test employment risk assessment."""
        result = self.server.get_employment_risk("APP-001")
        assert result["success"] is True
        assert result["data"]["employment_risk_level"] in ["low", "medium", "high"]

    def test_verify_applicant_data_completeness(self):
        """Test data completeness check."""
        result = self.server.verify_applicant_data_completeness("APP-001")
        assert result["success"] is True
        assert "completeness_percentage" in result["data"]

    def test_get_available_tools(self):
        """Test tool list generation."""
        tools = self.server.get_available_tools()
        assert len(tools) == 6
        tool_names = [t["name"] for t in tools]
        assert "get_applicant_profile" in tool_names
        assert "calculate_income_stability" in tool_names

    def test_handle_tool_call(self):
        """Test tool call handling."""
        result_json = self.server.handle_tool_call("get_applicant_profile", {"applicant_id": "APP-001"})
        result = json.loads(result_json)
        assert result["success"] is True


class TestRiskRulesDBServer:
    """Test RiskRulesDB MCP Server."""

    def setup_method(self):
        """Set up test fixtures."""
        self.server = RiskRulesDBServer()

    def test_calculate_dti_ratio(self):
        """Test DTI ratio calculation."""
        result = self.server.calculate_dti_ratio(
            income=75000,
            existing_liabilities=500,
            loan_amount=250000,
            tenure_months=360,
        )
        assert result["success"] is True
        assert "dti_ratio" in result["data"]
        assert "dti_risk_level" in result["data"]

    def test_analyze_credit_score_risk(self):
        """Test credit score risk analysis."""
        result = self.server.analyze_credit_score_risk(credit_score=750)
        assert result["success"] is True
        assert result["data"]["credit_rating"] == "very_good"
        assert result["data"]["credit_score_risk_level"] == "low"

    def test_analyze_credit_score_risk_invalid(self):
        """Test credit score risk analysis with invalid score."""
        result = self.server.analyze_credit_score_risk(credit_score=1000)
        assert result["success"] is False

    def test_assess_loan_amount_risk(self):
        """Test loan amount risk assessment."""
        result = self.server.assess_loan_amount_risk(
            loan_amount=250000,
            annual_income=75000,
        )
        assert result["success"] is True
        assert "loan_to_income_ratio" in result["data"]
        assert "loan_amount_risk" in result["data"]

    def test_detect_financial_anomalies(self):
        """Test anomaly detection."""
        result = self.server.detect_financial_anomalies(
            credit_score=600,
            dti_ratio=0.65,
            income=50000,
            existing_liabilities=100000,
            loan_amount=300000,
        )
        assert result["success"] is True
        assert len(result["data"]["anomalies"]) > 0

    def test_detect_no_anomalies(self):
        """Test anomaly detection with clean data."""
        result = self.server.detect_financial_anomalies(
            credit_score=750,
            dti_ratio=0.25,
            income=100000,
            existing_liabilities=20000,
            loan_amount=200000,
        )
        assert result["success"] is True
        assert len(result["data"]["anomalies"]) == 0

    def test_apply_risk_rules(self):
        """Test risk rule application."""
        result = self.server.apply_risk_rules(
            credit_score=720,
            dti_ratio=0.35,
            income_stability=85,
            loan_amount=250000,
            annual_income=75000,
        )
        assert result["success"] is True
        assert "policy_compliance" in result["data"]
        assert "composite_risk_score" in result["data"]

    def test_get_available_tools(self):
        """Test tool list generation."""
        tools = self.server.get_available_tools()
        assert len(tools) == 5
        tool_names = [t["name"] for t in tools]
        assert "calculate_dti_ratio" in tool_names


class TestDecisionSynthesisServer:
    """Test DecisionSynthesis MCP Server."""

    def setup_method(self):
        """Set up test fixtures."""
        self.server = DecisionSynthesisServer()

    def test_store_evaluation(self):
        """Test storing evaluation."""
        result = self.server.store_evaluation(
            application_id="LOAN-001",
            agent_name="applicant_profile_agent",
            evaluation_result={"income_stability_score": 85},
            confidence_score=92,
        )
        assert result["success"] is True

    def test_retrieve_evaluations(self):
        """Test retrieving evaluations."""
        # Store first
        self.server.store_evaluation(
            application_id="LOAN-002",
            agent_name="test_agent",
            evaluation_result={"score": 50},
        )

        # Retrieve
        result = self.server.retrieve_evaluations("LOAN-002")
        assert result["success"] is True
        assert "test_agent" in result["data"]["evaluations"]

    def test_calculate_composite_risk(self):
        """Test composite risk calculation."""
        # Store multiple evaluations
        self.server.store_evaluation(
            application_id="LOAN-003",
            agent_name="agent1",
            evaluation_result={"risk_score": 30},
        )
        self.server.store_evaluation(
            application_id="LOAN-003",
            agent_name="agent2",
            evaluation_result={"risk_score": 40},
        )

        # Calculate composite
        result = self.server.calculate_composite_risk("LOAN-003")
        assert result["success"] is True
        assert result["data"]["composite_risk_score"] == 35

    def test_prepare_decision_summary(self):
        """Test decision summary preparation."""
        result = self.server.prepare_decision_summary(
            application_id="LOAN-004",
            final_decision="APPROVED",
            risk_score=25,
            confidence_level=95,
            key_factors=["Strong credit", "Low DTI"],
        )
        assert result["success"] is True
        assert result["data"]["decision"] == "APPROVED"

    def test_validate_decision_consistency(self):
        """Test consistency validation."""
        self.server.store_evaluation(
            application_id="LOAN-005",
            agent_name="applicant_profile_agent",
            evaluation_result={},
        )

        result = self.server.validate_decision_consistency("LOAN-005")
        assert result["success"] is True

    def test_get_available_tools(self):
        """Test tool list generation."""
        tools = self.server.get_available_tools()
        assert len(tools) == 6


class TestNotificationSystemServer:
    """Test NotificationSystem MCP Server."""

    def setup_method(self):
        """Set up test fixtures."""
        self.server = NotificationSystemServer()

    def test_generate_case_id(self):
        """Test case ID generation."""
        result = self.server.generate_case_id()
        assert result["success"] is True
        assert result["data"]["case_id"].startswith("CASE-")

    def test_send_decision_notification(self):
        """Test sending notification."""
        result = self.server.send_decision_notification(
            application_id="LOAN-006",
            applicant_email="test@example.com",
            decision="APPROVED",
            risk_score=25,
            explanation="Approved based on strong profile",
        )
        assert result["success"] is True
        assert result["data"]["delivery_status"] == "sent"

    def test_log_action(self):
        """Test action logging."""
        result = self.server.log_action(
            application_id="LOAN-007",
            action="TEST_ACTION",
            details={"test": "data"},
        )
        assert result["success"] is True

    def test_execute_approval_decision(self):
        """Test approval decision execution."""
        result = self.server.execute_approval_decision(
            application_id="LOAN-008",
            case_id="CASE-001",
            risk_score=25,
            key_factors=["Strong credit"],
        )
        assert result["success"] is True
        assert result["data"]["decision"] == "APPROVED"

    def test_execute_rejection_decision(self):
        """Test rejection decision execution."""
        result = self.server.execute_rejection_decision(
            application_id="LOAN-009",
            case_id="CASE-002",
            risk_score=80,
            reason="High DTI ratio",
        )
        assert result["success"] is True
        assert result["data"]["decision"] == "REJECTED"

    def test_flag_for_manual_review(self):
        """Test flagging for manual review."""
        result = self.server.flag_for_manual_review(
            application_id="LOAN-010",
            case_id="CASE-003",
            reason="Borderline case",
            risk_score=50,
        )
        assert result["success"] is True
        assert result["data"]["status"] == "MANUAL_REVIEW"

    def test_retrieve_audit_trail(self):
        """Test retrieving audit trail."""
        self.server.log_action(
            application_id="LOAN-011",
            action="TEST",
        )

        result = self.server.retrieve_audit_trail("LOAN-011")
        assert result["success"] is True
        assert len(result["data"]["audit_entries"]) > 0

    def test_get_available_tools(self):
        """Test tool list generation."""
        tools = self.server.get_available_tools()
        assert len(tools) == 7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
