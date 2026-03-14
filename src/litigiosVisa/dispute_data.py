from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


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
