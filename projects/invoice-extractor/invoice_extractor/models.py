"""Typed shapes for an extracted invoice.

Money is `Decimal`, never `float`. Invoice totals get compared for equality
and summed across batches; binary floating point turns 0.1 + 0.2 into
0.30000000000000004 and a reconciliation check into a false alarm.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class LineItem(BaseModel):
    description: str
    quantity: Decimal = Field(default=Decimal("1"))
    unit_price: Decimal
    amount: Decimal

    model_config = {"str_strip_whitespace": True}


class Invoice(BaseModel):
    """One invoice as read off the page. Nothing here is trusted yet."""

    vendor: str | None = None
    invoice_number: str | None = None
    invoice_date: date | None = None
    due_date: date | None = None
    currency: str | None = Field(default=None, max_length=8)
    subtotal: Decimal | None = None
    tax: Decimal | None = None
    total: Decimal | None = None
    line_items: list[LineItem] = Field(default_factory=list)

    source_file: str | None = None
    """Set by the pipeline, not by the model."""

    model_config = {"str_strip_whitespace": True}

    @property
    def line_item_total(self) -> Decimal:
        return sum((li.amount for li in self.line_items), Decimal("0"))


# The schema handed to the model. Kept explicit rather than generated from the
# Pydantic model so that a field rename cannot silently change the prompt
# contract, and so dates stay plain strings for the model to fill.
EXTRACTION_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "vendor": {"type": ["string", "null"], "description": "Company that issued the invoice."},
        "invoice_number": {"type": ["string", "null"]},
        "invoice_date": {"type": ["string", "null"], "description": "ISO 8601, YYYY-MM-DD."},
        "due_date": {"type": ["string", "null"], "description": "ISO 8601, YYYY-MM-DD."},
        "currency": {"type": ["string", "null"], "description": "ISO 4217 code, e.g. QAR, USD."},
        "subtotal": {"type": ["number", "null"]},
        "tax": {"type": ["number", "null"]},
        "total": {"type": ["number", "null"]},
        "line_items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "quantity": {"type": "number"},
                    "unit_price": {"type": "number"},
                    "amount": {"type": "number"},
                },
                "required": ["description", "unit_price", "amount"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["vendor", "invoice_number", "total", "line_items"],
    "additionalProperties": False,
}
