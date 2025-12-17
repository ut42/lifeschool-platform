import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { contentService } from '../services/contentService'
import './Blogs.css'

function Blogs() {
  const [blogs, setBlogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function fetchBlogs() {
      try {
        setLoading(true)
        const data = await contentService.listContent('BLOG')
        setBlogs(data)
        setError(null)
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to load blogs')
      } finally {
        setLoading(false)
      }
    }
    fetchBlogs()
  }, [])

  if (loading) {
    return <div className="blogs-container"><div className="loading">Loading blogs...</div></div>
  }

  if (error) {
    return <div className="blogs-container"><div className="error">Error: {error}</div></div>
  }

  return (
    <div className="blogs-container">
      <h1>Blogs</h1>
      {blogs.length === 0 ? (
        <p className="no-content">No blogs available at the moment.</p>
      ) : (
        <div className="blogs-list">
          {blogs.map((blog) => (
            <Link key={blog.id} to={`/blogs/${blog.id}`} className="blog-card">
              <h3>{blog.title}</h3>
              <p className="blog-preview">{blog.body.substring(0, 200)}...</p>
              <div className="blog-meta">
                <span className="blog-type">Blog</span>
                <span className="blog-date">
                  {new Date(blog.created_at).toLocaleDateString()}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

export default Blogs

