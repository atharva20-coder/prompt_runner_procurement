<!-- PURPOSE: Professional Services supplier qualification script. Loaded when
     category = PROFESSIONAL_SERVICES. Captures services-specific context (engagement model,
     utilisation rates, scope clarity) to inform NARA's negotiation.
     Archetype: Professional services suppliers prioritize scope clarity, project pipeline, payment terms. -->

# PROFESSIONAL SERVICES QUALIFICATION SCRIPT

## State Fields

```json
{
  "script_loaded": true,
  "engagement_model": null,
  "utilisation_rate": null,
  "scope_clarity": null,
  "pipeline_dependency": null,
  "avoidance_count": 0,
  "exit_criteria_matched": false
}
```

**Field Descriptions:**

- `script_loaded`: Always true
- `engagement_model`: "T&M" | "FIXED_PRICE" | "RETAINER" | "OUTCOME_BASED" — billing model (Required)
- `utilisation_rate`: "HIGH" | "MODERATE" | "LOW" — how busy their team is (Required)
- `scope_clarity`: "CLEAR" | "EVOLVING" | "UNDEFINED" — how well-defined the SOW is (Required)
- `pipeline_dependency`: true | false — whether they depend on ongoing project pipeline (Optional)

---

## QUESTIONS (Ask in Priority Order)

### Question 1 (Priority: HIGH)

**Target Field:** `engagement_model`
**Question:** "How's the current engagement structured — T&M, fixed price, or retainer?"

**Field Mapping:**

- "T&M" / "time and materials" → `engagement_model = "T&M"`
- "fixed price" / "project-based" → `engagement_model = "FIXED_PRICE"`
- "retainer" / "monthly fee" → `engagement_model = "RETAINER"`
- "outcome-based" / "performance" → `engagement_model = "OUTCOME_BASED"`

---

### Question 2 (Priority: HIGH)

**Target Field:** `utilisation_rate`
**Question:** "How's the team's bandwidth? Are they staffed up or looking for more projects?"

**Field Mapping:**

- "fully staffed" / "at capacity" → `utilisation_rate = "HIGH"`
- "some availability" / "can take more" → `utilisation_rate = "MODERATE"`
- "looking for projects" / "bench available" → `utilisation_rate = "LOW"`

---

### Question 3 (Priority: HIGH)

**Target Field:** `scope_clarity`
**Question:** "How well-defined is the scope for the next phase — or are we still evolving it?"

**Field Mapping:**

- "well-defined" / "SOW is clear" → `scope_clarity = "CLEAR"`
- "evolving" / "some changes expected" → `scope_clarity = "EVOLVING"`
- "not defined yet" / "TBD" → `scope_clarity = "UNDEFINED"`

---

### Question 4 (Priority: MEDIUM)

**Target Field:** `pipeline_dependency`
**Question:** Infer — if supplier emphasises "continuation" or "next phase" frequently.

---

## LEVERAGE NOTES (For Negotiation Stage)

- If `utilisation_rate = "LOW"` → Supplier needs projects. Strong rate leverage
- If `engagement_model = "T&M"` → Push for fixed-price or blended rate for cost predictability
- If `scope_clarity = "CLEAR"` → Fixed price is achievable. Use for rate reduction
- If `pipeline_dependency = true` → Multi-project pipeline is a powerful concession lever

---

## EXIT CRITERIA

Exit to NEGOTIATION stage when:

1. All 3 required fields captured, OR
2. `avoidance_count` >= 3
