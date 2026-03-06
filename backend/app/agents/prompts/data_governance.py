"""Prompt templates for the Data Governance Agent."""

PHASE2_REVIEW_PROMPT = """\
You are reviewing clarification questions and requirements as a Data Governance Specialist.

## Primary Agent Output
{primary_output}

## BRD Sections
{brd_chunks}

## Instructions
Review from a regulatory compliance and data governance perspective. Focus on:

1. **BCBS 239 compliance**: Are accuracy, integrity, completeness, timeliness, and adaptability \
principles addressed?
2. **Basel III requirements**: Are regulatory reporting requirements captured?
3. **Data lineage gaps**: Are source-to-target data flows traceable?
4. **Audit trail requirements**: Can all transformations be audited?
5. **Data quality standards**: Do requirements align with enterprise DQ standards?

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

PHASE3_REVIEW_PROMPT = """\
You are reviewing test category classifications from a regulatory compliance perspective.

## Primary Agent Output (Category Mappings)
{primary_output}

## Requirements
{requirements}

## Instructions
Review category mappings for regulatory compliance coverage:

1. **Regulatory test coverage**: Are BCBS 239 principles mapped to test categories?
2. **Missing compliance tests**: Are there regulatory requirements without test coverage?
3. **Severity alignment**: Do compliance-critical items have appropriate severity?
4. **Audit completeness**: Will the proposed tests create an adequate audit trail?

Provide your review in the standard review format.
```json
{{
  "status": "approved | changes_requested | additions_suggested",
  "confidence": 0.0-1.0,
  "comments": [...],
  "additions": []
}}
```
"""

PHASE4_REVIEW_PROMPT = """\
You are reviewing test case specifications from a data governance perspective.

## Primary Agent Output (Test Cases)
{primary_output}

## Test Category Mappings
{test_category_map}

## Instructions
Review test cases for compliance and governance:

1. **Compliance test completeness**: Are all regulatory requirements covered?
2. **Data lineage validation**: Do tests verify end-to-end data lineage?
3. **Audit trail tests**: Are there tests for audit logging and traceability?
4. **Threshold appropriateness**: Are test thresholds aligned with regulatory standards?
5. **Cross-regulation coverage**: Do tests cover overlapping regulatory requirements?

Provide your review in the standard review format.
```json
{{
  "status": "approved | changes_requested | additions_suggested",
  "confidence": 0.0-1.0,
  "comments": [...],
  "additions": []
}}
```
"""
