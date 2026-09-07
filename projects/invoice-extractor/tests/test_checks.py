"""The arithmetic the model is not allowed to be trusted on."""

from datetime import date
from decimal import Decimal

import pytest

from invoice_extractor.checks import check_invoice, find_duplicates
from invoice_extractor.models import Invoice, LineItem

TODAY = date(2026, 9, 7)


def make(**kw) -> Invoice:
    base = dict(
        vendor="Gulf Office Supplies WLL",
        invoice_number="GOS-2026-0412",
        invoice_date=date(2026, 8, 14),
        subtotal=Decimal("400.00"),
        tax=Decimal("20.00"),
        total=Decimal("420.00"),
        line_items=[
            LineItem(description="paper", quantity=Decimal("4"), unit_price=Decimal("45.00"), amount=Decimal("180.00")),
            LineItem(description="markers", quantity=Decimal("3"), unit_price=Decimal("30.00"), amount=Decimal("90.00")),
            LineItem(description="organiser", quantity=Decimal("2"), unit_price=Decimal("65.00"), amount=Decimal("130.00")),
        ],
    )
    base.update(kw)
    return Invoice(**base)


def codes(inv, **kw):
    return {f.code for f in check_invoice(inv, today=TODAY, **kw)}


def test_a_correct_invoice_is_clean():
    assert check_invoice(make(), today=TODAY) == []


def test_line_that_does_not_multiply_out_is_caught():
    inv = make(line_items=[LineItem(description="markers", quantity=Decimal("3"),
                                    unit_price=Decimal("25.00"), amount=Decimal("90.00"))])
    assert "LINE_MATH" in codes(inv)


def test_total_that_does_not_match_subtotal_plus_tax_is_caught():
    assert "TOTAL_MISMATCH" in codes(make(total=Decimal("320.00")))


def test_subtotal_that_does_not_match_line_items_is_caught():
    assert "SUBTOTAL_MISMATCH" in codes(make(subtotal=Decimal("500.00")))


def test_one_riyal_of_rounding_is_tolerated():
    """Real invoices round. 0.01 of drift is not a finding."""
    assert check_invoice(make(subtotal=Decimal("400.01"), total=Decimal("420.01")), today=TODAY) == []


@pytest.mark.parametrize("field", ["vendor", "invoice_number", "invoice_date", "total"])
def test_missing_required_fields_are_errors(field):
    assert "MISSING_FIELD" in codes(make(**{field: None}))


def test_future_dated_invoice_is_an_error():
    assert "FUTURE_DATE" in codes(make(invoice_date=date(2027, 1, 1)))


def test_due_before_issue_is_a_warning():
    inv = make(due_date=date(2026, 8, 1))
    assert any(f.code == "DUE_BEFORE_ISSUE" and f.severity == "WARN"
               for f in check_invoice(inv, today=TODAY))


def test_negative_price_is_an_error():
    inv = make(line_items=[LineItem(description="refund", quantity=Decimal("1"),
                                    unit_price=Decimal("-10.00"), amount=Decimal("-10.00"))])
    assert "NEGATIVE_VALUE" in codes(inv)


def test_threshold_flags_large_invoices_for_approval():
    assert "NEEDS_APPROVAL" in codes(make(), approval_threshold=Decimal("100"))
    assert "NEEDS_APPROVAL" not in codes(make(), approval_threshold=Decimal("10000"))


def test_duplicate_invoice_number_from_same_vendor_is_caught():
    """The double-payment case that costs real money."""
    a = make(source_file="a.pdf")
    b = make(source_file="b.pdf")
    assert [f.code for f in find_duplicates([a, b])] == ["DUPLICATE_INVOICE"]


def test_same_number_from_a_different_vendor_is_not_a_duplicate():
    a = make(source_file="a.pdf")
    b = make(source_file="b.pdf", vendor="Someone Else Trading")
    assert find_duplicates([a, b]) == []


def test_blank_invoice_numbers_are_not_treated_as_duplicates():
    a = make(invoice_number=None, source_file="a.pdf")
    b = make(invoice_number=None, source_file="b.pdf")
    assert find_duplicates([a, b]) == []
