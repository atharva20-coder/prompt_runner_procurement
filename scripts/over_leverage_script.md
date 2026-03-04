# OVER LEVERAGE INVESTIGATION SCRIPT

## State Fields (included in `state` key of your JSON response)

```json
{
  "script_loaded": true,
  "premature_commitment": null,
  "total_emi_burden": null,
  "alternate_inflow_expected": null,
  "alternate_inflow_timeline": null,
  "deleveraging_plan": null,
  "avoidance_count": 0,
  "exit_criteria_matched": false
}
```

**Field Descriptions:**
- `script_loaded`: Always true when this script is loaded
- `total_emi_burden`: Total monthly EMI across all loans (Required)
- `alternate_inflow_expected`: true | false (Required)
- `alternate_inflow_timeline`: When alternate funds expected (Conditional)
- `deleveraging_plan`: Plan to reduce loan obligations (Required)
- `avoidance_count`: Number of non-responses so far (inherited from main prompt state)
- `exit_criteria_matched`: Set to true when exit criteria are met

---

## QUESTIONS (Ask in Priority Order)

### Question 1 (Priority: HIGH)
**Target Field:** `total_emi_burden`  
**Question:** "What's your total monthly EMI across all loans?"  
**Also Captures:** total_loans, monthly_income, leverage_ratio, other_lenders

**Field Mapping:**
- Capture total EMI amount: "50,000 per month" → `total_emi_burden = 50000`
- If income shared, calculate leverage_ratio

---

### Question 2 (Priority: HIGH)
**Target Field:** `alternate_inflow_expected`  
**Question:** "Any lump sum or funds expected soon?"  
**Also Captures:** alternate_inflow_detail, alternate_inflow_amount

**Field Mapping:**
- "yes" / "expecting" / "will get" → `alternate_inflow_expected = true`
- "no" / "nothing expected" → `alternate_inflow_expected = false`

---

### Question 3 (Priority: MEDIUM) — Conditional
**Condition:** Ask ONLY if `alternate_inflow_expected == true`  
**Target Field:** `alternate_inflow_timeline`  
**Question:** "When do you expect those?"  

---

### Question 4 (Priority: HIGH)
**Target Field:** `deleveraging_plan`  
**Question:** "Any plan to manage or reduce your loans?"  

**Field Mapping:**
- Capture plan: "Will close one loan", "Selling asset", "Consolidating", etc.

---

## EXIT CRITERIA

Exit to RECOVERY stage when:
1. All 3 required fields (`total_emi_burden`, `alternate_inflow_expected`, `deleveraging_plan`) captured, OR
2. `avoidance_count` >= 4