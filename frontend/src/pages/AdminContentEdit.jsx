import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { adminContentService } from '../services/contentService'
import { useAuth } from '../contexts/AuthContext'
import './AdminContentEdit.css'

function AdminContentEdit() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  const isEdit = !!id

  const [formData, setFormData] = useState({
    title: '',
    body: '',
    content_type: 'COURSE',
    metadata: '{}',
    seo_meta: '{}',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (user?.role !== 'ADMIN') {
      navigate('/')
      return
    }
    if (isEdit) {
      // Load existing content for editing
      // Note: We'd need a get endpoint for admin to fetch by ID
      // For now, we'll just show the form
    }
  }, [id, user, navigate, isEdit])

  function handleChange(e) {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      let metadata = {}
      let seo_meta = {}
      
      try {
        metadata = JSON.parse(formData.metadata || '{}')
      } catch {
        throw new Error('Invalid JSON in metadata field')
      }
      
      try {
        seo_meta = JSON.parse(formData.seo_meta || '{}')
      } catch {
        throw new Error('Invalid JSON in seo_meta field')
      }

      if (isEdit) {
        await adminContentService.updateContent(id, {
          title: formData.title,
          body: formData.body,
          metadata,
          seo_meta,
        })
      } else {
        await adminContentService.createContent({
          title: formData.title,
          body: formData.body,
          content_type: formData.content_type,
          metadata,
          seo_meta,
        })
      }
      navigate('/admin/content')
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to save content')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="admin-content-edit-container">
      <h1>{isEdit ? 'Edit Content' : 'Create Content'}</h1>

      {error && <div className="error">{error}</div>}

      <form onSubmit={handleSubmit} className="content-form">
        {!isEdit && (
          <div className="form-group">
            <label htmlFor="content_type">Content Type</label>
            <select
              id="content_type"
              name="content_type"
              value={formData.content_type}
              onChange={handleChange}
              required
            >
              <option value="COURSE">Course</option>
              <option value="BLOG">Blog</option>
              <option value="GALLERY">Gallery</option>
            </select>
          </div>
        )}

        <div className="form-group">
          <label htmlFor="title">Title</label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="body">Body</label>
          <textarea
            id="body"
            name="body"
            value={formData.body}
            onChange={handleChange}
            rows={10}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="metadata">Metadata (JSON)</label>
          <textarea
            id="metadata"
            name="metadata"
            value={formData.metadata}
            onChange={handleChange}
            rows={5}
            placeholder='{"key": "value"}'
          />
        </div>

        <div className="form-group">
          <label htmlFor="seo_meta">SEO Meta (JSON)</label>
          <textarea
            id="seo_meta"
            name="seo_meta"
            value={formData.seo_meta}
            onChange={handleChange}
            rows={5}
            placeholder='{"slug": "my-content", "description": "..."}'
          />
        </div>

        <div className="form-actions">
          <button type="button" onClick={() => navigate('/admin/content')} className="cancel-button">
            Cancel
          </button>
          <button type="submit" disabled={loading} className="submit-button">
            {loading ? 'Saving...' : isEdit ? 'Update' : 'Create'}
          </button>
        </div>
      </form>
    </div>
  )
}

export default AdminContentEdit

