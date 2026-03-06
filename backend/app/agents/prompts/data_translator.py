"""Prompt templates for the Data Translator Agent."""

PHASE2_REVIEW_PROMPT = """\
You are reviewing clarification questions and requirements as a Data Translation Specialist.

## Primary Agent Output
{primary_output}

## BRD Sections
{brd_chunks}

## Instructions
Review the Business Agent's clarification questions and extracted requirements. Focus on:

1. **Technical ambiguities**: Are there data-related ambiguities the Business Agent missed?
2. **Translation gaps**: Can each business rule be cleanly mapped to a test category?
3. **Missing data contexts**: Are source systems, data formats, and transformation logic clear?
4. **Category readiness**: Will these requirements be classifiable into the 7 operational test categories?

Provide your review as:
```json
{{
  "status": "approved | changes_requested | additions_suggested",
  "confidence": 0.0-1.0,
  "comments": [
    {{
      "target_id": "requirement or clarification reference",
      "severity": "critical | suggestion | info",
      "comment": "...",
      "proposed_change": "..."
    }}
  ],
  "additions": []
}}
```
"""

PHASE3_CLASSIFY_PROMPT = """\
You are mapping clarified requirements to operational test categories.

## Requirements
{requirements}

## BRD Sections
{brd_chunks}

## User Feedback (if revision requested)
{user_feedback}

## Instructions
Map each requirement to one or more of the 7 operational test categories:

1. **schema_contract** — Schema validation: data types, required columns, enum checks, regex patterns
2. **data_quality** — General DQ: NOT NULL, uniqueness, row counts, referential integrity, cross-source matching
3. **business_logic** — Business rule validation: range checks, calculation correctness, conditional logic
4. **metrics** — KPI and aggregation validation: metric calculations, thresholds, trend anomalies
5. **regulatory** — Compliance checks: BCBS 239, Basel III, audit trail completeness, reporting mandates
6. **freshness** — Timeliness: SLA compliance, data arrival latency, staleness detection
7. **consistency** — Cross-domain consistency: data agrees across domain boundaries, master data alignment

For each mapping, also infer the **business domain** from the requirement context \
(e.g., risk, customer, finance, hr, wholesale_sme, cross_domain).

For each mapping, provide:
- **requirement_id**: Reference to the requirement
- **test_category**: One of the 7 categories above
- **sub_category**: More specific classification
- **rationale**: Why this category applies
- **confidence**: 0.0-1.0 confidence score
- **pipeline_layer**: bronze | silver | gold
- **tool_suggestion**: dbt_test | great_expectations | custom_sql | dbt_macro
- **domain**: Inferred business domain

## Output Format
```json
[
  {{
    "requirement_id": "REQ-001",
    "test_category": "schema_contract",
    "sub_category": "required_columns",
    "rationale": "...",
    "confidence": 0.85,
    "pipeline_layer": "bronze",
    "tool_suggestion": "dbt_test",
    "domain": "customer"
  }}
]
```
"""
