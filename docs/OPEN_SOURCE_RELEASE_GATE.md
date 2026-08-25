# Workflow Intelligence — Open-Source Release Gate

## Decision status

STATUS: NOT READY FOR PUBLIC RELEASE

Candidate community license: Apache-2.0.
This is a proposed license, not yet applied to the repository.

## Why Apache-2.0 is the current candidate

Apache-2.0 is OSI-approved and commercially permissive. It allows use, modification,
redistribution, and commercial distribution while preserving attribution and patent terms.
The model fits the planned Community / Cloud / Enterprise separation.

## Audit completed

- Repository currently has no LICENSE file.
- Direct runtime/build requirements are numpy, pandas, and pytest.
- NumPy 2.5.2 declares: BSD-3-Clause, 0BSD, MIT, Zlib, and CC0-1.0.
- pandas 3.0.5 declares BSD-3-Clause.
- pytest 9.1.1 declares MIT and depends on colorama, iniconfig, packaging, pluggy, and pygments.
- No third-party dependency is intentionally vendored into the repository based on the current requirements file.

## Remaining release gates

1. Enumerate all source files and generated assets intended for public release.
2. Identify copied or adapted third-party code, text, data, images, schemas, and model artifacts.
3. Record third-party notices and license obligations in a NOTICE/THIRD_PARTY_NOTICES file.
4. Confirm every dependency used by the Community Edition is compatible with the selected license.
5. Separate proprietary hosted/enterprise code and secrets from the Community Edition tree.
6. Review trademark and naming boundaries for Workflow Intelligence branding.
7. Add CONTRIBUTING.md, SECURITY.md, and a responsible disclosure route.
8. Add reproducible installation and release instructions.
9. Run the complete test suite from a clean environment.
10. Perform a final human/legal review before public distribution.

## Commercial boundary

Community Edition: source-available under the selected OSI-approved license.

Cloud: managed hosting, organization controls, persistent collaboration, managed model
routing, operations, backups, reliability, and support.

Enterprise: private deployment, advanced governance, identity integration, compliance,
enterprise support, dedicated infrastructure, and custom integrations.

Services: implementation, workflow transformation, integration, training, and support.

## Evidence boundary

Open-source adoption is not revenue evidence.
A real paid transaction remains the commercial validation milestone.

Synthetic users, internal simulations, public business registrations, and model-generated
responses must never be represented as customers, demand, revenue, or testimonials.
