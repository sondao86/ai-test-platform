"""Prompt templates for the Data Architect Agent."""

PHASE1_REVIEW_PROMPT = """\
You are reviewing parsed BRD sections as a Data Architect.

## Primary Agent Output (BRD Chunks)
{primary_output}

## Raw Document
{raw_document}

## Instructions
Review the Business Agent's BRD parsing for structural and architectural completeness:

1. **Structural completeness**: Are all sections captured? Any content missed?
2. **Cross-references**: Are inter-section dependencies correctly identified?
3. **Data model implications**: Are data entities and relationships extractable from the sections?
4. **Section typing**: Are section types correctly classified?
5. **Architectural clarity**: Can data pipeline architecture be derived from these sections?

Provide your review as:
```json
{{
  "status": "approved | changes_requested | additions_suggested",
  "confidence": 0.0-1.0,
  "comments": [
    {{
      "target_id": "section reference",
      "severity": "critical | suggestion | info",
      "comment": "...",
      "proposed_change": "..."
    }}
  ],
  "additions": []
}}
```
"""

PHASE4_REVIEW_PROMPT = """\
You are reviewing test case specifications from a Data Architecture perspective.

## Primary Agent Output (Test Cases)
{primary_output}

## Test Category Mappings
{test_category_map}

## Requirements
{requirements}

## Instructions
Review test cases for architectural correctness:

1. **Cross-domain coverage**: Do tests cover data flows across domain boundaries?
2. **Data lineage tests**: Are source-to-target transformations tested end-to-end?
3. **Data model alignment**: Do tests align with the expected data model?
4. **Layer coverage**: Are all pipeline layers (bronze, silver, gold) tested?
5. **Dependency ordering**: Are test dependencies correctly structured?

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
