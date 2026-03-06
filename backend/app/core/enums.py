from enum import StrEnum


class PhaseEnum(StrEnum):
    INGEST = "ingest"
    CLARIFY = "clarify"
    CLASSIFY = "classify"
    GENERATE = "generate"


class PhaseNumber(int):
    """Phase number 1-4 mapping."""

    INGEST = 1
    CLARIFY = 2
    CLASSIFY = 3
    GENERATE = 4


PHASE_NUMBER_TO_ENUM = {
    1: PhaseEnum.INGEST,
    2: PhaseEnum.CLARIFY,
    3: PhaseEnum.CLASSIFY,
    4: PhaseEnum.GENERATE,
}


class TestCategoryEnum(StrEnum):
    SCHEMA_CONTRACT = "schema_contract"
    DATA_QUALITY = "data_quality"
    BUSINESS_LOGIC = "business_logic"
    METRICS = "metrics"
    REGULATORY = "regulatory"
    FRESHNESS = "freshness"
    CONSISTENCY = "consistency"


class PipelineLayerEnum(StrEnum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"


class DomainEnum(StrEnum):
    CUSTOMER = "customer"
    RISK = "risk"
    FINANCE = "finance"
    HR = "hr"
    WHOLESALE_SME = "wholesale_sme"
    CROSS_DOMAIN = "cross_domain"


class AgentRoleEnum(StrEnum):
    PRIMARY = "primary"
    REVIEWER = "reviewer"


class AgentIdEnum(StrEnum):
    BUSINESS = "business_agent"
    DATA_TRANSLATOR = "data_translator_agent"
    DATA_ENGINEER = "data_engineer_agent"
    DATA_GOVERNANCE = "data_governance_agent"
    DATA_OPS = "data_ops_agent"
    DATA_ARCHITECT = "data_architect_agent"
    BI_ANALYTICS = "bi_analytics_agent"


class ReviewStatusEnum(StrEnum):
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    ADDITIONS_SUGGESTED = "additions_suggested"


class UserDecisionEnum(StrEnum):
    APPROVED = "approved"
    REVISION_REQUESTED = "revision_requested"


class ProjectStatusEnum(StrEnum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class CommentSeverityEnum(StrEnum):
    CRITICAL = "critical"
    SUGGESTION = "suggestion"
    INFO = "info"


class ExecutionStatusEnum(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TestResultEnum(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"
    SKIP = "skip"


class ExecutorTypeEnum(StrEnum):
    DBT_TEST = "dbt_test"
    GREAT_EXPECTATIONS = "great_expectations"
    CUSTOM_SQL = "custom_sql"
    DBT_MACRO = "dbt_macro"
