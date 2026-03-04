<!-- PURPOSE: MRO / Indirect supplier qualification script. Loaded when
     category = MRO_INDIRECT. Captures indirect procurement context (catalog breadth,
     contract stickiness, basket consolidation) to inform NARA's negotiation.
     Archetype: MRO suppliers prioritize contract stickiness, basket size, catalog inclusion. -->

# MRO / INDIRECT QUALIFICATION SCRIPT

## State Fields

```json
{
  "script_loaded": true,
  "catalog_breadth": null,
  "contract_stickiness": null,
  "consolidation_opportunity": null,
  "service_level": null,
  "avoidance_count": 0,
  "exit_criteria_matched": false
}
```

**Field Descriptions:**

- `script_loaded`: Always true
- `catalog_breadth`: "WIDE" | "FOCUSED" | "NICHE" — range of SKUs they supply (Required)
- `contract_stickiness`: "HIGH" | "MODERATE" | "LOW" — switching costs for buyer (Required)
- `consolidation_opportunity`: true | false — can more categories be bundled with this supplier (Required)
- `service_level`: "EXCELLENT" | "GOOD" | "NEEDS_IMPROVEMENT" — delivery/service quality (Optional)

---

## QUESTIONS (Ask in Priority Order)

### Question 1 (Priority: HIGH)

**Target Field:** `catalog_breadth`
**Question:** "How wide is your catalog for our category? Are you covering most of what we need?"

**Field Mapping:**

- "full range" / "everything you need" → `catalog_breadth = "WIDE"`
- "core items" / "main products" → `catalog_breadth = "FOCUSED"`
- "specialised" / "specific items only" → `catalog_breadth = "NICHE"`

---

### Question 2 (Priority: HIGH)

**Target Field:** `contract_stickiness`
**Question:** "How integrated are we at this point — system connections, custom catalogs, anything like that?"

**Field Mapping:**

- "deeply integrated" / "punch-out catalog" / "EDI" → `contract_stickiness = "HIGH"`
- "some integration" / "standard setup" → `contract_stickiness = "MODERATE"`
- "minimal" / "could switch easily" → `contract_stickiness = "LOW"`

---

### Question 3 (Priority: HIGH)

**Target Field:** `consolidation_opportunity`
**Question:** "Any adjacent categories you could cover? We're looking at simplifying our supplier base."

**Field Mapping:**

- "yes" / lists additional categories → `consolidation_opportunity = true`
- "no" / "focused on current scope" → `consolidation_opportunity = false`

---

### Question 4 (Priority: MEDIUM)

**Target Field:** `service_level`
**Question:** Infer from SUPPLIER_CONTEXT and relationship context. If issues exist, probe lightly.

---

## LEVERAGE NOTES (For Negotiation Stage)

- If `catalog_breadth = "WIDE"` → Basket consolidation for volume discount
- If `contract_stickiness = "LOW"` → Buyer has switching leverage. Cite Competition effective
- If `consolidation_opportunity = true` → Bundling is a power lever — more basket for better rate
- If `service_level = "NEEDS_IMPROVEMENT"` → Leverage for price reduction or rebate improvement

---

## EXIT CRITERIA

Exit to NEGOTIATION stage when:

1. All 3 required fields captured, OR
2. `avoidance_count` >= 3
