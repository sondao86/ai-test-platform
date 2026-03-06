"""Prompt templates for the Data Ops Agent."""

PHASE4_REVIEW_PROMPT = """\
You are reviewing test case specifications from a DataOps perspective.

## Primary Agent Output (Test Cases)
{primary_output}

## Test Category Mappings
{test_category_map}

## Instructions
Review test cases for operational viability:

1. **Execution feasibility**: Can each test run within the suggested SLA?
2. **Resource impact**: Will tests cause performance issues on production systems?
3. **CI/CD integration**: Can tests be integrated into existing CI/CD pipelines?
4. **Monitoring & alerting**: Are failure conditions clearly defined for alerting?
5. **Scheduling considerations**: Are there dependency or ordering requirements?
6. **Idempotency**: Are tests idempotent and safe to re-run?

Provide your review as:
```json
{{
  "status": "approved | changes_requested | additions_suggested",
  "confidence": 0.0-1.0,
  "comments": [
    {{
      "target_id": "test case reference",
      "severity": "critical | suggestion | info",
      "comment": "...",
      "proposed_change": "..."
    }}
  ],
  "additions": []
}}
```
"""
