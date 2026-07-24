import { ProjectCard } from './ProjectCard.jsx'

export function ProjectList({ projects, currentUserId, onEdit, onDelete }) {
  if (!projects.length) {
    return (
      <section className="empty-state" aria-live="polite">
        <h2>No work items match your filters</h2>
        <p>Try clearing filters or add a new work item to your workspace.</p>
      </section>
    )
  }

  return (
    <section className="project-list" aria-label="Work items">
      {projects.map((project) => (
        <ProjectCard
          key={project.id}
          project={project}
          currentUserId={currentUserId}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </section>
  )
}
