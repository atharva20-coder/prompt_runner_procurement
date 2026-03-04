<!-- PURPOSE: Logistics / Freight supplier qualification script. Loaded when
     category = LOGISTICS_FREIGHT. Captures logistics-specific context (route structure,
     fill rates, lane pricing) to inform NARA's negotiation.
     Archetype: Logistics suppliers prioritize route consistency, volume fills, payment speed. -->

# LOGISTICS / FREIGHT QUALIFICATION SCRIPT

## State Fields

```json
{
  "script_loaded": true,
  "route_structure": null,
  "fill_rate": null,
  "lane_competition": null,
  "seasonal_impact": null,
  "avoidance_count": 0,
  "exit_criteria_matched": false
}
```

**Field Descriptions:**

- `script_loaded`: Always true
- `route_structure`: "DEDICATED" | "SHARED" | "MIXED" — lane allocation type (Required)
- `fill_rate`: "HIGH" | "MODERATE" | "LOW" — how full their trucks/containers run (Required)
- `lane_competition`: "HIGH" | "MODERATE" | "LOW" — competition on these specific routes (Required)
- `seasonal_impact`: "SIGNIFICANT" | "MODERATE" | "MINIMAL" — seasonal rate fluctuations (Optional)

---

## QUESTIONS (Ask in Priority Order)

### Question 1 (Priority: HIGH)

**Target Field:** `route_structure`
**Question:** "Are our routes on dedicated lanes or shared with other clients?"

**Field Mapping:**

- "dedicated" / "exclusive" → `route_structure = "DEDICATED"`
- "shared" / "pooled" → `route_structure = "SHARED"`
- "mix of both" → `route_structure = "MIXED"`

---

### Question 2 (Priority: HIGH)

**Target Field:** `fill_rate`
**Question:** "How are fill rates looking on our lanes? Running full loads?"

**Field Mapping:**

- "full" / "at capacity" / "100%" → `fill_rate = "HIGH"`
- "mostly full" / "75-90%" → `fill_rate = "MODERATE"`
- "partial loads" / "room to fill" → `fill_rate = "LOW"`

---

### Question 3 (Priority: HIGH)

**Target Field:** `lane_competition`
**Question:** "How many other carriers operate on these routes? Is it competitive?"

**Field Mapping:**

- "many carriers" / "very competitive" → `lane_competition = "HIGH"`
- "a few" / "some competition" → `lane_competition = "MODERATE"`
- "limited options" / "we're the main carrier" → `lane_competition = "LOW"`

---

### Question 4 (Priority: MEDIUM)

**Target Field:** `seasonal_impact`
**Question:** "Any seasonal spikes we should factor into the rate structure?"

**Field Mapping:**

- "significant peak seasons" → `seasonal_impact = "SIGNIFICANT"`
- "some variation" → `seasonal_impact = "MODERATE"`
- "fairly consistent" → `seasonal_impact = "MINIMAL"`

---

## LEVERAGE NOTES (For Negotiation Stage)

- If `fill_rate = "LOW"` → Supplier needs volume. Guaranteed fills for lower rate
- If `route_structure = "SHARED"` → Push for dedicated at lower rate via volume commitment
- If `lane_competition = "HIGH"` → Cite Competition strategy is highly effective
- If `seasonal_impact = "SIGNIFICANT"` → Lock off-peak rates, negotiate peak surcharge caps

---

## EXIT CRITERIA

Exit to NEGOTIATION stage when:

1. All 3 required fields captured, OR
2. `avoidance_count` >= 3
