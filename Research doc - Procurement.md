

**PRODUCT SPECIFICATION**

**Procurement AI Negotiation Agent**

Demo Build for VC Presentation

Date: March 2026  |  Status: Draft v8.0  |  Author: Shubham Verma

| Audience: | Engineering, Design, VC Demo |
| :---- | :---- |

# **1\. Overview**

This document specifies the product requirements for a Procurement AI Negotiation Agent designed as a demo for VC audiences. The agent autonomously conducts supplier negotiations on behalf of a procurement team, handling the full negotiation lifecycle from opening through closure.

The demo showcases three core capabilities: (a) structured negotiation with dynamic tactic selection, (b) per-message reasoning traces that expose the agent’s decision-making, and (c) a post-call Feedback Manager Agent that analyses the transcript and recommends improvements.

# **2\. Inputs**

The agent requires two categories of input before a negotiation session begins:

## **2.1 Customer Context**

Structured information about the buyer-supplier relationship that frames the negotiation. This maps to a “Keep Current Contract Terms” planning block:

| Field | Description |
| :---- | :---- |
| Supplier Name | Name and identifier of the supplier being negotiated with |
| Category | Procurement category (e.g., raw materials, logistics, IT services, SaaS) |
| Current Pricing | Existing unit price, any tiered/volume pricing structure currently in place |
| Current Payment Terms | Current net days (e.g., Net 30), any existing early payment discount structure |
| Current Rebate Structure | Existing rebate arrangements (flat, tiered, growth) or “None” if no rebate is in place |
| Contract Duration | Current contract length, renewal date, and whether auto-renewal is active |
| Volume Commitment | Current annual volume commitment or annual spend (₹). Used to calculate leverage and as a concession lever during negotiation. |

## **2.2 Negotiation Objectives**

Each negotiation session must define objectives on three axes, with both a Best Case (target) and Bare Minimum (walk-away) for each. Volume commitment is not an objective axis itself — it is a concession lever the agent can offer to achieve better outcomes on these three axes.

| Axis | Best Case (Target) | Bare Minimum (Walk-Away) | Concession Available |
| :---- | :---- | :---- | :---- |
| **Price** | 8% unit price reduction (₹92/unit) | 3% unit price reduction (₹97/unit) | Volume commitment increase to unlock tiered pricing |
| **Payment Terms** | Net 60 payment terms | Net 45 payment terms | Offer EPD (e.g., 2/10 Net 30\) if supplier prefers faster cash |
| **Rebate** | 1.5% annual flat rebate | No rebate required | Accept growth rebate (tied to YoY increase) instead of flat |

The gap between Best Case and Bare Minimum on each axis defines the agent’s negotiation room. The agent starts at Best Case and concedes toward Bare Minimum only as needed, using tactics to extract maximum value. Volume commitment can be increased as a cross-axis concession to unlock better terms on any of the three axes.

## **2.3 Negotiation Position Tracker**

The agent maintains a live Position Tracker across all three objective axes. This tracker is the convergence engine of the negotiation — it tells the agent which lever to push, how much to push, and whether a win-win is achievable.

### **2.3.1 What the Tracker Captures**

For each objective axis (Price, Payment Terms, Rebate), the tracker records three positions:

| Position | Definition | Source |
| :---- | :---- | :---- |
| **Buyer Best Case** | The ideal outcome the buyer wants. This is the opening anchor and the upper bound of the buyer’s range. | Set by the procurement team before the negotiation begins (Section 2.2). |
| **Buyer Bare Minimum** | The lowest acceptable outcome. If the supplier cannot reach this, the agent escalates or exits. | Set by the procurement team before the negotiation begins (Section 2.2). |
| **Supplier Preference** | The supplier’s stated or inferred preferred position on this axis. This is discovered during the conversation through the supplier’s counter-offers, objections, and signals. | Inferred from the conversation. Updated after every supplier message based on what they say, reject, accept, or push back on. |

### **2.3.2 Live Tracker Example**

The tracker updates after every exchange. Here is an example snapshot mid-negotiation:

| Axis | Buyer Best Case | Buyer Bare Min | Supplier Preference (inferred) | Current Offer |
| :---- | :---- | :---- | :---- | :---- |
| **Price** | ₹92/unit | ₹97/unit | ₹100/unit (won’t go below) | ₹96/unit |
| **Payment Terms** | Net 60 | Net 45 | Net 30 preferred (cash-flow concern) | Net 45 |
| **Rebate** | 1.5% flat | 0% (none) | Open to discussion (no strong objection) | Not yet raised |

### **2.3.3 How the Tracker Drives Convergence**

The three positions create a Zone of Possible Agreement (ZOPA) on each axis. The ZOPA is the overlap between the buyer’s acceptable range (Best Case to Bare Minimum) and the supplier’s acceptable range (inferred from their behaviour). The tracker drives two critical decisions:

**Decision 1 — Which lever to push:** The agent pushes hardest on the axis where the gap between the current offer and the Buyer Best Case is largest AND where the supplier’s preference suggests room to move. In the example above, Rebate has not been raised yet and the supplier shows no strong objection — this is the axis with the most untapped potential.

**Decision 2 — How much to push:** The agent calibrates its ask based on the distance between the Supplier Preference and the Buyer Bare Minimum. If the supplier’s preference is inside or close to the buyer’s range, the agent can push toward Best Case. If the supplier’s preference is far from Bare Minimum, the agent must prioritise getting into the zone before optimising within it.

### **2.3.4 Convergence Rules**

The agent follows these rules to converge toward a win-win:

* **ZOPA exists (overlap):** If the supplier’s preference overlaps with the buyer’s range on an axis, a ZOPA exists on that axis. The agent’s goal is to close the deal as close to Buyer Best Case as possible within the overlap zone.  
* **No ZOPA (gap):** If there is no overlap (supplier’s preference is outside the buyer’s range), the agent must either (a) use communication strategies (Framing, Cite Competition, Logrolling) to shift the supplier’s preference into the zone, or (b) trade value from another axis where ZOPA exists to compensate.  
* **Update after every exchange:** After every exchange, the agent updates the Supplier Preference based on the supplier’s latest message. A successful exchange (supplier moves toward buyer’s range) signals that the current strategy and lever combination is working — the agent continues. An unsuccessful exchange (supplier holds or moves away) signals a need to switch strategy, switch lever, or shift axis.  
* **Compare distances across axes:** The agent compares the distance between current positions on each axis. Axes where the distance is small are candidates for closure (use Summary/Recap to lock in). Axes where the distance is large are candidates for increased pressure or cross-axis trading.  
* **Close when all axes are in zone:** A deal is achievable when all three axes have reached at least the Bare Minimum. The agent attempts to close at the best possible position within the ZOPA on each axis before the supplier withdraws flexibility.

### **2.3.5 Supplier Preference Discovery**

The supplier’s preference is not given upfront — it is discovered through the conversation. The agent infers it from the following signals:

| Supplier Signal | What It Tells the Agent |
| :---- | :---- |
| Flat rejection of an offer on an axis | Supplier’s preference is far from the buyer’s position on this axis. The agent should not push harder here immediately — try a different lever or shift axis. |
| Counter-offer with a specific number | This IS the supplier’s stated preference (or close to it). The agent now knows the ZOPA boundary. Update the tracker. |
| Conditional acceptance (“We can do X if you give us Y”) | The supplier is flexible on this axis but needs something in return. This is a Logrolling opportunity. The agent should evaluate whether the trade is net-positive for the buyer. |
| Deflection or subject change | The supplier is uncomfortable on this axis. Their preference is likely far from the buyer’s position but they don’t want to state a hard number. The agent should use Ask What It Takes to draw them out. |
| Positive language without commitment | The supplier is open but non-committal. Their preference is likely in the buyer’s range but not confirmed. The agent should use Propose Options A/B to get a concrete response. |
| Emotional frustration or hardball | The agent has pushed too hard on this axis. De-escalate with We’re on the Same Side, then shift to a different axis before returning. |

| Rank | Supplier Desire | Evidence from Conversation | Implication for Our Strategy |
| :---- | :---- | :---- | :---- |
| 1 | **Fast payment (Net 30\)** | Supplier mentioned cash-flow twice. Rejected Net 60 immediately. Asked if EPD is available. | This is our strongest trading chip. We can concede on payment timing in exchange for gains on price or rebate. |
| 2 | **Protect list price** | Supplier refused to move on unit price but offered to discuss payment and rebates. Used “standard rate” language. | Direct price pressure will not work. Shift value extraction to payment terms and rebates, or offer volume commitment to unlock tiered pricing. |
| 3 | **Volume certainty** | Supplier asked about our projected annual volumes unprompted. Mentioned capacity planning. | Offer increased volume commitment as a concession lever to unlock better terms on other axes. |
| 4 | **Avoid rebates** | Supplier said rebates “erode margin.” No counter-offer on rebate structure. | Rebate is the supplier’s pain point. Use it as a “drop” concession — agree to reduce rebate ask in exchange for gains on price or payment. |

### **2.3.6 Exchange Outcome Tracking**

Every exchange (buyer offer → supplier response) is classified as successful or unsuccessful, which directly feeds the agent’s next move:

| Exchange Outcome | Definition | Agent’s Next Move |
| :---- | :---- | :---- |
| **Successful** | Supplier moved closer to the buyer’s range on this axis (accepted, counter-offered closer, or showed flexibility). | Continue with the same strategy-lever combination. Consider pushing slightly further on the same axis using Incremental Concession. Update Supplier Preference closer to buyer’s range. |
| **Partially Successful** | Supplier showed conditional willingness (“We could consider it if...”) but did not commit. | Explore the condition. If the trade is net-positive, use Logrolling or Labelled Concession to close. If the condition is unacceptable, Reframe the ask on a different lever within the same axis. |
| **Unsuccessful** | Supplier rejected, held firm, or moved further away from the buyer’s range. | Do NOT push harder on the same axis immediately. Switch communication strategy from the pool. If 2+ unsuccessful exchanges on this axis, shift to a different axis and try cross-axis trading (Section 5.3.4). Return to this axis later with a different lever. |

This tracking framework ensures the agent is always converging, not just talking. Every message either narrows the gap on an axis (successful), reveals a trade opportunity (partially successful), or signals a needed pivot (unsuccessful). The Position Tracker is the single source of truth for what the agent should do next.

# **3\. Negotiation Levers (Exhaustive)**

The agent draws from a comprehensive set of negotiation levers. These are the tradeable terms the agent can adjust during a negotiation. The levers are grouped into three categories:

## **3.1 Pricing Levers**

* **Straight unit price reduction** — Direct reduction of per-unit cost with no change to other terms  
* **Volume-based discounts (tiered pricing)** — Lower price in exchange for committed volume (e.g., ₹100/unit at 1K; ₹90/unit at 5K)  
* **Conditional discounts** — Price reduction tied to exclusivity, bundling, or another product commitment  
* **Commodity-linked pricing adjustments** — Re-adjust pricing when raw material/input costs drop but supplier price remains static  
* **Competitive price benchmarking** — Use market data or parallel supplier quotes to drive price down  
* **Bundling / spend consolidation** — Combine multiple categories (spares, consumables, services) into one deal for a better aggregate rate  
* **Value engineering / scope optimisation** — Reduce scope, simplify specifications, or standardise requirements to lower cost without cutting quality  
* **Cost-model transparency / open-book pricing** — Negotiate unit costs that automatically recalculate when volume or market indices change

## **3.2 Payment Terms Levers**

* **Payment days extension** — Push from Net 30 to Net 45/60/90 for working capital benefit  
* **Early payment discounts (EPD)** — Offer faster payment in exchange for a discount (e.g., 2/10 Net 30\)  
* **Dynamic discounting** — Real-time discount rates based on actual payment date  
* **Discount days window** — Negotiate the number of days to claim the early payment discount  
* **Creative payment structures** — Milestone-based, seasonal, or performance-linked payment structures  
* **Currency and FX terms** — Define who bears exchange rate fluctuation risk in cross-border deals

## **3.3 Rebate Levers**

* **Flat rebates / bonuses** — Fixed percentage back at period end (quarterly/annually)  
* **Volume-based rebates (tiered)** — Increasing rebate % as spend grows past defined thresholds  
* **Growth rebates** — Rebate tied to year-over-year spend growth rather than absolute volume  
* **General percentage of spend** — Unconditional rebate on total purchases regardless of milestones  
* **Marketing / co-promotion rebates** — Supplier offers rebate in exchange for marketing placement, co-branding, or referral

## **3.4 Compromise on one lever to get value in another lever**

| Supplier’s Top Desire | Buyer Gives (Low-Cost to Us) | Buyer Takes (High-Value to Us) | Net Result |
| :---- | :---- | :---- | :---- |
| Fast payment | Offer Net 35 instead of pushing for Net 60 | 5% price reduction the supplier would not give otherwise | Buyer wins on price. Supplier wins on cash-flow. Both improve. |
| Volume certainty | Commit to 20% higher annual volume | Tiered pricing at ₹92/unit (down from ₹100) | Buyer wins on unit cost. Supplier wins on revenue certainty. Both improve. |
| Protect list price | Accept current list price (no price reduction) | Net 55 payment terms \+ 1.5% annual rebate | Buyer wins on working capital \+ rebate. Supplier wins on list price. Both improve. |
| Avoid rebates | Drop rebate demand entirely | Deeper price cut or longer payment terms | Buyer wins on price or payment. Supplier wins on margin protection. Both improve. |

# **4\. Communication Strategies**

Distinct from negotiation levers (what to trade), communication strategies define how the agent frames, sequences, and delivers its messages. The agent selects from the following strategies based on the conversation state. Note: Strategic Silence has been excluded as it is not effective in a text-based channel where pauses are ambiguous.

| \# | Strategy | What the Agent Does | When to Use |
| :---- | :---- | :---- | :---- |
| 1 | **Ask What It Takes** | Directly ask the supplier: “What would you need from us to make this work?” Surfaces the supplier’s real constraints and opens creative solution space. | Early in negotiation or when hitting a stalemate |
| 2 | **Cite Competition** | Reference competitive benchmarks or alternative suppliers. E.g., “We’ve received quotes from other vendors at 12% below current rates.” Creates urgency without being adversarial. | When supplier is resistant to price movement |
| 3 | **Propose Options (A/B)** | Present two structured options. Option A: better pricing with shorter payment terms. Option B: current pricing with higher rebate. Gives the supplier a sense of control while both options serve the buyer. | Mid-negotiation to move from posturing to concrete terms |
| 4 | **We’re on the Same Side** | Reframe the negotiation as collaborative, not adversarial. E.g., “We both want this partnership to grow. Let’s find a structure that works for both of us.” Builds trust and rapport. | When supplier becomes defensive or adversarial |
| 5 | **Anchoring** | Open with an ambitious but credible first offer tied to market data. The anchor frames the entire negotiation range. E.g., “Based on our benchmarking, a rate of ₹88/unit is in line with market.” | Opening phase — sets the tone for the negotiation range |
| 6 | **Labelled Concession** | When making a concession, explicitly label it as costly to the buyer and demand reciprocity. E.g., “We’re making a significant move on volume commitment here. We’d expect a corresponding adjustment on payment terms.” | Anytime the agent concedes — ensures concessions are not taken for free |
| 7 | **Logrolling (Cross-Issue Trade)** | Trade across issues of different value to each side. E.g., if the supplier cares more about volume certainty than price, offer committed volume in exchange for a larger price cut. Maximises total deal value. | When single-issue negotiation stalls and there are multiple levers in play |
| 8 | **Framing / Reframing** | Present information in a way that highlights benefits to the supplier. E.g., instead of “We need a 10% cut,” say “With the volume we’re committing, your unit economics improve by 15%.” Shifts perception of the ask. | Throughout — especially when presenting demands that may feel large to the supplier |
| 9 | **Deadline / Urgency** | Introduce a genuine time constraint. E.g., “Our procurement committee meets on Friday; we’d need confirmed terms by Thursday to include this renewal.” Motivates faster decision-making. | Late-stage negotiation when supplier is dragging or to accelerate closure |
| 10 | **Flinch / Express Surprise** | React with clear surprise to an unreasonable counter-offer. In text, this might be: “That’s quite far from what we’d expected based on market rates.” Signals the offer is unacceptable and forces a recalibration. | When supplier makes an extreme or unreasonable counter-offer |
| 11 | **Incremental Concession (Salami)** | Make small, measured concessions rather than large moves. Each concession gets smaller to signal approaching the limit. Prevents giving away too much too fast. | Throughout the bargaining phase to protect margin |
| 12 | **Summary / Recap** | Periodically summarise what has been agreed so far. Locks in concessions, creates momentum, and prevents backtracking. E.g., “So far we’ve aligned on Net 45 and a 5% price reduction. Let’s now discuss rebates.” | At phase transitions and before closing |
| 13 | **Escalation to Authority** | Last-resort tactic. Claim limited authority: “I’d need to take this back to our procurement head for approval.” Used ONLY when the supplier cannot move even towards the Bare Minimum on any axis. This is the final step before a no-deal exit. | Only when supplier is completely unable to move towards Bare Minimum after all other strategies have been tried |

# **5\. Decision Engine: Strategy and Lever Selection Logic**

This section defines the “brain” of the negotiation agent — the logic that determines which communication strategy and which negotiation lever to deploy at each turn. The engine draws on three core inputs: the Position Tracker (Section 2.3) for gap analysis, the Supplier Desire Model (Section 2.4) for understanding what the supplier values and where asymmetric trades exist, and the pool-based selection model for choosing how to communicate. Rather than following a rigid sequence, the engine picks the best strategy-lever combination based on what the supplier just said, what their Desire Map reveals about trade opportunities, and the remaining gap to objectives.

## **5.1 Decision Inputs**

At each turn, the engine evaluates three primary selection criteria:

* **Supplier’s Last Response (Intent):** What did the supplier actually say? Is it an objection, a counter-offer, a question, a demand, an acceptance, or a deflection? The agent classifies the supplier’s last message to understand what it must respond to.  
* **Supplier’s Emotional Tone:** What is the supplier’s emotional tone? Cooperative, neutral, frustrated, defensive, adversarial? This determines the communication posture — whether to be collaborative, assertive, or de-escalating.  
* **Gap to Objectives (from Position Tracker):** Read from the Position Tracker (Section 2.3): where does the current offer stand on each of the three objective axes (Price, Payment Terms, Rebate) relative to Buyer Best Case, Buyer Bare Minimum, and the Supplier’s inferred preference? This determines which axis to push, how much room the agent has, and whether a ZOPA exists.

In addition, the engine tracks:

* **Phase:** Opening, Negotiation, or Closure — governs which strategies are in the pool.  
* **Levers Already Used:** Which levers have already been discussed, conceded, or are still untouched.  
* **Turn Count and Momentum:** How many turns have passed and whether the negotiation is progressing or stalling.

## **5.2 Communication Strategy Selection Rules**

The engine does NOT follow a rigid priority sequence. Instead, for each behaviour-phase combination, a pool of applicable strategies is available. The agent selects from the pool based on three contextual criteria: (1) what the supplier just said or asked, (2) the supplier’s emotional tone, and (3) which strategy best moves the deal toward the objective.

### **5.2.1 Strategy Pools by Behaviour and Phase**

The following table defines which strategies are available (as a pool, not a sequence) for each behaviour-phase combination:

| Supplier Behaviour | Phase | Available Strategy Pool |
| :---- | :---- | :---- |
| **Cooperative** | Opening | Anchoring, We’re on the Same Side, Framing |
| **Neutral / Non-committal** | Opening | Anchoring, Framing, Ask What It Takes |
| **Resistant** | Opening | Anchoring, Cite Competition, Framing, We’re on the Same Side |
| **Cooperative** | Negotiation | Ask What It Takes, Logrolling, Labelled Concession, Incremental Concession, Summary/Recap, Framing |
| **Neutral / Non-committal** | Negotiation | Propose Options A/B, Framing, Ask What It Takes, Logrolling, Deadline/Urgency, Flinch |
| **Resistant** | Negotiation | Cite Competition, Flinch, Incremental Concession, Propose Options A/B, Labelled Concession, Deadline/Urgency |
| **Adversarial / Hardball** | Negotiation | Flinch, We’re on the Same Side, Cite Competition, Deadline/Urgency, Propose Options A/B, Framing |
| **Stalemate (3+ turns)** | Negotiation | Ask What It Takes, Logrolling, Propose Options A/B, Framing, Deadline/Urgency, Incremental Concession |
| **Cooperative** | Closure | Summary/Recap, Labelled Concession, Framing |
| **Resistant / Dragging** | Closure | Deadline/Urgency, Propose Options A/B, Summary/Recap, Incremental Concession, Cite Competition |
| **Cannot reach Bare Minimum** | Any (last resort) | Escalation to Authority. Triggered ONLY when all strategies above have been tried and the supplier still cannot move toward Bare Minimum on any axis. Leads to human review or no-deal exit. |

### **5.2.2 How the Agent Picks from the Pool**

Once the pool is identified, the agent selects the single best strategy by evaluating:

| Selection Criterion | What the Agent Evaluates | Example |
| :---- | :---- | :---- |
| **1\. Supplier’s Last Response** | What did the supplier actually say? Did they raise an objection, make a counter-offer, ask a question, give a flat refusal, or show flexibility? | Supplier said “We can’t go below ₹100/unit.” → This is a price objection. Best strategy from pool: Cite Competition (if Resistant) or Logrolling (if Cooperative). |
| **2\. Emotional Tone** | Is the supplier frustrated, defensive, collaborative, or disengaged? The strategy must match the emotional context. | Supplier sounds frustrated → Avoid assertive strategies (Cite Competition, Flinch). Use We’re on the Same Side or Framing to de-escalate before making the next ask. |
| **3\. Progression Toward Objective** | Which strategy is most likely to move the supplier closer to accepting terms within our Best Case–Bare Minimum range? Does the conversation need to progress (make a new offer) or stabilise (lock in what’s been agreed)? | Price is at 96 (target 92, floor 97\) — we’re close to floor. Agent should stabilise with Summary/Recap on price and shift the conversation to payment terms using Logrolling. |

### 

### **5.2.3 Strategy Coverage Verification**

All 13 communication strategies appear at least once in the pool tables above:

| Strategy | Appears in Pools |
| :---- | :---- |
| 1\. Ask What It Takes | Neutral/Opening, Cooperative/Negotiation, Neutral/Negotiation, Stalemate |
| 2\. Cite Competition | Resistant/Opening, Resistant/Negotiation, Adversarial/Negotiation, Resistant/Closure |
| 3\. Propose Options A/B | Neutral/Negotiation, Resistant/Negotiation, Adversarial/Negotiation, Stalemate, Resistant/Closure |
| 4\. We’re on the Same Side | Cooperative/Opening, Resistant/Opening, Adversarial/Negotiation |
| 5\. Anchoring | Cooperative/Opening, Neutral/Opening, Resistant/Opening |
| 6\. Labelled Concession | Cooperative/Negotiation, Resistant/Negotiation, Cooperative/Closure |
| 7\. Logrolling | Cooperative/Negotiation, Neutral/Negotiation, Stalemate |
| 8\. Framing / Reframing | All Opening pools, Cooperative/Negotiation, Neutral/Negotiation, Adversarial/Negotiation, Stalemate, Cooperative/Closure |
| 9\. Deadline / Urgency | Neutral/Negotiation, Resistant/Negotiation, Adversarial/Negotiation, Stalemate, Resistant/Closure |
| 10\. Flinch | Neutral/Negotiation, Resistant/Negotiation, Adversarial/Negotiation |
| 11\. Incremental Concession | Cooperative/Negotiation, Resistant/Negotiation, Stalemate, Resistant/Closure |
| 12\. Summary / Recap | Cooperative/Negotiation, Cooperative/Closure, Resistant/Closure |
| 13\. Escalation to Authority | Cannot reach Bare Minimum (last resort only) |

## **5.3 Negotiation Lever Selection Rules**

Rather than a generic condition-to-lever mapping, the engine selects levers based on the specific axis being negotiated and the supplier’s actual objection. For each of the three objective axes, the following tables define the likely supplier objections and the pool of levers available to counter each. The agent picks the lever that most directly addresses the supplier’s stated concern.

### **5.3.1 Axis 1: Price**

When the negotiation is focused on unit price, the supplier may push back with specific objections. The agent selects from the following lever pool based on what the supplier said:

| Supplier Objection / Signal | Available Levers (Pool) | Selection Logic |
| :---- | :---- | :---- |
| “Our costs have gone up” | Commodity-linked repricing, Open-book pricing, Value engineering | If market data shows costs actually dropped, use commodity-linked repricing. If unclear, ask for open-book pricing to verify. If costs are genuine, propose value engineering to reduce the supplier’s cost base. |
| “This is our standard rate” | Competitive benchmarking, Volume-based tiered pricing, Bundling | Show market data with competitive benchmarking. If that fails, offer higher volume commitment in exchange for tiered pricing. If multi-category, propose bundling. |
| “We can’t go below X without losing margin” | Conditional discount, Volume commitment increase, EPD trade (shift to payment axis) | If the floor is close to our Bare Minimum, accept the price and shift value extraction to payment terms or rebates. If far from Bare Minimum, offer exclusivity or volume in exchange for a conditional discount. |
| “Your volume doesn’t justify a lower price” | Volume commitment increase, Bundling / spend consolidation, Growth-based tiered pricing | Offer to increase committed volume or consolidate spend across categories. If volume genuinely can’t increase, propose growth-based tiers that give the supplier confidence of future scale. |
| “We already gave you the best rate last year” | Competitive benchmarking, Commodity-linked repricing, Shift axis to payment/rebate | Markets change yearly. Use current benchmarking data. If commodity inputs dropped, use that. If the supplier is genuinely at floor, acknowledge price and pivot to extracting value on payment terms or rebates. |
| Supplier signals cash-flow pressure | EPD (early payment discount), Dynamic discounting | Offer faster payment in exchange for a price reduction. Supplier gets liquidity; buyer gets savings. This is a cross-axis trade: price improves because payment timeline shortens. |

### **5.3.2 Axis 2: Payment Terms**

When negotiating payment timing, suppliers typically resist extensions that hurt their working capital. The agent selects from the following lever pool:

| Supplier Objection / Signal | Available Levers (Pool) | Selection Logic |
| :---- | :---- | :---- |
| “We need cash within 30 days” | EPD structure (e.g., 2/10 Net 30), Dynamic discounting, Creative payment (milestone-based) | If the supplier needs fast cash, offer an EPD structure where paying early earns a discount. Alternatively, propose dynamic discounting with a sliding scale. If the project is phased, offer milestone-based payments. |
| “Extending payment hurts our working capital” | Partial extension (Net 30 to Net 45 instead of Net 60), EPD as a compromise, Volume commitment increase as a trade | If Net 60 is too far, settle for Net 45 (still above current). Offer EPD as a middle ground: they get the option for early cash. Or trade: “We’ll extend our volume commitment if you can accommodate Net 45.” |
| “Our finance team won’t approve Net 60” | Partial extension (Net 45), Discount-days window adjustment, Shift value to rebate axis | Accept the constraint and negotiate Net 45 as a compromise. Adjust the discount-days window to give both sides flexibility. If payment terms are fully stuck, pivot to extracting value on rebates. |
| “We’ve had bad experiences with late payments” | Commitment to on-time payment guarantee, EPD (incentivises our own timely payment), Auto-payment arrangement | Address the trust issue directly. Offer a formal on-time payment commitment. Propose EPD so we are financially incentivised to pay early. If possible, offer auto-debit or standing-order arrangements. |
| Supplier agrees to extension but wants something in return | Volume commitment increase, Contract duration extension, Price stability guarantee | This is a Logrolling opportunity. If supplier extends to Net 45/60, trade with something they value: committed volume, a longer contract, or a promise not to re-tender for a fixed period. |

### **5.3.3 Axis 3: Rebate**

Rebates are often the axis with the most creative room because they don’t affect list price or payment timing. The agent selects from the following lever pool:

| Supplier Objection / Signal | Available Levers (Pool) | Selection Logic |
| :---- | :---- | :---- |
| “We don’t offer rebates at your spend level” | Volume-tiered rebate (triggered at higher spend), Growth rebate (tied to YoY increase), Volume commitment increase | If current spend is below the supplier’s rebate threshold, offer to increase volume commitment to qualify. Alternatively, propose a growth rebate so the supplier only pays when our spend genuinely grows. |
| “Rebates erode our margin” | Growth rebate (performance-linked), Marketing/co-promotion rebate, General % of spend (small but unconditional) | Growth rebates only trigger on incremental revenue, so the supplier’s base margin is protected. Marketing rebates are a non-cash value exchange. A very small flat % may be acceptable if positioned as a loyalty gesture. |
| “We’d rather give you a price reduction instead” | Accept price reduction (shift value to price axis), Negotiate both (price cut \+ smaller rebate), Flat rebate as an add-on | If the price reduction offered exceeds the rebate value, accept it and count the win on the price axis. If the price cut is small, negotiate both: a modest price cut plus a small flat rebate. |
| “Your growth projection isn’t guaranteed” | Volume-tiered rebate (proof-based), Flat rebate (no growth needed), Contract duration extension as a trade | If the supplier doesn’t trust growth projections, shift to a volume-tiered structure where the rebate is earned only when spend is proven. If growth truly isn’t viable, propose a small flat rebate. Offer a longer contract term to give the supplier confidence. |
| Supplier is open to rebate but wants conditions | Volume-tiered rebate, Growth rebate with clear thresholds, Marketing/co-promotion rebate with defined scope | This is a positive signal. Negotiate the thresholds and conditions. Ensure the conditions are achievable based on historical spend. Use Summary/Recap to lock in the structure before negotiating the %. |

### **5.3.4 Cross-Axis Lever Trades**

When a single axis is stuck, the agent can shift value extraction to a different axis. This is the core Logrolling principle applied at the lever level:

| When This Axis Is Stuck | Shift Value To | Trade Example |
| :---- | :---- | :---- |
| **Price** | Payment terms extension or Rebate | “We understand your pricing position. If we can agree on Net 50 and a 1% annual rebate, we can work with the current unit price.” |
| **Payment Terms** | Price reduction or Rebate | “If Net 30 is firm, we’d need an additional 2% on unit price to make this work for our procurement targets.” |
| **Rebate** | Price reduction or Payment terms | “If rebates aren’t an option at our current spend, we’d need to revisit the unit price or extend payment terms to Net 55.” |

## **5.4 Combined Decision Flow**

At each turn, the engine runs the following sequence:

1. Read the supplier’s last message and classify: (a) intent (objection, counter-offer, question, acceptance, deflection), (b) emotional tone (cooperative, neutral, frustrated, defensive, adversarial), (c) which axis it relates to (price, payment terms, rebate, or general)  
2. Update the Position Tracker (Section 2.3): classify the last exchange as Successful, Partially Successful, or Unsuccessful. Update the Supplier Preference on the relevant axis based on what the supplier revealed.  
3. Read the updated Position Tracker to determine: which axis has the largest gap to Best Case, which axis has a ZOPA (overlap between buyer range and supplier preference), and which axis is stuck (2+ unsuccessful exchanges)  
4. Identify the current phase (Opening / Negotiation / Closure) and supplier behaviour category  
5. Look up the Strategy Pool table (Section 5.2.1) to get the set of applicable communication strategies  
6. From the pool, select the best strategy using the three criteria: supplier’s last response, emotional tone, and what best progresses toward the objective (Section 5.2.2)  
7. Decide which axis to push: (a) if an axis is stuck, pivot to a different axis; (b) if an axis has untapped potential (not yet raised, or supplier shows no objection), prioritise it; (c) if an axis has a ZOPA, push toward Buyer Best Case within the overlap  
8. Look up the relevant Lever table (Section 5.3.1, 5.3.2, or 5.3.3) for the selected axis. Select the lever that most directly addresses the supplier’s specific objection. If the axis is stuck, check the Cross-Axis Lever Trades table (Section 5.3.4) for a pivot  
9. Calibrate how much to push: if Supplier Preference is close to Buyer Bare Minimum, make a small ask (Incremental Concession). If Supplier Preference is inside the buyer’s range, push toward Best Case. If Supplier Preference is far from Bare Minimum, focus on getting into the zone first.  
10. Combine the selected strategy \+ lever \+ calibrated ask into a candidate response  
11. Generate 2–3 alternative paths with different strategy-lever combinations from the same pools  
12. Score each path on: (a) how directly it addresses the supplier’s last message, (b) expected acceptance probability, (c) value captured vs. Bare Minimum, (d) relationship preservation  
13. Select the highest-scoring path and generate the agent’s message  
14. Log the full reasoning trace including the Position Tracker snapshot (all paths, scores, selected path) for the Per-Message Reasoning Trace (Section 7\)

This decision flow ensures the agent never follows a rigid script. The Position Tracker is the single source of truth: it tells the agent which axis to push, how hard to push, and when to pivot. Every message is the output of a contextual evaluation that converges toward a win-win where the buyer achieves the best possible position within the ZOPA on each axis.

# **6\. Conversation Flow**

The negotiation follows a structured multi-phase flow. Each phase has a clear objective and a set of permitted strategies.

## **6.1 Phase 1: Opening**

**Objective:** Establish rapport, set the tone, and anchor the negotiation at the Best Case target.

1. Greet the supplier and reference the existing relationship context  
2. State the purpose of the conversation (contract renewal, re-negotiation, new terms review)  
3. Present the initial ask anchored to the Best Case objective (Anchoring strategy)  
4. Invite the supplier to respond

**Primary strategies:** Anchoring, We’re on the Same Side, Framing

## **6.2 Phase 2: Negotiation (Tactics Engine)**

**Objective:** Navigate supplier pushback and iterate toward an agreement using the defined communication strategies and negotiation levers.

The agent cycles through strategies dynamically based on: (a) the supplier’s response sentiment, (b) the remaining gap between current offer and Bare Minimum threshold, and (c) which levers are still available. The agent prioritises collaborative strategies first, then escalates to competitive ones if needed.

**Strategy selection logic:** The agent identifies the supplier’s behaviour, looks up the applicable strategy pool (Section 5.2.1), and picks the best fit based on the supplier’s last response, emotional tone, and what will most progress the deal. For example: if supplier is cooperative and raises a volume concern → Logrolling or Ask What It Takes from the pool. If supplier is resistant and rejects a price point → Cite Competition or Flinch from the pool.

## **6.3 Phase 3: Closure**

**Objective:** Finalize the agreement or escalate if Bare Minimum cannot be met.

* **Successful closure:** Summarise agreed terms, confirm mutual understanding, generate a draft term sheet for review.  
* **Escalation:** If the supplier’s best offer is below Bare Minimum, the agent flags for human review with a summary of the negotiation history and recommended next steps.  
* **No-deal exit:** Agent politely declines and logs the interaction, preserving the relationship for future attempts.

**Primary strategies:** Summary/Recap, Labelled Concession (for final trades), Deadline (if needed to close)

# **7\. Per-Message Reasoning Trace**

For every message the agent sends during the negotiation, the system generates a structured reasoning trace that is visible in the demo UI. This trace exposes the agent’s internal decision-making, making the demo compelling and transparent for VC audiences.

## **7.1 Reasoning Trace Structure**

Each agent message is accompanied by the following trace:

| Trace Field | Description |
| :---- | :---- |
| **Skills Used** | Which communication strategies and negotiation levers were considered for this turn. E.g., \[Anchoring, Cite Competition, Volume-based discount\] |
| **Paths Evaluated** | The candidate response paths the agent considered, with a brief rationale for each. E.g., Path A: “Concede 2% on price, hold on payment terms” (expected supplier acceptance: high). Path B: “Hold price, offer volume commitment” (expected acceptance: medium). |
| **Selected Path \+ Rationale** | Which path was chosen and why. E.g., “Selected Path A because supplier signalled price flexibility in last message and we are still above Bare Minimum on price.” |
| **Position Tracker Snapshot** | Full snapshot from the Position Tracker (Section 2.3) showing Buyer Best Case, Buyer Bare Minimum, Supplier Preference (inferred), and Current Offer on each axis. Also shows the exchange outcome classification (Successful / Partially Successful / Unsuccessful) for the last exchange. |
| **Confidence Score** | Agent’s confidence (0–100%) that the current negotiation trajectory will reach at least the Bare Minimum outcome. |

## **7.2 Example Reasoning Trace**

Below is an example of what appears alongside a single agent message in the demo UI:

| Agent Message | “We appreciate the counter-offer. Given our benchmarking data showing market rates at ₹90/unit, and considering our willingness to increase volume by 20%, we’d like to propose ₹93/unit with Net 50 terms. Would this structure work for your side?” |
| :---- | :---- |
| **Skills Used** | Competitive benchmarking, Volume commitment, Framing, Labelled Concession |
| **Paths Evaluated** | Path A: Hold at ₹90, push volume trade (acceptance: low — supplier already rejected ₹90). Path B: Move to ₹93 with volume \+ payment bundle (acceptance: high). Path C: Propose A/B options at ₹91 and ₹95 (acceptance: medium). |
| **Selected Path** | Path B — supplier’s last message signalled flexibility on price if volume increases. ₹93 is above Bare Minimum (₹97) and still captures 5% savings. Bundling payment term improvement adds perceived value. |
| **Position vs. Targets** | Price: ₹93 (target: ₹92, floor: ₹97) ✔. Payment: Net 50 (target: Net 60, floor: Net 45\) ✔. Rebate: not yet discussed. |
| **Confidence** | 78% — strong likelihood of closing within acceptable range |

# **8\. Feedback Manager Agent (Post-Call)**

After each negotiation session completes, a separate Feedback Manager Agent analyses the full transcript and reasoning traces to evaluate performance and recommend improvements. This is a critical differentiator for the demo, showing VC audiences that the system continuously learns and optimises.

## **8.1 Feedback Analysis Dimensions**

The Feedback Agent evaluates the negotiation across the following dimensions:

* **Outcome vs. Objectives:** Did the agent achieve the Best Case, Bare Minimum, or something in between? How much of the negotiation room was captured?  
* **Strategy Selection Effectiveness:** Were the right communication strategies used at the right moments? Were any strategies overused or underused? E.g., “The agent used Cite Competition three times but never tried Logrolling, missing a trade-off opportunity.”  
* **Lever Coverage:** Were all available levers explored? Which levers were left untouched? E.g., “Rebate levers were never introduced despite being available.”  
* **Concession Pattern Analysis:** Did the agent concede too much too quickly? Were concessions labelled and reciprocated? E.g., “The agent made 3 concessions on price before asking for anything in return.”  
* **Tone and Rapport Management:** Did the agent maintain a collaborative tone throughout? Did it adapt tone when the supplier became defensive or aggressive?  
* **Efficiency:** How many turns did the negotiation take? Was there unnecessary back-and-forth that could have been avoided?  
* **Missed Opportunities:** What alternative paths (from the reasoning traces) might have yielded a better outcome? The Feedback Agent can run counterfactual analysis on unchosen paths.

## **8.2 Feedback Output Format**

The Feedback Manager generates a structured report with:

| Section | Content |
| :---- | :---- |
| **Scorecard** | Numerical scores (0–100) for each dimension: Outcome Achievement, Strategy Effectiveness, Lever Coverage, Concession Discipline, Tone Management, Efficiency |
| **Highlights** | Top 3 things the agent did well (e.g., “Effective use of Anchoring in the opening set a strong initial frame”) |
| **Improvement Areas** | Top 3 specific, actionable improvements (e.g., “At turn 7, Logrolling would have been more effective than a second price concession”) |
| **Counterfactual Analysis** | For the top 2 unchosen paths, estimate what the outcome would have been and why the alternative may have been superior |
| **Learning Recommendations** | Suggested prompt/parameter adjustments for the negotiation agent to improve in future sessions |

# **9\. Guardrails and Alignment**

The agent operates within defined guardrails to ensure all negotiated outcomes comply with procurement policy:

* Never concede beyond the Bare Minimum threshold without human approval  
* Validate all supplier proposals against procurement strategy and risk thresholds before agreeing  
* Flag non-compliant requests, inaccurate data, or incorrect pricing structures  
* Maintain professional, non-adversarial tone throughout all interactions  
* Log every message exchange for audit trail and KPI measurement  
* Never share confidential internal pricing floors, BATNA details, or internal strategy with the supplier

# **10\. Outputs**

After each negotiation session, the agent produces:

| Output | Details |
| :---- | :---- |
| **Negotiation Summary** | Concise summary of what was discussed, strategies used, and outcome |
| **Agreed Terms (if deal)** | Structured output of final pricing, payment terms, rebates, and any conditions |
| **Savings Estimate** | Calculated savings vs. current contract and vs. Bare Minimum |
| **Conversation Transcript \+ Traces** | Full message-by-message log with per-message reasoning traces |
| **Escalation Report (if no deal)** | Supplier’s last offer, gap analysis, and recommended human follow-up actions |
| **Feedback Manager Report** | Scorecard, highlights, improvement areas, counterfactual analysis (see Section 8\) |

# **11\. Success Metrics (Demo KPIs)**

| Metric | Target | Benchmark (Pactum/Walmart) |
| :---- | :---- | :---- |
| Agreement Rate | \> 50% of negotiations | 64% achieved at Walmart |
| Average Savings | \> 1% cost reduction | 1.5% avg. at Walmart |
| Turnaround Time | \< 15 days per negotiation | 11 days avg. at Walmart |
| Payment Term Extension | \> 30 day improvement | 35 days avg. at Walmart |
| Lever Coverage | \> 3 levers explored per deal | N/A (new metric) |
| Feedback Score (Avg) | \> 75/100 across dimensions | N/A (new metric) |

# **12\. Demo Scenario (Suggested)**

**Supplier:** Acme Industrial Supplies (fictional, mid-tail supplier)

**Category:** Packaging materials

**Current Terms:** ₹100/unit, Net 30 payment, no rebate

**Annual Spend:** ₹2.5 Crore

**Best Case Target:** 8% unit price reduction (₹92/unit), Net 60 payment, 1.5% annual rebate

**Bare Minimum:** 3% unit price reduction (₹97/unit), Net 45 payment

Demo walkthrough: Agent receives inputs → Opens with Anchoring at Best Case → Supplier pushes back on price → Agent uses Ask What It Takes → Supplier requests volume guarantee → Agent uses Logrolling (volume for price) → Proposes Option A/B → Supplier selects Option B → Agent uses Summary/Recap to lock terms → Closes with agreed terms → Reasoning traces visible throughout → Feedback Manager Agent generates post-call report.

