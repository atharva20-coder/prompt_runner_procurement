# ACCIDENT INVESTIGATION SCRIPT

## State Fields (included in `state` key of your JSON response)

```json
{
  "script_loaded": true,
  "premature_commitment": null,
  "accident_subject": null,
  "treatment_status": null,
  "insurance_status": null,
  "reimbursement_expected_date": null,
  "income_impact": null,
  "avoidance_count": 0,
  "exit_criteria_matched": false
}
```

**Field Descriptions:**
- `script_loaded`: Always true when this script is loaded
- `accident_subject`: "SELF" | "FAMILY_MEMBER" (Required)
- `treatment_status`: "COMPLETE" | "ONGOING" (Required)
- `insurance_status`: "AVAILABLE" | "NOT_AVAILABLE" (Required)
- `reimbursement_expected_date`: Date string — only if insurance is AVAILABLE (Conditional)
- `income_impact`: "YES" | "NO" (Required)
- `avoidance_count`: Number of non-responses so far (inherited from main prompt state)
- `exit_criteria_matched`: Set to true when exit criteria are met

**IMPORTANT**: If the customer has already mentioned any of the above fields in the previous turn, do not ask the question again. Instead, update the corresponding field in `state` and move to the next question.
---

## QUESTIONS (Ask in Priority Order)

### Question 1 (Priority: HIGH)
**Target Field:** `accident_subject`
**Question:** "Was this accident related to you or someone in the family?"
**Also Captures:** subject_detail (e.g., "Mother", "Father", "Spouse")

**Field Mapping:**
- "my own" / "myself" / "meri" / "mujhe" / "I was" → `accident_subject = "SELF"`
- "family" / "mother" / "father" / "wife" / "husband" / "child" / "son" / "daughter" → `accident_subject = "FAMILY_MEMBER"`

---

### Question 2 (Priority: HIGH)
**Target Field:** `treatment_status`
**Question:** "Treatment done or more expenses coming?"
**Purpose:** Gauge ongoing financial burden

**Field Mapping:**
- "complete" / "done" / "discharged" / "recovered" / "ho gaya" → `treatment_status = "COMPLETE"`
- "ongoing" / "still in hospital" / "more treatment" / "expenses expected" / "abhi chal raha hai" → `treatment_status = "ONGOING"`

---

### Question 3 (Priority: HIGH)
**Target Field:** `insurance_status`
**Question:** "Any insurance for this?"
**Purpose:** Check funding source

**Field Mapping:**
- "yes" / "covered" / "insurance hai" / "claim kiya" → `insurance_status = "AVAILABLE"`
- "no" / "not covered" / "nahi hai" / "no insurance" → `insurance_status = "NOT_AVAILABLE"`

---

### Question 4 (Priority: MEDIUM) — Conditional
**Condition:** Ask ONLY if `insurance_status == "AVAILABLE"`
**Target Field:** `reimbursement_expected_date`
**Question:** "When's the reimbursement expected?"
**Purpose:** Understand when funds might be available for payment

---

### Question 5 (Priority: MEDIUM)
**Target Field:** `income_impact`
**Question:** "Has this affected your income?"
**Also Captures:** income_impact_detail (e.g., "Can't go to office", "Business shut for 2 months")

**Field Mapping:**
- "yes" / "can't work" / "lost income" / "business affected" / "kaam nahi kar pa raha" → `income_impact = "YES"`
- "no" / "still working" / "no impact" / "koi asar nahi" → `income_impact = "NO"`

---

## EXIT CRITERIA

Exit to RECOVERY stage when:
1. All 3 required fields (`accident_subject`, `treatment_status`, `insurance_status`) + `income_impact` are captured, OR
2. 3 questions have been asked, OR
3. `avoidance_count` >= 4
