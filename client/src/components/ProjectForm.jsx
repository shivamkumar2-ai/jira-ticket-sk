import { useState } from 'react'
import {
  CATEGORY_LABELS,
  CATEGORIES,
  PRIORITY_LABELS,
  PRIORITIES,
  STATUS_LABELS,
  STATUSES,
} from '../constants/index.js'

const emptyForm = {
  title: '',
  description: '',
  category: CATEGORIES.TASK,
  status: STATUSES.NOT_STARTED,
  priority: PRIORITIES.MEDIUM,
  progress: 0,
  tags: '',
  resourceUrl: '',
  notes: '',
}

function toFormValues(project) {
  if (!project) return emptyForm
  return {
    title: project.title,
    description: project.description,
    category: project.category,
    status: project.status,
    priority: project.priority,
    progress: project.progress,
    tags: (project.tags ?? []).join(', '),
    resourceUrl: project.resourceUrl ?? '',
    notes: project.notes ?? '',
  }
}

export function ProjectForm({ project, onSave, onCancel }) {
  const [values, setValues] = useState(() => toFormValues(project))
  const [errors, setErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)

  const handleChange = (field) => (event) => {
    const nextValue =
      field === 'progress' ? Number(event.target.value) : event.target.value
    setValues((prev) => ({ ...prev, [field]: nextValue }))
    setErrors((prev) => ({ ...prev, [field]: undefined, form: undefined }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setSubmitting(true)
    const result = await onSave(values)
    if (!result.ok) {
      setErrors(result.errors ?? {})
    }
    setSubmitting(false)
  }

  return (
    <div className="modal-backdrop" role="presentation">
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="project-form-title"
      >
        <header className="modal__header">
          <h2 id="project-form-title">
            {project ? 'Edit work item' : 'New work item'}
          </h2>
          <button type="button" className="modal__close" onClick={onCancel} aria-label="Close">
            ×
          </button>
        </header>

        <form className="project-form" onSubmit={handleSubmit} noValidate>
          {errors.form ? (
            <p className="form-error form-error--banner" role="alert">
              {errors.form}
            </p>
          ) : null}

          <label className="field">
            <span>Summary *</span>
            <input
              type="text"
              value={values.title}
              onChange={handleChange('title')}
              aria-invalid={Boolean(errors.title)}
              aria-describedby={errors.title ? 'title-error' : undefined}
            />
            {errors.title ? (
              <span id="title-error" className="form-error" role="alert">
                {errors.title}
              </span>
            ) : null}
          </label>

          <label className="field">
            <span>Description *</span>
            <textarea
              rows={3}
              value={values.description}
              onChange={handleChange('description')}
              aria-invalid={Boolean(errors.description)}
            />
            {errors.description ? (
              <span className="form-error" role="alert">
                {errors.description}
              </span>
            ) : null}
          </label>

          <div className="project-form__grid">
            <label className="field">
              <span>Issue type</span>
              <select value={values.category} onChange={handleChange('category')}>
                {Object.values(CATEGORIES).map((category) => (
                  <option key={category} value={category}>
                    {CATEGORY_LABELS[category]}
                  </option>
                ))}
              </select>
            </label>

            <label className="field">
              <span>Status</span>
              <select value={values.status} onChange={handleChange('status')}>
                {Object.values(STATUSES).map((status) => (
                  <option key={status} value={status}>
                    {STATUS_LABELS[status]}
                  </option>
                ))}
              </select>
            </label>

            <label className="field">
              <span>Priority</span>
              <select value={values.priority} onChange={handleChange('priority')}>
                {Object.values(PRIORITIES).map((priority) => (
                  <option key={priority} value={priority}>
                    {PRIORITY_LABELS[priority]}
                  </option>
                ))}
              </select>
            </label>

            <label className="field">
              <span>Progress (%)</span>
              <input
                type="number"
                min={0}
                max={100}
                value={values.progress}
                onChange={handleChange('progress')}
              />
              {errors.progress ? (
                <span className="form-error" role="alert">
                  {errors.progress}
                </span>
              ) : null}
            </label>
          </div>

          <label className="field">
            <span>Labels (comma-separated)</span>
            <input
              type="text"
              value={values.tags}
              onChange={handleChange('tags')}
              placeholder="bug, sprint-12, backend"
            />
            {errors.tags ? (
              <span className="form-error" role="alert">
                {errors.tags}
              </span>
            ) : null}
          </label>

          <label className="field">
            <span>Resource URL</span>
            <input
              type="url"
              value={values.resourceUrl}
              onChange={handleChange('resourceUrl')}
              placeholder="https://..."
            />
            {errors.resourceUrl ? (
              <span className="form-error" role="alert">
                {errors.resourceUrl}
              </span>
            ) : null}
          </label>

          <label className="field">
            <span>Comments</span>
            <textarea rows={3} value={values.notes} onChange={handleChange('notes')} />
            {errors.notes ? (
              <span className="form-error" role="alert">
                {errors.notes}
              </span>
            ) : null}
          </label>

          <div className="modal__actions">
            <button type="button" className="btn btn--ghost" onClick={onCancel}>
              Cancel
            </button>
            <button type="submit" className="btn btn--primary" disabled={submitting}>
              {project ? 'Save work item' : 'Create work item'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
