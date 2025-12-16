import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { examService } from '../services/examService'
import './CreateExam.css'

const CreateExam = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    start_date: '',
    end_date: '',
    fee: '0.00',
    status: 'DRAFT',
  })
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Redirect if not ADMIN
  if (user?.role !== 'ADMIN') {
    return (
      <div className="error-container">
        <h2>Access Denied</h2>
        <p>Only administrators can create exams.</p>
        <button onClick={() => navigate('/exams')} className="back-button">
          Go Back
        </button>
      </div>
    )
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setSubmitting(true)

    try {
      const examData = {
        ...formData,
        fee: parseFloat(formData.fee),
        start_date: new Date(formData.start_date).toISOString(),
        end_date: new Date(formData.end_date).toISOString(),
      }

      const createdExam = await examService.createExam(examData)
      setSuccess('Exam created successfully!')
      
      setTimeout(() => {
        navigate(`/exams/${createdExam.id}`)
      }, 1500)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create exam')
      console.error('Error creating exam:', err)
    } finally {
      setSubmitting(false)
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="create-exam-container">
      <div className="create-exam-card">
        <div className="create-exam-header">
          <h1>Radhe Radhe! 🙏</h1>
          <h2>Create New Exam</h2>
        </div>

        <div className="navigation-links">
          <button onClick={() => navigate('/exams')} className="nav-link">
            ← Back to Exams
          </button>
        </div>

        <form onSubmit={handleSubmit} className="create-exam-form">
          <div className="form-group">
            <label htmlFor="title">Title *</label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              placeholder="e.g., Mathematics Final Exam"
              required
              disabled={submitting}
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Exam description..."
              rows="4"
              disabled={submitting}
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="start_date">Start Date & Time *</label>
              <input
                type="datetime-local"
                id="start_date"
                name="start_date"
                value={formData.start_date}
                onChange={handleChange}
                required
                disabled={submitting}
              />
            </div>

            <div className="form-group">
              <label htmlFor="end_date">End Date & Time *</label>
              <input
                type="datetime-local"
                id="end_date"
                name="end_date"
                value={formData.end_date}
                onChange={handleChange}
                required
                disabled={submitting}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="fee">Fee (₹) *</label>
              <input
                type="number"
                id="fee"
                name="fee"
                value={formData.fee}
                onChange={handleChange}
                min="0"
                step="0.01"
                placeholder="0.00"
                required
                disabled={submitting}
              />
            </div>

            <div className="form-group">
              <label htmlFor="status">Status *</label>
              <select
                id="status"
                name="status"
                value={formData.status}
                onChange={handleChange}
                required
                disabled={submitting}
              >
                <option value="DRAFT">Draft</option>
                <option value="ACTIVE">Active</option>
              </select>
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}
          {success && <div className="success-message">{success}</div>}

          <div className="form-actions">
            <button type="submit" className="submit-button" disabled={submitting}>
              {submitting ? 'Creating...' : 'Create Exam'}
            </button>
            <button
              type="button"
              onClick={() => navigate('/exams')}
              className="cancel-button"
              disabled={submitting}
            >
              Cancel
            </button>
          </div>
        </form>

        <div className="create-exam-actions">
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </div>
      </div>
    </div>
  )
}

export default CreateExam


