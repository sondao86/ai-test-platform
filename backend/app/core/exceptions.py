from fastapi import HTTPException, status


class ProjectNotFoundError(HTTPException):
    def __init__(self, project_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )


class PhaseNotCompletedError(HTTPException):
    def __init__(self, phase: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Phase {phase} has not been completed yet",
        )


class PipelineAlreadyRunningError(HTTPException):
    def __init__(self, project_id: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Pipeline already running for project {project_id}",
        )


class InvalidPhaseTransitionError(HTTPException):
    def __init__(self, current: int, target: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition from phase {current} to phase {target}",
        )


class DocumentParseError(HTTPException):
    def __init__(self, filename: str, reason: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse {filename}: {reason}",
        )


class FileTooLargeError(HTTPException):
    def __init__(self, max_mb: int):
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size of {max_mb}MB",
        )


class TestCaseNotFoundError(HTTPException):
    def __init__(self, tc_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test case {tc_id} not found",
        )


class NoTestCasesForRerunError(HTTPException):
    def __init__(self, execution_id: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No active test cases to re-run from execution {execution_id}",
        )


class WikiConfigMissingError(HTTPException):
    def __init__(self, project_id: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Wiki configuration incomplete for project {project_id}. "
                "Required: azure_wiki_org, azure_wiki_project, azure_wiki_pat "
                "in PUT /projects/{id}/config."
            ),
        )


class WikiSyncFailedError(HTTPException):
    def __init__(self, project_id: str, reason: str):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Wiki sync failed for project {project_id}: {reason}",
        )
