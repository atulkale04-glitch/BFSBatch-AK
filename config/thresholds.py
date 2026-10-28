"""Decision thresholds and approval policies."""

# Credit Score Risk Categories
CREDIT_SCORE_THRESHOLDS = {
    "poor": (0, 579),
    "fair": (580, 669),
    "good": (670, 739),
    "very_good": (740, 799),
    "excellent": (800, 850),
}

# DTI Ratio Risk Categories
DTI_RATIO_THRESHOLDS = {
    "low_risk": (0, 0.35),
    "medium_risk": (0.35, 0.50),
    "high_risk": (0.50, 1.0),
}

# Loan Amount Risk Categories (as percentage of income)
LOAN_AMOUNT_RISK_THRESHOLDS = {
    "low_risk": (0, 3.0),  # Up to 3x annual income
    "medium_risk": (3.0, 5.0),  # 3x to 5x annual income
    "high_risk": (5.0, float("inf")),  # More than 5x annual income
}

# Income Stability Score Thresholds
INCOME_STABILITY_THRESHOLDS = {
    "low": (0, 50),
    "medium": (50, 75),
    "high": (75, 100),
}

# Approval Policies
APPROVAL_POLICY = {
    # Minimum requirements
    "min_credit_score": 650,
    "max_dti_ratio": 0.45,
    "min_income_stability": 70,

    # Decision thresholds
    "auto_approve_max_risk_score": 30,
    "auto_reject_min_risk_score": 75,
    "manual_review_risk_score_range": (30, 75),

    # Confidence thresholds
    "min_confidence_for_decision": 0.75,

    # Employment requirements
    "min_employment_stability_months": 6,
}

# Risk Score Calculation Weights
RISK_SCORE_WEIGHTS = {
    "credit_score": 0.35,
    "dti_ratio": 0.30,
    "income_stability": 0.20,
    "loan_amount_risk": 0.15,
}

# Feature Flags
FEATURE_FLAGS = {
    "enable_ml_scoring": False,
    "enable_external_credit_check": False,
    "enable_fraud_detection": False,
    "require_manual_review_for_high_amounts": True,
}
