<!-- PURPOSE: Raw Material / Commodity supplier qualification script. Loaded by the Procurement
     Qualification Stage when category = RAW_MATERIAL. Captures commodity-specific context
     (pricing basis, supply reliability, market volatility) to inform NARA's negotiation.
     Archetype: Raw material suppliers prioritize volume certainty, demand predictability, prompt payment. -->

# RAW MATERIAL / COMMODITY QUALIFICATION SCRIPT

## State Fields

```json
{
  "script_loaded": true,
  "pricing_basis": null,
  "supply_reliability": null,
  "market_volatility": null,
  "alternative_sourcing": null,
  "avoidance_count": 0,
  "exit_criteria_matched": false
}
```

**Field Descriptions:**

- `script_loaded`: Always true when this script is loaded
- `pricing_basis`: How they price — "spot-linked", "fixed", "index-linked", "formula-based" (Required)
- `supply_reliability`: "HIGH" | "MODERATE" | "LOW" — consistency of supply over past contracts (Required)
- `market_volatility`: "HIGH" | "MODERATE" | "LOW" — current market price volatility (Required)
- `alternative_sourcing`: true | false — whether buyer has other qualified sources (Optional)
- `avoidance_count`: Number of non-responses (inherited)
- `exit_criteria_matched`: Set to true when exit criteria met

---

## QUESTIONS (Ask in Priority Order)

### Question 1 (Priority: HIGH)

**Target Field:** `pricing_basis`
**Question:** "How's your pricing structured — spot-linked, fixed rate, or index-based?"

**Field Mapping:**

- "spot" / "market-linked" → `pricing_basis = "spot-linked"`
- "fixed" / "locked rate" → `pricing_basis = "fixed"`
- "index" / "formula" → `pricing_basis = "index-linked"`

---

### Question 2 (Priority: HIGH)

**Target Field:** `supply_reliability`
**Question:** "How's supply consistency been? Any disruptions or capacity constraints on your end?"

**Field Mapping:**

- "no issues" / "consistent" / "reliable" → `supply_reliability = "HIGH"`
- "some challenges" / "working on it" → `supply_reliability = "MODERATE"`
- "tight capacity" / "allocation issues" → `supply_reliability = "LOW"`

---

### Question 3 (Priority: HIGH)

**Target Field:** `market_volatility`
**Question:** "How are raw material prices trending in the market right now?"

**Field Mapping:**

- "volatile" / "fluctuating" / "unpredictable" → `market_volatility = "HIGH"`
- "stable" / "some movement" → `market_volatility = "MODERATE"`
- "steady" / "flat" → `market_volatility = "LOW"`

---

### Question 4 (Priority: MEDIUM)

**Target Field:** `alternative_sourcing`
**Question:** Infer from context — do NOT ask directly. Note from SUPPLIER_CONTEXT if multiple suppliers exist for this category.

---

## LEVERAGE NOTES (For Negotiation Stage)

- If `pricing_basis = "spot-linked"` → Push for fixed-rate with volume floor for price stability
- If `supply_reliability = "HIGH"` → Less leverage on supply; focus on price and terms
- If `market_volatility = "HIGH"` → Supplier may accept lower price for volume certainty
- If `alternative_sourcing = true` → Cite Competition strategy is effective

---

## EXIT CRITERIA

Exit to NEGOTIATION stage when:

1. All 3 required fields captured, OR
2. `avoidance_count` >= 3
