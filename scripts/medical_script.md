# MEDICAL INVESTIGATION SCRIPT

## State Fields (included in `state` key of your JSON response)

```json
{
  "script_loaded": true,
  "premature_commitment": null,
  "medical_subject": null,
  "medical_type": null,
  "insurance_status": null,
  "recovery_timeline": null,
  "avoidance_count": 0,
  "exit_criteria_matched": false
}
```

**Field Descriptions:**
- `script_loaded`: Always true when this script is loaded
- `medical_subject`: "SELF" | "FAMILY_MEMBER" (Required).
- `medical_type`: "PLANNED_TREATMENT" | "ILLNESS" | "ACCIDENT" (Required)
- `insurance_status`: "FULLY_COVERED" | "PARTIALLY_COVERED" | "REIMBURSEMENT_PENDING" | "NOT_AVAILABLE" (Required)
- `recovery_timeline`: When situation expected to improve (Optional)
- `avoidance_count`: Number of non-responses so far (inherited from main prompt state)
- `exit_criteria_matched`: Set to true when exit criteria are met

**IMPORTANT**: If the customer has already mentioned the medical subject, medical type, or insurance status in the previous turn, do not ask the question again. Instead, update the corresponding field in `state` and move to the next question.
---

## QUESTIONS (Ask in Priority Order)

### Question 1 (Priority: HIGH)
**Target Field:** `medical_subject`  
**Question:** "Is this related to your own health or someone in the family?"  
**Also Captures:** subject_detail (e.g., "Mother", "Father", "Spouse")

**Field Mapping:**
- "my own" / "myself" / "meri" → `medical_subject = "SELF"`
- "family" / "mother" / "father" / "wife" / "husband" / "child" → `medical_subject = "FAMILY_MEMBER"`

---

### Question 2 (Priority: HIGH)
**Target Field:** `medical_type`  
**Question:** "Was this a planned treatment, illness, or an accident?"  
**Also Captures:** condition (e.g., "Heart surgery", "Cancer treatment")

**Field Mapping:**
- "planned" / "surgery" / "operation scheduled" → `medical_type = "PLANNED_TREATMENT"`
- "illness" / "disease" / "bimari" / "sick" → `medical_type = "ILLNESS"`
- "accident" / "injury" / "fall" → `medical_type = "ACCIDENT"`

---

### Question 3 (Priority: HIGH)
**Target Field:** `insurance_status`  
**Question:** "Do you have any insurance or coverage supporting this?"  
**Also Captures:** insurance_available (true/false)

**Field Mapping:**
- "fully covered" / "insurance paying everything" → `insurance_status = "FULLY_COVERED"`
- "partial" / "some covered" / "co-pay" → `insurance_status = "PARTIALLY_COVERED"`
- "waiting for reimbursement" / "claim pending" / "paid upfront" → `insurance_status = "REIMBURSEMENT_PENDING"`
- "no insurance" / "not covered" / "nahi hai" → `insurance_status = "NOT_AVAILABLE"`

---

### Question 4 (Priority: MEDIUM) — Conditional
**Condition:** Ask ONLY if `insurance_status == "REIMBURSEMENT_PENDING"`  
**Target Field:** `recovery_timeline` (via insurance expected date)  
**Question:** "When do you expect the reimbursement to come through?"  
**Also Captures:** insurance_amount_pending, insurance_expected_date

---

### Question 4 (Priority: MEDIUM) — Alternative
**Condition:** Ask if Question 4 conditional not applicable and questions < 4  
**Target Field:** `recovery_timeline`  
**Question:** "When do you expect things to get better?"

---

## EXIT CRITERIA

Exit to RECOVERY stage when:
1. All 3 required fields (`medical_subject`, `medical_type`, `insurance_status`) are captured, OR
2. 4 questions have been asked, OR
3. `avoidance_count` >= 4