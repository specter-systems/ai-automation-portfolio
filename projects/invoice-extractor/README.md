# Invoice extractor

PDF invoices in, validated structured data out. Claude reads the page; plain Python decides
whether a human needs to look at it.

```
$ invoice-extract samples/*.pdf --csv out.csv --approval-threshold 5000
invoice_clean.pdf: clean
invoice_broken.pdf:
  [ERROR] LINE_MATH: 'Whiteboard markers, pack of 12': 3 x 25.00 = 75.00, but line reads 90.00.
  [ERROR] SUBTOTAL_MISMATCH: Line items sum to 400.00, subtotal reads 500.00.
  [ERROR] TOTAL_MISMATCH: Subtotal plus tax is 420.00, total reads 320.00.

Wrote 2 row(s) to out.csv
$ echo $?
1
```

## The idea

The interesting part of this is not the model call. Extracting fields from an invoice is a
solved problem and takes about twenty lines.

The part that decides whether you can actually put it in front of an accounts payable
process is what happens *after*: a language model reading a document is very good and
occasionally confidently wrong, and "confidently wrong" applied to a payment run is
expensive. So nothing the model returns is trusted on arithmetic. The system prompt tells it
to copy figures exactly and never compute a total that is not printed on the page, and then
[`checks.py`](invoice_extractor/checks.py) re-does every sum in Python.

That split — model for reading, deterministic code for judgement — is what makes the output
safe to route automatically. Findings carry a severity, and severity is the routing decision:

| Severity | Meaning |
| --- | --- |
| `ERROR` | Do not post. A person needs to see this. Exit code 1. |
| `WARN` | Post it, but flag for review. |

## What it catches

- Lines where quantity × unit price does not equal the amount shown
- Line items that do not sum to the stated subtotal
- Subtotal plus tax that does not equal the stated total
- Missing vendor, invoice number, date or total
- Invoices dated in the future, or due before they were issued
- Negative quantities and prices
- Totals over an approval threshold you set
- **The same invoice number from the same vendor twice in one batch** — the duplicate that
  turns into a double payment

Rounding is tolerated to 0.01, because real invoices round and a false alarm on every file
is the fastest way to get an automation switched off.

## Try it

```bash
pip install -e ".[dev]"
python samples/make_sample_invoices.py     # writes a clean invoice and a deliberately broken one
export ANTHROPIC_API_KEY=sk-...
invoice-extract samples/invoice_broken.pdf
```

`samples/invoice_broken.pdf` has a line that does not multiply out and a total that is 100
short, so you can watch the checks fire on a real file rather than taking my word for it.

## Tests

```bash
pytest -q      # 28 tests, no API key needed
```

The suite injects a stub client, so the whole pipeline — PDF parsing, extraction, checks,
CSV, exit codes — runs offline in CI. Money is `Decimal` throughout and there is a test that
keeps it that way; `float` in an accounts payable pipeline is how 0.1 + 0.2 becomes a
reconciliation ticket.

## Notes

- Scanned, image-only PDFs raise `NoTextLayer` rather than returning an empty string. Handing
  the model nothing is how you get an invented invoice. Run OCR first.
- Model defaults to `claude-haiku-4-5-20251001`; override with `INVOICE_MODEL`. Extraction is
  high volume and low reasoning, so the cheap fast model is the right call.
- Uses the Messages API structured-output format, so the response conforms to the JSON schema
  instead of being salvaged from prose with a regex.
- One bad file does not kill the batch — it is reported and the run continues.

## What this is not

A finished accounts payable product. It is one workflow taken end to end so you can see how I
build: typed boundaries, deterministic validation around the probabilistic bit, tests that run
without credentials, and a non-zero exit code when a human needs to intervene.

---

Part of the [Specter Systems](https://specter-systems.github.io) portfolio.
