# Loan Rejection Criteria

## Quick Answer

A loan application is **REJECTED** when the **Risk Score ≥ 70** (out of 100)

---

## Decision Thresholds

| Risk Score | Decision | Confidence |
|-----------|----------|-----------|
| < 30 | ✅ APPROVED | 90%+ |
| 30-49 | ✅ APPROVED | 75%+ |
| 50-69 | ❓ MANUAL_REVIEW | 60% |
| **≥ 70** | **❌ REJECTED** | **80%+** |

---

## How Risk Score is Calculated

The system starts with a **neutral base of 50 points** and adjusts based on:

### 1. **Credit Score** (±15 points - Most Important)
- **Excellent (750+):** -15 points ✓
- **Good (700-749):** -10 points ✓
- **Fair (650-699):** -5 points ✓
- **Poor (<650):** +15 points ✗

### 2. **DTI Ratio - Debt-to-Income** (±25 points - Very Important)
- **Low (≤ 35%):** -15 points ✓
- **Moderate (35-45%):** -5 points ✓
- **High (45-55%):** +10 points ✗
- **Very High (>55%):** +25 points ✗✗ **← Major rejection factor**

**DTI Calculation:**
```
Monthly Debt = (Existing Liabilities / 12) + (Estimated Loan Payment)
DTI Ratio = Monthly Debt / Monthly Income

Example:
- Monthly Income: $8,333 ($100k annual)
- Existing Liabilities: $30,000/month payment = $2,500
- Loan Amount: $250,000
- Estimated Loan Payment: $250k × 0.5% = $1,250
- Total Monthly Debt: $2,500 + $1,250 = $3,750
- DTI Ratio: $3,750 / $8,333 = 45% (HIGH - adds +10 points)
```

### 3. **Income** (±15 points)
- **High (≥$150k):** -15 points ✓
- **Good ($100k-$150k):** -10 points ✓
- **Adequate ($60k-$100k):** -5 points ✓
- **Low (<$60k):** +10 points ✗

### 4. **Loan-to-Income Ratio** (±15 points)
- **Healthy (≤ 2.5x):** -5 points ✓
- **Very High (> 5x):** +15 points ✗

**Example:**
```
- Income: $100,000
- Loan: $250,000
- Loan-to-Income Ratio: 2.5x (at threshold)
- Score: No adjustment (neutral)
```

### 5. **Age** (±5 points)
- **Prime Working Age (25-55):** -5 points ✓
- **Younger (<25):** +5 points ✗
- **Older (>55):** No adjustment (neutral)

### 6. **Employment Type** (±5 points)
- **Stable (Full-time, Government, Military):** -5 points ✓
- **Variable (Self-employed, Contract):** +5 points ✗
- **Other:** No adjustment (neutral)

---

## Scenarios Leading to REJECTION (Risk Score ≥ 70)

### Scenario 1: Poor Credit + High DTI
```
Base Score: 50

Credit Score: 600 (Poor)           → +15
DTI Ratio: 60% (Very High)         → +25
Income: $50,000 (Low)              → +10
Loan-to-Income: 5x (High)          → +15
Age: 22 (Young)                    → +5
Employment: Unemployed             → +5
────────────────────────────────────
TOTAL RISK SCORE: 125 → Clamped to 100

Decision: ❌ REJECTED (Risk ≥ 70)
Confidence: 80%+
```

### Scenario 2: Very High DTI Alone
```
Base Score: 50

Credit Score: 700 (Good)           → -10
DTI Ratio: 70% (Very High)         → +25
Income: $80,000 (Adequate)         → -5
Loan-to-Income: 3.5x               → 0
Age: 30 (Prime)                    → -5
Employment: Full-time              → -5
────────────────────────────────────
TOTAL RISK SCORE: 50

Decision: ❓ MANUAL_REVIEW (50-69 range)
- But if DTI is >60%, easily reaches 70+
```

### Scenario 3: Multiple Red Flags
```
Base Score: 50

Credit Score: 650 (Fair)           → -5
DTI Ratio: 55% (High)              → +10
Income: $45,000 (Low)              → +10
Loan-to-Income: 5.5x (Very High)   → +15
Age: 23 (Young)                    → +5
Employment: Self-employed          → +5
────────────────────────────────────
TOTAL RISK SCORE: 85

Decision: ❌ REJECTED (Risk ≥ 70)
Confidence: 85%+
```

---

## Common Rejection Triggers

### 🔴 **Critical (Immediate Rejection Risk)**

1. **DTI Ratio > 50%**
   - Monthly debt payments exceed 50% of income
   - Applicant can't afford other essentials
   - Example: $4,000+ debt on $8,000 income

2. **Credit Score < 600**
   - Poor payment history
   - Bankruptcy risk
   - Multiple defaults

3. **Loan-to-Income Ratio > 5x**
   - Borrowing 5+ times annual income
   - Unsustainable debt load
   - Example: $500k loan on $100k income

4. **Very High DTI (> 60%)**
   - Effectively guarantees rejection
   - Risk score alone +25 from DTI
   - Plus other negative factors push to 70+

### 🟡 **Warning Signs (Push Toward Rejection)**

5. **Low Income (< $50k annually)**
   - Limited repayment capacity
   - More vulnerable to job loss

6. **Young Age (< 25) with Other Issues**
   - Limited credit history
   - Unstable employment typically

7. **Self-Employed/Contract Work**
   - Income variability
   - Harder to verify stability

8. **Existing High Liabilities**
   - Already indebted
   - Less capacity for new loans

---

## How to AVOID Rejection

### 1. **Improve Credit Score** 
- Target: 700+
- Action: Pay bills on time, reduce outstanding debt
- Impact: -10 points

### 2. **Lower DTI Ratio**
- Target: Keep below 45%
- Action: Pay down existing debt before applying
- Impact: -5 to -15 points
- Example: Pay off $10k from existing liabilities to reduce monthly debt payments

### 3. **Increase Income**
- Target: $100k+
- Action: Seek better employment
- Impact: -10 points
- Alternative: Apply with co-signer

### 4. **Reduce Loan Amount**
- Target: Keep loan-to-income ≤ 2.5x
- Action: Request lower loan amount
- Impact: Reduces loan-to-income factor
- Example: Request $200k instead of $300k

### 5. **Secure Stable Employment**
- Target: Full-time or government job
- Action: Maintain steady employment
- Impact: -5 points

---

## Rejection Reasoning Examples

When an application is **REJECTED**, the system provides:

```
Decision: REJECTED
Risk Score: 75/100
Confidence: 82%

Reasoning:
"High-risk application with significant concerns including 
elevated debt levels, lower credit score, or unfavorable 
debt-to-income ratio."

Key Factors:
1. Very high debt-to-income ratio (>50%)
2. Fair credit history (650-699)
3. Multiple existing liabilities
```

---

## Comparison: Rejection vs Manual Review vs Approval

| Factor | REJECTED (≥70) | MANUAL_REVIEW (50-69) | APPROVED (<50) |
|--------|---|---|---|
| **Credit Score** | <650 or <700 with issues | 700-749 | 750+ or 700+ clean |
| **DTI Ratio** | >50% | 40-50% | <40% |
| **Income** | <$50k with debts | $60-100k | $100k+ |
| **Loan-to-Income** | >5x | 3-5x | <2.5x |
| **Employment** | Unstable/Variable | Mixed | Stable/Full-time |
| **Age** | <25 with other issues | 25-55 | 25-55 |

---

## Testing Rejection Scenarios

### Test Case 1: Guaranteed Rejection
```json
{
  "applicant_id": "REJECT-TEST-001",
  "age": 22,
  "income": 40000,
  "employment_type": "Unemployed",
  "credit_score": 580,
  "loan_amount": 300000,
  "loan_tenure_months": 360,
  "existing_liabilities": 50000,
  "location": "New York",
  "applicant_email": "reject@test.com"
}
```

**Expected:** REJECTED with risk_score ≥ 70

### Test Case 2: High DTI Rejection
```json
{
  "applicant_id": "REJECT-DTI-001",
  "age": 35,
  "income": 50000,
  "employment_type": "Full-time",
  "credit_score": 700,
  "loan_amount": 400000,
  "loan_tenure_months": 360,
  "existing_liabilities": 100000,
  "location": "New York",
  "applicant_email": "reject@test.com"
}
```

**Expected:** REJECTED due to extreme DTI ratio

### Test Case 3: Borderline (Manual Review)
```json
{
  "applicant_id": "MANUAL-TEST-001",
  "age": 35,
  "income": 75000,
  "employment_type": "Full-time",
  "credit_score": 680,
  "loan_amount": 250000,
  "loan_tenure_months": 360,
  "existing_liabilities": 45000,
  "location": "New York",
  "applicant_email": "manual@test.com"
}
```

**Expected:** MANUAL_REVIEW with risk_score 50-69

---

## API Response for Rejected Application

```json
{
  "application_id": "LOAN-20261029-XXXXXXXX",
  "status": "completed",
  "created_at": "2026-10-29T10:30:00",
  "message": "❌ Loan Decision: REJECTED",
  "decision": "REJECTED",
  "risk_score": 75.0,
  "confidence_score": 82.0,
  "case_id": "CASE-XXXXXXXX",
  "key_factors": [
    "Very high debt-to-income ratio (>50%)",
    "Fair credit history (650-699)",
    "Low annual income (<$60k)"
  ],
  "reasoning": "High-risk application with significant concerns including elevated debt levels, lower credit score, or unfavorable debt-to-income ratio."
}
```

---

## Summary

**An application is REJECTED when:**

✗ Risk Score ≥ 70  

**Common reasons:**
- DTI Ratio > 50%
- Credit Score < 650
- Loan-to-Income Ratio > 5x
- Multiple negative factors combined

**To avoid rejection:**
- Improve credit score to 700+
- Lower DTI ratio to <45%
- Increase income or reduce loan amount
- Secure stable employment
- Pay down existing debts before applying

---

*Last Updated: October 29, 2026*
