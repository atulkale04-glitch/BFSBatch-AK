"""Streamlit UI for Loan Approval System."""

import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, Any

API_BASE_URL = "http://localhost:8000/api/v1"

st.set_page_config(
    page_title="Loan Approval System",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("💰 AI-Powered Loan Approval System")
st.markdown(
    "Intelligent loan evaluation using multi-agent AI orchestration"
)

def main():
    """Main application entry point."""

    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Select a page:",
            ["Submit Application", "Check Status", "View Decision", "Dashboard"]
        )

    if page == "Submit Application":
        submit_application_page()
    elif page == "Check Status":
        check_status_page()
    elif page == "View Decision":
        view_decision_page()
    elif page == "Dashboard":
        dashboard_page()


def submit_application_page():
    """Page for submitting new loan applications."""

    st.header("📝 Submit Loan Application")

    with st.form("application_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Applicant Information")
            applicant_id = st.text_input(
                "Applicant ID",
                placeholder="APP-001",
                help="Unique identifier for the applicant"
            )
            age = st.number_input(
                "Age",
                min_value=18,
                max_value=100,
                value=35,
                help="Age between 18 and 100"
            )
            income = st.number_input(
                "Annual Income ($)",
                min_value=0.0,
                value=100000.0,
                step=1000.0,
                help="Annual income in USD"
            )
            employment_type = st.selectbox(
                "Employment Type",
                ["Full-time", "Part-time", "Self-employed", "Retired", "Unemployed"]
            )

        with col2:
            st.subheader("Loan & Credit Information")
            credit_score = st.number_input(
                "Credit Score",
                min_value=300,
                max_value=850,
                value=750,
                help="Credit score between 300 and 850"
            )
            loan_amount = st.number_input(
                "Loan Amount ($)",
                min_value=0.0,
                value=250000.0,
                step=1000.0,
                help="Requested loan amount in USD"
            )
            loan_tenure_months = st.number_input(
                "Loan Tenure (Months)",
                min_value=6,
                max_value=600,
                value=360,
                step=12,
                help="Loan repayment period in months"
            )
            existing_liabilities = st.number_input(
                "Existing Liabilities ($)",
                min_value=0.0,
                value=30000.0,
                step=1000.0,
                help="Total existing debt obligations"
            )

        st.subheader("Location & Contact")
        col3, col4 = st.columns(2)

        with col3:
            location = st.text_input(
                "Location",
                value="New York",
                help="City/State where applicant resides"
            )

        with col4:
            applicant_email = st.text_input(
                "Email Address",
                value="applicant@example.com",
                help="Contact email for notifications"
            )

        submitted = st.form_submit_button("Submit Application", use_container_width=True)

        if submitted:
            if not applicant_id:
                st.error("Please enter an Applicant ID")
            elif not applicant_email or "@" not in applicant_email:
                st.error("Please enter a valid email address")
            else:
                submit_loan_application(
                    applicant_id=applicant_id,
                    age=int(age),
                    income=float(income),
                    employment_type=employment_type,
                    credit_score=int(credit_score),
                    loan_amount=float(loan_amount),
                    loan_tenure_months=int(loan_tenure_months),
                    existing_liabilities=float(existing_liabilities),
                    location=location,
                    applicant_email=applicant_email,
                )


def submit_loan_application(**kwargs) -> None:
    """Submit loan application to API."""

    with st.spinner("Processing application..."):
        try:
            response = requests.post(
                f"{API_BASE_URL}/applications",
                json=kwargs,
                timeout=300
            )

            if response.status_code == 200:
                data = response.json()
                st.success("✅ Application submitted successfully!")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Application ID", data.get("application_id", "N/A")[:12] + "...")
                with col2:
                    st.metric("Status", data.get("status", "N/A").upper())
                with col3:
                    st.metric("Timestamp", datetime.now().strftime("%Y-%m-%d %H:%M"))

                st.info(data.get("message", "Application processing..."))

                if "application_id" in data:
                    st.session_state.last_application_id = data["application_id"]
                    st.balloons()
            else:
                st.error(f"Error: {response.status_code} - {response.text}")

        except requests.exceptions.Timeout:
            st.error("Request timed out. Please try again.")
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {str(e)}")
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")


def check_status_page():
    """Page for checking application status."""

    st.header("📊 Check Application Status")

    application_id = st.text_input(
        "Application ID",
        placeholder="Enter application ID to check status...",
        help="Paste the application ID from your submission confirmation"
    )

    if application_id:
        if st.button("Check Status", use_container_width=True):
            fetch_and_display_status(application_id)


def fetch_and_display_status(application_id: str) -> None:
    """Fetch and display application status."""

    with st.spinner("Fetching status..."):
        try:
            response = requests.get(
                f"{API_BASE_URL}/applications/{application_id}",
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Applicant ID", data.get("applicant_id", "N/A"))
                with col2:
                    status_color = "🟢" if data.get("status") == "completed" else "🟡"
                    st.metric("Status", f"{status_color} {data.get('status', 'N/A').upper()}")
                with col3:
                    if data.get("decision"):
                        decision_emoji = "✅" if data.get("decision") == "APPROVED" else "❌" if data.get("decision") == "REJECTED" else "❓"
                        st.metric("Decision", f"{decision_emoji} {data.get('decision', 'N/A')}")
                with col4:
                    st.metric("Risk Score", f"{data.get('risk_score', 'N/A')}/100")

                st.json(data)
            elif response.status_code == 404:
                st.warning("Application not found. Please check the ID.")
            else:
                st.error(f"Error: {response.status_code}")

        except Exception as e:
            st.error(f"Error fetching status: {str(e)}")


def view_decision_page():
    """Page for viewing detailed loan decisions."""

    st.header("⚖️ View Loan Decision")

    application_id = st.text_input(
        "Application ID",
        placeholder="Enter application ID to view decision...",
        help="Paste the application ID to see the decision details"
    )

    if application_id:
        if st.button("View Decision", use_container_width=True):
            fetch_and_display_decision(application_id)


def fetch_and_display_decision(application_id: str) -> None:
    """Fetch and display loan decision."""

    with st.spinner("Fetching decision..."):
        try:
            response = requests.get(
                f"{API_BASE_URL}/applications/{application_id}/decision",
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()

                decision = data.get("final_decision", "N/A")
                decision_emoji = "✅" if decision == "APPROVED" else "❌" if decision == "REJECTED" else "❓"

                st.subheader(f"{decision_emoji} Decision: {decision}")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Risk Score", f"{data.get('risk_score', 'N/A')}/100")
                with col2:
                    st.metric("Confidence Level", f"{data.get('confidence_level', 'N/A')}%")
                with col3:
                    st.metric("Case ID", data.get("case_id", "N/A")[:12] + "...")

                st.markdown("---")

                st.subheader("📋 Decision Factors")
                key_factors = data.get("key_factors", [])
                if key_factors:
                    for i, factor in enumerate(key_factors, 1):
                        st.write(f"{i}. {factor}")
                else:
                    st.info("No key factors provided")

                st.markdown("---")

                st.subheader("💭 Reasoning")
                reasoning = data.get("reasoning", "No reasoning provided")
                st.write(reasoning)

                st.markdown("---")

                if st.button("View Full Details", use_container_width=True):
                    st.json(data)

                if st.button("View Audit Trail", use_container_width=True):
                    fetch_and_display_audit_trail(application_id)

            elif response.status_code == 404:
                st.warning("Decision not found. Application may still be processing.")
            else:
                st.error(f"Error: {response.status_code}")

        except Exception as e:
            st.error(f"Error fetching decision: {str(e)}")


def fetch_and_display_audit_trail(application_id: str) -> None:
    """Fetch and display audit trail."""

    with st.spinner("Fetching audit trail..."):
        try:
            response = requests.get(
                f"{API_BASE_URL}/applications/{application_id}/audit-trail",
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()

                st.subheader("🔍 Audit Trail")
                audit_entries = data.get("audit_entries", [])

                if audit_entries:
                    for entry in audit_entries:
                        with st.expander(f"📝 {entry.get('action')} - {entry.get('timestamp')}"):
                            st.json(entry.get("details", {}))
                else:
                    st.info("No audit entries found")
            else:
                st.error(f"Error fetching audit trail: {response.status_code}")

        except Exception as e:
            st.error(f"Error fetching audit trail: {str(e)}")


def dashboard_page():
    """Dashboard showing system statistics."""

    st.header("📈 System Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Applications", "234", "+12")

    with col2:
        st.metric("Approval Rate", "68%", "+2%")

    with col3:
        st.metric("Avg Processing Time", "2.3s", "-0.5s")

    st.markdown("---")

    st.subheader("📊 Decision Distribution")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Approved", "159", "68%")

    with col2:
        st.metric("Rejected", "45", "19%")

    col3, col4 = st.columns(2)

    with col3:
        st.metric("Manual Review", "30", "13%")

    with col4:
        st.metric("Processing", "0", "0%")

    st.markdown("---")

    st.subheader("ℹ️ System Information")

    st.info("""
    **Loan Approval System**
    - Multi-Agent AI Orchestration
    - LangGraph Workflow Engine
    - Real-time Decision Making
    - Audit Trail Logging
    - 99.9% Uptime SLA
    """)


if __name__ == "__main__":
    main()
