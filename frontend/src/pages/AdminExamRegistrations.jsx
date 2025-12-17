import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { examService, registrationService, enrollmentService, exportService } from '../services/examService'
import './AdminExamRegistrations.css'

const AdminExamRegistrations = () => {
  const { examId } = useParams()
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [exam, setExam] = useState(null)
  const [registrations, setRegistrations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [enrolling, setEnrolling] = useState(false)
  const [enrollingId, setEnrollingId] = useState(null)
  const [bulkEnrolling, setBulkEnrolling] = useState(false)
  const [selectedRegistrations, setSelectedRegistrations] = useState(new Set())
  const [enrollmentMessage, setEnrollmentMessage] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [exporting, setExporting] = useState(false)

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

  const handleEnrollSingle = async (registrationId) => {
    setError('')
    setEnrollmentMessage('')
    setEnrolling(true)
    setEnrollingId(registrationId)

    try {
      await enrollmentService.enrollRegistration(registrationId)
      setEnrollmentMessage('Registration enrolled successfully!')
      // Refresh registrations
      await fetchData()
      setTimeout(() => setEnrollmentMessage(''), 3000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to enroll registration')
      console.error('Error enrolling registration:', err)
    } finally {
      setEnrolling(false)
      setEnrollingId(null)
    }
  }

  const handleBulkEnroll = async () => {
    if (selectedRegistrations.size === 0) {
      setError('Please select at least one registration to enroll')
      return
    }

    setError('')
    setEnrollmentMessage('')
    setBulkEnrolling(true)

    try {
      const registrationIds = Array.from(selectedRegistrations)
      const result = await enrollmentService.bulkEnrollRegistrations(registrationIds)
      
      const successCount = result.success.length
      const failedCount = result.failed.length
      
      if (failedCount === 0) {
        setEnrollmentMessage(`Successfully enrolled ${successCount} registration(s)!`)
      } else {
        setEnrollmentMessage(
          `Enrolled ${successCount} registration(s). ${failedCount} failed.`
        )
        if (result.failed.length > 0) {
          const failedReasons = result.failed
            .map(f => `Registration ${f.registration_id.slice(0, 8)}...: ${f.reason}`)
            .join('\n')
          console.warn('Failed enrollments:', failedReasons)
        }
      }
      
      // Refresh registrations
      await fetchData()
      setSelectedRegistrations(new Set())
      setTimeout(() => setEnrollmentMessage(''), 5000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to bulk enroll registrations')
      console.error('Error bulk enrolling:', err)
    } finally {
      setBulkEnrolling(false)
    }
  }

  const handleToggleSelection = (registrationId) => {
    const newSelection = new Set(selectedRegistrations)
    if (newSelection.has(registrationId)) {
      newSelection.delete(registrationId)
    } else {
      newSelection.add(registrationId)
    }
    setSelectedRegistrations(newSelection)
  }

  const handleSelectAll = () => {
    // Only select from filtered (visible) registrations
    const enrollableRegistrations = filteredRegistrations
      .filter(reg => canEnroll(reg.status))
      .map(reg => reg.registration_id)
    
    // Check if all visible enrollable are selected
    const allSelected = enrollableRegistrations.every(id => selectedRegistrations.has(id))
    
    if (allSelected) {
      // Deselect all visible enrollable
      const newSelection = new Set(selectedRegistrations)
      enrollableRegistrations.forEach(id => newSelection.delete(id))
      setSelectedRegistrations(newSelection)
    } else {
      // Select all visible enrollable
      const newSelection = new Set(selectedRegistrations)
      enrollableRegistrations.forEach(id => newSelection.add(id))
      setSelectedRegistrations(newSelection)
    }
  }

  const getStatusBadgeClass = (status) => {
    const statusLower = status.toLowerCase().replace('_', '-')
    return `status-badge-small ${statusLower}`
  }

  const canEnroll = (status) => {
    return ['REGISTERED', 'PAYMENT_PENDING', 'PAID'].includes(status)
  }

  const handleExportCSV = async () => {
    setError('')
    setExporting(true)

    try {
      await exportService.exportExamRegistrations(examId)
      setEnrollmentMessage('CSV exported successfully!')
      setTimeout(() => setEnrollmentMessage(''), 3000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to export CSV')
      console.error('Error exporting CSV:', err)
    } finally {
      setExporting(false)
    }
  }

  // Filter registrations based on search query
  const filteredRegistrations = registrations.filter((registration) => {
    if (!searchQuery.trim()) {
      return true
    }
    
    const query = searchQuery.toLowerCase().trim()
    const email = registration.user.email?.toLowerCase() || ''
    const name = registration.user.name?.toLowerCase() || ''
    const mobile = registration.user.mobile?.toLowerCase() || ''
    
    return email.includes(query) || name.includes(query) || mobile.includes(query)
  })

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
            <div className="exam-info-left">
              <h3>{exam.title}</h3>
              <span className={`status-badge ${exam.status.toLowerCase()}`}>
                {exam.status}
              </span>
            </div>
            <button
              onClick={handleExportCSV}
              className="export-csv-button"
              disabled={exporting}
            >
              {exporting ? 'Exporting...' : '📥 Export CSV'}
            </button>
          </div>
        )}

        {error && <div className="error-message">{error}</div>}
        {enrollmentMessage && <div className="success-message">{enrollmentMessage}</div>}

        {registrations.length === 0 ? (
          <div className="no-registrations">
            <p>No registrations found for this exam.</p>
          </div>
        ) : (
          <div className="registrations-section">
            <div className="search-section">
              <div className="search-container">
                <input
                  type="text"
                  placeholder="Search by email, name, or mobile number..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="search-input"
                />
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery('')}
                    className="clear-search-button"
                    title="Clear search"
                  >
                    ✕
                  </button>
                )}
              </div>
              {searchQuery && (
                <div className="search-results-info">
                  Showing {filteredRegistrations.length} of {registrations.length} registrations
                </div>
              )}
            </div>
            <div className="registrations-header">
              <h3>Registered Users ({filteredRegistrations.length})</h3>
              {filteredRegistrations.some(reg => canEnroll(reg.status)) && (
                <div className="bulk-actions">
                  <button
                    onClick={handleSelectAll}
                    className="select-all-button"
                    disabled={bulkEnrolling}
                  >
                    {selectedRegistrations.size > 0 ? 'Deselect All' : 'Select All Enrollable'}
                  </button>
                  {selectedRegistrations.size > 0 && (
                    <button
                      onClick={handleBulkEnroll}
                      className="bulk-enroll-button"
                      disabled={bulkEnrolling}
                    >
                      {bulkEnrolling ? 'Enrolling...' : `Enroll Selected (${selectedRegistrations.size})`}
                    </button>
                  )}
                </div>
              )}
            </div>
            {filteredRegistrations.length === 0 ? (
              <div className="no-search-results">
                <p>No registrations found matching "{searchQuery}"</p>
                <button
                  onClick={() => setSearchQuery('')}
                  className="clear-search-link"
                >
                  Clear search
                </button>
              </div>
            ) : (
              <div className="registrations-table">
                <table>
                  <thead>
                    <tr>
                      {filteredRegistrations.some(reg => canEnroll(reg.status)) && <th>Select</th>}
                    <th>Name</th>
                    <th>Email</th>
                    <th>Mobile</th>
                    <th>Status</th>
                    <th>Registered At</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredRegistrations.map((registration) => (
                    <tr key={registration.registration_id}>
                      {filteredRegistrations.some(reg => canEnroll(reg.status)) && (
                        <td>
                          {canEnroll(registration.status) && (
                            <input
                              type="checkbox"
                              checked={selectedRegistrations.has(registration.registration_id)}
                              onChange={() => handleToggleSelection(registration.registration_id)}
                              disabled={bulkEnrolling || enrolling}
                            />
                          )}
                        </td>
                      )}
                      <td>{registration.user.name}</td>
                      <td>{registration.user.email}</td>
                      <td>{registration.user.mobile || 'N/A'}</td>
                      <td>
                        <span className={getStatusBadgeClass(registration.status)}>
                          {registration.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td>{formatDate(registration.registered_at)}</td>
                      <td>
                        {canEnroll(registration.status) && (
                          <button
                            onClick={() => handleEnrollSingle(registration.registration_id)}
                            className="enroll-button"
                            disabled={enrolling || bulkEnrolling || enrollingId === registration.registration_id}
                          >
                            {enrolling && enrollingId === registration.registration_id
                              ? 'Enrolling...'
                              : 'Enroll'}
                          </button>
                        )}
                        {registration.status === 'ENROLLED' && (
                          <span className="enrolled-badge">✓ Enrolled</span>
                        )}
                      </td>
                    </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
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

