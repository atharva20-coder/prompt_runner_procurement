# SINGLE SOURCE DEPENDENCY INVESTIGATION SCRIPT

## State Fields (included in `state` key of your JSON response)

```json
{
  "script_loaded": true,
  "ip_lock_in_level": null,
  "switching_cost_estimate": null,
  "volume_consolidation_willingness": null,
  "contingency_stock_status": null,
  "avoidance_count": 0,
  "exit_criteria_matched": false
}
```

**Field Descriptions:**

- `script_loaded`: Always true when this script is loaded
- `ip_lock_in_level`: "HIGH" | "MODERATE" | "LOW" -> Extent to which our engineering or processes are locked into their proprietary IP or specific tooling (Required)
- `switching_cost_estimate`: Supplier's perception of our financial/time burden to resource (e.g., 12 months for recertification) (Required)
- `volume_consolidation_willingness`: `true` | `false` -> Can we secure preferential pricing if we officially consolidate 100% of category spend with them? (Required)
- `contingency_stock_status`: Existing safety stock or vendor-managed inventory (VMI) protecting us from stockouts (Optional)
- `avoidance_count`: Number of non-responses (inherited)
- `exit_criteria_matched`: Set to true when exit criteria are met

---

## QUESTIONS (Ask in Priority Order)

### Question 1 (Priority: HIGH)

**Target Field:** `ip_lock_in_level`  
**Question:** "Given our reliance on your specific tooling and tolerances, how customized do you view this assembly versus an off-the-shelf alternative?"  
**Also Captures:** customization_premium

**Field Mapping:**

- "Highly customized" / "Our proprietary process" → `ip_lock_in_level = "HIGH"`
- "Some specific tooling" / "Slightly modified" → `ip_lock_in_level = "MODERATE"`
- "Standard industry spec" / "Interchangeable" → `ip_lock_in_level = "LOW"`

---

### Question 2 (Priority: HIGH)

**Target Field:** `switching_cost_estimate`  
**Question:** "From your vantage point in the market, what's a typical PPAP or recertification timeline if we were to dual-source this footprint?"  
**Also Captures:** competitive_moat_perception

**Field Mapping:**

- Capture timeline/cost: "At least 18 months of testing", "Significant re-tooling cost", "Fairly quick if specs match"

---

### Question 3 (Priority: HIGH)

**Target Field:** `volume_consolidation_willingness`  
**Question:** "If we move from just a single source on this SKU to consolidating the entire adjacent category under a master strategic agreement, what margin compression can we expect?"  
**Also Captures:** leverage_creation

**Field Mapping:**

- "Open to aggressive pricing for 100% share" → `volume_consolidation_willingness = true`
- "Pricing is already fully optimized" → `volume_consolidation_willingness = false`

---

### Question 4 (Priority: MEDIUM)

**Target Field:** `contingency_stock_status`  
**Question:** "To mitigate this single point of failure within our supply chain, what VMI or strategic buffer stock are you actively holding for us?"  
**Also Captures:** risk_mitigation_posture

**Field Mapping:**

- Capture setup: "Holding 60 days on the floor", "Make-to-order only", "Consignment model active"

---

## EXIT CRITERIA

Exit to NEGOTIATION stage when:

1. All 3 required fields (`ip_lock_in_level`, `switching_cost_estimate`, `volume_consolidation_willingness`) are captured, OR
2. `avoidance_count` >= 3
