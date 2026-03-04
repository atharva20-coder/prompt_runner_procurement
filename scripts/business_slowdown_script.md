# BUSINESS SLOWDOWN INVESTIGATION SCRIPT

## State Fields (included in `state` key of your JSON response)

```json
{
  "script_loaded": true,
  "premature_commitment": null,
  "business_type": null,
  "slowdown_reason": null,
  "recovery_status": null,
  "alternate_income": null,
  "avoidance_count": 0,
  "exit_criteria_matched": false
}
```

**Field Descriptions:**
- `script_loaded`: Always true when this script is loaded
- `business_type`: Type of business - "Retail", "Manufacturing", "Services", etc. (Required)
- `slowdown_reason`: What caused slowdown (Required)
- `recovery_status`: "EXPECTED_SOON" | "EXPECTED_LATER" | "UNCERTAIN" | "NOT_EXPECTED" (Required)
- `alternate_income`: true | false (Optional)
- `avoidance_count`: Number of non-responses so far (inherited from main prompt state)
- `exit_criteria_matched`: Set to true when exit criteria are met

---

## QUESTIONS (Ask in Priority Order)

### Question 1 (Priority: HIGH)
**Target Field:** `business_type`  
**Question:** "What business are you in?"  
**Also Captures:** business_name

**Field Mapping:**
- Capture business type: "Retail shop", "Manufacturing", "Services", etc.

---

### Question 2 (Priority: HIGH)
**Target Field:** `slowdown_reason`  
**Question:** "What caused the slowdown?"  
**Also Captures:** slowdown_since, previous_monthly_income, current_monthly_income

**Field Mapping:**
- Capture reason: "Market slow", "Customer loss", "Competition", "Seasonal", etc.
- Note timing if shared: "since Diwali" → slowdown_since = "November 2025"

---

### Question 3 (Priority: HIGH)
**Target Field:** `recovery_status`  
**Question:** "See it recovering soon?"  
**Also Captures:** recovery_timeline

**Field Mapping:**
- "yes, soon" / "haan, jaldi" / "within month" → `recovery_status = "EXPECTED_SOON"`
- "will take time" / "2-3 months" → `recovery_status = "EXPECTED_LATER"`
- "not sure" / "pata nahi" → `recovery_status = "UNCERTAIN"`
- "unlikely" / "not recovering" → `recovery_status = "NOT_EXPECTED"`

---

### Question 4 (Priority: MEDIUM)
**Target Field:** `alternate_income`  
**Question:** "Any other income source?"  
**Also Captures:** alternate_business_detail

**Field Mapping:**
- "yes" / "haan" → `alternate_income = true`
- "no" / "nahi" → `alternate_income = false`

---

## EXIT CRITERIA

Exit to RECOVERY stage when:
1. All 3 required fields (`business_type`, `slowdown_reason`, `recovery_status`) captured, OR
2. `avoidance_count` >= 4