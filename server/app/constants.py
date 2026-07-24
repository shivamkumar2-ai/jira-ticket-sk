from enum import StrEnum


class ProjectStatus(StrEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class ProjectCategory(StrEnum):
    BUG = "bug"
    STORY = "story"
    TASK = "task"
    EPIC = "epic"
    SUBTASK = "subtask"
    INCIDENT = "incident"
    IMPROVEMENT = "improvement"


class ProjectPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SortOption(StrEnum):
    UPDATED_DESC = "updated_desc"
    UPDATED_ASC = "updated_asc"
    TITLE_ASC = "title_asc"
    PROGRESS_DESC = "progress_desc"
    PRIORITY_DESC = "priority_desc"


PRIORITY_WEIGHT = {
    ProjectPriority.HIGH: 3,
    ProjectPriority.MEDIUM: 2,
    ProjectPriority.LOW: 1,
}
