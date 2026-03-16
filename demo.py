#!/usr/bin/env python3
"""Demo script to test the dispute category search workflow."""

from litigiosVisa.dispute_data import (
    search_categories,
    get_category_by_id,
    DISPUTE_CATEGORIES,
    check_category_interactions,
)
from litigiosVisa.server import create_case, collect_case_data_cli


def demo_workflow():
    print("=" * 60)
    print("VISA DISPUTE CASE MANAGEMENT - DEMO")
    print("=" * 60)

    # Example dispute scenario
    scenario = "Customer says they were charged twice for the same purchase"

    print(f"\n[STEP 1] Customer presents dispute:")
    print(f"  Scenario: '{scenario}'")

    # Step 1: Search categories
    print(f"\n[STEP 2] Calling search_dispute_categories...")
    results = search_categories(scenario)

    print(f"\n  Found {len(results)} matching categories:")
    for r in results:
        print(f"  [{r['category_id']}] {r['name']}")
        print(f"      Score: {r['score']}, Time limit: {r['time_limit_days']} days")
        print(f"      Matched: {r.get('matched_keywords', [])}")

    # Select the best match
    if results:
        best_match = results[0]
        category_id = best_match["category_id"]

        # Step 2: Get full details
        print(f"\n[STEP 3] Calling get_full_dispute_condition for {category_id}...")
        details = get_category_by_id(category_id)

        print(f"\n  Category: {details.name}")
        print(f"  Description: {details.description}")
        print(f"\n  CONDITIONS:")
        for i, cond in enumerate(details.conditions, 1):
            print(f"    {i}. {cond}")

        print(f"\n  DOCUMENTATION REQUIRED:")
        for i, doc in enumerate(details.documentation_required, 1):
            print(f"    {i}. {doc}")

        print(f"\n  Time Limit: {details.time_limit_days} days")

        # Step 3: Validation decision
        print(f"\n[STEP 4] DISPUTE VALIDATION:")
        print(f"-" * 40)
        print(f"  Category: {details.name}")
        print(f"  Status: OK")
        print(f"  Recommendation: File dispute under category {category_id}")
        print(f"  Time remaining: {details.time_limit_days} days from transaction")
        print(f"\n  Actions needed:")
        for doc in details.documentation_required:
            print(f"    - Obtain {doc}")


def demo_interactions():
    print("\n" + "=" * 60)
    print("DEMO 2: CHECK INTERACTIONS")
    print("=" * 60)

    test_cases = [
        ["CDT-002", "CDT-004"],  # Complementary
        ["CDT-001", "CDT-003"],  # Conflict
        ["CDT-002", "CDT-009"],  # Overlap
        ["CDT-005", "CDT-010"],  # Complementary
    ]

    for categories in test_cases:
        print(f"\n  Checking: {categories}")
        interactions = check_category_interactions(categories)

        for interaction in interactions:
            print(f"\n  Result:")
            print(
                f"    {interaction['symbol']} {interaction['interaction'].upper()}: {interaction['description']}"
            )
            print(f"    Categories: {interaction['categories']}")
            print(f"    Action: {interaction['action']}")
            print(f"    Recommendation: {interaction['recommendation']}")


def demo_create_case():
    """Demo the create_case function."""
    print("\n" + "=" * 60)
    print("DEMO 3: CREATE CASE")
    print("=" * 60)

    case_result = create_case(
        scenario="Customer charged twice for laptop bag on Amazon",
        category_id="CDT-002",
        merchant_id="M001",
        cardholder_id="CH001",
        amount=149.99,
        currency="USD",
        transaction_date="2026-01-10",
        documentation_status="receipt, statement available",
        notes="Two identical charges, 1 minute apart",
    )

    print(f"\n  Case Registration Result:")
    print(f"    Case ID:     {case_result.get('case_id')}")
    print(f"    Status:      {case_result.get('status')}")
    print(f"    Category:    {case_result.get('category')}")
    print(f"    Created:     {case_result.get('created_at')}")
    print(f"    Message:     {case_result.get('message')}")

    return case_result


def demo_collect_case_data_cli():
    """Demo the CLI case collection function."""
    print("\n" + "=" * 60)
    print("DEMO 4: CLI CASE COLLECTION")
    print("=" * 60)
    print("\n  This function prompts for case data interactively.")
    print("  Run with: uv run visa-case-register")
    print("")


if __name__ == "__main__":
    demo_workflow()
    demo_interactions()
    demo_create_case()
    demo_collect_case_data_cli()
