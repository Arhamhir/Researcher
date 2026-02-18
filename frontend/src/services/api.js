import axios from 'axios';

// Use relative paths so Vite proxy can intercept
const api = axios.create({
  baseURL: '/',
  headers: {
    'Content-Type': 'application/json',
  },
});

// API endpoints
export const paperAPI = {
  // Check backend status
  checkStatus: async () => {
    const response = await api.get('/api/status');
    return response.data;
  },

  // Upload PDF for review
  uploadPaper: async (file, onUploadProgress) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });
    return response.data;
  },

  // Get review results
  getReview: async (paperId) => {
    const response = await api.get(`/api/review/${paperId}`);
    return response.data;
  },

  // Poll review status (for processing page)
  pollReviewStatus: async (paperId) => {
    try {
      const response = await api.get(`/api/review/${paperId}/status`);
      return response.data;
    } catch (error) {
      if (error.response?.status === 404) {
        return { status: 'processing' };
      }
      throw error;
    }
  },
};

export default api;
