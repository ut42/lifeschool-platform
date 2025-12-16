import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { examService } from '../services/examService'
import './ExamDetails.css'

const ExamDetails = () => {
  const { examId } = useParams()
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [exam, setExam] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchExam()
  }, [examId])

  const fetchExam = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await examService.getExamById(examId)
      setExam(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch exam details')
      console.error('Error fetching exam:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
    }).format(amount)
  }

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading exam details...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="error-container">
        <h2>Error</h2>
        <p>{error}</p>
        <button onClick={() => navigate('/exams')} className="back-button">
          Go Back to Exams
        </button>
      </div>
    )
  }

  if (!exam) {
    return (
      <div className="error-container">
        <h2>Exam Not Found</h2>
        <button onClick={() => navigate('/exams')} className="back-button">
          Go Back to Exams
        </button>
      </div>
    )
  }

  return (
    <div className="exam-details-container">
      <div className="exam-details-card">
        <div className="exam-details-header">
          <h1>Radhe Radhe! 🙏</h1>
          <h2>Exam Details</h2>
        </div>

        <div className="navigation-links">
          <button onClick={() => navigate('/exams')} className="nav-link">
            ← Back to Exams
          </button>
        </div>

        <div className="exam-details-content">
          <div className="detail-section">
            <div className="detail-header">
              <h3>{exam.title}</h3>
              <span className={`status-badge ${exam.status.toLowerCase()}`}>
                {exam.status}
              </span>
            </div>

            {exam.description && (
              <div className="detail-item">
                <label>Description:</label>
                <p>{exam.description}</p>
              </div>
            )}

            <div className="detail-grid">
              <div className="detail-item">
                <label>Start Date & Time:</label>
                <span>{formatDate(exam.start_date)}</span>
              </div>

              <div className="detail-item">
                <label>End Date & Time:</label>
                <span>{formatDate(exam.end_date)}</span>
              </div>

              <div className="detail-item">
                <label>Fee:</label>
                <span className="fee-amount">{formatCurrency(exam.fee)}</span>
              </div>

              <div className="detail-item">
                <label>Created At:</label>
                <span>{formatDate(exam.created_at)}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="exam-details-actions">
          {user?.role === 'ADMIN' && (
            <button onClick={() => navigate(`/exams/${examId}/edit`)} className="edit-button">
              Edit Exam
            </button>
          )}
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </div>
      </div>
    </div>
  )
}

export default ExamDetails

