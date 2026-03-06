"""Prompt templates for the BI & Analytics Agent."""

PHASE3_REVIEW_PROMPT = """\
You are reviewing test category classifications as a BI & Analytics Specialist.

## Primary Agent Output (Category Mappings)
{primary_output}

## Requirements
{requirements}

## Instructions
Review category mappings from an analytics and reporting perspective:

1. **Metric coverage**: Are all KPIs and metrics mapped to appropriate test categories?
2. **Aggregation testing**: Are there test categories for aggregation correctness?
3. **Anomaly detection**: Is there coverage for detecting unusual data patterns?
4. **Reporting requirements**: Will downstream reports/dashboards be adequately tested?
5. **Derived metrics**: Are calculated/derived metrics properly categorized?

Provide your review as:
```json
{{
  "status": "approved | changes_requested | additions_suggested",
  "confidence": 0.0-1.0,
  "comments": [
    {{
      "target_id": "mapping reference",
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
You are reviewing test case specifications as a BI & Analytics Specialist.

## Primary Agent Output (Test Cases)
{primary_output}

## Test Category Mappings
{test_category_map}

## Instructions
Review test cases from an analytics accuracy perspective:

1. **Metric accuracy tests**: Do test cases verify KPI calculations correctly?
2. **Aggregation tests**: Are SUM, AVG, COUNT, and other aggregations tested?
3. **Time-series tests**: Are temporal patterns and trends testable?
4. **Anomaly detection tests**: Are there tests for detecting outliers and anomalies?
5. **Dashboard-ready data**: Will tested data be immediately usable for reporting?

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
