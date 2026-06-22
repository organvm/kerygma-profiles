# DISCOVERY — organvm/kerygma-profiles

**Verdict:** VALUE FOUND → promote into the ranked tier.
**Date:** 2026-06-22 (auto-discovery)

## Value Thesis

`kerygma-profiles` is the multi-tenant social-identity control plane for the ORGANVM distribution layer. It operates as the central registry answering exactly which accounts, tone, hashtags, credentials, and content cadence apply when publishing on behalf of any given repository in the estate. Its latent value is immense leverage through multi-tenancy: by centralizing these social identity configurations as declarative YAML profiles, a single automated publishing pipeline (such as ORGAN-IV) can seamlessly distribute content for over 23 distinct products without any per-product code or configuration sprawl. It's a live, tested, and highly reusable infrastructure asset that transforms fragmented configuration-by-convention into a unified, machine-readable identity contract.

## Single Best Concrete First Task

**Harden the registry into a validated contract: ship a JSON schema (`profiles/profile.schema.json`) and wire `kerygma-profiles validate` into CI.** By adding a structural schema check for all profiles and enforcing it in the CI pipeline as a required gate, we prevent malformed or incomplete profiles from ever reaching downstream consumers. This task directly converts the existing `produces → ORGAN-IV` edge into a guaranteed, machine-checked interface, establishing the trust needed for all other distribution tools to depend on this repository.
