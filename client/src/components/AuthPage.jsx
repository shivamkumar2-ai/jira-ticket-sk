import { useState } from 'react'
import { getAuthErrorMessage, useAuth } from '../context/AuthContext.jsx'
import { ApiError } from '../api/client.js'

export function AuthPage() {
  const { login, register } = useAuth()
  const [mode, setMode] = useState('login')
  const [values, setValues] = useState({
    name: '',
    email: '',
    password: '',
  })
  const [errors, setErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)

  const handleChange = (field) => (event) => {
    setValues((prev) => ({ ...prev, [field]: event.target.value }))
    setErrors((prev) => ({ ...prev, [field]: undefined, form: undefined }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setSubmitting(true)
    setErrors({})

    try {
      if (mode === 'login') {
        await login({ email: values.email, password: values.password })
      } else {
        if (!values.name.trim()) {
          setErrors({ name: 'Name is required.' })
          return
        }
        await register({
          email: values.email,
          password: values.password,
          name: values.name,
        })
      }
    } catch (error) {
      if (error instanceof ApiError && Object.keys(error.errors).length > 0) {
        setErrors({ ...error.errors, form: getAuthErrorMessage(error) })
      } else {
        setErrors({ form: getAuthErrorMessage(error) })
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-card__header">
          <div className="app-header__logo" aria-hidden="true">
            V
          </div>
          <div>
            <p className="eyebrow">VeloDesk</p>
            <h1>{mode === 'login' ? 'Sign in' : 'Create account'}</h1>
            <p className="subtitle">
              {mode === 'login'
                ? 'Sign in to open your VeloDesk workspace.'
                : 'Create an account to start tracking work with your team.'}
            </p>
          </div>
        </div>

        <div className="auth-toggle" role="tablist" aria-label="Authentication mode">
          <button
            type="button"
            role="tab"
            aria-selected={mode === 'login'}
            className={mode === 'login' ? 'auth-toggle__btn auth-toggle__btn--active' : 'auth-toggle__btn'}
            onClick={() => setMode('login')}
          >
            Sign in
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={mode === 'register'}
            className={
              mode === 'register' ? 'auth-toggle__btn auth-toggle__btn--active' : 'auth-toggle__btn'
            }
            onClick={() => setMode('register')}
          >
            Sign up
          </button>
        </div>

        <form className="auth-form" onSubmit={handleSubmit} noValidate>
          {errors.form ? (
            <p className="form-error form-error--banner" role="alert">
              {errors.form}
            </p>
          ) : null}

          {mode === 'register' ? (
            <label className="field">
              <span>Name</span>
              <input
                type="text"
                value={values.name}
                onChange={handleChange('name')}
                autoComplete="name"
              />
              {errors.name ? (
                <span className="form-error" role="alert">
                  {errors.name}
                </span>
              ) : null}
            </label>
          ) : null}

          <label className="field">
            <span>Email</span>
            <input
              type="email"
              value={values.email}
              onChange={handleChange('email')}
              autoComplete="email"
              placeholder="you@example.com"
            />
            {errors.email ? (
              <span className="form-error" role="alert">
                {errors.email}
              </span>
            ) : null}
          </label>

          <label className="field">
            <span>Password</span>
            <input
              type="password"
              value={values.password}
              onChange={handleChange('password')}
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              placeholder={mode === 'register' ? 'At least 8 characters' : ''}
            />
            {errors.password ? (
              <span className="form-error" role="alert">
                {errors.password}
              </span>
            ) : null}
          </label>

          <button type="submit" className="btn btn--primary auth-form__submit" disabled={submitting}>
            {submitting ? 'Please wait…' : mode === 'login' ? 'Sign in' : 'Create account'}
          </button>
        </form>

        <p className="auth-hint">
          Demo account: <strong>demo@example.com</strong> / <strong>demo1234</strong>
        </p>
      </div>
    </div>
  )
}
