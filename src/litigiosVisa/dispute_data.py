from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


INTERACTION_TYPES = {
    "conflict": {
        "symbol": "⚠️",
        "description": "These categories cannot be filed together",
        "recommendation": "Choose one category only",
    },
    "complementary": {
        "symbol": "✓",
        "description": "These categories strengthen each other when filed together",
        "recommendation": "Consider filing both",
    },
    "overlap": {
        "symbol": "ⓘ",
        "description": "These categories have overlapping documentation requirements",
        "recommendation": "Gather combined documentation",
    },
    "sequential": {
        "symbol": "→",
        "description": "One category should be filed before the other",
        "recommendation": "File in order of priority",
    },
    "neutral": {
        "symbol": "—",
        "description": "No significant interaction between these categories",
        "recommendation": "Can be filed independently",
    },
}

INTERACTION_RULES: dict[tuple[str, str], str] = {
    # Conflicts - cannot file together
    ("CDT-001", "CDT-003"): "conflict",
    ("CDT-003", "CDT-001"): "conflict",
    ("CDT-001", "CDT-002"): "conflict",
    ("CDT-002", "CDT-001"): "conflict",
    ("CDT-005", "CDT-006"): "conflict",
    ("CDT-006", "CDT-005"): "conflict",
    ("CDT-007", "CDT-005"): "conflict",
    ("CDT-005", "CDT-007"): "conflict",
    # Complementary - strengthen each other
    ("CDT-002", "CDT-004"): "complementary",
    ("CDT-004", "CDT-002"): "complementary",
    ("CDT-005", "CDT-010"): "complementary",
    ("CDT-010", "CDT-005"): "complementary",
    ("CDT-001", "CDT-004"): "complementary",
    ("CDT-004", "CDT-001"): "complementary",
    ("CDT-008", "CDT-003"): "complementary",
    ("CDT-003", "CDT-008"): "complementary",
    # Overlap - shared documentation
    ("CDT-002", "CDT-009"): "overlap",
    ("CDT-009", "CDT-002"): "overlap",
    ("CDT-003", "CDT-004"): "overlap",
    ("CDT-004", "CDT-003"): "overlap",
    ("CDT-005", "CDT-010"): "overlap",
    ("CDT-010", "CDT-005"): "overlap",
    # Sequential - file in order
    ("CDT-004", "CDT-002"): "sequential",
    ("CDT-002", "CDT-004"): "sequential",
}


def get_interaction(cat1_id: str, cat2_id: str) -> str:
    key = (cat1_id.upper(), cat2_id.upper())
    return INTERACTION_RULES.get(key, "neutral")


def check_category_interactions(category_ids: list[str]) -> list[dict]:
    categories = [
        get_category_by_id(cat) for cat in category_ids if get_category_by_id(cat)
    ]

    if len(categories) < 2:
        return []

    interactions = []
    seen_pairs = set()

    for i, cat1 in enumerate(categories):
        for cat2 in categories[i + 1 :]:
            pair_key = tuple(sorted([cat1.category_id, cat2.category_id]))
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)

            interaction_type = get_interaction(cat1.category_id, cat2.category_id)
            interaction_info = INTERACTION_TYPES.get(
                interaction_type, INTERACTION_TYPES["neutral"]
            )

            result = {
                "categories": [cat1.category_id, cat2.category_id],
                "category_names": [cat1.name, cat2.name],
                "interaction": interaction_type,
                "symbol": interaction_info["symbol"],
                "description": interaction_info["description"],
                "recommendation": interaction_info["recommendation"],
            }

            if interaction_type == "conflict":
                result["action"] = "REMOVE_ONE"
            elif interaction_type == "complementary":
                result["action"] = "FILE_BOTH"
            elif interaction_type == "overlap":
                result["action"] = "COMBINE_DOCS"
            elif interaction_type == "sequential":
                result["action"] = "FILE_IN_ORDER"
            else:
                result["action"] = "INDEPENDENT"

            interactions.append(result)

    return interactions


@dataclass
class DisputeCategory:
    category_id: str
    name: str
    description: str
    conditions: list[str]
    documentation_required: list[str]
    time_limit_days: int
    keywords: list[str]


DISPUTE_CATEGORIES: list[DisputeCategory] = [
    DisputeCategory(
        category_id="CDT-001",
        name="Merchandise/Services Not Received",
        description="The cardholder claims they did not receive the merchandise or services purchased",
        conditions=[
            "Cardholder made a legitimate purchase",
            "Goods/services were not delivered",
            "Delivery was made to incorrect address",
            "Services were not rendered by the agreed date",
        ],
        documentation_required=[
            "Proof of delivery/signature",
            "Description of merchandise/services",
            "Date of expected delivery",
            "Cardholder communication history",
        ],
        time_limit_days=120,
        keywords=[
            "not received",
            "never arrived",
            "delivery",
            "shipping",
            "merchandise",
        ],
    ),
    DisputeCategory(
        category_id="CDT-002",
        name="Duplicate Charge",
        description="The cardholder claims they were charged multiple times for the same transaction",
        conditions=[
            "Multiple charges appear on statement for same purchase",
            "Charge amounts are identical or similar",
            "Transaction dates are the same or very close",
        ],
        documentation_required=[
            "Original transaction receipt",
            "All duplicate charge receipts",
            "Cardholder statement showing charges",
            "Merchant reconciliation records",
        ],
        time_limit_days=120,
        keywords=["duplicate", "charged twice", "multiple charges", "double charge"],
    ),
    DisputeCategory(
        category_id="CDT-003",
        name="Merchandise/Services Defective or Not as Described",
        description="The cardholder claims goods were defective or not as described",
        conditions=[
            "Goods received were defective or damaged",
            "Services did not meet specifications",
            "Product differed from what was advertised",
            "Wrong item was received",
        ],
        documentation_required=[
            "Photos of defective merchandise",
            "Product description/advertisement",
            "Return/refund attempts",
            "Correspondence with merchant",
        ],
        time_limit_days=120,
        keywords=["defective", "damaged", "not as described", "wrong item", "broken"],
    ),
    DisputeCategory(
        category_id="CDT-004",
        name="Credit Not Processed",
        description="The cardholder claims a credit/return was not processed to their account",
        conditions=[
            "Merchant issued a credit voucher",
            "Cardholder returned merchandise",
            "Credit was promised but not applied",
            "Credit processing time exceeded 30 days",
        ],
        documentation_required=[
            "Original purchase receipt",
            "Credit voucher copy",
            "Return shipment confirmation",
            "Communication showing credit promised",
        ],
        time_limit_days=120,
        keywords=["credit", "refund", "return", "not processed", "never credited"],
    ),
    DisputeCategory(
        category_id="CDT-005",
        name="Unauthorized Use",
        description="The cardholder claims a transaction was not authorized by them",
        conditions=[
            "Cardholder did not make the transaction",
            "Card was lost or stolen",
            "Cardholder signature was forged",
            "CVV/AVS verification failed",
        ],
        documentation_required=[
            "Cardholder affidavit",
            "Police report (if applicable)",
            "Evidence of card possession",
            "Transaction details and timestamps",
        ],
        time_limit_days=120,
        keywords=["unauthorized", "fraud", "not me", "stolen", "forged"],
    ),
    DisputeCategory(
        category_id="CDT-006",
        name="Cancelled Reservation/Recurring",
        description="Cardholder claims they cancelled a reservation or recurring payment",
        conditions=[
            "Cardholder cancelled within cancellation window",
            "Recurring payment was not stopped",
            "No-show policy was not disclosed",
            "Cancellation confirmation was provided",
        ],
        documentation_required=[
            "Cancellation confirmation",
            "Terms and conditions",
            "Communication with merchant",
            "Proof of cancellation timing",
        ],
        time_limit_days=120,
        keywords=["cancelled", "recurring", "subscription", "reservation", "no-show"],
    ),
    DisputeCategory(
        category_id="CDT-007",
        name="ATM Cash Not Received",
        description="Cardholder claims they did not receive cash from an ATM transaction",
        conditions=[
            "Transaction receipt was generated",
            "Cash was dispensed to another person",
            "ATM malfunction",
            "Transaction amount differs from cash received",
        ],
        documentation_required=[
            "ATM transaction receipt",
            "ATM camera footage request",
            "Cardholder account statement",
            "Bank investigation records",
        ],
        time_limit_days=120,
        keywords=["atm", "cash", "not received", "withdrawal", "machine"],
    ),
    DisputeCategory(
        category_id="CDT-008",
        name="Counterfeit Merchandise",
        description="Cardholder claims they received counterfeit goods",
        conditions=[
            "Goods are confirmed counterfeit",
            "Authenticity verification failed",
            "Brand owner certification of counterfeit",
        ],
        documentation_required=[
            "Photos of merchandise",
            "Brand authentication report",
            "Purchase receipt",
            "Comparison with authentic product",
        ],
        time_limit_days=120,
        keywords=["counterfeit", "fake", "knockoff", "fake brand", "replica"],
    ),
    DisputeCategory(
        category_id="CDT-009",
        name="Transaction Amount Differs",
        description="The cardholder claims the transaction amount differs from what they expected",
        conditions=[
            "Final charge differs from quoted amount",
            "Hidden fees were added",
            "Currency conversion discrepancy",
            "Tip was added without consent",
        ],
        documentation_required=[
            "Original quote/estimate",
            "Final receipt showing actual charge",
            "Menu/price list",
            "Currency conversion receipt",
        ],
        time_limit_days=120,
        keywords=["amount", "charged", "different", "quote", "price", "fee"],
    ),
    DisputeCategory(
        category_id="CDT-010",
        name="No Cardholder Liability (Zero Liability)",
        description="Cardholder reports they are not liable for unauthorized transactions under Zero Liability protection",
        conditions=[
            "Cardholder notified issuer promptly",
            "Card was not physically present for transaction",
            "Cardholder complied with security requirements",
            "No negligence proven",
        ],
        documentation_required=[
            "Notification date proof",
            "Transaction history",
            "Cardholder statement",
            "Fraud prevention measures used",
        ],
        time_limit_days=120,
        keywords=[
            "zero liability",
            "not liable",
            "protected",
            "security",
            "fraud protection",
        ],
    ),
]

CATEGORIES_BY_ID: dict[str, DisputeCategory] = {
    c.category_id: c for c in DISPUTE_CATEGORIES
}


def get_category_by_id(category_id: str) -> Optional[DisputeCategory]:
    return CATEGORIES_BY_ID.get(category_id.upper())


def search_categories(query: str) -> list[dict]:
    query_lower = query.lower()
    results = []

    for category in DISPUTE_CATEGORIES:
        score = 0
        matched_keywords = []

        for keyword in category.keywords:
            if keyword in query_lower:
                score += 1
                matched_keywords.append(keyword)

        if category.name.lower() in query_lower:
            score += 2

        for condition in category.conditions:
            if any(kw in condition.lower() for kw in query_lower.split()):
                score += 0.5

        if score > 0:
            results.append(
                {
                    "category_id": category.category_id,
                    "name": category.name,
                    "description": category.description,
                    "score": score,
                    "matched_keywords": matched_keywords,
                    "time_limit_days": category.time_limit_days,
                }
            )

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:5]
