"""Lightweight rule-based decision engine for instant loan decisions."""

import uuid
from typing import Dict, Any, List


def make_instant_decision(application_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Make an instant loan decision based on rules (no expensive API calls).

    Args:
        application_data: Loan application data

    Returns:
        Decision dict with decision, risk_score, confidence_score, case_id, key_factors, reasoning
    """

    # Extract key factors
    income = application_data.get("income", 0)
    credit_score = application_data.get("credit_score", 300)
    loan_amount = application_data.get("loan_amount", 0)
    existing_liabilities = application_data.get("existing_liabilities", 0)
    age = application_data.get("age", 18)
    employment_type = application_data.get("employment_type", "")

    # Calculate metrics
    monthly_income = income / 12
    monthly_debt = existing_liabilities / 12
    estimated_loan_payment = (loan_amount * 0.005)  # ~0.5% monthly
    total_monthly_debt = monthly_debt + estimated_loan_payment
    dti_ratio = total_monthly_debt / monthly_income if monthly_income > 0 else 1.0

    # Risk scoring
    risk_score = 50  # Start at neutral
    key_factors = []

    # Credit score assessment (0-30 points)
    if credit_score >= 750:
        risk_score -= 15
        key_factors.append("Excellent credit history (750+)")
    elif credit_score >= 700:
        risk_score -= 10
        key_factors.append("Good credit history (700-749)")
    elif credit_score >= 650:
        risk_score -= 5
        key_factors.append("Fair credit history (650-699)")
    else:
        risk_score += 15
        key_factors.append("Poor credit history (<650)")

    # DTI ratio assessment (0-25 points)
    if dti_ratio <= 0.35:
        risk_score -= 15
        key_factors.append("Low debt-to-income ratio (<35%)")
    elif dti_ratio <= 0.45:
        risk_score -= 5
        key_factors.append("Moderate debt-to-income ratio (35-45%)")
    elif dti_ratio <= 0.55:
        risk_score += 10
        key_factors.append("High debt-to-income ratio (45-55%)")
    else:
        risk_score += 25
        key_factors.append("Very high debt-to-income ratio (>55%)")

    # Income assessment (0-20 points)
    if income >= 150000:
        risk_score -= 15
        key_factors.append("High annual income (>$150k)")
    elif income >= 100000:
        risk_score -= 10
        key_factors.append("Good annual income ($100k-$150k)")
    elif income >= 60000:
        risk_score -= 5
        key_factors.append("Adequate annual income ($60k-$100k)")
    else:
        risk_score += 10
        key_factors.append("Lower annual income (<$60k)")

    # Loan-to-income assessment
    loan_to_income_ratio = loan_amount / income if income > 0 else 0
    if loan_to_income_ratio <= 2.5:
        risk_score -= 5
    elif loan_to_income_ratio > 5:
        risk_score += 15
        key_factors.append(f"High loan-to-income ratio ({loan_to_income_ratio:.1f}x)")

    # Age assessment
    if 25 <= age <= 55:
        risk_score -= 5
    elif age < 25:
        risk_score += 5

    # Employment type assessment
    if employment_type.lower() in ["full-time", "government", "military"]:
        risk_score -= 5
        key_factors.append("Stable employment type")
    elif employment_type.lower() in ["self-employed", "contract"]:
        risk_score += 5
        key_factors.append("Variable employment type")

    # Clamp risk score between 0-100
    risk_score = max(0, min(100, risk_score))

    # Make decision based on risk score
    if risk_score < 30:
        decision = "APPROVED"
        confidence = 90 + (30 - risk_score)
        reasoning = "Strong application profile with excellent credit history, low DTI ratio, and stable income. Automatic approval recommended."
    elif risk_score < 50:
        decision = "APPROVED"
        confidence = 75 + (50 - risk_score) / 2
        reasoning = "Good application profile with positive indicators. Approval recommended based on favorable financial metrics."
    elif risk_score < 70:
        decision = "MANUAL_REVIEW"
        confidence = 60
        reasoning = "Borderline application requiring manual expert review. Mixed financial indicators present both strengths and concerns."
    else:
        decision = "REJECTED"
        confidence = 80 + (risk_score - 70) / 3
        reasoning = "High-risk application with significant concerns including elevated debt levels, lower credit score, or unfavorable debt-to-income ratio."

    # Clamp confidence between 0-100
    confidence = max(0, min(100, confidence))

    # Generate case ID
    case_id = f"CASE-{uuid.uuid4().hex[:8].upper()}"

    return {
        "decision": decision,
        "risk_score": round(risk_score, 1),
        "confidence_score": round(confidence, 1),
        "case_id": case_id,
        "key_factors": key_factors[:3],  # Top 3 factors
        "reasoning": reasoning,
        "success": True,
        "status": "completed"
    }
