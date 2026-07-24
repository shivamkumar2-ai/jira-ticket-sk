import {
  CATEGORY_LABELS,
  PRIORITY_LABELS,
  STATUS_LABELS,
} from '../constants/index.js'

function formatDate(iso) {
  return new Date(iso).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

export function ProjectCard({ project, currentUserId, onEdit, onDelete }) {
  const canManage = project.ownerId === currentUserId

  return (
    <article className={`project-card project-card--${project.status}`}>
      <div className="project-card__header">
        <div>
          <p className="project-card__ticket-id">{project.id}</p>
          <p className="project-card__category">{CATEGORY_LABELS[project.category]}</p>
          <h3>{project.title}</h3>
        </div>
        <span className={`badge badge--${project.priority}`}>
          {PRIORITY_LABELS[project.priority]}
        </span>
      </div>

      <p className="project-card__description">{project.description}</p>

      <div className="project-card__meta">
        <span className={`status-pill status-pill--${project.status}`}>
          {STATUS_LABELS[project.status]}
        </span>
        <span>Owner: {project.ownerName}</span>
        <span>Updated {formatDate(project.updatedAt)}</span>
      </div>

      <div className="progress-block" aria-label={`Progress ${project.progress}%`}>
        <div className="progress-block__bar">
          <div className="progress-block__fill" style={{ width: `${project.progress}%` }} />
        </div>
        <span>{project.progress}%</span>
      </div>

      {project.tags?.length ? (
        <ul className="tag-list">
          {project.tags.map((tag) => (
            <li key={tag}>{tag}</li>
          ))}
        </ul>
      ) : null}

      {project.resourceUrl ? (
        <a
          className="project-card__link"
          href={project.resourceUrl}
          target="_blank"
          rel="noreferrer"
        >
          Open resource
        </a>
      ) : null}

      {project.notes ? <p className="project-card__notes">{project.notes}</p> : null}

      <div className="project-card__actions">
        {canManage ? (
          <>
            <button type="button" className="btn btn--ghost btn--small" onClick={() => onEdit(project)}>
              Edit
            </button>
            <button
              type="button"
              className="btn btn--danger btn--small"
              onClick={() => onDelete(project)}
            >
              Delete
            </button>
          </>
        ) : (
          <span className="project-card__readonly">View only — owned by {project.ownerName}</span>
        )}
      </div>
    </article>
  )
}
