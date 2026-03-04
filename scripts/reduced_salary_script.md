# REDUCED SALARY INVESTIGATION SCRIPT

## State Fields (included in `state` key of your JSON response)

```json
{
  "script_loaded": true,
  "premature_commitment": null,
  "reduction_type": null,
  "reduction_since": null,
  "alternate_income": null,
  "alternate_income_detail": null,
  "avoidance_count": 0,
  "exit_criteria_matched": false
}
```

**Field Descriptions:**
- `script_loaded`: Always true when this script is loaded
- `reduction_type`: "ONE_TIME" | "PERMANENT" (Required)
- `reduction_since`: When reduction started (Required)
- `alternate_income`: true | false (Required)
- `alternate_income_detail`: Description if true (Conditional)
- `avoidance_count`: Number of non-responses so far (inherited from main prompt state)
- `exit_criteria_matched`: Set to true when exit criteria are met

---

## QUESTIONS (Ask in Priority Order)

### Question 1 (Priority: HIGH)
**Target Field:** `reduction_type`  
**Question:** "Is this a temporary reduction or a longer-term change?"  
**Also Captures:** reduction_reason

**Field Mapping:**
- "temporary" / "for few months" / "will be restored" → `reduction_type = "ONE_TIME"`
- "permanent" / "new salary structure" / "won't change" → `reduction_type = "PERMANENT"`

---

### Question 2 (Priority: HIGH)
**Target Field:** `reduction_since`  
**Question:** "Since when has this reduction been in effect?"  
**Also Captures:** previous_salary, current_salary, reduction_percentage

**Field Mapping:**
- Capture date/month: "November se" → `reduction_since = "November 2025"`
- If customer shares amounts, calculate reduction_percentage

---

### Question 3 (Priority: HIGH)
**Target Field:** `alternate_income`  
**Question:** "Any other income source?"  

**Field Mapping:**
- "yes" / "haan" / "some income" → `alternate_income = true`
- "no" / "nahi" / "nothing else" → `alternate_income = false`

---

### Question 4 (Priority: MEDIUM) — Conditional
**Condition:** Ask ONLY if `alternate_income == true`  
**Target Field:** `alternate_income_detail`  
**Question:** "What's the source?"  
**Also Captures:** alternate_income_amount

---

## EXIT CRITERIA

Exit to RECOVERY stage when:
1. All 3 required fields (`reduction_type`, `reduction_since`, `alternate_income`) captured, OR
2. `avoidance_count` >= 4

---