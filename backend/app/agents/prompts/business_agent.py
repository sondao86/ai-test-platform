"""Prompt templates for the Business Agent."""

PHASE1_INGEST_PROMPT = """\
You are parsing a Business Requirements Document (BRD) into structured sections.

## Document
{raw_document}

## Instructions
Parse this BRD into structured sections. For each section, extract:
1. **section_title**: Clear, descriptive title
2. **section_type**: One of: executive_summary, business_context, functional_requirement, \
non_functional_requirement, data_requirement, kpi_definition, business_rule, \
acceptance_criteria, dependency, glossary, appendix, other
3. **content**: Full text content of the section
4. **order_index**: Sequential index (starting at 0)
5. **cross_references**: List of other section titles this section references or depends on
6. **metadata**: Any additional structured info (e.g., stakeholders mentioned, priority indicators)

## Output Format
Return a JSON array of section objects:
```json
[
  {{
    "section_title": "...",
    "section_type": "...",
    "content": "...",
    "order_index": 0,
    "cross_references": ["..."],
    "metadata": {{}}
  }}
]
```

Be thorough — do not skip any content. Preserve the original meaning and context.
"""

PHASE2_CLARIFY_PROMPT = """\
You are generating clarification questions for BRD requirements.

## BRD Sections
{brd_chunks}

## Previous Clarifications (if any)
{previous_clarifications}

## User Feedback (if revision requested)
{user_feedback}

## Instructions
For each BRD section, identify areas that need clarification before data pipeline tests can be \
generated. Focus on:

1. **Ambiguous business rules** — rules that could be interpreted multiple ways
2. **Missing thresholds/SLAs** — KPIs without specific targets or acceptable ranges
3. **Undefined data elements** — referenced fields/tables not clearly defined
4. **Implicit assumptions** — business logic that is assumed but not stated
5. **Edge cases** — boundary conditions not addressed

For each clarification question, provide:
- **question**: The specific question
- **category**: ambiguity | missing_threshold | undefined_element | implicit_assumption | edge_case
- **severity**: critical | high | medium | low
- **chunk_id**: The section this relates to (use section_title if no ID)
- **context**: Why this clarification is needed for test generation

## Output Format
Return a JSON array:
```json
[
  {{
    "question": "...",
    "category": "...",
    "severity": "...",
    "chunk_reference": "...",
    "context": {{}}
  }}
]
```

Also produce clarified requirements from the BRD sections:
```json
{{
  "clarifications": [...],
  "requirements": [
    {{
      "requirement_id": "REQ-001",
      "title": "...",
      "description": "...",
      "priority": "high|medium|low",
      "business_rules": ["..."],
      "kpis": ["..."],
      "data_elements": ["..."]
    }}
  ]
}}
```
"""
