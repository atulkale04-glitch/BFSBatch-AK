"""MCP Server: NotificationSystem - Decision execution and notifications."""

import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List

from src.utils.logger import get_logger

logger = get_logger(__name__)


class NotificationSystemServer:
    """MCP Server for executing decisions and sending notifications."""

    # Mock notification log
    NOTIFICATION_LOG = []
    AUDIT_LOG = []

    def __init__(self):
        """Initialize NotificationSystem MCP Server."""
        self.logger = get_logger("mcp_servers.notification_system")
        self.logger.info("NotificationSystem MCP Server initialized")

    def generate_case_id(self) -> Dict[str, Any]:
        """
        Generate a unique case ID for tracking.

        Returns:
            Generated case ID
        """
        self.logger.debug("Generating case ID")

        case_id = f"CASE-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

        return {
            "success": True,
            "data": {
                "case_id": case_id,
                "timestamp": str(datetime.utcnow()),
            },
        }

    def send_decision_notification(
        self,
        application_id: str,
        applicant_email: str,
        decision: str,
        risk_score: float,
        explanation: str,
    ) -> Dict[str, Any]:
        """
        Send decision notification to applicant.

        Args:
            application_id: Application ID
            applicant_email: Applicant email address
            decision: Final decision (APPROVED/REJECTED/MANUAL_REVIEW)
            risk_score: Risk score
            explanation: Decision explanation

        Returns:
            Notification status
        """
        self.logger.info(f"Sending notification for {application_id} to {applicant_email}")

        # Generate notification
        notification = {
            "notification_id": str(uuid.uuid4()),
            "application_id": application_id,
            "applicant_email": applicant_email,
            "decision": decision,
            "risk_score": risk_score,
            "explanation": explanation,
            "timestamp": str(datetime.utcnow()),
            "status": "sent",
        }

        self.NOTIFICATION_LOG.append(notification)

        return {
            "success": True,
            "data": {
                "message": f"Notification sent to {applicant_email}",
                "notification_id": notification["notification_id"],
                "delivery_status": "sent",
                "timestamp": notification["timestamp"],
            },
        }

    def log_action(
        self,
        application_id: str,
        action: str,
        details: Dict[str, Any] = None,
        case_id: str = None,
    ) -> Dict[str, Any]:
        """
        Log action to audit trail.

        Args:
            application_id: Application ID
            action: Action performed
            details: Additional details
            case_id: Associated case ID

        Returns:
            Log confirmation
        """
        self.logger.debug(f"Logging action for {application_id}: {action}")

        log_entry = {
            "log_id": str(uuid.uuid4()),
            "application_id": application_id,
            "action": action,
            "details": details or {},
            "case_id": case_id,
            "timestamp": str(datetime.utcnow()),
        }

        self.AUDIT_LOG.append(log_entry)

        return {
            "success": True,
            "data": {
                "log_id": log_entry["log_id"],
                "message": f"Action logged: {action}",
                "timestamp": log_entry["timestamp"],
            },
        }

    def execute_approval_decision(
        self,
        application_id: str,
        case_id: str,
        risk_score: float,
        key_factors: List[str],
    ) -> Dict[str, Any]:
        """
        Execute approval decision.

        Args:
            application_id: Application ID
            case_id: Case ID
            risk_score: Risk score
            key_factors: Key decision factors

        Returns:
            Execution result
        """
        self.logger.info(f"Executing APPROVED decision for {application_id}")

        # Log the action
        self.log_action(
            application_id,
            "DECISION_EXECUTED",
            {
                "decision": "APPROVED",
                "risk_score": risk_score,
                "key_factors": key_factors,
            },
            case_id,
        )

        return {
            "success": True,
            "data": {
                "message": "Approval decision executed",
                "application_id": application_id,
                "case_id": case_id,
                "decision": "APPROVED",
                "action_timestamp": str(datetime.utcnow()),
            },
        }

    def execute_rejection_decision(
        self,
        application_id: str,
        case_id: str,
        risk_score: float,
        reason: str,
    ) -> Dict[str, Any]:
        """
        Execute rejection decision.

        Args:
            application_id: Application ID
            case_id: Case ID
            risk_score: Risk score
            reason: Rejection reason

        Returns:
            Execution result
        """
        self.logger.info(f"Executing REJECTED decision for {application_id}")

        # Log the action
        self.log_action(
            application_id,
            "DECISION_EXECUTED",
            {
                "decision": "REJECTED",
                "risk_score": risk_score,
                "reason": reason,
            },
            case_id,
        )

        return {
            "success": True,
            "data": {
                "message": "Rejection decision executed",
                "application_id": application_id,
                "case_id": case_id,
                "decision": "REJECTED",
                "action_timestamp": str(datetime.utcnow()),
            },
        }

    def flag_for_manual_review(
        self,
        application_id: str,
        case_id: str,
        reason: str,
        risk_score: float,
    ) -> Dict[str, Any]:
        """
        Flag application for manual review.

        Args:
            application_id: Application ID
            case_id: Case ID
            reason: Review reason
            risk_score: Risk score

        Returns:
            Flag result
        """
        self.logger.info(f"Flagging {application_id} for manual review")

        # Log the action
        self.log_action(
            application_id,
            "FLAGGED_FOR_REVIEW",
            {
                "reason": reason,
                "risk_score": risk_score,
            },
            case_id,
        )

        return {
            "success": True,
            "data": {
                "message": "Application flagged for manual review",
                "application_id": application_id,
                "case_id": case_id,
                "status": "MANUAL_REVIEW",
                "review_reason": reason,
                "action_timestamp": str(datetime.utcnow()),
            },
        }

    def retrieve_audit_trail(self, application_id: str) -> Dict[str, Any]:
        """
        Retrieve audit trail for an application.

        Args:
            application_id: Application ID

        Returns:
            Audit trail entries
        """
        self.logger.debug(f"Retrieving audit trail for {application_id}")

        entries = [e for e in self.AUDIT_LOG if e["application_id"] == application_id]

        return {
            "success": True,
            "data": {
                "application_id": application_id,
                "audit_entries": entries,
                "entry_count": len(entries),
            },
        }

    def retrieve_notifications(self, application_id: str) -> Dict[str, Any]:
        """
        Retrieve notifications sent for an application.

        Args:
            application_id: Application ID

        Returns:
            Notification records
        """
        self.logger.debug(f"Retrieving notifications for {application_id}")

        notifications = [n for n in self.NOTIFICATION_LOG if n["application_id"] == application_id]

        return {
            "success": True,
            "data": {
                "application_id": application_id,
                "notifications": notifications,
                "notification_count": len(notifications),
            },
        }

    def get_case_summary(self, case_id: str) -> Dict[str, Any]:
        """
        Get summary of case by case ID.

        Args:
            case_id: Case ID

        Returns:
            Case summary
        """
        self.logger.debug(f"Retrieving case summary for {case_id}")

        # Find all audit entries and notifications for this case
        audit_entries = [e for e in self.AUDIT_LOG if e.get("case_id") == case_id]
        notifications = [n for n in self.NOTIFICATION_LOG if any(e.get("case_id") == case_id for e in audit_entries)]

        if not audit_entries:
            return {"error": f"Case {case_id} not found", "success": False}

        # Extract application ID
        application_id = audit_entries[0]["application_id"] if audit_entries else None

        return {
            "success": True,
            "data": {
                "case_id": case_id,
                "application_id": application_id,
                "audit_entries": len(audit_entries),
                "notifications_sent": len(notifications),
                "timeline": [
                    {
                        "timestamp": e["timestamp"],
                        "action": e["action"],
                        "details": e.get("details", {}),
                    }
                    for e in audit_entries
                ],
            },
        }

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools for Claude."""
        return [
            {
                "name": "generate_case_id",
                "description": "Generate a unique case ID for tracking",
                "input_schema": {"properties": {}, "required": []},
            },
            {
                "name": "send_decision_notification",
                "description": "Send decision notification to applicant",
                "input_schema": {
                    "properties": {
                        "application_id": {"type": "string", "description": "Application ID"},
                        "applicant_email": {"type": "string", "description": "Applicant email"},
                        "decision": {"type": "string", "description": "Final decision"},
                        "risk_score": {"type": "number", "description": "Risk score"},
                        "explanation": {"type": "string", "description": "Decision explanation"},
                    },
                    "required": [
                        "application_id",
                        "applicant_email",
                        "decision",
                        "risk_score",
                        "explanation",
                    ],
                },
            },
            {
                "name": "log_action",
                "description": "Log action to audit trail",
                "input_schema": {
                    "properties": {
                        "application_id": {"type": "string", "description": "Application ID"},
                        "action": {"type": "string", "description": "Action name"},
                        "details": {"type": "object", "description": "Additional details"},
                        "case_id": {"type": "string", "description": "Associated case ID"},
                    },
                    "required": ["application_id", "action"],
                },
            },
            {
                "name": "execute_approval_decision",
                "description": "Execute approval decision",
                "input_schema": {
                    "properties": {
                        "application_id": {"type": "string", "description": "Application ID"},
                        "case_id": {"type": "string", "description": "Case ID"},
                        "risk_score": {"type": "number", "description": "Risk score"},
                        "key_factors": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Key factors",
                        },
                    },
                    "required": ["application_id", "case_id", "risk_score", "key_factors"],
                },
            },
            {
                "name": "execute_rejection_decision",
                "description": "Execute rejection decision",
                "input_schema": {
                    "properties": {
                        "application_id": {"type": "string", "description": "Application ID"},
                        "case_id": {"type": "string", "description": "Case ID"},
                        "risk_score": {"type": "number", "description": "Risk score"},
                        "reason": {"type": "string", "description": "Rejection reason"},
                    },
                    "required": ["application_id", "case_id", "risk_score", "reason"],
                },
            },
            {
                "name": "flag_for_manual_review",
                "description": "Flag application for manual review",
                "input_schema": {
                    "properties": {
                        "application_id": {"type": "string", "description": "Application ID"},
                        "case_id": {"type": "string", "description": "Case ID"},
                        "reason": {"type": "string", "description": "Review reason"},
                        "risk_score": {"type": "number", "description": "Risk score"},
                    },
                    "required": ["application_id", "case_id", "reason", "risk_score"],
                },
            },
            {
                "name": "retrieve_audit_trail",
                "description": "Retrieve audit trail for an application",
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

        if tool_name == "generate_case_id":
            result = self.generate_case_id()
        elif tool_name == "send_decision_notification":
            result = self.send_decision_notification(
                tool_input.get("application_id", ""),
                tool_input.get("applicant_email", ""),
                tool_input.get("decision", ""),
                tool_input.get("risk_score", 0),
                tool_input.get("explanation", ""),
            )
        elif tool_name == "log_action":
            result = self.log_action(
                tool_input.get("application_id", ""),
                tool_input.get("action", ""),
                tool_input.get("details"),
                tool_input.get("case_id"),
            )
        elif tool_name == "execute_approval_decision":
            result = self.execute_approval_decision(
                tool_input.get("application_id", ""),
                tool_input.get("case_id", ""),
                tool_input.get("risk_score", 0),
                tool_input.get("key_factors", []),
            )
        elif tool_name == "execute_rejection_decision":
            result = self.execute_rejection_decision(
                tool_input.get("application_id", ""),
                tool_input.get("case_id", ""),
                tool_input.get("risk_score", 0),
                tool_input.get("reason", ""),
            )
        elif tool_name == "flag_for_manual_review":
            result = self.flag_for_manual_review(
                tool_input.get("application_id", ""),
                tool_input.get("case_id", ""),
                tool_input.get("reason", ""),
                tool_input.get("risk_score", 0),
            )
        elif tool_name == "retrieve_audit_trail":
            result = self.retrieve_audit_trail(tool_input.get("application_id", ""))
        else:
            result = {"error": f"Unknown tool: {tool_name}"}

        return json.dumps(result)
