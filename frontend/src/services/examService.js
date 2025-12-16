import { api } from './api'

export const examService = {
  // List exams (USER sees only ACTIVE, ADMIN sees all)
  async listExams() {
    const response = await api.get('/exams')
    return response.data
  },

  // Get exam by ID
  async getExamById(examId) {
    const response = await api.get(`/exams/${examId}`)
    return response.data
  },

  // Create exam (ADMIN only)
  async createExam(examData) {
    const response = await api.post('/exams/admin', examData)
    return response.data
  },

  // Update exam (ADMIN only)
  async updateExam(examId, examData) {
    const response = await api.put(`/exams/${examId}`, examData)
    return response.data
  },
}

export default examService

