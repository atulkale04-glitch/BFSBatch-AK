"""Compliance & Action Orchestrator Agent - Executes decisions and manages compliance."""

import json
import re
from typing import Any, Dict, List

from config.prompts import COMPLIANCE_PROMPT
from src.agents.base_agent import BaseAgent, Tool
from src.mcp_servers.notification_system import NotificationSystemServer
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ComplianceOrchestratorAgent(BaseAgent):
    """Agent for executing decisions and managing compliance/notifications."""

    def __init__(self):
        """Initialize Compliance & Action Orchestrator Agent."""
        self.mcp_server = NotificationSystemServer()

        # Register all MCP server tools
        tools = [
            Tool(
                name="generate_case_id",
                description="Generate a unique case ID for tracking and audit purposes",
                input_schema={"properties": {}, "required": []},
                handler=self._handle_generate_case_id,
            ),
            Tool(
                name="execute_approval_decision",
                description="Execute an approval decision and log the action",
                input_schema={
                    "properties": {
                        "application_id": {"type": "string", "description": "Application ID"},
                        "case_id": {"type": "string", "description": "Case ID"},
                        "risk_score": {"type": "number", "description": "Risk score (0-100)"},
                        "key_factors": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Key factors",
                        },
                    },
                    "required": ["application_id", "case_id", "risk_score", "key_factors"],
                },
                handler=self._handle_execute_approval_decision,
            ),
            Tool(
                name="execute_rejection_decision",
                description="Execute a rejection decision and log the action",
                input_schema={
                    "properties": {
                        "application_id": {"type": "string", "description": "Application ID"},
                        "case_id": {"type": "string", "description": "Case ID"},
                        "risk_score": {"type": "number", "description": "Risk score (0-100)"},
                        "reason": {"type": "string", "description": "Rejection reason"},
                    },
                    "required": ["application_id", "case_id", "risk_score", "reason"],
                },
                handler=self._handle_execute_rejection_decision,
            ),
            Tool(
                name="flag_for_manual_review",
                description="Flag an application for manual review by a specialist",
                input_schema={
                    "properties": {
                        "application_id": {"type": "string", "description": "Application ID"},
                        "case_id": {"type": "string", "description": "Case ID"},
                        "reason": {"type": "string", "description": "Review reason"},
                        "risk_score": {"type": "number", "description": "Risk score (0-100)"},
                    },
                    "required": ["application_id", "case_id", "reason", "risk_score"],
                },
                handler=self._handle_flag_for_manual_review,
            ),
            Tool(
                name="send_decision_notification",
                description="Send decision notification to applicant",
                input_schema={
                    "properties": {
                        "application_id": {"type": "string", "description": "Application ID"},
                        "applicant_email": {"type": "string", "description": "Applicant email"},
                        "decision": {"type": "string", "description": "Final decision"},
                        "risk_score": {"type": "number", "description": "Risk score"},
                        "explanation": {"type": "string", "description": "Explanation"},
                    },
                    "required": ["application_id", "applicant_email", "decision", "risk_score", "explanation"],
                },
                handler=self._handle_send_decision_notification,
            ),
            Tool(
                name="log_action",
                description="Log action to audit trail",
                input_schema={
                    "properties": {
                        "application_id": {"type": "string", "description": "Application ID"},
                        "action": {"type": "string", "description": "Action name"},
                        "details": {"type": "object", "description": "Additional details"},
                        "case_id": {"type": "string", "description": "Case ID"},
                    },
                    "required": ["application_id", "action"],
                },
                handler=self._handle_log_action,
            ),
            Tool(
                name="retrieve_audit_trail",
                description="Retrieve complete audit trail for an application",
                input_schema={
                    "properties": {
                        "application_id": {"type": "string", "description": "Application ID"}
                    },
                    "required": ["application_id"],
                },
                handler=self._handle_retrieve_audit_trail,
            ),
        ]

        super().__init__(
            agent_name="compliance_orchestrator_agent",
            system_prompt=COMPLIANCE_PROMPT,
            tools=tools,
        )

    def _handle_generate_case_id(self) -> Dict[str, Any]:
        """Handle generate_case_id tool call."""
        return self.mcp_server.generate_case_id()

    def _handle_execute_approval_decision(
        self,
        application_id: str,
        case_id: str,
        risk_score: float,
        key_factors: List[str],
    ) -> Dict[str, Any]:
        """Handle execute_approval_decision tool call."""
        return self.mcp_server.execute_approval_decision(application_id, case_id, risk_score, key_factors)

    def _handle_execute_rejection_decision(
        self,
        application_id: str,
        case_id: str,
        risk_score: float,
        reason: str,
    ) -> Dict[str, Any]:
        """Handle execute_rejection_decision tool call."""
        return self.mcp_server.execute_rejection_decision(application_id, case_id, risk_score, reason)

    def _handle_flag_for_manual_review(
        self,
        application_id: str,
        case_id: str,
        reason: str,
        risk_score: float,
    ) -> Dict[str, Any]:
        """Handle flag_for_manual_review tool call."""
        return self.mcp_server.flag_for_manual_review(application_id, case_id, reason, risk_score)

    def _handle_send_decision_notification(
        self,
        application_id: str,
        applicant_email: str,
        decision: str,
        risk_score: float,
        explanation: str,
    ) -> Dict[str, Any]:
        """Handle send_decision_notification tool call."""
        return self.mcp_server.send_decision_notification(
            application_id, applicant_email, decision, risk_score, explanation
        )

    def _handle_log_action(
        self,
        application_id: str,
        action: str,
        details: Dict[str, Any] = None,
        case_id: str = None,
    ) -> Dict[str, Any]:
        """Handle log_action tool call."""
        return self.mcp_server.log_action(application_id, action, details, case_id)

    def _handle_retrieve_audit_trail(self, application_id: str) -> Dict[str, Any]:
        """Handle retrieve_audit_trail tool call."""
        return self.mcp_server.retrieve_audit_trail(application_id)

    def _format_input_for_claude(self, input_data: Dict[str, Any]) -> str:
        """Format compliance data into a prompt for Claude."""
        application_id = input_data.get("application_id", "")
        decision = input_data.get("decision", "")
        applicant_email = input_data.get("applicant_email", "")
        risk_score = input_data.get("risk_score", 0)
        explanation = input_data.get("explanation", "")

        return f"""Execute the following decision and manage compliance:

Application ID: {application_id}
Decision: {decision}
Risk Score: {risk_score}
Applicant Email: {applicant_email}

Decision Explanation:
{explanation}

Please perform the following compliance and action tasks:
1. Generate a unique case ID using generate_case_id
2. Based on the decision type:
   - If APPROVED: Execute approval using execute_approval_decision
   - If REJECTED: Execute rejection using execute_rejection_decision
   - If MANUAL_REVIEW: Flag for review using flag_for_manual_review
3. Send notification to applicant using send_decision_notification
4. Log the action using log_action
5. Retrieve the complete audit trail using retrieve_audit_trail

Provide a compliance summary including:
- Case ID generated
- Action Taken (APPROVED/REJECTED/FLAGGED)
- Notification Status
- Audit Trail Summary

Format your final response as JSON with keys: case_id, action_taken, notification_status, audit_entries_count"""

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
                    "case_id": "CASE-UNKNOWN",
                    "action_taken": "unknown",
                    "notification_status": "unknown",
                    "audit_entries_count": 0,
                    "summary": text_content,
                }
        except json.JSONDecodeError:
            result = {
                "case_id": "CASE-UNKNOWN",
                "action_taken": "unknown",
                "notification_status": "unknown",
                "audit_entries_count": 0,
                "summary": text_content,
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

        if "case_id" not in data:
            errors.append("Missing case_id")

        if "action_taken" not in data:
            errors.append("Missing action_taken")
        elif data["action_taken"] not in ["APPROVED", "REJECTED", "MANUAL_REVIEW", "unknown"]:
            errors.append("action_taken must be APPROVED, REJECTED, MANUAL_REVIEW, or unknown")

        if "notification_status" not in data:
            errors.append("Missing notification_status")

        return len(errors) == 0, errors
