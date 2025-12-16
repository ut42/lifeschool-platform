import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { examService, registrationService } from '../services/examService'
import './AdminExamRegistrations.css'

const AdminExamRegistrations = () => {
  const { examId } = useParams()
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [exam, setExam] = useState(null)
  const [registrations, setRegistrations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (user?.role !== 'ADMIN') {
      navigate('/exams')
      return
    }
    fetchData()
  }, [examId, user])

  const fetchData = async () => {
    try {
      setLoading(true)
      setError('')
      
      // Fetch exam details
      const examData = await examService.getExamById(examId)
      setExam(examData)
      
      // Fetch registrations
      const regs = await registrationService.getExamRegistrations(examId)
      setRegistrations(regs)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch registrations')
      console.error('Error fetching data:', err)
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

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading registrations...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="error-container">
        <h2>Error</h2>
        <p>{error}</p>
        <button onClick={() => navigate(`/exams/${examId}`)} className="back-button">
          Go Back to Exam
        </button>
      </div>
    )
  }

  return (
    <div className="admin-registrations-container">
      <div className="admin-registrations-card">
        <div className="admin-registrations-header">
          <h1>Radhe Radhe! 🙏</h1>
          <h2>Exam Registrations</h2>
        </div>

        <div className="navigation-links">
          <button onClick={() => navigate(`/exams/${examId}`)} className="nav-link">
            ← Back to Exam Details
          </button>
        </div>

        {exam && (
          <div className="exam-info-section">
            <h3>{exam.title}</h3>
            <span className={`status-badge ${exam.status.toLowerCase()}`}>
              {exam.status}
            </span>
          </div>
        )}

        {registrations.length === 0 ? (
          <div className="no-registrations">
            <p>No registrations found for this exam.</p>
          </div>
        ) : (
          <div className="registrations-section">
            <div className="registrations-header">
              <h3>Registered Users ({registrations.length})</h3>
            </div>
            <div className="registrations-table">
              <table>
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Mobile</th>
                    <th>Status</th>
                    <th>Registered At</th>
                  </tr>
                </thead>
                <tbody>
                  {registrations.map((registration) => (
                    <tr key={registration.registration_id}>
                      <td>{registration.user.name}</td>
                      <td>{registration.user.email}</td>
                      <td>{registration.user.mobile || 'N/A'}</td>
                      <td>
                        <span className="status-badge-small registered">
                          {registration.status}
                        </span>
                      </td>
                      <td>{formatDate(registration.registered_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        <div className="admin-registrations-actions">
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </div>
      </div>
    </div>
  )
}

export default AdminExamRegistrations

