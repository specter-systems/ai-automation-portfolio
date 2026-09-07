import json
from dataclasses import dataclass
from pathlib import Path

import pytest

SAMPLES = Path(__file__).resolve().parents[1] / "samples"


@dataclass
class _Block:
    text: str
    type: str = "text"


@dataclass
class _Response:
    content: list


class StubClient:
    """Stands in for anthropic.Anthropic. Records the call, returns fixed JSON."""

    def __init__(self, payload: dict):
        self._payload = payload
        self.calls: list[dict] = []
        self.messages = self

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return _Response(content=[_Block(text=json.dumps(self._payload))])


@pytest.fixture
def clean_payload() -> dict:
    return {
        "vendor": "Gulf Office Supplies WLL",
        "invoice_number": "GOS-2026-0412",
        "invoice_date": "2026-08-14",
        "due_date": "2026-09-13",
        "currency": "QAR",
        "subtotal": 400.00,
        "tax": 20.00,
        "total": 420.00,
        "line_items": [
            {"description": "A4 paper, 80gsm, box", "quantity": 4, "unit_price": 45.00, "amount": 180.00},
            {"description": "Whiteboard markers, pack of 12", "quantity": 3, "unit_price": 30.00, "amount": 90.00},
            {"description": "Desk organiser", "quantity": 2, "unit_price": 65.00, "amount": 130.00},
        ],
    }


@pytest.fixture
def samples_dir() -> Path:
    if not (SAMPLES / "invoice_clean.pdf").exists():
        import subprocess, sys
        subprocess.run([sys.executable, str(SAMPLES / "make_sample_invoices.py")], check=True)
    return SAMPLES
