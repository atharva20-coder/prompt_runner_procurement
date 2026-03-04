# QUALITY DEFECT RESOLUTION INVESTIGATION SCRIPT

## State Fields (included in `state` key of your JSON response)

```json
{
  "script_loaded": true,
  "defect_root_cause": null,
  "containment_action_status": null,
  "cost_of_poor_quality_liability": null,
  "corrective_action_timeline": null,
  "avoidance_count": 0,
  "exit_criteria_matched": false
}
```

**Field Descriptions:**

- `script_loaded`: Always true when this script is loaded
- `defect_root_cause`: Core issue identified via 8D or RCA (e.g., material fatigue, process drift, operator error) (Required)
- `containment_action_status`: Immediate steps taken to quarantine WIP (Work In Progress) and prevent escapes to our lines (Required)
- `cost_of_poor_quality_liability`: Supplier's willingness to accept financial liability for COPQ (Machine down-time, scrap, rework) (Required)
- `corrective_action_timeline`: ETA for full SCAR (Supplier Corrective Action Report) closure and permanent preventive action (Optional)
- `avoidance_count`: Number of non-responses (inherited)
- `exit_criteria_matched`: Set to true when exit criteria are met

---

## QUESTIONS (Ask in Priority Order)

### Question 1 (Priority: HIGH)

**Target Field:** `defect_root_cause`  
**Question:** "Looking at the recent spike in quality escapes, what is your engineering team isolating as the true root cause in the 8D?"  
**Also Captures:** process_capability_cpm

**Field Mapping:**

- Capture root cause: "Raw material inclusion from Tier-2", "Tooling wear out of spec", "Software bug in QA module"

---

### Question 2 (Priority: HIGH)

**Target Field:** `containment_action_status`  
**Question:** "Have you successfully cordoned off the affected lots, and is the WIP currently 100% sorted before hitting our docks?"  
**Also Captures:** quarantine_effectiveness

**Field Mapping:**

- Capture status: "Implementing 3rd-party sort", "All WIP isolated", "Still determining scope of impact"

---

### Question 3 (Priority: HIGH)

**Target Field:** `cost_of_poor_quality_liability`  
**Question:** "Given the line downtime and rework this caused on our end, are you processing the RMA (Return Merchandise Authorization) and acknowledging the COPQ chargebacks?"  
**Also Captures:** financial_restitution

**Field Mapping:**

- Capture liability stance: "Accept full responsibility", "Will issue credit for parts only no labor", "Contesting the chargeback"

---

### Question 4 (Priority: MEDIUM)

**Target Field:** `corrective_action_timeline`  
**Question:** "When can we expect the formal SCAR closed out with validated permanent preventive actions?"  
**Also Captures:** process_control_updates

**Field Mapping:**

- Capture timeline: "Within 48 hours", "End of the week", "Requires new equipment validation, Q3"

---

## EXIT CRITERIA

Exit to NEGOTIATION stage when:

1. All 3 required fields (`defect_root_cause`, `containment_action_status`, `cost_of_poor_quality_liability`) are captured, OR
2. `avoidance_count` >= 3
