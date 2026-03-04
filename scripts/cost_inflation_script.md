# COST INFLATION INVESTIGATION SCRIPT

## State Fields (included in `state` key of your JSON response)

```json
{
  "script_loaded": true,
  "cost_driver_index": null,
  "tco_impact_percentage": null,
  "value_engineering_efforts": null,
  "open_book_indexation_willingness": null,
  "avoidance_count": 0,
  "exit_criteria_matched": false
}
```

**Field Descriptions:**

- `script_loaded`: Always true when this script is loaded
- `cost_driver_index`: Primary variable cost driver (e.g., LME constraints, regional labor index, logistics spot rates) (Required)
- `tco_impact_percentage`: Estimated % increase on the Total Cost of Ownership (Required)
- `value_engineering_efforts`: Supplier's internal initiatives to absorb variance before passing on PPV (Purchase Price Variance) (Required)
- `open_book_indexation_willingness`: `true` | `false` -> willingness to move to an open-book pricing model tied to a recognized index (Optional)
- `avoidance_count`: Number of non-responses (inherited)
- `exit_criteria_matched`: Set to true when exit criteria are met

---

## QUESTIONS (Ask in Priority Order)

### Question 1 (Priority: HIGH)

**Target Field:** `cost_driver_index`  
**Question:** "What specific commodity index or macroeconomic driver is creating this inflationary pressure on your BOM?"  
**Also Captures:** secondary_cost_drivers

**Field Mapping:**

- Capture macro cause: "LME Copper surge", "Resin index volatility", "Ocean freight spot rates", "Tier-2 labor shortages", etc.

---

### Question 2 (Priority: HIGH)

**Target Field:** `tco_impact_percentage`  
**Question:** "Looking at the landed cost, what is the net percentage impact of this PPV on our current rate card?"  
**Also Captures:** timing_of_impact

**Field Mapping:**

- Capture percentage: "High single digits", "12% material variance", "5% direct labor bump"

---

### Question 3 (Priority: HIGH)

**Target Field:** `value_engineering_efforts`  
**Question:** "Before passing this variance through, what value engineering or lean initiatives have you executed internally to buffer the cost?"  
**Also Captures:** process_optimizations

**Field Mapping:**

- Capture mitigation: "Dual-sourcing sub-components", "Yield improvements on the line", "Scrap reduction", "Fully optimized, forced to pass through"

---

### Question 4 (Priority: MEDIUM)

**Target Field:** `open_book_indexation_willingness`  
**Question:** "Would your commercial team be open to transitioning this SKU to an open-book model with index-linked pricing to share the risk?"  
**Also Captures:** transparency_interest

**Field Mapping:**

- "yes" / "we can review" → `open_book_indexation_willingness = true`
- "no" / "proprietary" → `open_book_indexation_willingness = false`

---

## EXIT CRITERIA

Exit to NEGOTIATION stage when:

1. All 3 required fields (`cost_driver_index`, `tco_impact_percentage`, `value_engineering_efforts`) are captured, OR
2. `avoidance_count` >= 3
