<!-- PURPOSE: Manufacturing / Components supplier qualification script. Loaded when
     category = MANUFACTURING. Captures production-specific context (lead times, MOQ,
     capacity utilisation) to inform NARA's negotiation strategy.
     Archetype: Manufacturing suppliers prioritize production stability, long-term contracts, MOQ. -->

# MANUFACTURING / COMPONENTS QUALIFICATION SCRIPT

## State Fields

```json
{
  "script_loaded": true,
  "lead_time_status": null,
  "capacity_utilisation": null,
  "moq_flexibility": null,
  "quality_issues": null,
  "avoidance_count": 0,
  "exit_criteria_matched": false
}
```

**Field Descriptions:**

- `script_loaded`: Always true
- `lead_time_status`: "ON_TRACK" | "EXTENDED" | "VARIABLE" — current delivery performance (Required)
- `capacity_utilisation`: "HIGH" | "MODERATE" | "LOW" — how full their production lines are (Required)
- `moq_flexibility`: "FLEXIBLE" | "RIGID" | "MODERATE" — willingness to adjust minimum orders (Required)
- `quality_issues`: true | false — any recent quality concerns (Optional)

---

## QUESTIONS (Ask in Priority Order)

### Question 1 (Priority: HIGH)

**Target Field:** `lead_time_status`
**Question:** "How are lead times looking? Any changes from what we've been seeing?"

**Field Mapping:**

- "on track" / "same as before" / "standard" → `lead_time_status = "ON_TRACK"`
- "extended" / "longer" / "6-8 weeks now" → `lead_time_status = "EXTENDED"`
- "depends" / "varies" → `lead_time_status = "VARIABLE"`

---

### Question 2 (Priority: HIGH)

**Target Field:** `capacity_utilisation`
**Question:** "How's your production schedule? Running at full capacity or is there room?"

**Field Mapping:**

- "full" / "at capacity" / "tight" → `capacity_utilisation = "HIGH"`
- "some room" / "moderate" → `capacity_utilisation = "MODERATE"`
- "plenty of room" / "looking for orders" → `capacity_utilisation = "LOW"`

---

### Question 3 (Priority: HIGH)

**Target Field:** `moq_flexibility`
**Question:** "Any flexibility on minimum order quantities if we adjust the structure?"

**Field Mapping:**

- "yes" / "we can adjust" → `moq_flexibility = "FLEXIBLE"`
- "standard MOQ" / "can't change" → `moq_flexibility = "RIGID"`
- "depends on volume" / "case by case" → `moq_flexibility = "MODERATE"`

---

### Question 4 (Priority: MEDIUM)

**Target Field:** `quality_issues`
**Question:** Infer from context — check SUPPLIER_CONTEXT for any quality-related notes. If none, skip.

---

## LEVERAGE NOTES (For Negotiation Stage)

- If `capacity_utilisation = "LOW"` → Supplier needs orders. Strong price leverage
- If `lead_time_status = "EXTENDED"` → Offer production stability for price. Stable cadence = cheaper
- If `moq_flexibility = "FLEXIBLE"` → Use MOQ as trade lever in cross-axis deals
- If `quality_issues = true` → Leverage for price reduction or rebate improvement

---

## EXIT CRITERIA

Exit to NEGOTIATION stage when:

1. All 3 required fields captured, OR
2. `avoidance_count` >= 3
