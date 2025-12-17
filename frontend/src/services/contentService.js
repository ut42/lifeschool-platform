import { api } from './api'

export const contentService = {
  // List published content (public access)
  async listContent(type) {
    const response = await api.get(`/content?type=${type}`)
    return response.data
  },

  // Get published content by ID (public access)
  async getContentById(contentId) {
    const response = await api.get(`/content/${contentId}`)
    return response.data
  },
}

export const adminContentService = {
  // List all content for admin (DRAFT + PUBLISHED)
  async listContent(type) {
    const response = await api.get(`/admin/content?type=${type}`)
    return response.data
  },

  // Create content (ADMIN only)
  async createContent(contentData) {
    const response = await api.post('/admin/content', contentData)
    return response.data
  },

  // Update content (ADMIN only, only DRAFT)
  async updateContent(contentId, contentData) {
    const response = await api.put(`/admin/content/${contentId}`, contentData)
    return response.data
  },

  // Publish content (ADMIN only)
  async publishContent(contentId) {
    const response = await api.post(`/admin/content/${contentId}/publish`)
    return response.data
  },
}

export default contentService

