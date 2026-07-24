export const STATUSES = {
  NOT_STARTED: 'not_started',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
}

export const STATUS_LABELS = {
  [STATUSES.NOT_STARTED]: 'To Do',
  [STATUSES.IN_PROGRESS]: 'In Progress',
  [STATUSES.COMPLETED]: 'Done',
}

export const CATEGORIES = {
  BUG: 'bug',
  STORY: 'story',
  TASK: 'task',
  EPIC: 'epic',
  SUBTASK: 'subtask',
  INCIDENT: 'incident',
  IMPROVEMENT: 'improvement',
}

export const CATEGORY_LABELS = {
  [CATEGORIES.BUG]: 'Bug',
  [CATEGORIES.STORY]: 'Story',
  [CATEGORIES.TASK]: 'Task',
  [CATEGORIES.EPIC]: 'Epic',
  [CATEGORIES.SUBTASK]: 'Sub-task',
  [CATEGORIES.INCIDENT]: 'Incident',
  [CATEGORIES.IMPROVEMENT]: 'Improvement',
}

export const PRIORITIES = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
}

export const PRIORITY_LABELS = {
  [PRIORITIES.LOW]: 'Low',
  [PRIORITIES.MEDIUM]: 'Medium',
  [PRIORITIES.HIGH]: 'High',
}

export const STORAGE_KEY = 'velodesk-work-items'
