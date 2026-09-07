"""Extraction, driven by a stub client so the suite needs no API key."""

from datetime import date
from decimal import Decimal

from conftest import StubClient

from invoice_extractor.extract import extract_invoice
from invoice_extractor.models import EXTRACTION_SCHEMA


def test_parses_a_structured_response(clean_payload):
    inv = extract_invoice("...", client=StubClient(clean_payload), source_file="invoice_clean.pdf")
    assert inv.vendor == "Gulf Office Supplies WLL"
    assert inv.invoice_date == date(2026, 8, 14)
    assert inv.total == Decimal("420.00")
    assert len(inv.line_items) == 3
    assert inv.source_file == "invoice_clean.pdf"


def test_money_survives_as_decimal_not_float(clean_payload):
    """0.1 + 0.2 problems do not belong in an accounts payable pipeline."""
    inv = extract_invoice("...", client=StubClient(clean_payload))
    assert isinstance(inv.total, Decimal)
    assert inv.line_item_total == Decimal("400.00")


def test_the_request_pins_the_json_schema(clean_payload):
    client = StubClient(clean_payload)
    extract_invoice("Invoice text here", client=client)
    sent = client.calls[0]
    assert sent["output_config"]["format"]["type"] == "json_schema"
    assert sent["output_config"]["format"]["schema"] is EXTRACTION_SCHEMA
    assert "Invoice text here" in sent["messages"][0]["content"]


def test_system_prompt_forbids_computing_totals(clean_payload):
    client = StubClient(clean_payload)
    extract_invoice("...", client=client)
    assert "never compute" in client.calls[0]["system"].lower()


def test_nulls_become_defaults_not_type_errors():
    payload = {"vendor": None, "invoice_number": None, "total": None, "line_items": []}
    inv = extract_invoice("...", client=StubClient(payload))
    assert inv.vendor is None and inv.line_items == []
