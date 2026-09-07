"""End to end: PDFs in, CSV and exit code out."""

import csv

import invoice_extractor.cli as cli
from conftest import StubClient


def _patch(monkeypatch, payload):
    client = StubClient(payload)
    real = cli.extract_invoice
    monkeypatch.setattr(
        cli, "extract_invoice",
        lambda text, **kw: real(text, client=client, **kw),
    )


def test_clean_invoice_exits_zero_and_writes_a_row(tmp_path, monkeypatch, samples_dir, clean_payload):
    _patch(monkeypatch, clean_payload)
    out = tmp_path / "out.csv"
    code = cli.main([str(samples_dir / "invoice_clean.pdf"), "--csv", str(out)])
    assert code == 0
    rows = list(csv.DictReader(out.open()))
    assert len(rows) == 1
    assert rows[0]["invoice_number"] == "GOS-2026-0412"
    assert rows[0]["status"] == "OK"


def test_bad_arithmetic_exits_one_and_is_marked_for_review(tmp_path, monkeypatch, samples_dir, clean_payload):
    broken = dict(clean_payload, total=320.00)
    _patch(monkeypatch, broken)
    out = tmp_path / "out.csv"
    code = cli.main([str(samples_dir / "invoice_broken.pdf"), "--csv", str(out)])
    assert code == 1
    assert list(csv.DictReader(out.open()))[0]["status"] == "REVIEW"


def test_the_same_invoice_twice_is_reported(monkeypatch, samples_dir, clean_payload, capsys):
    _patch(monkeypatch, clean_payload)
    code = cli.main([str(samples_dir / "invoice_clean.pdf"), str(samples_dir / "invoice_broken.pdf")])
    assert code == 1
    assert "DUPLICATE_INVOICE" in capsys.readouterr().out


def test_a_scan_is_skipped_without_killing_the_batch(tmp_path, monkeypatch, samples_dir, clean_payload, capsys):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    blank = tmp_path / "scan.pdf"
    canvas.Canvas(str(blank), pagesize=A4).save()
    _patch(monkeypatch, clean_payload)
    out = tmp_path / "out.csv"
    code = cli.main([str(blank), str(samples_dir / "invoice_clean.pdf"), "--csv", str(out)])
    assert code == 1
    assert "SKIPPED" in capsys.readouterr().err
    assert len(list(csv.DictReader(out.open()))) == 1
