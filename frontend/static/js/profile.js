/**
 * Profile Page JavaScript
 * Handles user profile display, editing, and management
 */

class ProfileManager {
    constructor() {
        this.user = null;
        this.isLoading = false;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadProfile();
    }
    
    setupEventListeners() {
        // Edit profile form
        const editForm = document.getElementById('editProfileForm');
        if (editForm) {
            editForm.addEventListener('submit', (e) => this.handleProfileUpdate(e));
        }
        
        // Change password form
        const passwordForm = document.getElementById('changePasswordForm');
        if (passwordForm) {
            passwordForm.addEventListener('submit', (e) => this.handlePasswordChange(e));
        }
        
        // Password validation
        const newPasswordField = document.getElementById('newPassword');
        const confirmPasswordField = document.getElementById('confirmNewPassword');
        
        if (newPasswordField && confirmPasswordField) {
            confirmPasswordField.addEventListener('input', () => {
                this.validatePasswordMatch();
            });
        }
        
        // Connection request actions
        document.addEventListener('click', (e) => {
            if (e.target.matches('.btn-accept-connection')) {
                const connectionId = e.target.dataset.connectionId;
                this.respondToConnection(connectionId, 'accepted');
            } else if (e.target.matches('.btn-decline-connection')) {
                const connectionId = e.target.dataset.connectionId;
                this.respondToConnection(connectionId, 'declined');
            }
        });
    }
    
    async loadProfile() {
        try {
            this.showLoading(true);
            
            const response = await API.getUserProfile();
            
            if (response.success) {
                this.user = response.user;
                this.displayProfile();
                this.loadRecentActivity();
                this.loadRecentDocuments();
                
                if (this.user.user_type === 'lawyer') {
                    this.loadConnectionRequests();
                    this.showLawyerSections();
                }
            } else {
                throw new Error(response.message || 'Failed to load profile');
            }
            
        } catch (error) {
            console.error('Load profile error:', error);
            Utils.showAlert(`Failed to load profile: ${error.message}`, 'error');
        } finally {
            this.showLoading(false);
        }
    }
    
    displayProfile() {
        if (!this.user) return;
        
        // Update sidebar
        this.updateSidebar();
        
        // Update profile information
        this.updateProfileInfo();
        
        // Update edit form
        this.populateEditForm();
    }
    
    updateSidebar() {
        const initials = this.getInitials(this.user.name);
        const joinedDays = this.getDaysSinceJoin(this.user.created_at);
        
        // Update avatar and basic info
        document.getElementById('userInitials').textContent = initials;
        document.getElementById('userName').textContent = this.user.name;
        document.getElementById('userType').textContent = this.user.user_type === 'lawyer' ? 'Legal Professional' : 'Client';
        document.getElementById('joinedDays').textContent = joinedDays;
        
        // Update stats (will be loaded separately)
        this.updateStats();
    }
    
    updateProfileInfo() {
        const container = document.getElementById('profileInfo');
        if (!container) return;
        
        const profileFields = [
            {
                label: '<i class="fas fa-envelope me-2"></i>Email Address',
                value: this.user.email,
                id: 'email'
            },
            {
                label: '<i class="fas fa-phone me-2"></i>Phone Number',
                value: this.user.phone_no || 'Not provided',
                id: 'phone'
            },
            {
                label: '<i class="fas fa-calendar me-2"></i>Member Since',
                value: new Date(this.user.created_at).toLocaleDateString('en-IN', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                }),
                id: 'joined'
            }
        ];
        
        // Add lawyer-specific fields
        if (this.user.user_type === 'lawyer') {
            profileFields.push(
                {
                    label: '<i class="fas fa-graduation-cap me-2"></i>Degree',
                    value: this.user.degree || 'Not specified',
                    id: 'degree'
                },
                {
                    label: '<i class="fas fa-university me-2"></i>Institution',
                    value: this.user.college || 'Not specified',
                    id: 'college'
                },
                {
                    label: '<i class="fas fa-award me-2"></i>Qualifications',
                    value: this.user.qualifications || 'Not specified',
                    id: 'qualifications'
                }
            );
        }
        
        container.innerHTML = profileFields.map(field => `
            <div class="col-md-6 profile-info-item">
                <div class="profile-info-label">${field.label}</div>
                <div class="profile-info-value">${Utils.escapeHtml(field.value)}</div>
            </div>
        `).join('');
    }
    
    populateEditForm() {
        if (!this.user) return;
        
        document.getElementById('editName').value = this.user.name || '';
        document.getElementById('editEmail').value = this.user.email || '';
        document.getElementById('editPhone').value = this.user.phone_no || '';
        
        if (this.user.user_type === 'lawyer') {
            document.getElementById('editLawyerFields').style.display = 'block';
            document.getElementById('editDegree').value = this.user.degree || '';
            document.getElementById('editCollege').value = this.user.college || '';
            document.getElementById('editQualifications').value = this.user.qualifications || '';
        }
    }
    
    async updateStats() {
        try {
            // Load document count
            const docsResponse = await API.getDocuments();
            if (docsResponse.success) {
                document.getElementById('documentCount').textContent = docsResponse.documents.length;
            }
            
            // Load connection count for lawyers
            if (this.user.user_type === 'lawyer') {
                const statsResponse = await API.getLawyerStats();
                if (statsResponse.success) {
                    document.getElementById('connectionCount').textContent = statsResponse.stats.accepted_connections;
                    document.getElementById('connectionStats').style.display = 'block';
                }
            }
            
        } catch (error) {
            console.error('Failed to load stats:', error);
        }
    }
    
    async loadRecentActivity() {
        const container = document.getElementById('recentActivity');
        if (!container) return;
        
        try {
            // For now, create mock activity based on user data
            const activities = this.generateMockActivity();
            
            if (activities.length === 0) {
                container.innerHTML = `
                    <div class="text-center py-4">
                        <i class="fas fa-history text-muted" style="font-size: 2rem;"></i>
                        <p class="mt-2 text-muted">No recent activity</p>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = activities.map(activity => `
                <div class="activity-item">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <i class="${activity.icon} text-${activity.color} me-2"></i>
                            <strong>${activity.title}</strong>
                            <p class="mb-1 text-muted">${activity.description}</p>
                        </div>
                        <small class="activity-time">${activity.time}</small>
                    </div>
                </div>
            `).join('');
            
        } catch (error) {
            console.error('Failed to load activity:', error);
            container.innerHTML = `
                <div class="text-center py-4">
                    <p class="text-muted">Failed to load activity</p>
                </div>
            `;
        }
    }
    
    generateMockActivity() {
        const activities = [];
        const now = new Date();
        
        // Profile created activity
        const joinDate = new Date(this.user.created_at);
        activities.push({
            icon: 'fas fa-user-plus',
            color: 'cyan',
            title: 'Account Created',
            description: 'Welcome to Kanoon Ki Pechaan! Your account has been successfully created.',
            time: this.getRelativeTime(joinDate)
        });
        
        // Recent login (mock)
        const recentLogin = new Date(now.getTime() - (Math.random() * 24 * 60 * 60 * 1000));
        activities.push({
            icon: 'fas fa-sign-in-alt',
            color: 'success',
            title: 'Recent Login',
            description: 'You signed in to your account.',
            time: this.getRelativeTime(recentLogin)
        });
        
        return activities.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)).slice(0, 5);
    }
    
    async loadRecentDocuments() {
        const container = document.getElementById('recentDocuments');
        if (!container) return;
        
        try {
            const response = await API.getDocuments();
            
            if (response.success && response.documents.length > 0) {
                const recentDocs = response.documents
                    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
                    .slice(0, 3);
                
                container.innerHTML = recentDocs.map(doc => `
                    <div class="document-item">
                        <div class="d-flex justify-content-between align-items-start">
                            <div class="flex-grow-1">
                                <h6 class="mb-1">${Utils.escapeHtml(doc.title)}</h6>
                                <p class="text-muted small mb-1">
                                    Uploaded ${new Date(doc.created_at).toLocaleDateString()}
                                </p>
                                ${doc.summary ? `
                                    <p class="text-muted small mb-0">${Utils.escapeHtml(doc.summary.substring(0, 100))}...</p>
                                ` : ''}
                            </div>
                            <div class="flex-shrink-0 ms-3">
                                <span class="badge ${this.getAnalysisStatusClass(doc.analysis_status)}">
                                    ${doc.analysis_status || 'pending'}
                                </span>
                            </div>
                        </div>
                    </div>
                `).join('');
                
                // Add "View All" link
                container.innerHTML += `
                    <div class="text-center mt-3">
                        <a href="/documents" class="btn btn-outline-primary btn-sm">
                            <i class="fas fa-eye me-2"></i>View All Documents
                        </a>
                    </div>
                `;
            } else {
                container.innerHTML = `
                    <div class="text-center py-4">
                        <i class="fas fa-folder-open text-muted" style="font-size: 2rem;"></i>
                        <p class="mt-2 text-muted">No documents uploaded yet</p>
                        <a href="/documents" class="btn btn-outline-primary btn-sm">
                            <i class="fas fa-upload me-2"></i>Upload Your First Document
                        </a>
                    </div>
                `;
            }
            
        } catch (error) {
            console.error('Failed to load documents:', error);
            container.innerHTML = `
                <div class="text-center py-4">
                    <p class="text-muted">Failed to load documents</p>
                </div>
            `;
        }
    }
    
    async loadConnectionRequests() {
        const container = document.getElementById('connectionRequests');
        const pendingCountElement = document.getElementById('pendingCount');
        
        if (!container || this.user.user_type !== 'lawyer') return;
        
        try {
            const response = await API.getConnections();
            
            if (response.success) {
                const pendingRequests = response.connections.filter(conn => conn.connection_status === 'pending');
                
                if (pendingCountElement) {
                    pendingCountElement.textContent = pendingRequests.length;
                }
                
                if (pendingRequests.length === 0) {
                    container.innerHTML = `
                        <div class="text-center py-4">
                            <i class="fas fa-handshake text-muted" style="font-size: 2rem;"></i>
                            <p class="mt-2 text-muted">No pending connection requests</p>
                        </div>
                    `;
                    return;
                }
                
                container.innerHTML = pendingRequests.map(request => `
                    <div class="connection-request-item">
                        <div class="d-flex justify-content-between align-items-start">
                            <div class="flex-grow-1">
                                <h6 class="mb-1">${Utils.escapeHtml(request.client_name || 'Client')}</h6>
                                <p class="text-muted small mb-2">
                                    Requested ${new Date(request.created_at).toLocaleDateString()}
                                </p>
                                ${request.case_description ? `
                                    <p class="small mb-3">${Utils.escapeHtml(request.case_description)}</p>
                                ` : ''}
                                <div class="btn-group" role="group">
                                    <button type="button" class="btn btn-success btn-sm btn-accept-connection" 
                                            data-connection-id="${request.id}">
                                        <i class="fas fa-check me-1"></i>Accept
                                    </button>
                                    <button type="button" class="btn btn-danger btn-sm btn-decline-connection" 
                                            data-connection-id="${request.id}">
                                        <i class="fas fa-times me-1"></i>Decline
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `).join('');
            }
            
        } catch (error) {
            console.error('Failed to load connection requests:', error);
            container.innerHTML = `
                <div class="text-center py-4">
                    <p class="text-muted">Failed to load connection requests</p>
                </div>
            `;
        }
    }
    
    showLawyerSections() {
        document.getElementById('lawyerQuickActions').style.display = 'block';
        document.getElementById('connectionsSection').style.display = 'block';
    }
    
    async handleProfileUpdate(e) {
        e.preventDefault();
        
        if (this.isLoading) return;
        
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData.entries());
        
        // Basic validation
        if (!data.name.trim()) {
            Utils.showAlert('Name is required', 'warning');
            return;
        }
        
        this.isLoading = true;
        
        try {
            const response = await API.updateProfile(data);
            
            if (response.success) {
                Utils.showAlert('Profile updated successfully!', 'success');
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('editProfileModal'));
                modal.hide();
                
                // Reload profile
                this.loadProfile();
                
            } else {
                throw new Error(response.message || 'Failed to update profile');
            }
            
        } catch (error) {
            console.error('Update profile error:', error);
            Utils.showAlert(`Failed to update profile: ${error.message}`, 'error');
        } finally {
            this.isLoading = false;
        }
    }
    
    async handlePasswordChange(e) {
        e.preventDefault();
        
        if (this.isLoading) return;
        
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData.entries());
        
        // Validation
        if (!this.validatePasswordForm(data)) {
            return;
        }
        
        this.isLoading = true;
        
        try {
            const response = await API.changePassword({
                current_password: data.current_password,
                new_password: data.new_password
            });
            
            if (response.success) {
                Utils.showAlert('Password changed successfully!', 'success');
                
                // Close modal and reset form
                const modal = bootstrap.Modal.getInstance(document.getElementById('changePasswordModal'));
                modal.hide();
                e.target.reset();
                
            } else {
                throw new Error(response.message || 'Failed to change password');
            }
            
        } catch (error) {
            console.error('Change password error:', error);
            Utils.showAlert(`Failed to change password: ${error.message}`, 'error');
        } finally {
            this.isLoading = false;
        }
    }
    
    validatePasswordForm(data) {
        if (!data.current_password) {
            Utils.showAlert('Current password is required', 'warning');
            return false;
        }
        
        if (!data.new_password || data.new_password.length < 6) {
            Utils.showAlert('New password must be at least 6 characters', 'warning');
            return false;
        }
        
        if (data.new_password !== data.confirm_password) {
            Utils.showAlert('Password confirmation does not match', 'warning');
            return false;
        }
        
        return true;
    }
    
    validatePasswordMatch() {
        const newPassword = document.getElementById('newPassword').value;
        const confirmPassword = document.getElementById('confirmNewPassword').value;
        const confirmField = document.getElementById('confirmNewPassword');
        
        if (confirmPassword && newPassword !== confirmPassword) {
            confirmField.setCustomValidity('Passwords do not match');
            confirmField.classList.add('is-invalid');
        } else {
            confirmField.setCustomValidity('');
            confirmField.classList.remove('is-invalid');
        }
    }
    
    async respondToConnection(connectionId, response) {
        try {
            const apiResponse = await API.respondToConnection(connectionId, response);
            
            if (apiResponse.success) {
                Utils.showAlert(`Connection request ${response}!`, 'success');
                this.loadConnectionRequests(); // Reload requests
                this.updateStats(); // Update stats
            } else {
                throw new Error(apiResponse.message || `Failed to ${response} connection`);
            }
            
        } catch (error) {
            console.error('Respond to connection error:', error);
            Utils.showAlert(`Failed to ${response} connection: ${error.message}`, 'error');
        }
    }
    
    // Utility methods
    getInitials(name) {
        return name.split(' ')
            .map(word => word.charAt(0).toUpperCase())
            .slice(0, 2)
            .join('');
    }
    
    getDaysSinceJoin(joinDate) {
        const now = new Date();
        const join = new Date(joinDate);
        const diffTime = Math.abs(now - join);
        return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    }
    
    getRelativeTime(date) {
        const now = new Date();
        const diffTime = now - new Date(date);
        const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
        const diffHours = Math.floor(diffTime / (1000 * 60 * 60));
        const diffMinutes = Math.floor(diffTime / (1000 * 60));
        
        if (diffDays > 0) {
            return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
        } else if (diffHours > 0) {
            return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
        } else if (diffMinutes > 0) {
            return `${diffMinutes} minute${diffMinutes > 1 ? 's' : ''} ago`;
        } else {
            return 'Just now';
        }
    }
    
    getAnalysisStatusClass(status) {
        switch (status) {
            case 'completed': return 'bg-success';
            case 'processing': return 'bg-warning';
            case 'failed': return 'bg-danger';
            default: return 'bg-secondary';
        }
    }
    
    showLoading(show) {
        // Could add loading indicators if needed
    }
}

// Global function for change password button
function changePassword() {
    const modal = new bootstrap.Modal(document.getElementById('changePasswordModal'));
    modal.show();
}

// Initialize profile manager when page loads
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('profileInfo')) {
        window.profileManager = new ProfileManager();
    }
});