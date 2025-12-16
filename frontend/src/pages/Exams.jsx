import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { examService, registrationService } from '../services/examService'
import './Exams.css'

const Exams = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [exams, setExams] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [registrations, setRegistrations] = useState([])
  const [registrationCounts, setRegistrationCounts] = useState({})

  useEffect(() => {
    fetchExams()
    if (user?.role === 'USER') {
      fetchRegistrations()
    }
  }, [user])

  useEffect(() => {
    // Fetch counts when exams are loaded (for admin)
    if (user?.role === 'ADMIN' && exams.length > 0) {
      fetchRegistrationCounts()
    }
  }, [exams, user])

  const fetchExams = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await examService.listExams()
      setExams(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch exams')
      console.error('Error fetching exams:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchRegistrations = async () => {
    try {
      const data = await registrationService.getMyRegistrations()
      setRegistrations(data)
    } catch (err) {
      console.error('Error fetching registrations:', err)
      // Don't show error to user, just log it
    }
  }

  const fetchRegistrationCounts = async () => {
    if (exams.length === 0) return
    
    try {
      const counts = {}
      // Fetch counts for all exams in parallel
      const countPromises = exams.map(async (exam) => {
        try {
          const count = await registrationService.getExamRegistrationCount(exam.id)
          return { examId: exam.id, count }
        } catch (err) {
          console.error(`Error fetching count for exam ${exam.id}:`, err)
          return { examId: exam.id, count: 0 }
        }
      })
      
      const results = await Promise.all(countPromises)
      results.forEach(({ examId, count }) => {
        counts[examId] = count
      })
      
      setRegistrationCounts(counts)
    } catch (err) {
      console.error('Error fetching registration counts:', err)
      // Don't show error to user, just log it
    }
  }

  const getRegistration = (examId) => {
    return registrations.find(reg => reg.exam_id === examId)
  }

  const getRegistrationStatusDisplay = (status) => {
    const statusMap = {
      'REGISTERED': '✓ Registered',
      'PAYMENT_PENDING': '⏳ Payment Pending',
      'PAID': '✓ Paid',
      'ENROLLED': '🎓 Enrolled',
    }
    return statusMap[status] || '✓ Registered'
  }

  const getRegistrationStatusClass = (status) => {
    const statusLower = status.toLowerCase().replace('_', '-')
    return `registration-status-badge ${statusLower}`
  }

  const handleViewExam = (examId) => {
    navigate(`/exams/${examId}`)
  }

  const handleCreateExam = () => {
    navigate('/exams/create')
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
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
        <p>Loading exams...</p>
      </div>
    )
  }

  return (
    <div className="exams-container">
      <div className="exams-card">
        <div className="exams-header">
          <h1>Radhe Radhe! 🙏</h1>
          <h2>Exams</h2>
          {user?.role === 'ADMIN' && (
            <button onClick={handleCreateExam} className="create-exam-button">
              + Create Exam
            </button>
          )}
        </div>

        <div className="navigation-links">
          <button onClick={() => navigate('/profile')} className="nav-link">
            ← Back to Profile
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        {exams.length === 0 ? (
          <div className="no-exams">
            <p>No exams available.</p>
            {user?.role === 'ADMIN' && (
              <button onClick={handleCreateExam} className="create-exam-button">
                Create Your First Exam
              </button>
            )}
          </div>
        ) : (
          <div className="exams-list">
            {exams.map((exam) => (
              <div key={exam.id} className="exam-card" onClick={() => handleViewExam(exam.id)}>
                <div className="exam-header">
                  <h3>{exam.title}</h3>
                  <span className={`status-badge ${exam.status.toLowerCase()}`}>
                    {exam.status}
                  </span>
                </div>
                {exam.description && (
                  <p className="exam-description">{exam.description}</p>
                )}
                <div className="exam-details">
                  <div className="exam-detail-item">
                    <span className="detail-label">Start:</span>
                    <span>{formatDate(exam.start_date)}</span>
                  </div>
                  <div className="exam-detail-item">
                    <span className="detail-label">End:</span>
                    <span>{formatDate(exam.end_date)}</span>
                  </div>
                  <div className="exam-detail-item">
                    <span className="detail-label">Fee:</span>
                    <span className="fee-amount">{formatCurrency(exam.fee)}</span>
                  </div>
                </div>
                <div className="exam-footer">
                  <div className="exam-footer-left">
                    {user?.role === 'USER' && (() => {
                      const registration = getRegistration(exam.id)
                      if (registration) {
                        return (
                          <span className={getRegistrationStatusClass(registration.status)}>
                            {getRegistrationStatusDisplay(registration.status)}
                          </span>
                        )
                      }
                      return null
                    })()}
                  </div>
                  <div className="exam-footer-right">
                    <div className="exam-footer-right-content">
                      {user?.role === 'ADMIN' && registrationCounts[exam.id] !== undefined && (
                        <span className="registration-count-badge">
                          {registrationCounts[exam.id]} {registrationCounts[exam.id] === 1 ? 'Registration' : 'Registrations'}
                        </span>
                      )}
                      <button className="view-button">View Details →</button>
                      {user?.role === 'ADMIN' && (
                        <button
                          className="edit-button-small"
                          onClick={(e) => {
                            e.stopPropagation()
                            navigate(`/exams/${exam.id}/edit`)
                          }}
                        >
                          Edit
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="exams-actions">
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </div>
      </div>
    </div>
  )
}

export default Exams

