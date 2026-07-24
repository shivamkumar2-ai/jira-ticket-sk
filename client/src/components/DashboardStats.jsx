function StatCard({ label, value, hint }) {
  return (
    <article className="stat-card">
      <p className="stat-card__label">{label}</p>
      <p className="stat-card__value">{value}</p>
      {hint ? <p className="stat-card__hint">{hint}</p> : null}
    </article>
  )
}

export function DashboardStats({ stats }) {
  return (
    <section className="dashboard-stats" aria-label="Workspace summary">
      <StatCard label="Total work items" value={stats.total} />
      <StatCard label="In progress" value={stats.inProgress} />
      <StatCard label="Done" value={stats.completed} />
      <StatCard label="To Do" value={stats.notStarted} />
      <StatCard
        label="Average progress"
        value={`${stats.avgProgress}%`}
        hint="Across all items in your workspace"
      />
    </section>
  )
}
