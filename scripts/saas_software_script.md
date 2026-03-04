<!-- PURPOSE: SaaS/Software supplier qualification script. Loaded by the Procurement
     Qualification Stage when category = SAAS_SOFTWARE. Captures software-specific context
     (license model, contract flexibility, competitor landscape) to inform NARA's
     negotiation strategy. Archetype: SaaS suppliers prioritize ARR, logo value, expansion. -->

# SAAS / SOFTWARE QUALIFICATION SCRIPT

## State Fields (included in `state` key of your JSON response)

```json
{
  "script_loaded": true,
  "license_model": null,
  "contract_flexibility": null,
  "competitor_pressure": null,
  "renewal_dependency": null,
  "avoidance_count": 0,
  "exit_criteria_matched": false
}
```

**Field Descriptions:**

- `script_loaded`: Always true when this script is loaded
- `license_model`: How they price — "per-seat", "per-usage", "flat-fee", "tiered" (Required)
- `contract_flexibility`: "FLEXIBLE" | "RIGID" | "MODERATE" — willingness to restructure (Required)
- `competitor_pressure`: "HIGH" | "MODERATE" | "LOW" — how much competitive pressure they face (Required)
- `renewal_dependency`: true | false — whether their revenue model depends heavily on renewals (Optional)
- `avoidance_count`: Number of non-responses (inherited)
- `exit_criteria_matched`: Set to true when exit criteria are met

---

## QUESTIONS (Ask in Priority Order)

### Question 1 (Priority: HIGH)

**Target Field:** `license_model`
**Question:** "How's your licensing structured — per seat, usage-based, or flat fee?"
**Also Captures:** pricing_flexibility_signal

**Field Mapping:**

- "per seat" / "per user" → `license_model = "per-seat"`
- "usage-based" / "consumption" → `license_model = "per-usage"`
- "flat fee" / "enterprise" → `license_model = "flat-fee"`
- "tiered" / "volume bands" → `license_model = "tiered"`

---

### Question 2 (Priority: HIGH)

**Target Field:** `contract_flexibility`
**Question:** "Any room to restructure the contract terms — maybe multi-year or different billing cycles?"

**Field Mapping:**

- "yes" / "open to it" / "we can discuss" → `contract_flexibility = "FLEXIBLE"`
- "standard terms" / "our pricing is set" → `contract_flexibility = "RIGID"`
- "depends" / "case by case" → `contract_flexibility = "MODERATE"`

---

### Question 3 (Priority: HIGH)

**Target Field:** `competitor_pressure`
**Question:** "How's the competitive landscape looking for {category}? We're always evaluating market options."

**Field Mapping:**

- Multiple competitors mentioned / acknowledges competition → `competitor_pressure = "HIGH"`
- Some competition / few alternatives → `competitor_pressure = "MODERATE"`
- Niche / few competitors / dominant position → `competitor_pressure = "LOW"`

---

### Question 4 (Priority: MEDIUM)

**Target Field:** `renewal_dependency`
**Question:** Infer from conversation — if supplier emphasises "long-term partnership" or "renewal" frequently.

**Field Mapping:**

- Frequent renewal/retention language → `renewal_dependency = true`
- Transaction-focused language → `renewal_dependency = false`

---

## LEVERAGE NOTES (For Negotiation Stage)

- If `license_model = "per-seat"` → Volume commitment is strong lever (more seats = lower rate)
- If `contract_flexibility = "FLEXIBLE"` → Multi-year lock-in for price reduction
- If `competitor_pressure = "HIGH"` → Cite Competition strategy is highly effective
- If `renewal_dependency = true` → Logo value and long-term commitment are free concessions

---

## EXIT CRITERIA

Exit to NEGOTIATION stage when:

1. All 3 required fields captured (`license_model`, `contract_flexibility`, `competitor_pressure`), OR
2. `avoidance_count` >= 3
