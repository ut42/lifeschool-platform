import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { registrationService, examService, paymentService } from '../services/examService'
import './MyRegistrations.css'

const MyRegistrations = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [registrations, setRegistrations] = useState([])
  const [exams, setExams] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [processingPayment, setProcessingPayment] = useState({})
  const [paymentSuccess, setPaymentSuccess] = useState({})

  useEffect(() => {
    fetchRegistrations()
  }, [])

  const fetchRegistrations = async () => {
    try {
      setLoading(true)
      setError('')
      const regs = await registrationService.getMyRegistrations()
      setRegistrations(regs)

      // Fetch exam details for each registration
      const examPromises = regs.map(reg => 
        examService.getExamById(reg.exam_id).catch(() => null)
      )
      const examResults = await Promise.all(examPromises)
      const examMap = {}
      regs.forEach((reg, index) => {
        if (examResults[index]) {
          examMap[reg.exam_id] = examResults[index]
        }
      })
      setExams(examMap)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch registrations')
      console.error('Error fetching registrations:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleViewExam = (examId) => {
    navigate(`/exams/${examId}`)
  }

  const handleInitiatePayment = async (registrationId) => {
    setError('')
    setProcessingPayment(prev => ({ ...prev, [registrationId]: true }))
    setPaymentSuccess(prev => ({ ...prev, [registrationId]: false }))

    try {
      await paymentService.initiatePayment(registrationId)
      // Refresh registrations to get updated status
      await fetchRegistrations()
      setPaymentSuccess(prev => ({ ...prev, [registrationId]: 'initiated' }))
      setTimeout(() => {
        setPaymentSuccess(prev => {
          const newState = { ...prev }
          delete newState[registrationId]
          return newState
        })
      }, 3000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to initiate payment')
      console.error('Error initiating payment:', err)
    } finally {
      setProcessingPayment(prev => {
        const newState = { ...prev }
        delete newState[registrationId]
        return newState
      })
    }
  }

  const handleConfirmPayment = async (registrationId) => {
    setError('')
    setProcessingPayment(prev => ({ ...prev, [registrationId]: true }))
    setPaymentSuccess(prev => ({ ...prev, [registrationId]: false }))

    try {
      await paymentService.confirmPayment(registrationId)
      // Refresh registrations to get updated status
      await fetchRegistrations()
      setPaymentSuccess(prev => ({ ...prev, [registrationId]: 'confirmed' }))
      setTimeout(() => {
        setPaymentSuccess(prev => {
          const newState = { ...prev }
          delete newState[registrationId]
          return newState
        })
      }, 3000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to confirm payment')
      console.error('Error confirming payment:', err)
    } finally {
      setProcessingPayment(prev => {
        const newState = { ...prev }
        delete newState[registrationId]
        return newState
      })
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
        <p>Loading your registrations...</p>
      </div>
    )
  }

  return (
    <div className="registrations-container">
      <div className="registrations-card">
        <div className="registrations-header">
          <h1>Radhe Radhe! 🙏</h1>
          <h2>My Registrations</h2>
        </div>

        <div className="navigation-links">
          <button onClick={() => navigate('/profile')} className="nav-link">
            ← Back to Profile
          </button>
          <button onClick={() => navigate('/exams')} className="nav-link">
            Browse Exams
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        {registrations.length === 0 ? (
          <div className="no-registrations">
            <p>You haven't registered for any exams yet.</p>
            <button onClick={() => navigate('/exams')} className="browse-button">
              Browse Available Exams
            </button>
          </div>
        ) : (
          <div className="registrations-list">
            {registrations.map((registration) => {
              const exam = exams[registration.exam_id]
              return (
                <div key={registration.id} className="registration-card">
                  {exam ? (
                    <>
                      <div className="registration-header">
                        <h3>{exam.title}</h3>
                        <span className={`status-badge ${exam.status.toLowerCase()}`}>
                          {exam.status}
                        </span>
                      </div>
                      {exam.description && (
                        <p className="exam-description">{exam.description}</p>
                      )}
                      <div className="registration-details">
                        <div className="detail-item">
                          <label>Start Date:</label>
                          <span>{formatDate(exam.start_date)}</span>
                        </div>
                        <div className="detail-item">
                          <label>End Date:</label>
                          <span>{formatDate(exam.end_date)}</span>
                        </div>
                        <div className="detail-item">
                          <label>Fee:</label>
                          <span className="fee-amount">{formatCurrency(exam.fee)}</span>
                        </div>
                        <div className="detail-item">
                          <label>Registered On:</label>
                          <span>{formatDate(registration.created_at)}</span>
                        </div>
                      </div>
                      <div className="registration-footer">
                        <div className="registration-status-section">
                          <span className={`payment-status-badge ${registration.status.toLowerCase().replace('_', '-')}`}>
                            {registration.status.replace('_', ' ')}
                          </span>
                          {registration.status === 'REGISTERED' && (
                            <button
                              onClick={() => handleInitiatePayment(registration.id)}
                              className="pay-button"
                              disabled={processingPayment[registration.id]}
                            >
                              {processingPayment[registration.id] ? 'Processing...' : 'Pay Now'}
                            </button>
                          )}
                          {registration.status === 'PAYMENT_PENDING' && (
                            <button
                              onClick={() => handleConfirmPayment(registration.id)}
                              className="confirm-payment-button"
                              disabled={processingPayment[registration.id]}
                            >
                              {processingPayment[registration.id] ? 'Processing...' : 'Confirm Payment'}
                            </button>
                          )}
                          {paymentSuccess[registration.id] === 'initiated' && (
                            <span className="success-message-small">✓ Payment initiated</span>
                          )}
                          {paymentSuccess[registration.id] === 'confirmed' && (
                            <span className="success-message-small">✓ Payment confirmed</span>
                          )}
                        </div>
                        <button
                          onClick={() => handleViewExam(exam.id)}
                          className="view-exam-button"
                        >
                          View Exam Details →
                        </button>
                      </div>
                    </>
                  ) : (
                    <div className="exam-loading">
                      <p>Loading exam details...</p>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}

        <div className="registrations-actions">
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </div>
      </div>
    </div>
  )
}

export default MyRegistrations

