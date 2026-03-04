# CUSTOMER PAYMENT DELAY INVESTIGATION SCRIPT

## State Fields (included in `state` key of your JSON response)

```json
{
  "script_loaded": true,
  "premature_commitment": null,
  "receivable_amount": null,
  "expected_payment_date": null,
  "customer_confirmed": null,
  "avoidance_count": 0,
  "exit_criteria_matched": false
}
```

**Field Descriptions:**

- `script_loaded`: Always true when this script is loaded
- `receivable_amount`: Amount pending from customers (Required)
- `expected_payment_date`: When payment expected (Required)
- `customer_confirmed`: true | false (Required)
- `avoidance_count`: Number of non-responses so far (inherited from main prompt state)
- `exit_criteria_matched`: Set to true when exit criteria are met

---

## QUESTIONS (Ask in Priority Order)

### Question 1 (Priority: HIGH)

**Target Field:** `expected_payment_date`  
**Question:** "When's your customer's payment expected?"  
**Also Captures:** receivable_amount, receivable_from

**Field Mapping:**

- Capture date: "End of December" → `expected_payment_date = "End of December"`
- If amount shared, capture: `receivable_amount = amount`

---

### Question 2 (Priority: HIGH)

**Target Field:** `customer_confirmed`  
**Question:** "Has your customer confirmed a date?"

**Field Mapping:**

- "yes" / "confirmed" / "committed" → `customer_confirmed = true`
- "no" / "not sure" / "waiting" → `customer_confirmed = false`

---

### Question 3 (Priority: MEDIUM)

**Target Field:** `receivable_amount` (if not captured in Q1)  
**Question:** "How much are you expecting?"  
**Also Captures:** partial_expected

**Field Mapping:**

- Capture amount in rupees

---

## EXIT CRITERIA

Exit to RECOVERY stage when:

1. All 3 required fields captured, OR
2. `avoidance_count` >= 4

---
