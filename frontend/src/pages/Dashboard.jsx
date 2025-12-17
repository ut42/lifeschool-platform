import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import './Dashboard.css'

const Dashboard = () => {
  const { user, loading } = useAuth()
  const navigate = useNavigate()

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="spinner"></div>
        <p>Loading your dashboard...</p>
      </div>
    )
  }

  const isProfileComplete = user?.is_profile_complete && user?.mobile

  return (
    <div className="dashboard-container">
      <div className="dashboard-hero">
        <h1>Radhe Radhe! 🙏</h1>
        <h2>Welcome to LifeSchool</h2>
        <p>
          One place to explore <strong>courses</strong>, read <strong>blogs</strong>, browse the
          <strong> gallery</strong>, and manage your <strong>exams & registrations</strong>.
        </p>
      </div>

      {!isProfileComplete && (
        <div className="dashboard-notice">
          <p>
            Your profile is not complete yet. Please add your mobile number so that we can complete your
            registrations smoothly.
          </p>
          <button className="primary-button" onClick={() => navigate('/profile')}>
            Complete Profile →
          </button>
        </div>
      )}

      <div className="dashboard-grid">
        {/* Exams & Registrations */}
        <div className="dashboard-card exams" onClick={() => navigate('/exams')}>
          <h3>Exams</h3>
          <p>Browse available exams and register in a few clicks.</p>
          <span className="card-link">Go to Exams →</span>
        </div>

        <div className="dashboard-card registrations" onClick={() => navigate('/registrations')}>
          <h3>My Registrations</h3>
          <p>See all your exam registrations, status, and payments.</p>
          <span className="card-link">View Registrations →</span>
        </div>

        {/* CMS Public Content */}
        <div className="dashboard-card courses" onClick={() => navigate('/courses')}>
          <h3>Courses</h3>
          <p>Explore our curated learning paths and course content.</p>
          <span className="card-link">View Courses →</span>
        </div>

        <div className="dashboard-card blogs" onClick={() => navigate('/blogs')}>
          <h3>Blogs</h3>
          <p>Read insights, stories, and guidance from LifeSchool.</p>
          <span className="card-link">Read Blogs →</span>
        </div>

        <div className="dashboard-card gallery" onClick={() => navigate('/gallery')}>
          <h3>Gallery</h3>
          <p>Browse photos and moments from our events and sessions.</p>
          <span className="card-link">Open Gallery →</span>
        </div>

        {/* Profile */}
        <div className="dashboard-card profile" onClick={() => navigate('/profile')}>
          <h3>My Profile</h3>
          <p>View your details and update your mobile number anytime.</p>
          <span className="card-link">Go to Profile →</span>
        </div>

        {/* Admin-only CMS management */}
        {user?.role === 'ADMIN' && (
          <div className="dashboard-card admin" onClick={() => navigate('/admin/content')}>
            <h3>Content Management</h3>
            <p>Create and publish courses, blogs, and gallery items.</p>
            <span className="card-link">Manage Content →</span>
          </div>
        )}
      </div>
    </div>
  )
}

export default Dashboard

