<!-- PURPOSE: Packaging / Consumables supplier qualification script. Loaded when
     category = PACKAGING_CONSUMABLES. Captures packaging-specific context (forecast
     visibility, volume bands, material flexibility) to inform NARA's negotiation.
     Archetype: Packaging suppliers prioritize forecast visibility, volume bands, payment terms. -->

# PACKAGING / CONSUMABLES QUALIFICATION SCRIPT

## State Fields

```json
{
  "script_loaded": true,
  "forecast_sharing": null,
  "volume_band_status": null,
  "material_flexibility": null,
  "lead_time_reliability": null,
  "avoidance_count": 0,
  "exit_criteria_matched": false
}
```

**Field Descriptions:**

- `script_loaded`: Always true
- `forecast_sharing`: "FULL" | "PARTIAL" | "NONE" — how much demand forecast we share (Required)
- `volume_band_status`: "AT_THRESHOLD" | "BELOW" | "ABOVE" — where current volume sits vs. pricing tiers (Required)
- `material_flexibility`: "FLEXIBLE" | "LIMITED" | "RIGID" — willingness to adjust specs/materials (Required)
- `lead_time_reliability`: "RELIABLE" | "VARIABLE" | "PROBLEMATIC" — delivery consistency (Optional)

---

## QUESTIONS (Ask in Priority Order)

### Question 1 (Priority: HIGH)

**Target Field:** `forecast_sharing`
**Question:** "How much forecast visibility do you have from us — full quarterly, partial, or limited?"

**Field Mapping:**

- "full" / "quarterly forecast" / "good visibility" → `forecast_sharing = "FULL"`
- "some" / "monthly updates" → `forecast_sharing = "PARTIAL"`
- "limited" / "order by order" → `forecast_sharing = "NONE"`

---

### Question 2 (Priority: HIGH)

**Target Field:** `volume_band_status`
**Question:** "Where are we sitting on your volume tiers? Close to the next bracket?"

**Field Mapping:**

- "right at the threshold" / "about to hit next tier" → `volume_band_status = "AT_THRESHOLD"`
- "below" / "not yet at next tier" → `volume_band_status = "BELOW"`
- "above" / "already in top tier" → `volume_band_status = "ABOVE"`

---

### Question 3 (Priority: HIGH)

**Target Field:** `material_flexibility`
**Question:** "Any flexibility on materials or specs? We're open to alternatives if the value is there."

**Field Mapping:**

- "yes" / "alternatives available" → `material_flexibility = "FLEXIBLE"`
- "some options" / "minor adjustments" → `material_flexibility = "LIMITED"`
- "standard only" / "no substitutes" → `material_flexibility = "RIGID"`

---

### Question 4 (Priority: MEDIUM)

**Target Field:** `lead_time_reliability`
**Question:** "How's delivery reliability been? Any consistency issues?"

**Field Mapping:**

- "consistent" / "on time" → `lead_time_reliability = "RELIABLE"`
- "mostly" / "some delays" → `lead_time_reliability = "VARIABLE"`
- "issues" / "unreliable" → `lead_time_reliability = "PROBLEMATIC"`

---

## LEVERAGE NOTES (For Negotiation Stage)

- If `forecast_sharing = "NONE"` → Offer full forecast for pricing improvement (free lever)
- If `volume_band_status = "AT_THRESHOLD"` → Small volume increase triggers next price tier
- If `material_flexibility = "FLEXIBLE"` → Value engineering lever available for cost reduction
- If `lead_time_reliability = "PROBLEMATIC"` → Leverage for service credits or price reduction

---

## EXIT CRITERIA

Exit to NEGOTIATION stage when:

1. All 3 required fields captured, OR
2. `avoidance_count` >= 3
