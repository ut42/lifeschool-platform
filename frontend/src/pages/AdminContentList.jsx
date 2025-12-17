import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { adminContentService } from '../services/contentService'
import { useAuth } from '../contexts/AuthContext'
import './AdminContentList.css'

function AdminContentList() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [contentType, setContentType] = useState('COURSE')
  const [contents, setContents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [publishing, setPublishing] = useState(null)

  useEffect(() => {
    if (user?.role !== 'ADMIN') {
      navigate('/')
      return
    }
    fetchContent()
  }, [contentType, user, navigate])

  async function fetchContent() {
    try {
      setLoading(true)
      const data = await adminContentService.listContent(contentType)
      setContents(data)
      setError(null)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load content')
    } finally {
      setLoading(false)
    }
  }

  async function handlePublish(contentId) {
    try {
      setPublishing(contentId)
      await adminContentService.publishContent(contentId)
      await fetchContent()
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to publish content')
    } finally {
      setPublishing(null)
    }
  }

  if (loading) {
    return <div className="admin-content-container"><div className="loading">Loading...</div></div>
  }

  return (
    <div className="admin-content-container">
      <div className="admin-content-header">
        <h1>Content Management</h1>
        <Link to="/admin/content/create" className="create-button">
          + Create Content
        </Link>
      </div>

      <div className="content-type-selector">
        <button
          className={contentType === 'COURSE' ? 'active' : ''}
          onClick={() => setContentType('COURSE')}
        >
          Courses
        </button>
        <button
          className={contentType === 'BLOG' ? 'active' : ''}
          onClick={() => setContentType('BLOG')}
        >
          Blogs
        </button>
        <button
          className={contentType === 'GALLERY' ? 'active' : ''}
          onClick={() => setContentType('GALLERY')}
        >
          Gallery
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      <div className="content-list">
        {contents.length === 0 ? (
          <p className="no-content">No {contentType.toLowerCase()} content yet.</p>
        ) : (
          contents.map((content) => (
            <div key={content.id} className="content-item">
              <div className="content-info">
                <h3>{content.title}</h3>
                <p className="content-preview">{content.body.substring(0, 150)}...</p>
                <div className="content-meta">
                  <span className={`status-badge ${content.status.toLowerCase()}`}>
                    {content.status}
                  </span>
                  <span className="content-date">
                    {new Date(content.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
              <div className="content-actions">
                {content.status === 'DRAFT' && (
                  <>
                    <Link
                      to={`/admin/content/${content.id}/edit`}
                      className="edit-button"
                    >
                      Edit
                    </Link>
                    <button
                      onClick={() => handlePublish(content.id)}
                      disabled={publishing === content.id}
                      className="publish-button"
                    >
                      {publishing === content.id ? 'Publishing...' : 'Publish'}
                    </button>
                  </>
                )}
                {content.status === 'PUBLISHED' && (
                  <span className="published-badge">Published</span>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default AdminContentList

