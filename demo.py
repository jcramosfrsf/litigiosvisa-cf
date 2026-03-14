#!/usr/bin/env python3
"""Demo script to test the dispute category search workflow."""

from litigiosVisa.dispute_data import (
    search_categories,
    get_category_by_id,
    DISPUTE_CATEGORIES,
)


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


if __name__ == "__main__":
    demo_workflow()
