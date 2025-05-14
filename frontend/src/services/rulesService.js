import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const getAuthHeader = () => {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
};

export const rulesService = {
    // Get all rules
    getAllRules: async () => {
        try {
            const response = await axios.get(`${API_URL}/api/rules`, {
                headers: getAuthHeader()
            });
            return response.data;
        } catch (error) {
            throw error.response?.data || error.message;
        }
    },

    // Create a new rule
    createRule: async (ruleData) => {
        try {
            const response = await axios.post(`${API_URL}/api/rules`, ruleData, {
                headers: getAuthHeader()
            });
            return response.data;
        } catch (error) {
            throw error.response?.data || error.message;
        }
    },

    // Update an existing rule
    updateRule: async (ruleId, ruleData) => {
        try {
            const response = await axios.put(`${API_URL}/api/rules/${ruleId}`, ruleData, {
                headers: getAuthHeader()
            });
            return response.data;
        } catch (error) {
            throw error.response?.data || error.message;
        }
    },

    // Delete a rule
    deleteRule: async (ruleId) => {
        try {
            const response = await axios.delete(`${API_URL}/api/rules/${ruleId}`, {
                headers: getAuthHeader()
            });
            return response.data;
        } catch (error) {
            throw error.response?.data || error.message;
        }
    },

    // Get rule by ID
    getRuleById: async (ruleId) => {
        try {
            const response = await axios.get(`${API_URL}/api/rules/${ruleId}`, {
                headers: getAuthHeader()
            });
            return response.data;
        } catch (error) {
            throw error.response?.data || error.message;
        }
    }
}; 