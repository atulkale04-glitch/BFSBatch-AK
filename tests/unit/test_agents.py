"""Test specialized agent implementations."""

import pytest

from src.agents.applicant_profile_agent import ApplicantProfileAgent
from src.agents.compliance_orchestrator_agent import ComplianceOrchestratorAgent
from src.agents.financial_risk_agent import FinancialRiskAgent
from src.agents.loan_decision_agent import LoanDecisionAgent


class TestApplicantProfileAgent:
    """Test Applicant Profile Agent."""

    def setup_method(self):
        """Set up test fixtures."""
        self.agent = ApplicantProfileAgent()

    def test_agent_initialization(self):
        """Test agent initializes correctly."""
        assert self.agent.agent_name == "applicant_profile_agent"
        assert len(self.agent.tools) == 5

    def test_tool_names(self):
        """Test all tools are registered."""
        tool_names = [tool.name for tool in self.agent.tools]
        assert "get_applicant_profile" in tool_names
        assert "get_employment_history" in tool_names
        assert "get_credit_history" in tool_names
        assert "calculate_income_stability" in tool_names
        assert "get_employment_risk" in tool_names

    def test_format_input_for_claude(self):
        """Test input formatting for Claude."""
        input_data = {
            "applicant_id": "APP-001",
            "loan_amount": 250000,
            "credit_score": 720,
        }
        formatted = self.agent._format_input_for_claude(input_data)
        assert "APP-001" in formatted
        assert "250" in formatted  # Will appear as part of currency formatting
        assert "720" in formatted

    def test_validate_output_valid(self):
        """Test output validation with valid data."""
        output = {
            "success": True,
            "data": {
                "income_stability_score": 85,
                "employment_risk": "low",
                "credit_history_summary": "Good history",
                "completeness_flags": [],
            },
        }
        is_valid, errors = self.agent.validate_output(output)
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_output_invalid_score(self):
        """Test output validation with invalid score."""
        output = {
            "success": True,
            "data": {
                "income_stability_score": 150,  # Invalid: > 100
                "employment_risk": "low",
                "credit_history_summary": "Good",
                "completeness_flags": [],
            },
        }
        is_valid, errors = self.agent.validate_output(output)
        assert is_valid is False
        assert any("income_stability_score" in e for e in errors)

    def test_validate_output_invalid_risk_level(self):
        """Test output validation with invalid risk level."""
        output = {
            "success": True,
            "data": {
                "income_stability_score": 85,
                "employment_risk": "unknown",  # Invalid value
                "credit_history_summary": "Good",
                "completeness_flags": [],
            },
        }
        is_valid, errors = self.agent.validate_output(output)
        assert is_valid is False


class TestFinancialRiskAgent:
    """Test Financial Risk Agent."""

    def setup_method(self):
        """Set up test fixtures."""
        self.agent = FinancialRiskAgent()

    def test_agent_initialization(self):
        """Test agent initializes correctly."""
        assert self.agent.agent_name == "financial_risk_agent"
        assert len(self.agent.tools) == 5

    def test_tool_names(self):
        """Test all tools are registered."""
        tool_names = [tool.name for tool in self.agent.tools]
        assert "calculate_dti_ratio" in tool_names
        assert "analyze_credit_score_risk" in tool_names
        assert "assess_loan_amount_risk" in tool_names
        assert "detect_financial_anomalies" in tool_names
        assert "apply_risk_rules" in tool_names

    def test_format_input_for_claude(self):
        """Test input formatting for Claude."""
        input_data = {
            "applicant_id": "APP-001",
            "income": 75000,
            "credit_score": 720,
            "loan_amount": 250000,
        }
        formatted = self.agent._format_input_for_claude(input_data)
        assert "75" in formatted  # Will appear as part of currency formatting
        assert "720" in formatted
        assert "250" in formatted  # Will appear as part of currency formatting

    def test_validate_output_valid(self):
        """Test output validation with valid data."""
        output = {
            "success": True,
            "data": {
                "dti_ratio": 0.35,
                "credit_score_risk": "low",
                "loan_amount_risk": "low",
                "composite_risk_score": 30,
                "anomalies": [],
            },
        }
        is_valid, errors = self.agent.validate_output(output)
        assert is_valid is True

    def test_validate_output_invalid_risk_score(self):
        """Test output validation with invalid risk score."""
        output = {
            "success": True,
            "data": {
                "dti_ratio": 0.35,
                "credit_score_risk": "low",
                "loan_amount_risk": "low",
                "composite_risk_score": 150,  # Invalid: > 100
                "anomalies": [],
            },
        }
        is_valid, errors = self.agent.validate_output(output)
        assert is_valid is False


class TestLoanDecisionAgent:
    """Test Loan Decision Agent."""

    def setup_method(self):
        """Set up test fixtures."""
        self.agent = LoanDecisionAgent()

    def test_agent_initialization(self):
        """Test agent initializes correctly."""
        assert self.agent.agent_name == "loan_decision_agent"
        assert len(self.agent.tools) == 4

    def test_tool_names(self):
        """Test all tools are registered."""
        tool_names = [tool.name for tool in self.agent.tools]
        assert "retrieve_evaluations" in tool_names
        assert "calculate_composite_risk" in tool_names
        assert "resolve_conflicting_recommendations" in tool_names
        assert "prepare_decision_summary" in tool_names

    def test_format_input_for_claude(self):
        """Test input formatting for Claude."""
        input_data = {
            "application_id": "LOAN-001",
            "loan_amount": 250000,
            "income": 75000,
        }
        formatted = self.agent._format_input_for_claude(input_data)
        assert "LOAN-001" in formatted
        assert "250" in formatted  # Will appear as part of currency formatting

    def test_validate_output_valid(self):
        """Test output validation with valid data."""
        output = {
            "success": True,
            "data": {
                "final_decision": "APPROVED",
                "risk_score": 35,
                "confidence_level": 90,
                "key_factors": ["Strong credit", "Low DTI"],
            },
        }
        is_valid, errors = self.agent.validate_output(output)
        assert is_valid is True

    def test_validate_output_invalid_decision(self):
        """Test output validation with invalid decision."""
        output = {
            "success": True,
            "data": {
                "final_decision": "MAYBE",  # Invalid value
                "risk_score": 35,
                "confidence_level": 90,
                "key_factors": [],
            },
        }
        is_valid, errors = self.agent.validate_output(output)
        assert is_valid is False
        assert any("final_decision" in e for e in errors)

    def test_validate_output_invalid_confidence(self):
        """Test output validation with invalid confidence."""
        output = {
            "success": True,
            "data": {
                "final_decision": "APPROVED",
                "risk_score": 35,
                "confidence_level": 150,  # Invalid: > 100
                "key_factors": [],
            },
        }
        is_valid, errors = self.agent.validate_output(output)
        assert is_valid is False


class TestComplianceOrchestratorAgent:
    """Test Compliance & Action Orchestrator Agent."""

    def setup_method(self):
        """Set up test fixtures."""
        self.agent = ComplianceOrchestratorAgent()

    def test_agent_initialization(self):
        """Test agent initializes correctly."""
        assert self.agent.agent_name == "compliance_orchestrator_agent"
        assert len(self.agent.tools) == 7

    def test_tool_names(self):
        """Test all tools are registered."""
        tool_names = [tool.name for tool in self.agent.tools]
        assert "generate_case_id" in tool_names
        assert "execute_approval_decision" in tool_names
        assert "execute_rejection_decision" in tool_names
        assert "flag_for_manual_review" in tool_names
        assert "send_decision_notification" in tool_names
        assert "log_action" in tool_names
        assert "retrieve_audit_trail" in tool_names

    def test_format_input_for_claude(self):
        """Test input formatting for Claude."""
        input_data = {
            "application_id": "LOAN-001",
            "decision": "APPROVED",
            "applicant_email": "test@example.com",
            "risk_score": 35,
        }
        formatted = self.agent._format_input_for_claude(input_data)
        assert "LOAN-001" in formatted
        assert "APPROVED" in formatted
        assert "test@example.com" in formatted

    def test_validate_output_valid(self):
        """Test output validation with valid data."""
        output = {
            "success": True,
            "data": {
                "case_id": "CASE-20241028-ABC123",
                "action_taken": "APPROVED",
                "notification_status": "sent",
                "audit_entries_count": 2,
            },
        }
        is_valid, errors = self.agent.validate_output(output)
        assert is_valid is True

    def test_validate_output_invalid_action(self):
        """Test output validation with invalid action."""
        output = {
            "success": True,
            "data": {
                "case_id": "CASE-20241028-ABC123",
                "action_taken": "UNKNOWN",  # Invalid value
                "notification_status": "sent",
            },
        }
        is_valid, errors = self.agent.validate_output(output)
        assert is_valid is False


class TestAgentIntegration:
    """Test agent integration."""

    def test_all_agents_instantiate(self):
        """Test all agents can be instantiated."""
        agents = [
            ApplicantProfileAgent(),
            FinancialRiskAgent(),
            LoanDecisionAgent(),
            ComplianceOrchestratorAgent(),
        ]
        assert len(agents) == 4
        assert all(agent.tools for agent in agents)

    def test_agents_have_system_prompts(self):
        """Test all agents have system prompts."""
        agents = [
            ApplicantProfileAgent(),
            FinancialRiskAgent(),
            LoanDecisionAgent(),
            ComplianceOrchestratorAgent(),
        ]
        for agent in agents:
            assert agent.system_prompt is not None
            assert len(agent.system_prompt) > 0

    def test_agents_can_format_input(self):
        """Test all agents can format input for Claude."""
        agents = [
            ApplicantProfileAgent(),
            FinancialRiskAgent(),
            LoanDecisionAgent(),
            ComplianceOrchestratorAgent(),
        ]
        test_data = {
            "applicant_id": "APP-001",
            "application_id": "LOAN-001",
            "loan_amount": 250000,
            "income": 75000,
            "credit_score": 720,
            "decision": "APPROVED",
            "applicant_email": "test@example.com",
        }

        for agent in agents:
            formatted = agent._format_input_for_claude(test_data)
            assert isinstance(formatted, str)
            assert len(formatted) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
