# Workflow Intelligence Community Edition — Release Status

Status: HARDENED / PUBLISHED
Release: v0.1.1
License: Apache-2.0
Release form: public Community Edition + sdist/wheel

## Current verification

- Community test suite: 83 tests expected after this documentation guard is merged.
- Clean Python 3.12 verification environment: PASS.
- Source distribution + wheel build: PASS.
- GitHub Actions workflow syntax/static validation: PASS.
- CI matrix: Python 3.12 and 3.13.
- Security workflows: CodeQL, Dependency Review, OpenSSF Scorecard, and SBOM.
- Release artifacts are attested before GitHub Release creation.
- PyPI uses Trusted Publishing and now consumes canonical GitHub Release artifacts.

## Published artifacts

GitHub Release v0.1.1:

- wheel SHA-256: `a60ac9975ed505a8d706523997d9ba4ba660343aaf596462ce4845fca43514ae`
- sdist SHA-256: `b7166537ef1df7f5f006a2cca5d5c4f52d0d56d78ae87830b21a90c82ae2d171`

PyPI 0.1.1 (published, unyanked):

- wheel SHA-256: `64894e6cfec27a837236d5e49b4c8e3dc568da26d76202189e6a4d8e3ff3d828`
- sdist SHA-256: `f8d988778a16bc967fb0186409ec2eac642abbe70e346ee10f1290e42bd468be`

## Provenance note

v0.1.1 was published before the canonical-artifact PyPI workflow existed. GitHub Release and PyPI therefore contain independently built archives with different archive hashes. A member-by-member comparison found no payload differences across the wheel contents or sdist contents.

Future releases use GitHub Release as the canonical byte source for PyPI publication. The PyPI workflow downloads the existing release assets, validates a strict semantic release tag and the exact expected wheel/sdist names, prints hashes, and fails loudly on duplicate uploads.

## Commercial boundary

Community Edition remains usable and self-hostable. Paid value is expected from hosted operations, managed AI, organizational administration, governance, private deployment, support, implementation, and commercial integrations.

## Publication state

The repository is public, GitHub Release v0.1.1 exists, and `workflow-intelligence` 0.1.1 is live on PyPI. Publication controls remain fail-closed around artifact identity and Trusted Publishing.
