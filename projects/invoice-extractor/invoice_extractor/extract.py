"""Turn invoice text into a validated `Invoice`.

Uses the Messages API structured-output format, so the model returns JSON that
already conforms to `EXTRACTION_SCHEMA` instead of prose we have to salvage
with a regex. Pydantic then re-validates, because a schema-shaped response is
not the same thing as a correct one.

The client is injected rather than constructed here — that is what lets the
test suite run with no API key and no network.
"""

from __future__ import annotations

import json
import os
from typing import Any, Protocol

from .models import EXTRACTION_SCHEMA, Invoice

DEFAULT_MODEL = os.environ.get("INVOICE_MODEL", "claude-haiku-4-5-20251001")

SYSTEM = (
    "You read invoices and return structured data. Copy values exactly as "
    "printed; never compute, correct or infer a total that is not on the page. "
    "If a field is absent, return null for it rather than guessing."
)


class MessagesClient(Protocol):
    """The slice of the Anthropic client this module actually uses."""

    @property
    def messages(self) -> Any: ...


def build_client() -> MessagesClient:
    from anthropic import Anthropic

    return Anthropic()  # reads ANTHROPIC_API_KEY


def extract_invoice(
    text: str,
    *,
    client: MessagesClient | None = None,
    model: str = DEFAULT_MODEL,
    source_file: str | None = None,
) -> Invoice:
    client = client or build_client()
    response = client.messages.create(
        model=model,
        max_tokens=2048,
        system=SYSTEM,
        output_config={"format": {"type": "json_schema", "schema": EXTRACTION_SCHEMA}},
        messages=[{"role": "user", "content": f"Invoice text:\n\n{text}"}],
    )
    payload = json.loads(_text_of(response))
    invoice = Invoice.model_validate(_drop_nulls(payload))
    invoice.source_file = source_file
    return invoice


def _text_of(response: Any) -> str:
    """Concatenate the text blocks of a Messages response."""
    parts = [b.text for b in response.content if getattr(b, "type", None) == "text"]
    if not parts:
        raise ValueError("Model returned no text content.")
    return "".join(parts)


def _drop_nulls(payload: dict) -> dict:
    """Let Pydantic defaults apply instead of forcing None into typed fields."""
    out = {k: v for k, v in payload.items() if v is not None}
    items = out.get("line_items")
    if isinstance(items, list):
        out["line_items"] = [{k: v for k, v in li.items() if v is not None} for li in items]
    return out
