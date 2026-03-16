# Visa Dispute Management MCP Server

A Model Context Protocol (MCP) server for managing Visa card dispute cases. This server provides tools for searching dispute categories, checking dispute conditions, analyzing category interactions, and querying dispute transaction data.

## Overview

This project implements an MCP server that helps evaluate whether a Visa dispute case should be approved or rejected. It uses:

- **FastMCP** - For the MCP server implementation
- **SQLite** - For storing dispute, merchant, and transaction data
- **Python** - Core language (3.14+)

## Features

- **Search Dispute Categories** - Find relevant dispute categories from customer descriptions
- **Get Full Conditions** - Retrieve complete requirements for each dispute category
- **Check Interactions** - Analyze conflicts between multiple dispute categories
- **Generate SQL Queries** - Convert natural language to SQL for data retrieval
- **Execute SQL Queries** - Run read-only queries against the dispute database
- **Create Case** - Register a new dispute case in the local VisaCases database

## Dispute Categories

| ID | Name |
|----|------|
| CDT-001 | Merchandise/Services Not Received |
| CDT-002 | Duplicate Charge |
| CDT-003 | Merchandise/Services Defective or Not as Described |
| CDT-004 | Credit Not Processed |
| CDT-005 | Unauthorized Use |
| CDT-006 | Cancelled Reservation/Recurring |
| CDT-007 | ATM Cash Not Received |
| CDT-008 | Counterfeit Merchandise |
| CDT-009 | Transaction Amount Differs |
| CDT-010 | No Cardholder Liability (Zero Liability) |

## Local Deployment

### Prerequisites

- Python 3.14 or higher
- uv (Python package manager)

### Installation

1. Clone the repository and navigate to the project directory:

```bash
cd litigiosVisaV2
```

2. Install dependencies using uv:

```bash
uv sync
```

3. Verify the MCP server starts correctly:

```bash
uv run visa-dispute
```

The server should start and display FastMCP information. Press Ctrl+C to stop.

## OpenCode Configuration

### Step 1: Configure OpenCode

Add the MCP server configuration to your OpenCode config file. Edit `~/.config/opencode/config.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "litigios-visa": {
      "type": "local",
      "command": ["/path/to/litigiosVisaV2/.venv/bin/visa-dispute"],
      "enabled": true
    }
  }
}
```

Replace `/path/to/litigiosVisaV2` with your actual project path.

### Step 2: Restart OpenCode

After saving the configuration, restart OpenCode. The MCP server should connect automatically.

### Step 3: Verify Connection

Run the following command to verify the MCP server is connected:

```bash
opencode mcp list
```

You should see:
```
MCP Servers
  litigios-visa (connected)
```

## Usage

### Available Tools

Once connected, the following tools are available:

1. **search_dispute_categories(scenario)** - Search for matching dispute categories
2. **get_full_dispute_condition(category_id)** - Get full requirements for a category
3. **check_interactions(categories)** - Check for conflicts between categories
4. **generate_sql_query(intent)** - Generate SQL from natural language
5. **execute_sql_query(sql)** - Execute a read-only SQL query
6. **create_case(...)** - Register a new dispute case in the local VisaCases database

### Example: Dispute Evaluation

Start a new OpenCode session in the project directory:

```bash
opencode litigiosVisaV2
```

Load the example case:

```bash
cat disputes/dispute_one.md
```

Process the dispute using the MCP tools:

```
User: Evaluate this dispute case:
"I bought a laptop bag from Amazon for $149.99 on January 10, 2026. 
Today I checked my credit card statement and I see TWO charges for the 
same amount from Amazon - both on January 10th."

Agent: Let me search for matching dispute categories...

(search_dispute_categories)
Result: CDT-002 (Duplicate Charge) with score 5/5

Now let me get the full conditions for this category...

(get_full_dispute_condition "CDT-002")
Result: 
- Conditions: Multiple charges, identical amounts, same/close dates
- Documentation required: Original receipt, duplicate receipt, statement
- Time limit: 120 days

Let me check the transaction history...

(generate_sql_query "disputes from Amazon")
(execute_sql_query <generated SQL>)
Result: Found 2 disputes for Amazon, including this one

Let me verify the transactions...

(execute_sql_query "SELECT * FROM transactions WHERE merchant_id = 'M001'")
Result: Two transactions (TXN001, TXN002) - $149.99, 1 minute apart

DECISION: OK
All conditions met:
- Multiple charges: Yes (2 transactions)
- Identical amounts: Yes ($149.99 each)
- Same date: Yes (2026-01-10)
- Documentation: Available
- Time limit: Within 120 days

Recommend filing dispute for CDT-002 (Duplicate Charge)
```

## Project Structure

```
litigiosVisaV2/
├── src/litigiosVisa/
│   ├── server.py          # MCP server implementation
│   ├── dispute_data.py    # Dispute categories and interactions
│   └── database.py        # SQLite database and queries
├── data/
│   ├── dispute.db         # SQLite database (generated)
│   └── merchants-dispute-management-guidelines.pdf
├── disputes/
│   └── dispute_one.md     # Example dispute case
├── SYSTEM_PROMPT.md       # Agent instructions
├── demo.py                # Demo script
├── pyproject.toml         # Project configuration
└── uv.lock                # Lock file
```

## Running the Demo

To run the demonstration script:

```bash
uv run python demo.py
```

This will show:
1. Dispute category search workflow
2. Category interaction checks (conflicts, complementary, overlap)

## Testing the MCP Server

To test the MCP server directly:

```bash
uv run visa-dispute
```

The server will start on stdio transport, waiting for MCP client connections.

## CLI Case Registration

To register a new case interactively via command line:

```bash
uv run visa-case-register
```

This will prompt for:
- Scenario description
- Category ID
- Merchant ID
- Cardholder ID
- Amount
- Currency (default: USD)
- Transaction Date
- Documentation Status
- Notes (optional)

## Security

- Only SELECT queries are allowed in execute_sql_query
- Forbidden keywords: DROP, DELETE, INSERT, UPDATE, ALTER, TRUNCATE, CREATE, GRANT, REVOKE
- Word boundary matching prevents false positives (e.g., "CREATED_AT" is allowed)

## License

MIT
