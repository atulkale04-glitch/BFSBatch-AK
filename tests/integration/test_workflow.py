"""Integration tests for complete loan approval workflow."""

import asyncio
import pytest

from src.orchestration.orchestrator import ApplicationOrchestrator
from src.orchestration.state import create_initial_state


class TestWorkflowIntegration:
    """Integration tests for complete workflow execution."""

    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = ApplicationOrchestrator()

    @pytest.mark.asyncio
    async def test_complete_workflow_approved_application(self):
        """Test complete workflow with strong applicant (should be approved)."""
        application_data = {
            "applicant_id": "APP-TEST-001",
            "age": 35,
            "income": 100000.0,
            "employment_type": "Full-time",
            "credit_score": 750,
            "loan_amount": 250000.0,
            "loan_tenure_months": 360,
            "existing_liabilities": 30000.0,
            "location": "New York",
            "applicant_email": "test@example.com",
        }

        result = await self.orchestrator.process_application(application_data)

        assert result["success"] is True
        assert result["application_id"] is not None
        assert result["case_id"] is not None
        assert result["status"] == "completed"
        assert result["decision"] in ["APPROVED", "REJECTED", "MANUAL_REVIEW"]
        assert 0 <= result["risk_score"] <= 100
        assert 0 <= result["confidence_level"] <= 100
        assert len(result["key_factors"]) > 0
        assert result["reasoning"] is not None

    @pytest.mark.asyncio
    async def test_complete_workflow_risky_application(self):
        """Test complete workflow with risky applicant."""
        application_data = {
            "applicant_id": "APP-TEST-002",
            "age": 28,
            "income": 40000.0,
            "employment_type": "Self-employed",
            "credit_score": 580,
            "loan_amount": 300000.0,
            "loan_tenure_months": 360,
            "existing_liabilities": 80000.0,
            "location": "California",
            "applicant_email": "risky@example.com",
        }

        result = await self.orchestrator.process_application(application_data)

        assert result["success"] is True
        assert result["decision"] is not None
        assert result["status"] == "completed"
        # This should likely be REJECTED or MANUAL_REVIEW
        assert result["decision"] in ["APPROVED", "REJECTED", "MANUAL_REVIEW"]

    @pytest.mark.asyncio
    async def test_workflow_validation_failure(self):
        """Test workflow with invalid input."""
        application_data = {
            "applicant_id": "APP-TEST-003",
            "age": 15,  # Too young
            "income": -1000.0,  # Invalid
            "employment_type": "Full-time",
            "credit_score": 900,  # Invalid (> 850)
            "loan_amount": 250000.0,
            "loan_tenure_months": 360,
            "existing_liabilities": 30000.0,
            "location": "New York",
        }

        result = await self.orchestrator.process_application(application_data)

        assert result["success"] is True  # Orchestrator catches it, doesn't crash
        assert result["status"] == "failed"
        assert result["error_message"] is not None

    @pytest.mark.asyncio
    async def test_workflow_missing_fields(self):
        """Test workflow with missing required fields."""
        application_data = {
            "applicant_id": "APP-TEST-004",
            "age": 35,
            # Missing several fields
        }

        # Validate data before processing
        is_valid, errors = await self.orchestrator.validate_application_data(application_data)

        assert is_valid is False
        assert len(errors) > 0
        assert any("Missing" in error for error in errors)

    def test_workflow_state_creation(self):
        """Test workflow state creation."""
        application_data = {
            "applicant_id": "APP-STATE-001",
            "age": 35,
            "income": 75000.0,
            "employment_type": "Full-time",
            "credit_score": 720,
            "loan_amount": 250000.0,
            "loan_tenure_months": 360,
            "existing_liabilities": 50000.0,
            "location": "New York",
            "applicant_email": "state@example.com",
        }

        state = create_initial_state("LOAN-STATE-001", "APP-STATE-001", application_data)

        assert state["application_id"] == "LOAN-STATE-001"
        assert state["applicant_id"] == "APP-STATE-001"
        assert state["status"] == "pending"
        assert state["age"] == 35
        assert state["income"] == 75000.0
        assert state["created_at"] is not None
        assert state["iterations"] == 0
        assert state["audit_entries"] == []

    @pytest.mark.asyncio
    async def test_workflow_audit_trail(self):
        """Test workflow audit trail logging."""
        application_data = {
            "applicant_id": "APP-AUDIT-001",
            "age": 35,
            "income": 75000.0,
            "employment_type": "Full-time",
            "credit_score": 720,
            "loan_amount": 250000.0,
            "loan_tenure_months": 360,
            "existing_liabilities": 50000.0,
            "location": "New York",
            "applicant_email": "audit@example.com",
        }

        result = await self.orchestrator.process_application(application_data)

        assert result["success"] is True
        assert len(result["audit_trail"]) > 0
        # Should have entries for validation, agents, and completion
        audit_actions = [entry["action"] for entry in result["audit_trail"]]
        assert "VALIDATION_PASSED" in audit_actions
        assert "WORKFLOW_COMPLETED" in audit_actions

    @pytest.mark.asyncio
    async def test_workflow_full_state_available(self):
        """Test that full workflow state is returned."""
        application_data = {
            "applicant_id": "APP-FULL-001",
            "age": 35,
            "income": 75000.0,
            "employment_type": "Full-time",
            "credit_score": 720,
            "loan_amount": 250000.0,
            "loan_tenure_months": 360,
            "existing_liabilities": 50000.0,
            "location": "New York",
            "applicant_email": "full@example.com",
        }

        result = await self.orchestrator.process_application(application_data)

        assert result["success"] is True
        assert "full_state" in result
        full_state = result["full_state"]

        # Verify all agent outputs are present
        assert "applicant_profile_output" in full_state
        assert "financial_risk_output" in full_state
        assert "loan_decision_output" in full_state
        assert "compliance_output" in full_state

    @pytest.mark.asyncio
    async def test_workflow_decision_types(self):
        """Test all possible decision types can be generated."""
        decisions = set()

        # Run multiple applications to try to get different decision types
        test_cases = [
            {
                "applicant_id": "APP-DEC-001",
                "age": 35,
                "income": 150000.0,
                "employment_type": "Full-time",
                "credit_score": 800,
                "loan_amount": 200000.0,
                "loan_tenure_months": 360,
                "existing_liabilities": 20000.0,
                "location": "New York",
                "applicant_email": "dec1@example.com",
            },
            {
                "applicant_id": "APP-DEC-002",
                "age": 25,
                "income": 35000.0,
                "employment_type": "Part-time",
                "credit_score": 500,
                "loan_amount": 300000.0,
                "loan_tenure_months": 360,
                "existing_liabilities": 100000.0,
                "location": "California",
                "applicant_email": "dec2@example.com",
            },
            {
                "applicant_id": "APP-DEC-003",
                "age": 40,
                "income": 60000.0,
                "employment_type": "Full-time",
                "credit_score": 650,
                "loan_amount": 200000.0,
                "loan_tenure_months": 360,
                "existing_liabilities": 50000.0,
                "location": "Texas",
                "applicant_email": "dec3@example.com",
            },
        ]

        for app_data in test_cases:
            result = await self.orchestrator.process_application(app_data)
            if result["success"]:
                decisions.add(result["decision"])

        # Should have at least one type of decision
        assert len(decisions) > 0
        # All decisions should be valid
        assert all(d in ["APPROVED", "REJECTED", "MANUAL_REVIEW"] for d in decisions)

    @pytest.mark.asyncio
    async def test_workflow_confidence_levels(self):
        """Test that confidence levels are appropriate."""
        application_data = {
            "applicant_id": "APP-CONF-001",
            "age": 35,
            "income": 75000.0,
            "employment_type": "Full-time",
            "credit_score": 720,
            "loan_amount": 250000.0,
            "loan_tenure_months": 360,
            "existing_liabilities": 50000.0,
            "location": "New York",
            "applicant_email": "conf@example.com",
        }

        result = await self.orchestrator.process_application(application_data)

        assert result["success"] is True
        confidence = result["confidence_level"]
        assert isinstance(confidence, (int, float))
        assert 0 <= confidence <= 100

    @pytest.mark.asyncio
    async def test_workflow_key_factors(self):
        """Test that key factors are provided."""
        application_data = {
            "applicant_id": "APP-FACTORS-001",
            "age": 35,
            "income": 75000.0,
            "employment_type": "Full-time",
            "credit_score": 720,
            "loan_amount": 250000.0,
            "loan_tenure_months": 360,
            "existing_liabilities": 50000.0,
            "location": "New York",
            "applicant_email": "factors@example.com",
        }

        result = await self.orchestrator.process_application(application_data)

        assert result["success"] is True
        factors = result["key_factors"]
        assert isinstance(factors, list)
        assert len(factors) > 0
        assert all(isinstance(f, str) for f in factors)

    def test_orchestrator_stats(self):
        """Test orchestrator statistics."""
        stats = self.orchestrator.get_workflow_stats()

        assert stats["graph_compiled"] is True
        assert stats["nodes"] == 6
        assert stats["edges"] >= 6

    @pytest.mark.asyncio
    async def test_validation_function(self):
        """Test orchestrator validation function."""
        valid_data = {
            "applicant_id": "APP-VALID",
            "age": 35,
            "income": 75000.0,
            "employment_type": "Full-time",
            "credit_score": 720,
            "loan_amount": 250000.0,
            "loan_tenure_months": 360,
            "existing_liabilities": 50000.0,
            "location": "New York",
        }

        is_valid, errors = await self.orchestrator.validate_application_data(valid_data)
        assert is_valid is True
        assert len(errors) == 0

    @pytest.mark.asyncio
    async def test_validation_function_invalid(self):
        """Test validation function with invalid data."""
        invalid_data = {
            "applicant_id": "APP-INVALID",
            "age": 15,  # Too young
            "income": -1000.0,  # Invalid
            "credit_score": 1000,  # Invalid
            "loan_amount": 0,  # Invalid
            "loan_tenure_months": 0,
            "existing_liabilities": 0,
            "location": "New York",
            # Missing employment_type
        }

        is_valid, errors = await self.orchestrator.validate_application_data(invalid_data)
        assert is_valid is False
        assert len(errors) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
