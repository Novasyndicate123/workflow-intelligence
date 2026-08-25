# Workflow Intelligence — Economic Proof Layer

Workflow Intelligence is an open-source evidence and decision layer for discovering work worth investigating, proving whether an automation opportunity is economically meaningful, and preserving the evidence behind that decision.

## The problem

Most automation programs begin by asking what can be automated. This project starts with a harder question:

> **What work is worth automating, and what evidence proves it?**

The Community Edition helps teams move through:

**Observe → Evidence → Opportunity → Control → Proof → Outcome**

## What the Community Edition provides

- Local/self-hosted workflow assessment primitives
- Evidence → normalization → confidence → provenance → decision patterns
- Economic opportunity and prioritization components
- Bounded experiment planning and review gates
- Acquisition/review evidence structures
- Reproducible tests and source documentation

## What it is not

This is not positioned as another general-purpose workflow automation engine. It is designed to sit above automation platforms and help determine **which work should be automated, why, and whether the change produced measurable value**.

## Commercial path

The open-source core is intentionally usable on its own.

Commercial value is expected around it through hosted operations, managed AI/model routing, organizational administration, enterprise governance, private deployment, support, implementation, and commercial integrations.

See `COMMERCIAL.md` for the current boundary.

## Evidence rules

- Never fabricate validation, users, revenue, or outcomes.
- Synthetic evidence cannot satisfy the human-validation gate.
- Public business records are prospects, not customer intent.
- Revenue claims require actual payment evidence.
- Human approval remains required for external execution.

## Development

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m build
```

The repository CI tests Python 3.12 and 3.13, runs dependency review and CodeQL, and produces versioned release artifacts with provenance/attestation workflows.

## Release status

`v0.1.0` is the verified Community Edition release candidate. Public publication is intentionally separated from the private laboratory repository.

The current release gate requires final legal/dependency attribution review plus creation of the public repository and publication destination.
