from __future__ import annotations

from fastmcp import FastMCP
from litigiosVisa.dispute_data import (
    search_categories,
    get_category_by_id,
    DisputeCategory,
    DISPUTE_CATEGORIES,
    check_category_interactions,
    INTERACTION_TYPES,
)

mcp = FastMCP("litigios-visa")


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
def generate_sql_query(intent: str) -> str:
    """
    Generate SQL query from natural language intent.

    This is a template-based generator for common SQL queries against
    the merchant dispute history database.

    Args:
        intent: Natural language description of what data to retrieve

    Returns:
        Generated SELECT SQL query
    """
    intent_lower = intent.lower()

    templates = {
        "recent_disputes": "SELECT * FROM disputes ORDER BY created_at DESC LIMIT 10",
        "by_merchant": "SELECT * FROM disputes WHERE merchant_name LIKE '%{merchant}%'",
        "by_amount": "SELECT * FROM disputes WHERE amount > {min_amount} AND amount < {max_amount}",
        "by_status": "SELECT * FROM disputes WHERE status = '{status}'",
        "by_date": "SELECT * FROM disputes WHERE created_at >= '{start_date}' AND created_at <= '{end_date}'",
    }

    for key, query in templates.items():
        if key.replace("_", " ") in intent_lower:
            return query

    return f"-- Could not generate SQL for: {intent}\n-- Available patterns: recent_disputes, by_merchant, by_amount, by_status, by_date"


@mcp.tool()
def execute_sql_query(sql: str) -> list[dict]:
    """
    Execute a read-only SQL query against the dispute database.

    Only SELECT statements are allowed for security.

    Args:
        sql: SQL query to execute

    Returns:
        List of result rows as dictionaries
    """
    sql_upper = sql.strip().upper()

    if not sql_upper.startswith("SELECT"):
        return [{"error": "Only SELECT queries are allowed for security reasons"}]

    if any(
        keyword in sql_upper
        for keyword in ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "TRUNCATE"]
    ):
        return [{"error": "Only read-only SELECT queries are allowed"}]

    return [
        {
            "message": "Database not yet initialized. Run ingestion pipeline to set up SQLite database."
        }
    ]


def main():
    mcp.run()
