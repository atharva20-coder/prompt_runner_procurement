# DEMAND SURGE ALLOCATION INVESTIGATION SCRIPT

## State Fields (included in `state` key of your JSON response)

```json
{
  "script_loaded": true,
  "surge_capacity_limit": null,
  "expedite_premium_rate": null,
  "inventory_buffer_status": null,
  "tier_two_readiness": null,
  "avoidance_count": 0,
  "exit_criteria_matched": false
}
```

**Field Descriptions:**

- `script_loaded`: Always true when this script is loaded
- `surge_capacity_limit`: Maximal upside flexibility above forecasted baseline (e.g., +20% run rate) (Required)
- `expedite_premium_rate`: Financial delta required to prioritize our allocations over competing accounts (e.g., Overtime pay, air freight) (Required)
- `inventory_buffer_status`: Existing raw/finished goods inventory that can be immediately drawn down (Required)
- `tier_two_readiness`: Can the supplier's critical upstream nodes handle the aggregated surge? (Optional)
- `avoidance_count`: Number of non-responses (inherited)
- `exit_criteria_matched`: Set to true when exit criteria are met

---

## QUESTIONS (Ask in Priority Order)

### Question 1 (Priority: HIGH)

**Target Field:** `surge_capacity_limit`  
**Question:** "With our sudden demand upside, what is your absolute ceiling for upside flex without breaking SLAs on standard lead times?"  
**Also Captures:** utilization_headroom

**Field Mapping:**

- Capture limit: "20% above baseline", "Flat capacity, requires allocation", "Can handle double volume with 3rd shift"

---

### Question 2 (Priority: HIGH)

**Target Field:** `expedite_premium_rate`  
**Question:** "If we need to jump the queue to secure allocation, what is the exact premium for expediting via OT or air freight?"  
**Also Captures:** cost_of_speed

**Field Mapping:**

- Capture rate: "$15/unit expedite fee", "Straight pass-through of OT costs", "No premium, just extended lead times"

---

### Question 3 (Priority: HIGH)

**Target Field:** `inventory_buffer_status`  
**Question:** "How much finished goods inventory or safety stock do you have on the floor that we can immediately draw down to bridge the gap?"  
**Also Captures:** working_capital_leverage

**Field Mapping:**

- Capture buffer: "4 weeks of coverage available", "Running JIT, zero buffer", "VMI is fully stocked"

---

### Question 4 (Priority: MEDIUM)

**Target Field:** `tier_two_readiness`  
**Question:** "Assuming your lines can handle the surge, are your Tier-2 raw material suppliers equally prepared to step up allocations?"  
**Also Captures:** upstream_risk

**Field Mapping:**

- Capture readiness: "Resin supply is locked in", "Packaging is the bottleneck constraint", "Need 4 weeks to secure upstream material"

---

## EXIT CRITERIA

Exit to NEGOTIATION stage when:

1. All 3 required fields (`surge_capacity_limit`, `expedite_premium_rate`, `inventory_buffer_status`) are captured, OR
2. `avoidance_count` >= 3
