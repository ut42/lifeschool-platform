import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { examService, registrationService, paymentService } from '../services/examService'
import './ExamDetails.css'

const ExamDetails = () => {
  const { examId } = useParams()
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [exam, setExam] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [registering, setRegistering] = useState(false)
  const [registrationSuccess, setRegistrationSuccess] = useState(false)
  const [isRegistered, setIsRegistered] = useState(false)
  const [registration, setRegistration] = useState(null)
  const [processingPayment, setProcessingPayment] = useState(false)
  const [paymentSuccess, setPaymentSuccess] = useState('')

  useEffect(() => {
    fetchExam()
    if (user?.role === 'USER') {
      checkRegistrationStatus()
    }
  }, [examId, user])

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

  const checkRegistrationStatus = async () => {
    try {
      const registrations = await registrationService.getMyRegistrations()
      const userRegistration = registrations.find(reg => reg.exam_id === examId)
      setIsRegistered(!!userRegistration)
      if (userRegistration) {
        setRegistration(userRegistration)
      } else {
        setRegistration(null)
      }
    } catch (err) {
      console.error('Error checking registration status:', err)
    }
  }

  const handleRegister = async () => {
    if (!user?.is_profile_complete) {
      setError('Please complete your profile (add mobile number) before registering for exams')
      return
    }

    setError('')
    setRegistrationSuccess(false)
    setRegistering(true)

    try {
      await registrationService.registerForExam(examId)
      setRegistrationSuccess(true)
      setIsRegistered(true)
      // Refresh registration status to get the new registration
      await checkRegistrationStatus()
      setTimeout(() => {
        setRegistrationSuccess(false)
      }, 3000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to register for exam')
      console.error('Error registering for exam:', err)
    } finally {
      setRegistering(false)
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

          {user?.role === 'USER' && exam?.status === 'ACTIVE' && (
            <div className="registration-section">
              {isRegistered ? (
                <div className="registration-status-container">
                  <div className="registration-status registered">
                    <span className="status-icon">✓</span>
                    <span>You are registered for this exam</span>
                  </div>
                  {registration && (
                    <div className="payment-actions">
                      <span className={`payment-status-badge ${registration.status.toLowerCase().replace('_', '-')}`}>
                        Status: {registration.status.replace('_', ' ')}
                      </span>
                      {registration.status === 'REGISTERED' && (
                        <button
                          onClick={async () => {
                            setProcessingPayment(true)
                            setPaymentSuccess('')
                            try {
                              await paymentService.initiatePayment(registration.id)
                              await checkRegistrationStatus()
                              setPaymentSuccess('initiated')
                              setTimeout(() => setPaymentSuccess(''), 3000)
                            } catch (err) {
                              setError(err.response?.data?.detail || 'Failed to initiate payment')
                            } finally {
                              setProcessingPayment(false)
                            }
                          }}
                          className="pay-button"
                          disabled={processingPayment}
                        >
                          {processingPayment ? 'Processing...' : 'Pay Now'}
                        </button>
                      )}
                      {registration.status === 'PAYMENT_PENDING' && (
                        <button
                          onClick={async () => {
                            setProcessingPayment(true)
                            setPaymentSuccess('')
                            try {
                              await paymentService.confirmPayment(registration.id)
                              await checkRegistrationStatus()
                              setPaymentSuccess('confirmed')
                              setTimeout(() => setPaymentSuccess(''), 3000)
                            } catch (err) {
                              setError(err.response?.data?.detail || 'Failed to confirm payment')
                            } finally {
                              setProcessingPayment(false)
                            }
                          }}
                          className="confirm-payment-button"
                          disabled={processingPayment}
                        >
                          {processingPayment ? 'Processing...' : 'Confirm Payment'}
                        </button>
                      )}
                      {paymentSuccess === 'initiated' && (
                        <span className="success-message-small">✓ Payment initiated</span>
                      )}
                      {paymentSuccess === 'confirmed' && (
                        <span className="success-message-small">✓ Payment confirmed</span>
                      )}
                    </div>
                  )}
                </div>
              ) : (
                <div className="registration-section-content">
                  {!user?.is_profile_complete && (
                    <div className="warning-message">
                      ⚠️ Please complete your profile (add mobile number) to register for exams
                    </div>
                  )}
                  <button
                    onClick={handleRegister}
                    className="register-button"
                    disabled={registering || !user?.is_profile_complete}
                  >
                    {registering ? 'Registering...' : 'Register for Exam'}
                  </button>
                </div>
              )}
              {registrationSuccess && (
                <div className="success-message">
                  ✓ Successfully registered for this exam!
                </div>
              )}
            </div>
          )}
        </div>

        <div className="exam-details-actions">
          {user?.role === 'ADMIN' && (
            <>
              <button onClick={() => navigate(`/exams/${examId}/edit`)} className="edit-button">
                Edit Exam
              </button>
              <button onClick={() => navigate(`/admin/exams/${examId}/registrations`)} className="view-registrations-button">
                View Registrations
              </button>
            </>
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

