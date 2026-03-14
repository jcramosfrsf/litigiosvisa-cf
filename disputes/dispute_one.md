# Dispute Case: DSP-001 - Amazon Duplicate Charge

## Customer Scenario

> "I bought a laptop bag from Amazon for $149.99 on January 10, 2026. Today I checked my credit card statement and I see TWO charges for the same amount from Amazon - both on January 10th. I've never been charged twice for a single purchase before. I want to dispute the duplicate charge."

---

## Case Details

| Field | Value |
|-------|-------|
| Dispute ID | DSP-001 |
| Cardholder | CH001 |
| Merchant | Amazon.com (M001) |
| Transaction Date | 2026-01-10 |
| Amount | $149.99 USD |
| Category | Duplicate Charge (CDT-002) |
| Status | Pending |

---

## Transaction Records

### Transaction 1
- Transaction ID: TXN001
- Amount: $149.99
- Time: 2026-01-10 14:30:00
- Status: completed

### Transaction 2  
- Transaction ID: TXN002
- Amount: $149.99
- Time: 2026-01-10 14:31:00 (one minute later!)
- Status: completed

---

## Expected Agent Workflow

```
1. search_dispute_categories("I was charged twice for the same purchase")
   → Expected: CDT-002 (Duplicate Charge) with high score

2. get_full_dispute_condition("CDT-002")
   → Expected: Conditions and documentation requirements

3. generate_sql_query("disputes from Amazon")
   → Expected: SQL to check merchant history

4. execute_sql_query(<generated SQL>)
   → Expected: Show DSP001 and other Amazon disputes

5. check_interactions(["CDT-002"])
   → Expected: Single category, no conflicts
```

---

## Expected Decision

### Conditions Analysis

| Condition | Status |
|-----------|--------|
| Multiple charges on statement | ✓ MET - Two identical $149.99 charges |
| Charge amounts identical | ✓ MET - Both $149.99 |
| Transaction dates same/close | ✓ MET - Both on 2026-01-10, 1 min apart |

### Documentation Available

| Document | Available |
|----------|-----------|
| Original transaction receipt | ✓ Yes (TXN001) |
| Duplicate charge receipt | ✓ Yes (TXN002) |
| Cardholder statement | ✓ Yes |
| Merchant reconciliation | ✓ Yes |

### Time Limit Check

- Transaction date: 2026-01-10
- Filing date: 2026-01-12
- Days elapsed: 2 days
- Time limit: 120 days
- **Within time limit:** ✓ YES

---

## Expected Output

```
DISPUTE EVALUATION
==================
Scenario: Customer charged twice for $149.99 Amazon purchase
Category: CDT-002 - Duplicate Charge
Match Score: 5/5
Time Limit: 118 days remaining (of 120)

CONDITIONS MET:
✓ Multiple charges appear on statement for same purchase
✓ Charge amounts are identical ($149.99)
✓ Transaction dates are the same (2026-01-10)

DOCUMENTATION:
✓ Original transaction receipt available
✓ Duplicate charge receipt available
✓ Cardholder statement shows both charges

DATABASE CHECK:
- Recent disputes for Amazon: 2
- This case: First duplicate charge case

DECISION: OK ✓
REASONING: All conditions met, documentation available, within time limit.
The two transactions are 1 minute apart with identical amounts - clear duplicate charge.
Recommend filing dispute for $149.99 (one of the two charges).
```

---

## Testing Instructions

1. Start the MCP server: `uv run visa-dispute`
2. Load this dispute case into the agent
3. Follow the workflow using the tools
4. Verify the decision matches "OK"
5. Check that reasoning is clear and complete
