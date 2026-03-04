<!-- PURPOSE: IT Hardware / Equipment supplier qualification script. Loaded when
     category = IT_HARDWARE. Captures hardware-specific context (order patterns,
     standardisation level, maintenance/warranty) to inform NARA's negotiation.
     Archetype: IT Hardware suppliers prioritize order size, standardisation, maintenance contracts. -->

# IT HARDWARE / EQUIPMENT QUALIFICATION SCRIPT

## State Fields

```json
{
  "script_loaded": true,
  "order_pattern": null,
  "standardisation_level": null,
  "maintenance_bundling": null,
  "refresh_cycle": null,
  "avoidance_count": 0,
  "exit_criteria_matched": false
}
```

**Field Descriptions:**

- `script_loaded`: Always true
- `order_pattern`: "BULK" | "RECURRING" | "AD_HOC" — how buyer typically orders (Required)
- `standardisation_level`: "HIGH" | "MODERATE" | "LOW" — how standardised SKUs are across buyer's org (Required)
- `maintenance_bundling`: true | false — whether maintenance/warranty is bundled or separate (Required)
- `refresh_cycle`: "ANNUAL" | "BIENNIAL" | "AS_NEEDED" — hardware refresh cadence (Optional)

---

## QUESTIONS (Ask in Priority Order)

### Question 1 (Priority: HIGH)

**Target Field:** `order_pattern`
**Question:** "How do our orders typically come in — bulk purchases, regular scheduled orders, or ad hoc?"

**Field Mapping:**

- "bulk" / "large orders" / "one-time" → `order_pattern = "BULK"`
- "regular" / "scheduled" / "quarterly" → `order_pattern = "RECURRING"`
- "as needed" / "ad hoc" / "varies" → `order_pattern = "AD_HOC"`

---

### Question 2 (Priority: HIGH)

**Target Field:** `standardisation_level`
**Question:** "Are we standardised on specific models, or is it a mix across our org?"

**Field Mapping:**

- "standardised" / "same models" / "consistent" → `standardisation_level = "HIGH"`
- "mostly standard" / "some variation" → `standardisation_level = "MODERATE"`
- "mixed" / "different models" / "custom" → `standardisation_level = "LOW"`

---

### Question 3 (Priority: HIGH)

**Target Field:** `maintenance_bundling`
**Question:** "Is maintenance and warranty bundled in, or do we handle that separately?"

**Field Mapping:**

- "bundled" / "included" / "all-in" → `maintenance_bundling = true`
- "separate" / "add-on" / "extra cost" → `maintenance_bundling = false`

---

### Question 4 (Priority: MEDIUM)

**Target Field:** `refresh_cycle`
**Question:** "What's our typical refresh cycle — annual, every couple of years?"

**Field Mapping:**

- "annual" / "every year" → `refresh_cycle = "ANNUAL"`
- "every 2 years" / "biennial" → `refresh_cycle = "BIENNIAL"`
- "as needed" / "when required" → `refresh_cycle = "AS_NEEDED"`

---

## LEVERAGE NOTES (For Negotiation Stage)

- If `order_pattern = "BULK"` → Large order leverage for unit price reduction
- If `standardisation_level = "HIGH"` → Operational savings for supplier; negotiate shared benefit
- If `maintenance_bundling = false` → Bundle maintenance for total cost reduction
- If `refresh_cycle = "ANNUAL"` → Predictable revenue for supplier; use for rate lock

---

## EXIT CRITERIA

Exit to NEGOTIATION stage when:

1. All 3 required fields captured, OR
2. `avoidance_count` >= 3
