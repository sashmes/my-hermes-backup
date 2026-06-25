---
name: local-business-compliance
description: "Conduct systematic research on state and local business regulations, corporate structure trade-offs, and compliance frameworks for launching micro-enterprises and local service businesses."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [research, business, legal, compliance, licensing, startup]
    homepage: https://github.com/NousResearch/hermes-agent
    related_skills: [logseq-vault, ocr-and-documents]
---

# Local Business Compliance & Launch Research

This skill provides a standardized framework for analyzing, compiling, and reporting local business regulations, corporate structures, state/federal licensing requirements, tax implications, and insurance needs for launching small businesses or micro-enterprises (e.g., handymen, local service providers, retail, or home-based businesses).

## Methodology

When a user requests research or assistance starting a local business in a specific city/state:

### 1. Identify the Jurisdictional Layers
Always break down compliance requirements into three distinct layers:
*   **Federal Level:** IRS registrations (EIN), federal licenses (if applicable to regulated sectors like transport or agriculture).
*   **State Level:** Professional licensing boards (e.g., CSLB in CA), Secretary of State filings (LLC/Corporation registration), state franchise taxes, state-mandated insurances (Workers' Comp, disability).
*   **Municipal/County Level:** City business licenses/tax registration, County Fictitious Business Name (FBN/DBA) filings, Zoning/Home Occupation permits (for residential-based operations), local health/fire/environmental checks.

### 2. Corporate Structure Trade-off Analysis
Analyze the trade-offs of the most common legal structures for a lean micro-enterprise:
*   **Sole Proprietorship:**
    *   *Pros:* Low cost, no complex state formation, pass-through taxes (Schedule C).
    *   *Cons:* Unlimited personal liability.
*   **LLC (Limited Liability Company):**
    *   *Pros:* Liability shield protecting personal assets.
    *   *Cons:* State filing fees, annual minimum franchise taxes (e.g., California's $800 minimum tax), additional state-mandated bonds or high-coverage general liability insurance.

### 3. Professional Licensing Thresholds (The "Handyman" Trap)
Many states have strict monetary thresholds or trade limits for unlicensed contractors (often called handypeople):
*   Verify the exact current dollar limit (always double-check since laws change, e.g., California's threshold doubled to $1,000 under AB 2622 on Jan 1, 2025).
*   Identify whether materials and labor are combined in the limit.
*   Document advertising disclaimers, employment limitations (unlicensed often means solo-only), permit rules, and penalty structures.

### 4. Risk Mitigation & Insurance Audit
Delineate recommended insurance lines:
*   **General Liability:** $1M/$2M standard limits.
*   **Commercial Auto:** For transport of tools/goods.
*   **Workers' Comp:** Mandatory if the entity has employees, and increasingly mandated for certain hazardous specialty trades regardless of employees.

---

## Linked References & Knowledge Bases

This skill maintains specific local/state dossiers under the `references/` directory. Consult them when handling tasks in those jurisdictions:

*   [`references/california-handyman-long-beach.md`](references/california-handyman-long-beach.md) - Deep regulatory and licensing dossier for starting an unlicensed/licensed handyman business in Long Beach, California (fully updated for the 2025/2026 AB 2622 framework).
