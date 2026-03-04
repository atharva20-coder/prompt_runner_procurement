# OTHER CATEGORY INVESTIGATION SCRIPT

## State Fields (included in `state` key of your JSON response)

```json
{
  "script_loaded": true,
  "premature_commitment": null,
  "stated_reason": null,
  "recovery_timeline": null,
  "alternate_support": null,
  "avoidance_count": 0,
  "exit_criteria_matched": false
}
```

**Field Descriptions:**
- `script_loaded`: Always true when this script is loaded
- `stated_reason`: Customer's stated reason in detail (Required)
- `recovery_timeline`: When situation expected to improve (Required)
- `alternate_support`: true | false (Required)
- `avoidance_count`: Number of non-responses so far (inherited from main prompt state)
- `exit_criteria_matched`: Set to true when exit criteria are met

---

## QUESTIONS (Ask in Priority Order)

### Question 1 (Priority: HIGH)
**Target Field:** `stated_reason`  
**Question:** "What led to this?"  
**Also Captures:** event_timing, nature_of_issue

**Field Mapping:**
- Capture detailed reason verbatim
- Note any timing mentioned

---

### Question 2 (Priority: HIGH)
**Target Field:** `recovery_timeline`  
**Question:** "When do you see things improving?"  
**Also Captures:** nature_of_issue (ONE_TIME vs STRUCTURAL)

**Field Mapping:**
- Specific timeline → `recovery_timeline = "<timeline>"`
- "Not sure" / "Unknown" → `recovery_timeline = "Uncertain"`

---

### Question 3 (Priority: HIGH)
**Target Field:** `alternate_support`  
**Question:** "Any other income or support?"  

**Field Mapping:**
- "yes" → `alternate_support = true`
- "no" → `alternate_support = false`

---

## EXIT CRITERIA

Exit to RECOVERY stage when:
1. All 3 required fields captured OR
2. `avoidance_count` >= 4

---