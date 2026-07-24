import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { ApiError } from '../api/client.js'
import {
  createProject,
  deleteProject as deleteProjectApi,
  fetchProjectStats,
  fetchProjects,
  updateProject,
} from '../api/projects.js'
import { fetchUsers } from '../api/users.js'
import { validateProject } from '../utils/validation.js'
import { SORT_OPTIONS } from '../utils/filters.js'

function buildDefaultFilters(userId) {
  return {
    search: '',
    status: '',
    category: '',
    priority: '',
    sort: SORT_OPTIONS.UPDATED_DESC,
    users: userId ? [userId] : [],
  }
}

const emptyStats = {
  total: 0,
  inProgress: 0,
  completed: 0,
  notStarted: 0,
  avgProgress: 0,
}

export function useProjects(currentUser) {
  const defaultFilters = useMemo(
    () => buildDefaultFilters(currentUser?.id),
    [currentUser?.id],
  )

  const [filteredProjects, setFilteredProjects] = useState([])
  const [stats, setStats] = useState(emptyStats)
  const [workspaceUsers, setWorkspaceUsers] = useState([])
  const [filters, setFilters] = useState(defaultFilters)
  const [loading, setLoading] = useState(true)
  const [listLoading, setListLoading] = useState(false)
  const [error, setError] = useState(null)
  const [toast, setToast] = useState(null)
  const [editingProject, setEditingProject] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState(null)
  const hasLoadedRef = useRef(false)

  useEffect(() => {
    setFilters(defaultFilters)
    hasLoadedRef.current = false
  }, [defaultFilters])

  const showToast = useCallback((message, type = 'success') => {
    setToast({ message, type })
  }, [])

  const loadStats = useCallback(async (activeFilters, options = {}) => {
    const nextStats = await fetchProjectStats(activeFilters, options)
    setStats(nextStats)
  }, [])

  const loadProjects = useCallback(async (activeFilters, { signal, initial = false } = {}) => {
    if (initial) {
      setLoading(true)
    } else {
      setListLoading(true)
    }

    try {
      const items = await fetchProjects(activeFilters, { signal })
      setFilteredProjects(items)
      setError(null)
    } catch (err) {
      if (err.name === 'AbortError') {
        return
      }
      const message =
        err instanceof ApiError
          ? err.message
          : 'Unable to load your work items.'
      setError(message)
    } finally {
      if (initial) {
        setLoading(false)
      } else {
        setListLoading(false)
      }
    }
  }, [])

  useEffect(() => {
    if (!currentUser?.id) {
      return undefined
    }

    const controller = new AbortController()

    async function initialLoad() {
      setLoading(true)
      try {
        const users = await fetchUsers({ signal: controller.signal })
        setWorkspaceUsers(users)

        const activeFilters = buildDefaultFilters(currentUser.id)
        setFilters(activeFilters)

        await Promise.all([
          loadProjects(activeFilters, { signal: controller.signal, initial: true }),
          loadStats(activeFilters, { signal: controller.signal }),
        ])
        hasLoadedRef.current = true
      } catch (err) {
        if (err.name !== 'AbortError') {
          const message =
            err instanceof ApiError
              ? err.message
              : 'Unable to load your work items.'
          setError(message)
          setLoading(false)
        }
      }
    }

    initialLoad()
    return () => controller.abort()
  }, [currentUser?.id, loadProjects, loadStats])

  useEffect(() => {
    if (!hasLoadedRef.current || !filters.users.length) {
      return undefined
    }

    const controller = new AbortController()
    const delay = filters.search ? 300 : 0
    const timer = setTimeout(() => {
      loadProjects(filters, { signal: controller.signal })
      loadStats(filters, { signal: controller.signal })
    }, delay)

    return () => {
      clearTimeout(timer)
      controller.abort()
    }
  }, [filters, loadProjects, loadStats])

  const updateFilter = useCallback((key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }))
  }, [])

  const toggleUserFilter = useCallback((userId, checked) => {
    setFilters((prev) => {
      const nextUsers = checked
        ? [...new Set([...prev.users, userId])]
        : prev.users.filter((id) => id !== userId)
      return { ...prev, users: nextUsers }
    })
  }, [])

  const clearFilters = useCallback(() => {
    setFilters(defaultFilters)
  }, [defaultFilters])

  const openCreateForm = useCallback(() => {
    setEditingProject(null)
    setShowForm(true)
  }, [])

  const openEditForm = useCallback((project) => {
    setEditingProject(project)
    setShowForm(true)
  }, [])

  const closeForm = useCallback(() => {
    setShowForm(false)
    setEditingProject(null)
  }, [])

  const saveProject = useCallback(
    async (input) => {
      const result = validateProject(input, { isEdit: Boolean(editingProject) })
      if (!result.isValid) {
        return { ok: false, errors: result.errors }
      }

      try {
        if (editingProject) {
          await updateProject(editingProject.id, result.values)
          showToast('Work item updated.')
        } else {
          await createProject(result.values)
          showToast('Work item created.')
        }

        await Promise.all([loadProjects(filters), loadStats(filters)])
        closeForm()
        return { ok: true }
      } catch (err) {
        if (err instanceof ApiError && Object.keys(err.errors).length > 0) {
          return { ok: false, errors: err.errors }
        }

        const message =
          err instanceof ApiError ? err.message : 'Failed to save the work item.'
        showToast(message, 'error')
        return { ok: false, errors: { form: message } }
      }
    },
    [closeForm, editingProject, filters, loadProjects, loadStats, showToast],
  )

  const confirmDelete = useCallback((project) => {
    setDeleteTarget(project)
  }, [])

  const cancelDelete = useCallback(() => {
    setDeleteTarget(null)
  }, [])

  const deleteProject = useCallback(async () => {
    if (!deleteTarget) return

    try {
      await deleteProjectApi(deleteTarget.id)
      showToast('Work item deleted.')
      setDeleteTarget(null)
      await Promise.all([loadProjects(filters), loadStats(filters)])
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : 'Failed to delete the work item.'
      showToast(message, 'error')
    }
  }, [deleteTarget, filters, loadProjects, loadStats, showToast])

  const dismissToast = useCallback(() => setToast(null), [])

  const retryLoad = useCallback(async () => {
    setError(null)
    setLoading(true)
    try {
      const users = await fetchUsers()
      setWorkspaceUsers(users)
      await Promise.all([
        loadProjects(filters, { initial: true }),
        loadStats(filters),
      ])
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : 'Unable to load your work items.'
      setError(message)
      setLoading(false)
    }
  }, [filters, loadProjects, loadStats])

  return {
    stats,
    filteredProjects,
    workspaceUsers,
    filters,
    loading,
    listLoading,
    error,
    toast,
    showForm,
    editingProject,
    deleteTarget,
    updateFilter,
    toggleUserFilter,
    clearFilters,
    openCreateForm,
    openEditForm,
    closeForm,
    saveProject,
    confirmDelete,
    cancelDelete,
    deleteProject,
    dismissToast,
    retryLoad,
  }
}
