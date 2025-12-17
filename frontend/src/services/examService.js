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

export const registrationService = {
  // Register for an exam (USER only)
  async registerForExam(examId) {
    const response = await api.post(`/exams/${examId}/register`)
    return response.data
  },

  // Get user's registrations
  async getMyRegistrations() {
    const response = await api.get('/auth/me/registrations')
    return response.data
  },

  // Get exam registrations (ADMIN only)
  async getExamRegistrations(examId) {
    const response = await api.get(`/admin/exams/${examId}/registrations`)
    return response.data
  },

  // Get registration count for an exam (ADMIN only)
  async getExamRegistrationCount(examId) {
    const response = await api.get(`/admin/exams/${examId}/registrations`)
    return response.data.length
  },
}

export const paymentService = {
  // Initiate payment for a registration (USER only)
  async initiatePayment(registrationId) {
    const response = await api.post(`/payments/registrations/${registrationId}/pay`)
    return response.data
  },

  // Confirm payment (mocked) (USER only)
  async confirmPayment(registrationId) {
    const response = await api.post(`/payments/${registrationId}/confirm`)
    return response.data
  },
}

export const enrollmentService = {
  // Enroll a single registration (ADMIN only)
  async enrollRegistration(registrationId) {
    const response = await api.post(`/admin/registrations/${registrationId}/enroll`)
    return response.data
  },

  // Bulk enroll multiple registrations (ADMIN only)
  async bulkEnrollRegistrations(registrationIds) {
    const response = await api.post('/admin/registrations/enroll/bulk', {
      registration_ids: registrationIds,
    })
    return response.data
  },
}

export const exportService = {
  // Export exam registrations as CSV (ADMIN only)
  async exportExamRegistrations(examId) {
    const response = await api.get(`/admin/exams/${examId}/registrations/export`, {
      responseType: 'blob', // Important for file download
    })
    
    // Create blob URL and trigger download
    const blob = new Blob([response.data], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `exam_${examId}_registrations.csv`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    
    return true
  },
}

export default examService
