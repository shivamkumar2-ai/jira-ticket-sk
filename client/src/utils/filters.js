export const SORT_OPTIONS = {
  UPDATED_DESC: 'updated_desc',
  UPDATED_ASC: 'updated_asc',
  TITLE_ASC: 'title_asc',
  PROGRESS_DESC: 'progress_desc',
  PRIORITY_DESC: 'priority_desc',
}

const PRIORITY_WEIGHT = { high: 3, medium: 2, low: 1 }

export function filterProjects(projects, { search, status, category, priority, sort }) {
  const query = search.trim().toLowerCase()

  let result = projects.filter((project) => {
    if (status && project.status !== status) return false
    if (category && project.category !== category) return false
    if (priority && project.priority !== priority) return false

    if (!query) return true

    const haystack = [
      project.title,
      project.description,
      project.notes,
      ...(project.tags ?? []),
    ]
      .join(' ')
      .toLowerCase()

    return haystack.includes(query)
  })

  result = [...result].sort((a, b) => {
    switch (sort) {
      case SORT_OPTIONS.UPDATED_ASC:
        return new Date(a.updatedAt) - new Date(b.updatedAt)
      case SORT_OPTIONS.TITLE_ASC:
        return a.title.localeCompare(b.title)
      case SORT_OPTIONS.PROGRESS_DESC:
        return b.progress - a.progress
      case SORT_OPTIONS.PRIORITY_DESC:
        return PRIORITY_WEIGHT[b.priority] - PRIORITY_WEIGHT[a.priority]
      case SORT_OPTIONS.UPDATED_DESC:
      default:
        return new Date(b.updatedAt) - new Date(a.updatedAt)
    }
  })

  return result
}

export function computeStats(projects) {
  const total = projects.length
  const completed = projects.filter((p) => p.status === 'completed').length
  const inProgress = projects.filter((p) => p.status === 'in_progress').length
  const notStarted = projects.filter((p) => p.status === 'not_started').length
  const avgProgress = total
    ? Math.round(projects.reduce((sum, p) => sum + p.progress, 0) / total)
    : 0

  return { total, completed, inProgress, notStarted, avgProgress }
}
