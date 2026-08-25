# Workflow Intelligence — Community Edition Scope

## Release posture

The Community Edition is intended to contain the reusable Workflow Intelligence engine, deterministic evidence/decision primitives, local assessment tooling, tests, and documentation that can be redistributed under an OSI-approved license after final legal review.

## Included candidate surface

- `core/` reusable workflow, evidence, opportunity, validation, and acquisition components that do not depend on private infrastructure.
- `tests/` tests required to reproduce the Community Edition behavior.
- Public-facing assessment/application code required for local use.
- Documentation describing installation, architecture, evidence rules, and reproducible experiments.

## Excluded from the initial public release

- `.venv*`, `.aider*`, `.qwen/`, model caches, generated logs, screenshots, temporary work products, and laboratory output.
- Customer records, evidence ledgers, payment/revenue records, private research data, and local secrets.
- Machine-specific operator scripts that hard-code `the local laboratory workspace` or other local deployment paths.
- Local Qwen runtime workers and orchestration wrappers unless they are refactored into a portable, documented integration.
- Hosted-service infrastructure, enterprise governance services, private deployment automation, and commercial extensions.

## Licensing gate

Candidate community license: Apache-2.0.

This is a candidate, not a final legal clearance. Before publication, perform a complete dependency, source, asset, trademark, contributor, and generated-content review and have the final release terms reviewed by appropriate legal counsel.

## Commercial boundary

The open-source core remains genuinely usable and self-hostable. Commercial value is expected to come from hosted operations, managed AI/model routing, organizational administration, enterprise governance, private deployment, support, implementation, and other separately defined services.

## Release rule

Do not publish the laboratory directory wholesale. Create a clean release tree from this scope and verify that every published file has a known origin and licensing basis.
