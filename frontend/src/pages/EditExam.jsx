import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { examService } from '../services/examService'
import './EditExam.css'

const EditExam = () => {
  const { examId } = useParams()
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    start_date: '',
    end_date: '',
    fee: '0.00',
    status: 'DRAFT',
  })

  // Redirect if not ADMIN
  if (user?.role !== 'ADMIN') {
    return (
      <div className="error-container">
        <h2>Access Denied</h2>
        <p>Only administrators can edit exams.</p>
        <button onClick={() => navigate('/exams')} className="back-button">
          Go Back
        </button>
      </div>
    )
  }

  useEffect(() => {
    fetchExam()
  }, [examId])

  const fetchExam = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await examService.getExamById(examId)
      
      // Format dates for datetime-local input
      const startDate = new Date(data.start_date)
      const endDate = new Date(data.end_date)
      
      setFormData({
        title: data.title,
        description: data.description || '',
        start_date: startDate.toISOString().slice(0, 16),
        end_date: endDate.toISOString().slice(0, 16),
        fee: data.fee.toString(),
        status: data.status,
      })
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch exam details')
      console.error('Error fetching exam:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setSubmitting(true)

    try {
      // Only send fields that have changed
      const updateData = {}
      
      if (formData.title.trim() !== '') {
        updateData.title = formData.title.trim()
      }
      
      if (formData.description !== undefined) {
        updateData.description = formData.description.trim() || null
      }
      
      if (formData.start_date) {
        updateData.start_date = new Date(formData.start_date).toISOString()
      }
      
      if (formData.end_date) {
        updateData.end_date = new Date(formData.end_date).toISOString()
      }
      
      if (formData.fee !== undefined) {
        updateData.fee = parseFloat(formData.fee)
      }
      
      if (formData.status) {
        updateData.status = formData.status
      }

      const updatedExam = await examService.updateExam(examId, updateData)
      setSuccess('Exam updated successfully!')
      
      setTimeout(() => {
        navigate(`/exams/${examId}`)
      }, 1500)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update exam')
      console.error('Error updating exam:', err)
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

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading exam details...</p>
      </div>
    )
  }

  return (
    <div className="edit-exam-container">
      <div className="edit-exam-card">
        <div className="edit-exam-header">
          <h1>Radhe Radhe! 🙏</h1>
          <h2>Edit Exam</h2>
        </div>

        <div className="navigation-links">
          <button onClick={() => navigate(`/exams/${examId}`)} className="nav-link">
            ← Back to Exam Details
          </button>
        </div>

        <form onSubmit={handleSubmit} className="edit-exam-form">
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
              {submitting ? 'Updating...' : 'Update Exam'}
            </button>
            <button
              type="button"
              onClick={() => navigate(`/exams/${examId}`)}
              className="cancel-button"
              disabled={submitting}
            >
              Cancel
            </button>
          </div>
        </form>

        <div className="edit-exam-actions">
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </div>
      </div>
    </div>
  )
}

export default EditExam


