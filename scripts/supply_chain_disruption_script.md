# SUPPLY CHAIN DISRUPTION INVESTIGATION SCRIPT

## State Fields (included in `state` key of your JSON response)

```json
{
  "script_loaded": true,
  "disruption_node": null,
  "force_majeure_invoked": null,
  "alternative_routing_premium": null,
  "lead_time_variance": null,
  "avoidance_count": 0,
  "exit_criteria_matched": false
}
```

**Field Descriptions:**

- `script_loaded`: Always true when this script is loaded
- `disruption_node`: The exact breakdown point (e.g., Tier-2 supplier insolvency, port congestion, geopolitical trade restriction) (Required)
- `force_majeure_invoked`: `true` | `false` -> Are they officially claiming Force Majeure, or is this a managed escalation? (Required)
- `alternative_routing_premium`: Estimated premium costs for expedited freight or alternative sourcing to bridge the gap (Required)
- `lead_time_variance`: The delta in standard lead time (e.g., +4 weeks to dock) (Optional)
- `avoidance_count`: Number of non-responses (inherited)
- `exit_criteria_matched`: Set to true when exit criteria are met

---

## QUESTIONS (Ask in Priority Order)

### Question 1 (Priority: HIGH)

**Target Field:** `disruption_node`  
**Question:** "Can you map out exactly where the disruption node is? Is this a Tier-2 component failure or a logistics bottleneck?"  
**Also Captures:** root_cause_analysis

**Field Mapping:**

- Capture node: "Red Sea freight diversion", "Sub-tier supplier bankruptcy", "Customs embargo"

---

### Question 2 (Priority: HIGH)

**Target Field:** `force_majeure_invoked`  
**Question:** "From a contractual standpoint, is your legal team positioning this under a Force Majeure clause, or are we treating this as a managed commercial escalation?"  
**Also Captures:** liability_stance

**Field Mapping:**

- "yes" / "Force Majeure applies" → `force_majeure_invoked = true`
- "no" / "working through it" → `force_majeure_invoked = false`

---

### Question 3 (Priority: HIGH)

**Target Field:** `alternative_routing_premium`  
**Question:** "What is the premium variance to air-freight or dual-source the shortage, and how are we splitting that liability?"  
**Also Captures:** cost_mitigation_strategy

**Field Mapping:**

- Capture premium: "$50k expedite fee", "Absorbing air freight on our end", "Need a 10% premium for alternative raw material"

---

### Question 4 (Priority: MEDIUM)

**Target Field:** `lead_time_variance`  
**Question:** "Assuming standard routing, what is the net variance to our baseline lead time for the next three POs?"  
**Also Captures:** safety_stock_implications

**Field Mapping:**

- Capture variance: "+3 weeks", "Delayed until Q3", "Rolling delays of 10 days per shipment"

---

## EXIT CRITERIA

Exit to NEGOTIATION stage when:

1. All 3 required fields (`disruption_node`, `force_majeure_invoked`, `alternative_routing_premium`) are captured, OR
2. `avoidance_count` >= 3
