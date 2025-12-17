import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { contentService } from '../services/contentService'
import './Courses.css'

function Courses() {
  const [courses, setCourses] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function fetchCourses() {
      try {
        setLoading(true)
        const data = await contentService.listContent('COURSE')
        setCourses(data)
        setError(null)
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to load courses')
      } finally {
        setLoading(false)
      }
    }
    fetchCourses()
  }, [])

  if (loading) {
    return <div className="courses-container"><div className="loading">Loading courses...</div></div>
  }

  if (error) {
    return <div className="courses-container"><div className="error">Error: {error}</div></div>
  }

  return (
    <div className="courses-container">
      <h1>Courses</h1>
      {courses.length === 0 ? (
        <p className="no-content">No courses available at the moment.</p>
      ) : (
        <div className="courses-grid">
          {courses.map((course) => (
            <Link key={course.id} to={`/courses/${course.id}`} className="course-card">
              <h3>{course.title}</h3>
              <p className="course-preview">{course.body.substring(0, 150)}...</p>
              <div className="course-meta">
                <span className="course-type">Course</span>
                <span className="course-date">
                  {new Date(course.created_at).toLocaleDateString()}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

export default Courses

