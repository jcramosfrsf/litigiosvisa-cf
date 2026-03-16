from __future__ import annotations

import re
from fastmcp import FastMCP
from litigiosVisa.dispute_data import (
    search_categories,
    get_category_by_id,
    DisputeCategory,
    DISPUTE_CATEGORIES,
    check_category_interactions,
    INTERACTION_TYPES,
)
from litigiosVisa.database import (
    init_database,
    execute_query,
    get_table_schema,
    init_visa_cases_database,
    insert_visa_case,
    get_case_by_id,
    get_all_cases,
)

mcp = FastMCP("litigios-visa")

init_database()
init_visa_cases_database()


@mcp.tool()
def search_dispute_categories(scenario: str) -> list[dict]:
    """
    Search dispute categories by scenario description.

    Use this tool first when a cardholder presents a dispute scenario.
    It will return ranked candidate dispute categories based on keywords
    and description matching.

    Args:
        scenario: Free text description of the dispute situation

    Returns:
        List of candidate dispute categories with category_id, name,
        description, score, and time limit
    """
    if not scenario or not scenario.strip():
        return [
            {
                "error": "Scenario cannot be empty",
                "suggestion": "Provide a description of the dispute situation",
            }
        ]

    results = search_categories(scenario)

    if not results:
        return [
            {
                "message": "No specific category matched. Try describing the issue differently.",
                "suggestion": "Include keywords like: not received, duplicate charge, defective, credit, unauthorized, cancelled, ATM, counterfeit, amount differs",
            }
        ]

    return [
        {
            "category_id": r["category_id"],
            "name": r["name"],
            "description": r["description"],
            "score": r["score"],
            "matched_keywords": r.get("matched_keywords", []),
            "time_limit_days": r["time_limit_days"],
        }
        for r in results
    ]


@mcp.tool()
def get_full_dispute_condition(category_id: str) -> dict:
    """
    Get full dispute condition details by category ID.

    After identifying the correct category from search_dispute_categories,
    call this tool to get the complete requirements for filing the dispute.

    Args:
        category_id: The dispute category ID (e.g., 'CDT-001')

    Returns:
        Dictionary with full category details including conditions,
        documentation requirements, and time limits
    """
    if not category_id or not category_id.strip():
        return {"error": "category_id cannot be empty"}

    category = get_category_by_id(category_id)

    if not category:
        available = [c.category_id for c in DISPUTE_CATEGORIES]
        return {
            "error": f"Category '{category_id}' not found",
            "available_categories": available,
        }

    return {
        "category_id": category.category_id,
        "name": category.name,
        "description": category.description,
        "conditions": category.conditions,
        "documentation_required": category.documentation_required,
        "time_limit_days": category.time_limit_days,
        "keywords": category.keywords,
    }


@mcp.tool()
def check_interactions(category: list[str]) -> list[dict]:
    """
    Check interactions between dispute categories.

    Sometimes multiple dispute categories may apply to the same case.
    This tool helps identify if there are conflicts, complementary benefits,
    or documentation overlaps between categories.

    Args:
        category: List of category IDs to check (e.g., ["CDT-001", "CDT-004"])

    Returns:
        List of interaction results with:
        - categories: pair of category IDs
        - category_names: pair of category names
        - interaction: type (conflict/complementary/overlap/sequential/neutral)
        - symbol: visual indicator
        - description: what this interaction means
        - recommendation: suggested action
        - action: REMOVE_ONE, FILE_BOTH, COMBINE_DOCS, FILE_IN_ORDER, or INDEPENDENT
    """
    if not category:
        return [
            {
                "error": "No categories provided",
                "suggestion": "Provide a list of category IDs",
            }
        ]

    if len(category) < 2:
        return [
            {
                "error": "Need at least 2 categories to check interactions",
                "suggestion": "Provide at least 2 category IDs",
            }
        ]

    interactions = check_category_interactions(category)

    if not interactions:
        return [
            {
                "error": "No valid categories found",
                "available": [c.category_id for c in DISPUTE_CATEGORIES],
            }
        ]

    return interactions


@mcp.tool()
def generate_sql_query(intent: str) -> dict:
    """
    Generate SQL query from natural language intent.

    This is a template-based generator for common SQL queries against
    the merchant dispute history database. Returns both the generated
    SQL and the executed results.

    Available tables:
    - disputes: dispute_id, merchant_id, cardholder_id, amount, currency,
                dispute_category, status, reason_code, transaction_date,
                created_at, resolved_at, outcome
    - merchants: merchant_id, name, category, country, created_at
    - transactions: transaction_id, merchant_id, cardholder_id, amount,
                   currency, transaction_type, status, timestamp

    Args:
        intent: Natural language description of what data to retrieve.
                Examples:
                - "show me recent disputes"
                - "disputes for Amazon"
                - "pending disputes over 100 dollars"
                - "disputes by status approved"
                - "disputes from January 2026"

    Returns:
        Dictionary with generated SQL and optional results
    """
    if not intent or not intent.strip():
        return {
            "error": "Intent cannot be empty",
            "suggestion": "Provide a description of what data you want to retrieve",
        }

    intent_lower = intent.lower()
    sql = None
    explanation = ""

    # Priority order - most specific first
    # 1. Count/summary queries
    if any(kw in intent_lower for kw in ["count", "total", "how many", "summary"]):
        if "status" in intent_lower:
            sql = "SELECT status, COUNT(*) as count FROM disputes GROUP BY status ORDER BY count DESC"
            explanation = "Count of disputes grouped by status"
        elif "amount" in intent_lower or "value" in intent_lower:
            sql = "SELECT SUM(amount) as total_amount, COUNT(*) as total_disputes, AVG(amount) as avg_amount FROM disputes"
            explanation = "Total amount in dispute"
        elif "category" in intent_lower:
            sql = "SELECT dispute_category, COUNT(*) as count FROM disputes GROUP BY dispute_category"
            explanation = "Count of disputes by category"
        else:
            sql = "SELECT COUNT(*) as total FROM disputes"
            explanation = "Total count of disputes"

    # 2. By outcome
    elif any(
        kw in intent_lower for kw in ["outcome", "result", "approved", "rejected"]
    ):
        outcome = "approved" if "approved" in intent_lower else "rejected"
        sql = f"SELECT * FROM disputes WHERE outcome = '{outcome}'"
        explanation = f"Disputes with outcome: {outcome}"

    # 3. By status
    elif any(kw in intent_lower for kw in ["pending", "resolved", "investigating"]):
        status = (
            "pending"
            if "pending" in intent_lower
            else "resolved"
            if "resolved" in intent_lower
            else "investigating"
        )
        sql = f"SELECT * FROM disputes WHERE status = '{status}'"
        explanation = f"Disputes with status: {status}"

    # 4. By merchant name
    elif "amazon" in intent_lower:
        sql = "SELECT d.*, m.name as merchant_name, m.category as merchant_category FROM disputes d JOIN merchants m ON d.merchant_id = m.merchant_id WHERE m.name LIKE '%Amazon%'"
        explanation = "Disputes from Amazon merchant"
    elif "walmart" in intent_lower:
        sql = "SELECT d.*, m.name as merchant_name FROM disputes d JOIN merchants m ON d.merchant_id = m.merchant_id WHERE m.name LIKE '%Walmart%'"
        explanation = "Disputes from Walmart merchant"
    elif "netflix" in intent_lower:
        sql = "SELECT d.*, m.name as merchant_name FROM disputes d JOIN merchants m ON d.merchant_id = m.merchant_id WHERE m.name LIKE '%Netflix%'"
        explanation = "Disputes from Netflix merchant"
    elif "merchant" in intent_lower:
        sql = "SELECT d.*, m.name as merchant_name FROM disputes d JOIN merchants m ON d.merchant_id = m.merchant_id LIMIT 20"
        explanation = "Disputes with merchant info"

    # 5. By amount
    elif any(kw in intent_lower for kw in ["over", "above", "greater than"]) and any(
        char.isdigit() for char in intent
    ):
        import re

        nums = re.findall(r"\d+", intent)
        if nums:
            amount = nums[0]
            sql = f"SELECT * FROM disputes WHERE amount > {amount}"
            explanation = f"Disputes over ${amount}"
    elif any(kw in intent_lower for kw in ["under", "below", "less than"]) and any(
        char.isdigit() for char in intent
    ):
        import re

        nums = re.findall(r"\d+", intent)
        if nums:
            amount = nums[0]
            sql = f"SELECT * FROM disputes WHERE amount < {amount}"
            explanation = f"Disputes under ${amount}"

    # 6. Recent/latest
    elif any(
        kw in intent_lower
        for kw in ["recent", "latest", "newest", "recent disputes", "latest disputes"]
    ):
        sql = "SELECT * FROM disputes ORDER BY created_at DESC LIMIT 10"
        explanation = "10 most recent disputes"

    # 7. By category
    elif "cdt-" in intent_lower or "category" in intent_lower:
        import re

        match = re.search(r"(CDT-\d+)", intent.upper())
        if match:
            cat = match.group(1)
            sql = f"SELECT * FROM disputes WHERE dispute_category = '{cat}'"
            explanation = f"Disputes of category {cat}"
        else:
            sql = "SELECT * FROM disputes ORDER BY created_at DESC LIMIT 10"
            explanation = "Recent disputes"

    # 8. All disputes
    elif "all" in intent_lower:
        sql = "SELECT * FROM disputes ORDER BY created_at DESC"
        explanation = "All disputes"

    # Default
    else:
        sql = "SELECT * FROM disputes ORDER BY created_at DESC LIMIT 10"
        explanation = "10 most recent disputes (default)"

    return {
        "intent": intent,
        "generated_sql": sql,
        "explanation": explanation,
        "note": "Use execute_sql_query to run this query",
    }


@mcp.tool()
def execute_sql_query(sql: str) -> dict:
    """
    Execute a read-only SQL query against the dispute database.

    Only SELECT statements are allowed for security.

    Args:
        sql: SQL query to execute. Can be a full SELECT statement or
             use 'recent', 'pending', 'approved', 'merchantname', etc.

    Returns:
        Dictionary with results or error message. Results include:
        - rows: list of result rows
        - count: number of rows returned
        - sql: the executed query
    """
    if not sql or not sql.strip():
        return {"error": "SQL query cannot be empty"}

    sql_upper = sql.strip().upper()

    # Security checks
    if not sql_upper.startswith("SELECT"):
        return {
            "error": "Only SELECT queries are allowed for security reasons",
            "hint": "Use generate_sql_query to create a valid SELECT query",
        }

    forbidden_patterns = [
        r"\bDROP\b",
        r"\bDELETE\b",
        r"\bINSERT\b",
        r"\bUPDATE\b",
        r"\bALTER\b",
        r"\bTRUNCATE\b",
        r"\bCREATE\b",
        r"\bGRANT\b",
        r"\bREVOKE\b",
        r"\bEXEC\b",
        r"\bEXECUTE\b",
    ]
    import re

    for pattern in forbidden_patterns:
        if re.search(pattern, sql_upper):
            return {
                "error": f"Forbidden keyword detected. Only read-only SELECT queries are allowed",
                "hint": "Avoid DROP, DELETE, INSERT, UPDATE, ALTER, TRUNCATE, CREATE, GRANT, REVOKE",
            }

    # Execute the query
    results = execute_query(sql)

    if not results:
        return {
            "sql": sql,
            "rows": [],
            "count": 0,
            "message": "Query executed successfully but returned no results",
        }

    if "error" in results[0]:
        return {"sql": sql, "error": results[0]["error"]}

    return {
        "sql": sql,
        "rows": results,
        "count": len(results),
        "message": f"Successfully returned {len(results)} row(s)",
    }


@mcp.tool()
def create_case(
    scenario: str,
    category_id: str,
    merchant_id: str,
    cardholder_id: str,
    amount: float,
    currency: str = "USD",
    transaction_date: str = "",
    documentation_status: str = "",
    notes: str = "",
) -> dict:
    """
    Register a new dispute case in the VisaCases local database.

    Use this tool after evaluating a dispute case to register it for
    tracking and follow-up purposes.

    Args:
        scenario: Free text description of the dispute situation
        category_id: The dispute category ID (e.g., 'CDT-002')
        merchant_id: The merchant identifier (e.g., 'M001')
        cardholder_id: The cardholder identifier (e.g., 'CH001')
        amount: Transaction amount in the specified currency
        currency: Currency code (default: 'USD')
        transaction_date: Date of the transaction (YYYY-MM-DD format)
        documentation_status: Description of available documentation
        notes: Additional notes about the case

    Returns:
        Dictionary with:
        - case_id: Generated case identifier (e.g., 'CASE-001')
        - status: Case status ('registered')
        - created_at: ISO timestamp of registration
    """
    if not scenario or not scenario.strip():
        return {"error": "Scenario cannot be empty"}

    if not category_id or not category_id.strip():
        return {"error": "category_id cannot be empty"}

    if not merchant_id or not merchant_id.strip():
        return {"error": "merchant_id cannot be empty"}

    if not cardholder_id or not cardholder_id.strip():
        return {"error": "cardholder_id cannot be empty"}

    if amount is None or amount <= 0:
        return {"error": "amount must be a positive number"}

    category = get_category_by_id(category_id)
    if not category:
        available = [c.category_id for c in DISPUTE_CATEGORIES]
        return {
            "error": f"Category '{category_id}' not found",
            "available_categories": available,
        }

    result = insert_visa_case(
        scenario=scenario,
        category_id=category_id,
        merchant_id=merchant_id,
        cardholder_id=cardholder_id,
        amount=amount,
        currency=currency,
        transaction_date=transaction_date,
        documentation_status=documentation_status,
        notes=notes,
    )

    return {
        "case_id": result["case_id"],
        "status": result["status"],
        "created_at": result["created_at"],
        "message": f"Case {result['case_id']} registered successfully",
        "category": category.name,
    }


def collect_case_data_cli() -> dict:
    """
    Interactive CLI function to collect case data from user input.
    Prompts for each field and returns the case registration result.
    """
    print("\n" + "=" * 50)
    print("  VISA DISPUTE CASE REGISTRATION")
    print("=" * 50 + "\n")

    print("Available Categories:")
    for cat in DISPUTE_CATEGORIES:
        print(f"  {cat.category_id}: {cat.name}")
    print()

    scenario = input("Scenario (description of the dispute): ").strip()
    if not scenario:
        print("Error: Scenario cannot be empty")
        return {"error": "Scenario cannot be empty"}

    category_id = input("Category ID (e.g., CDT-002): ").strip().upper()
    if not category_id:
        print("Error: Category ID cannot be empty")
        return {"error": "Category ID cannot be empty"}

    category = get_category_by_id(category_id)
    if not category:
        print(f"Error: Category '{category_id}' not found")
        print(f"Available: {[c.category_id for c in DISPUTE_CATEGORIES]}")
        return {"error": f"Category '{category_id}' not found"}

    merchant_id = input("Merchant ID (e.g., M001): ").strip()
    if not merchant_id:
        print("Error: Merchant ID cannot be empty")
        return {"error": "Merchant ID cannot be empty"}

    cardholder_id = input("Cardholder ID (e.g., CH001): ").strip()
    if not cardholder_id:
        print("Error: Cardholder ID cannot be empty")
        return {"error": "Cardholder ID cannot be empty"}

    amount_str = input("Amount (e.g., 149.99): ").strip()
    try:
        amount = float(amount_str)
        if amount <= 0:
            print("Error: Amount must be positive")
            return {"error": "Amount must be positive"}
    except ValueError:
        print("Error: Invalid amount")
        return {"error": "Invalid amount"}

    currency = input("Currency (default: USD): ").strip() or "USD"
    transaction_date = input("Transaction Date (YYYY-MM-DD): ").strip()
    documentation_status = input("Documentation Status: ").strip()
    notes = input("Notes (optional): ").strip()

    result = create_case(
        scenario=scenario,
        category_id=category_id,
        merchant_id=merchant_id,
        cardholder_id=cardholder_id,
        amount=amount,
        currency=currency,
        transaction_date=transaction_date,
        documentation_status=documentation_status,
        notes=notes,
    )

    print("\n" + "-" * 50)
    if "error" in result:
        print(f"ERROR: {result['error']}")
    else:
        print(f"CASE REGISTERED SUCCESSFULLY!")
        print(f"  Case ID:     {result['case_id']}")
        print(f"  Status:      {result['status']}")
        print(f"  Category:    {result['category']}")
        print(f"  Created:     {result['created_at']}")
        print(f"  Message:     {result['message']}")
    print("-" * 50 + "\n")

    return result


def main():
    mcp.run()
