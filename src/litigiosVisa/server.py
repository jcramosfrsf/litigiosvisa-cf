from __future__ import annotations

from fastmcp import FastMCP

mcp = FastMCP("litigios-visa")


@mcp.tool()
def search_dispute_categories(scenario: str) -> list[dict]:
    """Search dispute categories by scenario description."""
    return [{"message": "Message received"}]


@mcp.tool()
def get_full_dispute_condition(category_id: str) -> dict:
    """Get full dispute condition details by category ID."""
    return {"message": "Message received"}


@mcp.tool()
def check_interactions(category: list[str]) -> list[dict]:
    """Check interactions between dispute categories."""
    return [{"message": "Message received"}]


@mcp.tool()
def generate_sql_query(intent: str) -> str:
    """Generate SQL query from natural language intent."""
    return "Message received"


@mcp.tool()
def execute_sql_query(sql: str) -> list[dict]:
    """Execute a read-only SQL query."""
    return [{"message": "Message received"}]


def main():
    mcp.run()
