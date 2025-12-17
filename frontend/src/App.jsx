import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Profile from './pages/Profile'
import Exams from './pages/Exams'
import CreateExam from './pages/CreateExam'
import ExamDetails from './pages/ExamDetails'
import EditExam from './pages/EditExam'
import MyRegistrations from './pages/MyRegistrations'
import AdminExamRegistrations from './pages/AdminExamRegistrations'
import Courses from './pages/Courses'
import Blogs from './pages/Blogs'
import Gallery from './pages/Gallery'
import AdminContentList from './pages/AdminContentList'
import AdminContentEdit from './pages/AdminContentEdit'
import ProtectedRoute from './components/ProtectedRoute'
import './App.css'

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="app">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <Profile />
                </ProtectedRoute>
              }
            />
            <Route
              path="/exams"
              element={
                <ProtectedRoute>
                  <Exams />
                </ProtectedRoute>
              }
            />
            <Route
              path="/exams/create"
              element={
                <ProtectedRoute>
                  <CreateExam />
                </ProtectedRoute>
              }
            />
            <Route
              path="/exams/:examId"
              element={
                <ProtectedRoute>
                  <ExamDetails />
                </ProtectedRoute>
              }
            />
            <Route
              path="/exams/:examId/edit"
              element={
                <ProtectedRoute>
                  <EditExam />
                </ProtectedRoute>
              }
            />
            <Route
              path="/registrations"
              element={
                <ProtectedRoute>
                  <MyRegistrations />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/exams/:examId/registrations"
              element={
                <ProtectedRoute adminOnly>
                  <AdminExamRegistrations />
                </ProtectedRoute>
              }
            />
            {/* Public Content Routes */}
            <Route path="/courses" element={<Courses />} />
            <Route path="/blogs" element={<Blogs />} />
            <Route path="/gallery" element={<Gallery />} />
            {/* Admin Content Routes */}
            <Route
              path="/admin/content"
              element={
                <ProtectedRoute adminOnly>
                  <AdminContentList />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/content/create"
              element={
                <ProtectedRoute adminOnly>
                  <AdminContentEdit />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/content/:id/edit"
              element={
                <ProtectedRoute adminOnly>
                  <AdminContentEdit />
                </ProtectedRoute>
              }
            />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  )
}

export default App

