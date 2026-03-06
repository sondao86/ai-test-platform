"""Consolidation prompt template — used by primary agents to address reviewer feedback."""

CONSOLIDATION_PROMPT = """\
You are the primary agent for this phase. You have received reviews from multiple specialist agents.

## Your Original Output
{primary_output}

## Reviewer Feedback
{reviews}

## Consolidation Protocol
Address each reviewer's feedback according to severity:
- **Critical** comments → MUST address (accept the change or justify rejection with clear reasoning)
- **Suggestion** comments → SHOULD address if it improves quality
- **Info** comments → MAY address, they will be visible to the user regardless

When reviewers conflict with each other, flag the conflict for user decision.

## Instructions
1. Review all feedback carefully
2. Produce an updated version of your output that incorporates accepted feedback
3. Produce a changelog explaining every decision

## Output Format
```json
{{
  "consolidated_output": <your updated output — same format as original>,
  "changelog": {{
    "accepted": [
      {{
        "from_agent": "agent_id",
        "comment_summary": "...",
        "action_taken": "..."
      }}
    ],
    "rejected_with_reason": [
      {{
        "from_agent": "agent_id",
        "comment_summary": "...",
        "rejection_reason": "..."
      }}
    ],
    "additions_merged": [
      {{
        "from_agent": "agent_id",
        "description": "..."
      }}
    ],
    "conflicts_for_user": [
      {{
        "agents": ["agent_id_1", "agent_id_2"],
        "description": "...",
        "options": ["option_a", "option_b"],
        "conflict_flag": true
      }}
    ]
  }}
}}
```

Be thorough in your consolidation. The user will see both your consolidated output and the \
full review history, so be transparent about what you accepted and rejected.
"""
