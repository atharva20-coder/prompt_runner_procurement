# CAPACITY CONSTRAINT INVESTIGATION SCRIPT

## State Fields (included in `state` key of your JSON response)

```json
{
  "script_loaded": true,
  "bottleneck_node": null,
  "oee_expansion_timeline": null,
  "allocation_ceiling": null,
  "capex_co_investment_required": null,
  "avoidance_count": 0,
  "exit_criteria_matched": false
}
```

**Field Descriptions:**

- `script_loaded`: Always true when this script is loaded
- `bottleneck_node`: Specific restriction (e.g., labor constraints, machine utilization, raw material allocation) (Required)
- `oee_expansion_timeline`: Lead time expected to improve Overall Equipment Effectiveness (OEE) or bring new capacity online (Required)
- `allocation_ceiling`: Maximum volume allocation without jeopardizing SLA or OTIF (On-Time In-Full) metrics (Required)
- `capex_co_investment_required`: `true` | `false` -> Do they need a hard volume commitment to justify CapEx expansion? (Optional)
- `avoidance_count`: Number of non-responses (inherited)
- `exit_criteria_matched`: Set to true when exit criteria are met

---

## QUESTIONS (Ask in Priority Order)

### Question 1 (Priority: HIGH)

**Target Field:** `bottleneck_node`  
**Question:** "Are your current bottlenecks rooted in direct labor availability, machine utilization limits, or upstream Tier-2 allocations?"  
**Also Captures:** secondary_constraints

**Field Mapping:**

- Capture node: "Injection molding lines at capacity", "Labor shortage on 3rd shift", "Semiconductor allocation", etc.

---

### Question 2 (Priority: HIGH)

**Target Field:** `oee_expansion_timeline`  
**Question:** "What is your roadmap for expanding capacity or improving OEE, and what's the lead time for stabilization?"  
**Also Captures:** expansion_plans

**Field Mapping:**

- Capture timeline: "Q3 CapEx deployment", "Next quarter", "No immediate capital plans"

---

### Question 3 (Priority: HIGH)

**Target Field:** `allocation_ceiling`  
**Question:** "What is the hard allocation ceiling you can commit to us without putting our OTIF metrics at risk?"  
**Also Captures:** utilization_rate

**Field Mapping:**

- Capture limit: "Current baseline + 15%", "Capped until Q4", "10k units maximum run rate"

---

### Question 4 (Priority: MEDIUM)

**Target Field:** `capex_co_investment_required`  
**Question:** "If we provided a firm, multi-year volume forecast, would that underwrite the CapEx needed to unblock this node?"  
**Also Captures:** strategic_partnership_interest

**Field Mapping:**

- "yes" / "that mitigates the risk" → `capex_co_investment_required = true`
- "no" / "capital constrained" → `capex_co_investment_required = false`

---

## EXIT CRITERIA

Exit to NEGOTIATION stage when:

1. All 3 required fields (`bottleneck_node`, `oee_expansion_timeline`, `allocation_ceiling`) are captured, OR
2. `avoidance_count` >= 3
