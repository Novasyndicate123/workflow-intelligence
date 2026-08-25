# Workflow Intelligence — Release Hardening Baseline

Release: 0.1.1
Status: hardened / staged / not published

## Positioning

Workflow Intelligence is the category. The Community Edition is positioned as an Economic Proof Layer for workflow automation decisions: evidence first, economic value second, automation third.

## Supply-chain controls

- GitHub Actions are pinned to full commit SHAs with version comments.
- CI uses least-privilege permissions.
- CodeQL is enabled for Python.
- Dependency Review is enabled on pull requests.
- OpenSSF Scorecard is enabled and publishes SARIF results.
- Dependabot is configured for GitHub Actions and pip requirements.
- SBOM generation is automated with SPDX output.
- Release artifacts are attested with GitHub artifact attestations.
- PyPI publication is isolated behind a dedicated Trusted Publishing workflow and environment.

## Packaging controls

- Source tree and binary release artifacts are separate.
- PEP 639 SPDX license metadata is declared.
- LICENSE and third-party notices are included in distribution archives.
- Source distribution and wheel build successfully from a clean checkout.
- Community test suite: 76/76 passing.

## Publication boundary

The staged release is not publicly published by this workflow. Final publication requires a real public repository, configured PyPI Trusted Publisher, legal/dependency review, and final operator authorization.
