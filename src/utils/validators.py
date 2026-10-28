"""Input validation utilities."""

from typing import List

from src.models.schemas import LoanApplicationRequest


def validate_application_data(app: LoanApplicationRequest) -> tuple[bool, List[str]]:
    """
    Validate loan application data for completeness and consistency.

    Returns:
        Tuple of (is_valid, list_of_error_messages)
    """
    errors = []

    # Validate income range
    if app.income < 10000:
        errors.append("Annual income must be at least $10,000")

    if app.income > 1000000:
        errors.append("Annual income exceeds maximum threshold")

    # Validate loan amount
    if app.loan_amount < 5000:
        errors.append("Loan amount must be at least $5,000")

    if app.loan_amount > 5000000:
        errors.append("Loan amount exceeds maximum threshold")

    # Validate loan tenure
    if app.loan_tenure_months < 12:
        errors.append("Loan tenure must be at least 12 months")

    if app.loan_tenure_months > 360:
        errors.append("Loan tenure cannot exceed 30 years (360 months)")

    # Validate liabilities
    if app.existing_liabilities < 0:
        errors.append("Existing liabilities cannot be negative")

    if app.existing_liabilities > app.income * 10:
        errors.append("Existing liabilities seem disproportionately high")

    # Validate age
    if app.age < 18:
        errors.append("Applicant must be at least 18 years old")

    if app.age > 100:
        errors.append("Applicant age seems invalid")

    # Validate credit score
    if app.credit_score < 300 or app.credit_score > 850:
        errors.append("Credit score must be between 300 and 850")

    # Validate employment type
    valid_employment_types = [
        "Full-time",
        "Part-time",
        "Self-employed",
        "Retired",
        "Student",
        "Unemployed",
    ]
    if app.employment_type not in valid_employment_types:
        errors.append(f"Employment type must be one of: {', '.join(valid_employment_types)}")

    # Validate location
    if len(app.location.strip()) < 2:
        errors.append("Location must be valid")

    return len(errors) == 0, errors


def calculate_dti_ratio(income: float, liabilities: float, loan_amount: float, tenure_months: int) -> float:
    """
    Calculate Debt-to-Income (DTI) ratio.

    DTI = (Monthly Debt Obligations) / (Gross Monthly Income)
    """
    monthly_income = income / 12
    monthly_liabilities = liabilities / 12

    # Estimate monthly loan payment (approximate using simple formula)
    annual_rate = 0.07  # Assume 7% annual interest rate
    monthly_rate = annual_rate / 12
    num_payments = tenure_months

    if monthly_rate > 0:
        monthly_payment = (loan_amount * monthly_rate * (1 + monthly_rate) ** num_payments) / (
            (1 + monthly_rate) ** num_payments - 1
        )
    else:
        monthly_payment = loan_amount / num_payments

    total_monthly_debt = monthly_liabilities + monthly_payment

    if monthly_income == 0:
        return 0.0

    dti = total_monthly_debt / monthly_income
    return round(dti, 4)
