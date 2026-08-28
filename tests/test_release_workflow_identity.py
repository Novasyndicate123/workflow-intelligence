"""Contract tests for fail-closed GitHub Release identity."""

from pathlib import Path
import re


WORKFLOW_PATH = (
    Path(__file__).resolve().parents[1] / ".github" / "workflows" / "release.yml"
)
WORKFLOW = WORKFLOW_PATH.read_text(encoding="utf-8")


def _block(text: str, key: str) -> str:
    lines = text.splitlines()
    match = re.search(rf"^(?P<i> *){re.escape(key)}:\s*$", text, re.MULTILINE)
    assert match, f"missing {key!r} mapping"
    start = text[: match.start()].count("\n") + 1
    indent = len(match.group("i"))
    out: list[str] = []
    for line in lines[start:]:
        if line.strip() and len(line) - len(line.lstrip()) <= indent:
            break
        out.append(line)
    return "\n".join(out)


def test_manual_release_requires_tag_input() -> None:
    dispatch = _block(WORKFLOW, "workflow_dispatch")
    inputs = _block(dispatch, "inputs")
    tag = _block(inputs, "tag")
    assert re.search(r"(?m)^\s*required:\s*true\s*$", tag)


def test_release_tag_is_validated_before_checkout() -> None:
    validation = re.search(r"\^v\[0-9\]\+\\\.\[0-9\]\+\\\.\[0-9\]\+\$", WORKFLOW)
    checkout = WORKFLOW.find("uses: actions/checkout@")
    assert validation, "release tag must use strict vMAJOR.MINOR.PATCH validation"
    assert validation.start() < checkout, "tag validation must happen before checkout"


def test_checkout_targets_selected_release_tag() -> None:
    assert re.search(
        r"uses:\s*actions/checkout@[^\n]+\n(?:.*\n){0,5}\s*ref:\s*\$\{\{\s*env\.RELEASE_TAG\s*\}\}",
        WORKFLOW,
    )


def test_checked_out_commit_must_equal_tag_commit() -> None:
    assert "git rev-list -n 1 \"$RELEASE_TAG\"" in WORKFLOW
    assert "git rev-parse HEAD" in WORKFLOW
    assert re.search(r"HEAD_COMMIT.*TAG_COMMIT|TAG_COMMIT.*HEAD_COMMIT", WORKFLOW, re.DOTALL)


def test_project_version_must_match_release_tag() -> None:
    assert "tomllib" in WORKFLOW
    assert "pyproject.toml" in WORKFLOW
    assert "${RELEASE_TAG#v}" in WORKFLOW
    assert re.search(
        r"PROJECT_VERSION.*EXPECTED_VERSION|EXPECTED_VERSION.*PROJECT_VERSION",
        WORKFLOW,
        re.DOTALL,
    )


def test_github_release_creation_verifies_existing_tag() -> None:
    command = re.sub(r"\\\r?\n\s*", " ", WORKFLOW)
    assert re.search(
        r"gh\s+release\s+create\s+\"?\$RELEASE_TAG\"?.*--verify-tag",
        command,
        re.DOTALL,
    )
