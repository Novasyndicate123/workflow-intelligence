# Workflow Intelligence — Release Hardening Baseline

Release: 0.1.1
Status: hardened / published

## Positioning

Workflow Intelligence Community Edition is an Economic Proof Layer for workflow automation decisions: evidence first, economic value second, automation third.

## Supply-chain controls

- GitHub Actions are pinned to immutable commit SHAs with version comments.
- CI uses least-privilege permissions.
- CodeQL is enabled for Python.
- Dependency Review is enabled on pull requests.
- OpenSSF Scorecard publishes SARIF results.
- Dependabot monitors GitHub Actions and pip requirements.
- SBOM generation is automated with SPDX output.
- Release artifacts are attested with GitHub artifact attestations.
- PyPI publication uses Trusted Publishing behind the `pypi` environment.
- PyPI now consumes the exact wheel and sdist from an existing GitHub Release instead of rebuilding source.
- Release tags must match strict `vMAJOR.MINOR.PATCH`, and the downloaded artifact set must be exactly the expected wheel and sdist.
- Duplicate PyPI uploads remain fail-loud; `skip-existing` is not enabled.

## Packaging controls

- Source tree and binary release artifacts are separate.
- PEP 639 SPDX license metadata is declared.
- LICENSE and third-party notices are included in distribution archives.
- Source distribution and wheel build successfully from a clean Python 3.12 environment.

## Published v0.1.1 provenance

- GitHub Release v0.1.1 was published on 2026-08-25.
- GitHub Release wheel SHA-256: `a60ac9975ed505a8d706523997d9ba4ba660343aaf596462ce4845fca43514ae`.
- GitHub Release sdist SHA-256: `b7166537ef1df7f5f006a2cca5d5c4f52d0d56d78ae87830b21a90c82ae2d171`.
- PyPI 0.1.1 is published and unyanked.
- PyPI wheel SHA-256: `64894e6cfec27a837236d5e49b4c8e3dc568da26d76202189e6a4d8e3ff3d828`.
- PyPI sdist SHA-256: `f8d988778a16bc967fb0186409ec2eac642abbe70e346ee10f1290e42bd468be`.
- v0.1.1 predates canonical-artifact publishing, so GitHub Release and PyPI archives were built independently and have different archive hashes.
- A payload comparison found the wheel members and sdist members content-equivalent despite those archive-level hash differences.

## Publication boundary

GitHub Release is now the canonical artifact source. Publishing a release creates and attests the distributions; the PyPI workflow downloads those exact assets and validates their release identity before Trusted Publishing. Manual recovery requires an explicit existing release tag.
