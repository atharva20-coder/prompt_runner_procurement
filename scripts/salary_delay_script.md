# SALARY DELAY INVESTIGATION SCRIPT

## State Fields (included in `state` key of your JSON response)

```json
{
  "script_loaded": true,
  "premature_commitment": null,
  "usual_salary_date": null,
  "expected_salary_date": null,
  "delay_frequency": null,
  "avoidance_count": 0,
  "exit_criteria_matched": false
}
```

**Field Descriptions:**
- `script_loaded`: Always true when this script is loaded
- `usual_salary_date`: Day of month salary usually received (Required)
- `expected_salary_date`: When salary expected this time (Required)
- `delay_frequency`: "FIRST_TIME" | "OCCASIONAL" | "RECURRING" (Required)
- `avoidance_count`: Number of non-responses so far (inherited from main prompt state)
- `exit_criteria_matched`: Set to true when exit criteria are met

---

## QUESTIONS (Ask in Priority Order)

### Question 1 (Priority: HIGH)
**Target Field:** `usual_salary_date`  
**Question:** "When do you usually get paid?"  
**Also Captures:** employer_info

**Field Mapping:**
- Capture day of month (e.g., "1st", "5th", "7th")
- Convert to number: "1st" → 1, "end of month" → 30

---

### Question 2 (Priority: HIGH)
**Target Field:** `expected_salary_date`  
**Question:** "When's salary expected this time?"  
**Also Captures:** expected_amount, current_delay_days

**Field Mapping:**
- Capture specific date or relative time
- "20th December" → `expected_salary_date = "20-Dec-2025"`
- "Next week" → `expected_salary_date = "Within 7 days"`

---

### Question 3 (Priority: HIGH)
**Target Field:** `delay_frequency`  
**Question:** "Has this happened before, or is it unusual this time?"  
**Also Captures:** employer_confirmation

**Field Mapping:**
- "first time" / "pehli baar" / "never before" → `delay_frequency = "FIRST_TIME"`
- "sometimes" / "kabhi kabhi" / "occasionally" → `delay_frequency = "OCCASIONAL"`
- "every month" / "regular issue" / "hamesha" → `delay_frequency = "RECURRING"`

---

## EXIT CRITERIA

Exit to RECOVERY stage when:
1. All 3 required fields captured, OR
2. `avoidance_count` >= 4