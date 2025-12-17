import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { contentService } from '../services/contentService'
import './Gallery.css'

function Gallery() {
  const [galleryItems, setGalleryItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function fetchGallery() {
      try {
        setLoading(true)
        const data = await contentService.listContent('GALLERY')
        setGalleryItems(data)
        setError(null)
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to load gallery')
      } finally {
        setLoading(false)
      }
    }
    fetchGallery()
  }, [])

  if (loading) {
    return <div className="gallery-container"><div className="loading">Loading gallery...</div></div>
  }

  if (error) {
    return <div className="gallery-container"><div className="error">Error: {error}</div></div>
  }

  return (
    <div className="gallery-container">
      <h1>Gallery</h1>
      {galleryItems.length === 0 ? (
        <p className="no-content">No gallery items available at the moment.</p>
      ) : (
        <div className="gallery-grid">
          {galleryItems.map((item) => (
            <Link key={item.id} to={`/gallery/${item.id}`} className="gallery-card">
              <h3>{item.title}</h3>
              <p className="gallery-preview">{item.body.substring(0, 100)}...</p>
              <div className="gallery-meta">
                <span className="gallery-type">Gallery</span>
                <span className="gallery-date">
                  {new Date(item.created_at).toLocaleDateString()}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

export default Gallery

