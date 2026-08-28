"""Contract tests for publishing canonical GitHub Release artifacts to PyPI."""

from pathlib import Path
import re


WORKFLOW_PATH = (
    Path(__file__).resolve().parents[1] / ".github" / "workflows" / "publish-pypi.yml"
)
WORKFLOW = WORKFLOW_PATH.read_text(encoding="utf-8")


def _active_text(text: str) -> str:
    """Discard full-line comments while retaining shell parameter expansion."""
    return "\n".join(
        line for line in text.splitlines() if not line.lstrip().startswith("#")
    )


def _mapping_block(text: str, key: str) -> str:
    """Return the indented YAML mapping beneath a simple key."""
    lines = text.splitlines()
    key_pattern = re.compile(
        rf"^(?P<indent> *){re.escape(key)}:\s*(?:#.*)?$", re.MULTILINE
    )
    match = key_pattern.search(text)
    if match is None:
        return ""

    key_line = text[: match.start()].count("\n")
    key_indent = len(match.group("indent"))
    block = []
    for line in lines[key_line + 1 :]:
        if not line.strip():
            block.append(line)
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent <= key_indent:
            break
        block.append(line)
    return "\n".join(block)


def _step_containing(text: str, marker: str) -> str:
    """Return the list item containing marker, independent of its display name."""
    lines = text.splitlines()
    marker_line = next(i for i, line in enumerate(lines) if marker in line)
    start = marker_line
    item_indent = None
    while start >= 0:
        item = re.match(r"^(?P<indent> *)-\s+", lines[start])
        if item:
            item_indent = len(item.group("indent"))
            break
        start -= 1
    assert item_indent is not None, f"{marker!r} is not contained in a workflow step"

    end = len(lines)
    for index in range(start + 1, len(lines)):
        item = re.match(r"^(?P<indent> *)-\s+", lines[index])
        if item and len(item.group("indent")) == item_indent:
            end = index
            break
    return "\n".join(lines[start:end])


def _strict_tag_patterns(text: str) -> list[re.Pattern[str]]:
    patterns = []
    for candidate in re.findall(r"\^v[^\s'\"`]+\$", text):
        python_pattern = candidate.replace("[[:digit:]]", "[0-9]")
        try:
            patterns.append(re.compile(python_pattern))
        except re.error:
            continue
    return patterns


def test_publish_uses_existing_release_artifacts_without_rebuilding() -> None:
    active = _active_text(WORKFLOW)

    assert not re.search(r"\bpython\s+-m\s+build\b", active, re.IGNORECASE), (
        "PyPI publishing must consume the GitHub Release artifacts, not rebuild them"
    )
    assert not re.search(
        r"\buses:\s*actions/(?:checkout|setup-python)@", active, re.IGNORECASE
    ), "the publishing job must not check out source or set up a build environment"

    command_text = re.sub(r"\\\r?\n\s*", " ", active)
    download = re.search(
        r"\bgh\s+release\s+download\s+(?!--)(?P<tag>\S+)",
        command_text,
        re.IGNORECASE,
    )
    assert download, "the selected GitHub Release tag must be passed to gh release download"
    assert "github.event.release.tag_name" in active
    assert re.search(r"(?:github\.event\.)?inputs\.tag\b", active)
    assert re.search(
        r"--pattern(?:=|\s+)[\"']workflow_intelligence-\*\.whl[\"']", active
    )
    assert re.search(
        r"--pattern(?:=|\s+)[\"']workflow_intelligence-\*\.tar\.gz[\"']",
        active,
    )


def test_manual_publish_requires_an_existing_release_tag() -> None:
    dispatch = _mapping_block(WORKFLOW, "workflow_dispatch")
    inputs = _mapping_block(dispatch, "inputs")
    tag = _mapping_block(inputs, "tag")

    assert tag, "workflow_dispatch must declare a tag input"
    assert re.search(r"(?m)^\s*required:\s*true\s*(?:#.*)?$", tag), (
        "the workflow_dispatch tag input must be required"
    )


def test_selected_tag_and_downloaded_artifact_set_are_exact() -> None:
    active = _active_text(WORKFLOW)
    tag_patterns = _strict_tag_patterns(active)
    accepted = ("v0.1.2", "v12.345.6789")
    rejected = ("1.2.3", "v1.2", "v1.2.3.4", "v1.2.3-rc1", "v1.2.x")
    assert any(
        all(pattern.fullmatch(tag) for tag in accepted)
        and not any(pattern.fullmatch(tag) for tag in rejected)
        for pattern in tag_patterns
    ), "the selected release tag must be validated as strict vMAJOR.MINOR.PATCH"

    version_ref = r"(?:\$\{[A-Za-z_][A-Za-z0-9_]*(?:(?::1)|#v)?\}|\$[A-Za-z_][A-Za-z0-9_]*)"
    wheel = re.search(
        rf"workflow_intelligence-(?P<version>{version_ref})-py3-none-any\.whl", active
    )
    sdist = re.search(
        rf"workflow_intelligence-(?P<version>{version_ref})\.tar\.gz", active
    )
    assert wheel and sdist, (
        "validation must name the exact wheel and sdist expected for the release version"
    )
    assert wheel.group("version") == sdist.group("version"), (
        "the expected wheel and sdist must be derived from the same release version"
    )
    assert re.search(r"(?:-eq|-ne|==|!=)\s*[\"']?2\b", active), (
        "validation must enforce that exactly two distribution artifacts were downloaded"
    )
    assert len(re.findall(r"!?\s+-f\s+", active)) >= 2, (
        "validation must verify that the expected distribution files exist"
    )


def test_pypi_action_publishes_dist_and_prints_hashes() -> None:
    step = _step_containing(WORKFLOW, "pypa/gh-action-pypi-publish@")
    assert re.search(r"(?m)^\s*packages-dir:\s*[\"']?dist/[\"']?\s*$", step)
    assert re.search(r"(?m)^\s*print-hash:\s*true\s*$", step, re.IGNORECASE)


def test_pypi_duplicates_remain_fail_loud() -> None:
    step = _step_containing(WORKFLOW, "pypa/gh-action-pypi-publish@")
    assert not re.search(
        r"(?m)^\s*skip-existing:\s*true\s*$", step, re.IGNORECASE
    ), "skip-existing would hide duplicate or provenance errors in production publishing"
