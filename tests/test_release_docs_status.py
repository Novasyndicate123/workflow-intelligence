"""Regression guards for public release-status documentation."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HARDENING = (ROOT / "RELEASE_HARDENING.md").read_text(encoding="utf-8")
STATUS = (ROOT / "RELEASE_STATUS.md").read_text(encoding="utf-8")


def test_release_docs_have_no_literal_powershell_newline_escapes() -> None:
    for text in (HARDENING, STATUS):
        assert "`r`n" not in text


def test_v011_release_docs_reflect_publication_truth() -> None:
    combined = f"{HARDENING}\n{STATUS}"
    for stale_claim in ("NOT PUBLISHED", "not published", "not been published"):
        assert stale_claim not in combined
    assert "Status: HARDENED / PUBLISHED" in STATUS
    assert "Release: v0.1.1" in STATUS
    assert "PyPI" in combined
    assert "GitHub Release" in combined


def test_current_release_status_does_not_hardcode_test_count() -> None:
    import re

    assert not re.search(r"Community test suite:\s*\d+", STATUS)
    assert "CI" in STATUS
