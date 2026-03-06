"""Prompt templates for the Data Engineer Agent."""

PHASE3_REVIEW_PROMPT = """\
You are reviewing test category classifications as a Data Engineer.

## Primary Agent Output (Category Mappings)
{primary_output}

## Requirements
{requirements}

## Instructions
Review the Data Translator's category mappings. Focus on:

1. **Tool feasibility**: Can the suggested tool actually implement this test?
2. **Pipeline layer correctness**: Is the test at the right layer (bronze vs gold)?
3. **Missing test patterns**: Are there common data engineering test patterns not covered?
4. **Implementation complexity**: Flag any mappings that are overly complex or infeasible

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

PHASE4_GENERATE_PROMPT = """\
You are generating concrete test case specifications for data pipelines.

## Test Category Mappings
{test_category_map}

## Requirements
{requirements}

## BRD Sections
{brd_chunks}

## User Feedback (if revision requested)
{user_feedback}

## Instructions
For each test category mapping, generate a detailed test case specification:

1. **test_id**: Unique identifier (e.g., TC-DQ-001, TC-BL-001, TC-SC-001)
2. **title**: Descriptive test title
3. **description**: What the test validates and why
4. **test_category**: From the mapping (schema_contract | data_quality | business_logic | metrics | regulatory | freshness | consistency)
5. **pipeline_layer**: bronze | silver | gold
6. **domain**: Business domain from the mapping (e.g., risk, customer, finance, hr, wholesale_sme, cross_domain)
7. **tool**: dbt_test | great_expectations | custom_sql | dbt_macro
8. **sql_logic**: The actual SQL query or logic (if applicable)
9. **dbt_test_yaml**: dbt test YAML config (if tool is dbt)
10. **great_expectations_config**: GX expectation config (if tool is GX)
11. **input_data**: Sample input data for testing
12. **expected_result**: Expected outcome
13. **severity**: critical | high | medium | low
14. **priority**: 1-5 (1 = highest)
15. **sla_seconds**: Max execution time allowed
16. **tags**: Structured tags for traceability. Use the format: \
["domain:<domain>", "layer:<layer>", "category:<category>", "priority:P<n>", "req:<requirement_id>"]

## Output Format
```json
[
  {{
    "test_id": "TC-SC-001",
    "title": "Verify all required customer columns exist and have correct types",
    "description": "...",
    "test_category": "schema_contract",
    "pipeline_layer": "bronze",
    "domain": "customer",
    "tool": "dbt_test",
    "sql_logic": "SELECT ...",
    "dbt_test_yaml": "...",
    "great_expectations_config": null,
    "input_data": {{}},
    "expected_result": {{}},
    "severity": "critical",
    "priority": 1,
    "sla_seconds": 30,
    "tags": ["domain:customer", "layer:bronze", "category:schema_contract", "priority:P1", "req:REQ-001"]
  }}
]
```

Generate comprehensive test cases. Each requirement should have at least one test case. \
Critical requirements should have multiple test cases covering different scenarios.
"""
