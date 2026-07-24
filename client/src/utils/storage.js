import { STORAGE_KEY } from '../constants/index.js'
import { seedProjects } from '../data/seedData.js'

export class StorageError extends Error {
  constructor(message, cause) {
    super(message)
    this.name = 'StorageError'
    this.cause = cause
  }
}

export function loadProjects() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) {
      return { projects: structuredClone(seedProjects), seeded: true }
    }

    const parsed = JSON.parse(raw)
    if (!Array.isArray(parsed)) {
      throw new StorageError('Stored data is not an array.')
    }

    return { projects: parsed, seeded: false }
  } catch (error) {
    if (error instanceof StorageError) {
      throw error
    }
    throw new StorageError('Failed to read projects from local storage.', error)
  }
}

export function saveProjects(projects) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(projects))
  } catch (error) {
    throw new StorageError('Failed to save projects to local storage.', error)
  }
}

export function resetToSeedData() {
  const projects = structuredClone(seedProjects)
  saveProjects(projects)
  return projects
}
