import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import './Profile.css'

const Profile = () => {
  const { user, updateMobile, logout, loading } = useAuth()
  const navigate = useNavigate()
  const [mobile, setMobile] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    if (user?.mobile) {
      setMobile(user.mobile)
    }
  }, [user])

  const handleMobileSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setSubmitting(true)

    if (!mobile || mobile.length !== 10) {
      setError('Mobile number must be exactly 10 digits')
      setSubmitting(false)
      return
    }

    const result = await updateMobile(mobile)
    setSubmitting(false)

    if (result.success) {
      setSuccess('Mobile number updated successfully!')
    } else {
      setError(result.error || 'Failed to update mobile number')
    }
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading...</p>
      </div>
    )
  }

  return (
    <div className="profile-container">
      <div className="profile-card">
        <div className="profile-header">
          <h1>Radhe Radhe! 🙏</h1>
          <h2>Your Profile</h2>
        </div>

        <div className="profile-info">
          <div className="info-item">
            <label>Email:</label>
            <span>{user?.email}</span>
          </div>
          <div className="info-item">
            <label>Name:</label>
            <span>{user?.name}</span>
          </div>
          <div className="info-item">
            <label>Role:</label>
            <span>{user?.role}</span>
          </div>
          <div className="info-item">
            <label>Profile Status:</label>
            <span className={user?.is_profile_complete ? 'complete' : 'incomplete'}>
              {user?.is_profile_complete ? '✓ Complete' : '✗ Incomplete'}
            </span>
          </div>
        </div>

        {!user?.is_profile_complete && (
          <div className="mobile-section">
            <h3>Complete Your Profile</h3>
            <p className="section-description">
              Please provide your 10-digit mobile number to complete your profile.
            </p>

            <form onSubmit={handleMobileSubmit} className="mobile-form">
              <div className="form-group">
                <label htmlFor="mobile">Mobile Number</label>
                <input
                  type="tel"
                  id="mobile"
                  value={mobile}
                  onChange={(e) => {
                    const value = e.target.value.replace(/\D/g, '')
                    if (value.length <= 10) {
                      setMobile(value)
                    }
                  }}
                  placeholder="1234567890"
                  maxLength={10}
                  required
                  disabled={submitting}
                />
                <small>Enter exactly 10 digits</small>
              </div>

              {error && <div className="error-message">{error}</div>}
              {success && <div className="success-message">{success}</div>}

              <button type="submit" className="submit-button" disabled={submitting}>
                {submitting ? 'Updating...' : 'Update Mobile Number'}
              </button>
            </form>
          </div>
        )}

        {user?.is_profile_complete && user?.mobile && (
          <div className="mobile-section">
            <div className="info-item">
              <label>Mobile Number:</label>
              <span>{user.mobile}</span>
            </div>
          </div>
        )}

        <div className="profile-actions">
          {user?.is_profile_complete && (
            <>
              <button onClick={() => navigate('/exams')} className="primary-button">
                View Exams →
              </button>
              {user?.role === 'USER' && (
                <button onClick={() => navigate('/registrations')} className="secondary-button">
                  My Registrations →
                </button>
              )}
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

export default Profile

