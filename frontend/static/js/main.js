/**
 * Kanoon Ki Pechaan - Main JavaScript
 * Common utilities and functionality
 */

// Global variables
window.API_BASE_URL = window.location.origin + '/api';
window.currentUser = null;

// Utility Functions
const Utils = {
    // Show loading overlay
    showLoading() {
        document.getElementById('loadingOverlay').classList.remove('d-none');
    },

    // Hide loading overlay
    hideLoading() {
        document.getElementById('loadingOverlay').classList.add('d-none');
    },

    // Show alert message
    showAlert(message, type = 'info', duration = 5000) {
        const alertContainer = document.getElementById('alertContainer');
        const alertId = 'alert-' + Date.now();
        
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert" id="${alertId}">
                <i class="fas fa-${this.getAlertIcon(type)} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        alertContainer.innerHTML = alertHtml + alertContainer.innerHTML;
        
        // Auto-dismiss after duration
        if (duration > 0) {
            setTimeout(() => {
                const alertElement = document.getElementById(alertId);
                if (alertElement) {
                    const alert = new bootstrap.Alert(alertElement);
                    alert.close();
                }
            }, duration);
        }
    },

    // Get alert icon based on type
    getAlertIcon(type) {
        const icons = {
            'success': 'check-circle',
            'danger': 'exclamation-triangle',
            'warning': 'exclamation-circle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    },

    // Format date
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    // Format file size
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    // Truncate text
    truncateText(text, maxLength = 150) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    },

    // Validate email
    validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },

    // Validate password
    validatePassword(password) {
        if (password.length < 6) {
            return { valid: false, message: 'Password must be at least 6 characters long' };
        }
        return { valid: true, message: 'Password is valid' };
    },

    // Debounce function
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Copy to clipboard
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showAlert('Copied to clipboard!', 'success', 2000);
        } catch (err) {
            this.showAlert('Failed to copy to clipboard', 'danger');
        }
    },

    // Escape HTML to prevent XSS
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};

// API Helper Functions
const API = {
    // Make API request
    async request(endpoint, options = {}) {
        const url = `${window.API_BASE_URL}${endpoint}`;
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include'
        };

        const requestOptions = { ...defaultOptions, ...options };

        // Add JSON body if data is provided
        if (options.data) {
            requestOptions.body = JSON.stringify(options.data);
        }

        try {
            const response = await fetch(url, requestOptions);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || `HTTP error! status: ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },

    // GET request
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    },

    // POST request
    async post(endpoint, data) {
        return this.request(endpoint, { 
            method: 'POST',
            data
        });
    },

    // PUT request
    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            data
        });
    },

    // DELETE request
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    },

    // File upload
    async uploadFile(endpoint, formData) {
        const url = `${window.API_BASE_URL}${endpoint}`;
        
        try {
            const response = await fetch(url, {
                method: 'POST',
                body: formData,
                credentials: 'include'
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || `HTTP error! status: ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error('File upload failed:', error);
            throw error;
        }
    },

    // Authentication APIs
    async login(credentials) {
        return this.post('/auth/login', credentials);
    },

    async register(userData) {
        return this.post('/auth/register', userData);
    },

    async getUserProfile() {
        return this.get('/auth/profile');
    },

    async updateProfile(profileData) {
        return this.put('/auth/profile', profileData);
    },

    async changePassword(passwordData) {
        return this.put('/auth/change-password', passwordData);
    },

    // Document APIs
    async getDocuments() {
        return this.get('/documents');
    },

    async getDocument(documentId) {
        return this.get(`/documents/${documentId}`);
    },

    async uploadDocument(formData, onProgress) {
        const url = `${window.API_BASE_URL}/documents/upload`;
        
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable && onProgress) {
                    const percentage = Math.round((e.loaded / e.total) * 100);
                    onProgress(percentage);
                }
            });
            
            xhr.addEventListener('load', () => {
                try {
                    const data = JSON.parse(xhr.responseText);
                    if (xhr.status >= 200 && xhr.status < 300) {
                        resolve(data);
                    } else {
                        reject(new Error(data.message || `HTTP error! status: ${xhr.status}`));
                    }
                } catch (error) {
                    reject(error);
                }
            });
            
            xhr.addEventListener('error', () => {
                reject(new Error('Upload failed'));
            });
            
            xhr.open('POST', url);
            xhr.withCredentials = true;
            xhr.send(formData);
        });
    },

    async analyzeDocument(documentId) {
        return this.post(`/documents/${documentId}/analyze`);
    },

    async deleteDocument(documentId) {
        return this.delete(`/documents/${documentId}`);
    },

    // Chatbot APIs
    async getChatSessions() {
        return this.get('/chatbot/sessions');
    },

    async getChatSession(sessionId) {
        return this.get(`/chatbot/sessions/${sessionId}`);
    },

    async createChatSession() {
        return this.post('/chatbot/sessions');
    },

    async sendMessage(sessionId, message) {
        return this.post(`/chatbot/sessions/${sessionId}/messages`, { message });
    },

    async deleteChatSession(sessionId) {
        return this.delete(`/chatbot/sessions/${sessionId}`);
    },

    // Lawyer Network APIs
    async searchLawyers(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.get(`/lawyers/search?${queryString}`);
    },

    async getLawyerProfile(lawyerId) {
        return this.get(`/lawyers/profile/${lawyerId}`);
    },

    async getLawyerSpecializations() {
        return this.get('/lawyers/specializations');
    },

    async connectWithLawyer(connectionData) {
        return this.post('/lawyers/connect', connectionData);
    },

    async getConnections() {
        return this.get('/lawyers/connections');
    },

    async respondToConnection(connectionId, response) {
        return this.put(`/lawyers/connections/${connectionId}/respond`, { response });
    },

    async getLawyerStats() {
        return this.get('/lawyers/stats');
    },

    async getFeaturedLawyers() {
        return this.get('/lawyers/featured');
    }
};

// Session Management
const Session = {
    // Check if user is authenticated
    async checkAuth() {
        try {
            const response = await API.get('/auth/verify');
            if (response.success && response.authenticated) {
                window.currentUser = response.user;
                this.updateNavbar(response.user);
                return true;
            } else {
                window.currentUser = null;
                return false;
            }
        } catch (error) {
            console.error('Auth check failed:', error);
            window.currentUser = null;
            return false;
        }
    },

    // Update navbar with user info
    updateNavbar(user) {
        const usernameElement = document.getElementById('navUsername');
        if (usernameElement && user) {
            usernameElement.textContent = user.name || user.email;
        }
    },

    // Logout user
    async logout() {
        try {
            Utils.showLoading();
            await API.post('/auth/logout');
            window.currentUser = null;
            window.location.href = '/';
        } catch (error) {
            Utils.showAlert('Logout failed. Please try again.', 'danger');
        } finally {
            Utils.hideLoading();
        }
    }
};

// Form Helper Functions
const FormHelpers = {
    // Clear form validation
    clearValidation(form) {
        const inputs = form.querySelectorAll('.form-control');
        inputs.forEach(input => {
            input.classList.remove('is-invalid', 'is-valid');
        });
        
        const feedback = form.querySelectorAll('.invalid-feedback');
        feedback.forEach(fb => fb.remove());
    },

    // Show field error
    showFieldError(input, message) {
        input.classList.add('is-invalid');
        
        // Remove existing feedback
        const existingFeedback = input.parentNode.querySelector('.invalid-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }
        
        // Add new feedback
        const feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        feedback.textContent = message;
        input.parentNode.appendChild(feedback);
    },

    // Show field success
    showFieldSuccess(input) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
        
        // Remove error feedback
        const feedback = input.parentNode.querySelector('.invalid-feedback');
        if (feedback) {
            feedback.remove();
        }
    },

    // Validate form field
    validateField(input, rules = {}) {
        const value = input.value.trim();
        
        // Required validation
        if (rules.required && !value) {
            this.showFieldError(input, `${input.name || 'This field'} is required`);
            return false;
        }
        
        // Email validation
        if (rules.email && value && !Utils.validateEmail(value)) {
            this.showFieldError(input, 'Please enter a valid email address');
            return false;
        }
        
        // Password validation
        if (rules.password && value) {
            const validation = Utils.validatePassword(value);
            if (!validation.valid) {
                this.showFieldError(input, validation.message);
                return false;
            }
        }
        
        // Min length validation
        if (rules.minLength && value.length < rules.minLength) {
            this.showFieldError(input, `Minimum ${rules.minLength} characters required`);
            return false;
        }
        
        // Max length validation
        if (rules.maxLength && value.length > rules.maxLength) {
            this.showFieldError(input, `Maximum ${rules.maxLength} characters allowed`);
            return false;
        }
        
        // Custom validation
        if (rules.custom && typeof rules.custom === 'function') {
            const customResult = rules.custom(value);
            if (customResult !== true) {
                this.showFieldError(input, customResult);
                return false;
            }
        }
        
        this.showFieldSuccess(input);
        return true;
    }
};

// Global functions
window.logout = Session.logout.bind(Session);

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    // Check authentication status
    Session.checkAuth();
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Add loading states to buttons
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('btn') && e.target.type === 'submit') {
            e.target.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
            e.target.disabled = true;
        }
    });
    
    // Auto-hide alerts after 5 seconds
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { Utils, API, Session, FormHelpers };
}