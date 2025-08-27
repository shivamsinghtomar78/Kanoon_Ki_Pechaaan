/**
 * Lawyers Network JavaScript
 * Handles lawyer search, profiles, and connection management
 */

class LawyerNetwork {
    constructor() {
        this.currentLawyers = [];
        this.currentPage = 1;
        this.totalPages = 1;
        this.isLoading = false;
        this.searchTimeout = null;
        this.viewMode = 'grid'; // 'grid' or 'list'
        this.specializations = [];
        
        this.init();
    }
    
    init() {
        this.loadSpecializations();
        this.setupEventListeners();
        this.loadLawyers();
    }
    
    setupEventListeners() {
        // Search form
        const searchForm = document.getElementById('lawyerSearchForm');
        if (searchForm) {
            searchForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.performSearch();
            });
        }
        
        // Real-time search
        const searchInput = document.getElementById('searchQuery');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                clearTimeout(this.searchTimeout);
                this.searchTimeout = setTimeout(() => {
                    this.performSearch();
                }, 500);
            });
        }
        
        // Filter changes
        const filters = ['specializationFilter', 'locationFilter', 'sortBy'];
        filters.forEach(filterId => {
            const element = document.getElementById(filterId);
            if (element) {
                element.addEventListener('change', () => this.performSearch());
            }
        });
        
        // Experience filter
        document.querySelectorAll('input[name="experienceFilter"]').forEach(radio => {
            radio.addEventListener('change', () => this.performSearch());
        });
        
        // View mode toggle
        const gridViewBtn = document.getElementById('gridView');
        const listViewBtn = document.getElementById('listView');
        
        if (gridViewBtn && listViewBtn) {
            gridViewBtn.addEventListener('click', () => this.setViewMode('grid'));
            listViewBtn.addEventListener('click', () => this.setViewMode('list'));
        }
        
        // Connection form
        const connectionForm = document.getElementById('connectionForm');
        if (connectionForm) {
            connectionForm.addEventListener('submit', (e) => this.handleConnectionRequest(e));
        }
        
        // Dynamic event delegation for lawyer cards
        document.addEventListener('click', (e) => {
            if (e.target.matches('.btn-view-profile') || e.target.closest('.btn-view-profile')) {
                const btn = e.target.matches('.btn-view-profile') ? e.target : e.target.closest('.btn-view-profile');
                const lawyerId = btn.dataset.lawyerId;
                this.viewLawyerProfile(lawyerId);
            } else if (e.target.matches('.btn-connect') || e.target.closest('.btn-connect')) {
                const btn = e.target.matches('.btn-connect') ? e.target : e.target.closest('.btn-connect');
                const lawyerId = btn.dataset.lawyerId;
                this.showConnectionModal(lawyerId);
            }
        });
    }
    
    async loadSpecializations() {
        try {
            const response = await API.getLawyerSpecializations();
            if (response.success) {
                this.specializations = response.specializations;
                this.populateSpecializationFilter();
            }
        } catch (error) {
            console.error('Failed to load specializations:', error);
        }
    }
    
    populateSpecializationFilter() {
        const select = document.getElementById('specializationFilter');
        if (!select) return;
        
        // Clear existing options (except "All")
        while (select.children.length > 1) {
            select.removeChild(select.lastChild);
        }
        
        // Add specialization options
        this.specializations.forEach(spec => {
            const option = document.createElement('option');
            option.value = spec.id;
            option.textContent = spec.name;
            select.appendChild(option);
        });
    }
    
    async loadLawyers(page = 1) {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showLoading(true);
        
        try {
            const params = this.buildSearchParams();
            params.page = page;
            
            const response = await API.searchLawyers(params);
            
            if (response.success) {
                this.currentLawyers = response.lawyers;
                this.currentPage = response.pagination.page;
                this.totalPages = response.pagination.pages;
                
                this.renderLawyers();
                this.renderPagination();
                this.updateResultsCount(response.pagination.total);
            } else {
                throw new Error(response.message || 'Failed to load lawyers');
            }
            
        } catch (error) {
            console.error('Load lawyers error:', error);
            Utils.showAlert(`Failed to load lawyers: ${error.message}`, 'error');
            this.renderLawyers([]);
        } finally {
            this.isLoading = false;
            this.showLoading(false);
        }
    }
    
    performSearch() {
        this.currentPage = 1;
        this.loadLawyers(1);
    }
    
    buildSearchParams() {
        return {
            query: document.getElementById('searchQuery')?.value || '',
            specialization: document.getElementById('specializationFilter')?.value || '',
            location: document.getElementById('locationFilter')?.value || '',
            experience: document.querySelector('input[name="experienceFilter"]:checked')?.value || '',
            sort_by: document.getElementById('sortBy')?.value || 'name',
            per_page: 12
        };
    }
    
    renderLawyers(lawyers = this.currentLawyers) {
        const container = document.getElementById('lawyersGrid');
        if (!container) return;
        
        if (lawyers.length === 0) {
            container.innerHTML = `
                <div class="col-12">
                    <div class="text-center py-5">
                        <i class="fas fa-search text-muted" style="font-size: 4rem;"></i>
                        <h4 class="mt-3 text-muted">No Lawyers Found</h4>
                        <p class="text-muted">Try adjusting your search criteria or filters.</p>
                        <button class="btn btn-outline-primary" onclick="location.reload()">
                            <i class="fas fa-refresh me-2"></i>Reset Filters
                        </button>
                    </div>
                </div>
            `;
            return;
        }
        
        const lawyerCards = lawyers.map(lawyer => this.createLawyerCard(lawyer)).join('');
        container.innerHTML = lawyerCards;
    }
    
    createLawyerCard(lawyer) {
        const initials = this.getInitials(lawyer.name);
        const connectionStatus = this.getConnectionStatusBadge(lawyer.connection_status);
        const specializations = this.formatSpecializations(lawyer.qualifications);
        
        const cardClass = this.viewMode === 'list' ? 'col-12' : 'col-lg-4 col-md-6';
        const cardBodyClass = this.viewMode === 'list' ? 'd-flex align-items-center' : '';
        
        return `
            <div class="${cardClass} mb-4">
                <div class="glass-card lawyer-card h-100">
                    ${connectionStatus}
                    <div class="card-body ${cardBodyClass}">
                        ${this.viewMode === 'grid' ? this.createGridLayout(lawyer, initials, specializations) : this.createListLayout(lawyer, initials, specializations)}
                    </div>
                </div>
            </div>
        `;
    }
    
    createGridLayout(lawyer, initials, specializations) {
        return `
            <div class="text-center">
                <div class="lawyer-avatar mb-3">
                    ${initials}
                </div>
                
                <h5 class="card-title mb-2">${Utils.escapeHtml(lawyer.name)}</h5>
                
                <div class="mb-3">
                    ${specializations}
                </div>
                
                <p class="text-muted small mb-3">
                    <i class="fas fa-graduation-cap me-2"></i>
                    ${Utils.escapeHtml(lawyer.degree || 'Legal Professional')}
                </p>
                
                ${lawyer.college ? `
                    <p class="text-muted small mb-3">
                        <i class="fas fa-university me-2"></i>
                        ${Utils.escapeHtml(lawyer.college)}
                    </p>
                ` : ''}
                
                <div class="lawyer-stats">
                    <div class="stat-item">
                        <div class="stat-number">${lawyer.total_connections || 0}</div>
                        <div class="stat-label">Connections</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">${this.getExperienceYears(lawyer)}</div>
                        <div class="stat-label">Years</div>
                    </div>
                </div>
                
                <div class="mt-3">
                    <div class="btn-group w-100" role="group">
                        <button type="button" class="btn btn-outline-primary btn-view-profile" 
                                data-lawyer-id="${lawyer.id}">
                            <i class="fas fa-eye"></i> View
                        </button>
                        ${this.canConnect(lawyer) ? `
                            <button type="button" class="btn btn-primary btn-connect" 
                                    data-lawyer-id="${lawyer.id}">
                                <i class="fas fa-handshake"></i> Connect
                            </button>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }
    
    createListLayout(lawyer, initials, specializations) {
        return `
            <div class="lawyer-avatar me-3">
                ${initials}
            </div>
            
            <div class="lawyer-info flex-grow-1">
                <h5 class="card-title mb-2">${Utils.escapeHtml(lawyer.name)}</h5>
                
                <div class="mb-2">
                    ${specializations}
                </div>
                
                <p class="text-muted small mb-1">
                    <i class="fas fa-graduation-cap me-2"></i>
                    ${Utils.escapeHtml(lawyer.degree || 'Legal Professional')}
                </p>
                
                ${lawyer.college ? `
                    <p class="text-muted small mb-0">
                        <i class="fas fa-university me-2"></i>
                        ${Utils.escapeHtml(lawyer.college)}
                    </p>
                ` : ''}
            </div>
            
            <div class="lawyer-actions">
                <div class="text-center mb-3">
                    <small class="text-muted d-block">${lawyer.total_connections || 0} connections</small>
                    <small class="text-muted">${this.getExperienceYears(lawyer)} years exp.</small>
                </div>
                
                <div class="btn-group-vertical d-grid gap-2">
                    <button type="button" class="btn btn-outline-primary btn-sm btn-view-profile" 
                            data-lawyer-id="${lawyer.id}">
                        <i class="fas fa-eye me-2"></i>View Profile
                    </button>
                    ${this.canConnect(lawyer) ? `
                        <button type="button" class="btn btn-primary btn-sm btn-connect" 
                                data-lawyer-id="${lawyer.id}">
                            <i class="fas fa-handshake me-2"></i>Connect
                        </button>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    getInitials(name) {
        return name.split(' ')
            .map(word => word.charAt(0).toUpperCase())
            .slice(0, 2)
            .join('');
    }
    
    getConnectionStatusBadge(status) {
        if (!status) return '';
        
        const statusConfig = {
            pending: { icon: 'fas fa-clock', text: 'Pending' },
            accepted: { icon: 'fas fa-check', text: 'Connected' },
            declined: { icon: 'fas fa-times', text: 'Declined' }
        };
        
        const config = statusConfig[status];
        if (!config) return '';
        
        return `
            <div class="connection-status ${status}">
                <i class="${config.icon} me-1"></i>${config.text}
            </div>
        `;
    }
    
    formatSpecializations(qualifications) {
        if (!qualifications) return '<span class="specialization-badge">General Practice</span>';
        
        // Extract likely specializations from qualifications
        const specs = qualifications.toLowerCase();
        const specializations = [];
        
        if (specs.includes('criminal')) specializations.push('Criminal Law');
        if (specs.includes('civil')) specializations.push('Civil Law');
        if (specs.includes('family')) specializations.push('Family Law');
        if (specs.includes('corporate')) specializations.push('Corporate Law');
        if (specs.includes('tax')) specializations.push('Tax Law');
        if (specs.includes('property') || specs.includes('real estate')) specializations.push('Property Law');
        
        if (specializations.length === 0) specializations.push('General Practice');
        
        return specializations
            .slice(0, 3)
            .map(spec => `<span class="specialization-badge">${spec}</span>`)
            .join('');
    }
    
    getExperienceYears(lawyer) {
        // Simple estimation based on join date or default
        if (lawyer.created_at) {
            const joinDate = new Date(lawyer.created_at);
            const now = new Date();
            const years = Math.max(1, Math.floor((now - joinDate) / (365 * 24 * 60 * 60 * 1000)));
            return years;
        }
        return '1+';
    }
    
    canConnect(lawyer) {
        // Can connect if no existing connection and not self
        return !lawyer.connection_status && window.currentUser && window.currentUser.id !== lawyer.id;
    }
    
    setViewMode(mode) {
        this.viewMode = mode;
        
        // Update button states
        const gridBtn = document.getElementById('gridView');
        const listBtn = document.getElementById('listView');
        
        if (gridBtn && listBtn) {
            gridBtn.classList.toggle('active', mode === 'grid');
            listBtn.classList.toggle('active', mode === 'list');
        }
        
        // Update container classes
        const container = document.getElementById('lawyersContainer');
        if (container) {
            container.classList.toggle('list-view', mode === 'list');
        }
        
        this.renderLawyers();
    }
    
    async viewLawyerProfile(lawyerId) {
        try {
            const response = await API.getLawyerProfile(lawyerId);
            
            if (response.success) {
                this.showLawyerProfileModal(response.lawyer, response.connection_status);
            } else {
                throw new Error(response.message || 'Failed to load profile');
            }
            
        } catch (error) {
            console.error('View profile error:', error);
            Utils.showAlert(`Failed to load profile: ${error.message}`, 'error');
        }
    }
    
    showLawyerProfileModal(lawyer, connectionStatus) {
        const modal = document.getElementById('lawyerProfileModal');
        const content = document.getElementById('lawyerProfileContent');
        const connectBtn = document.getElementById('connectButton');
        
        if (!modal || !content) return;
        
        // Update modal content
        content.innerHTML = this.createProfileContent(lawyer);
        
        // Update connect button
        if (connectBtn) {
            if (this.canConnect(lawyer) && !connectionStatus) {
                connectBtn.style.display = 'block';
                connectBtn.onclick = () => this.showConnectionModal(lawyer.id);
            } else {
                connectBtn.style.display = 'none';
            }
        }
        
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
    }
    
    createProfileContent(lawyer) {
        const initials = this.getInitials(lawyer.name);
        const specializations = this.formatSpecializations(lawyer.qualifications);
        
        return `
            <div class="text-center mb-4">
                <div class="lawyer-avatar mb-3" style="width: 120px; height: 120px; font-size: 3rem;">
                    ${initials}
                </div>
                <h3>${Utils.escapeHtml(lawyer.name)}</h3>
                <p class="text-muted">${Utils.escapeHtml(lawyer.degree || 'Legal Professional')}</p>
            </div>
            
            <div class="row">
                <div class="col-md-6">
                    <h6 class="text-cyan">
                        <i class="fas fa-graduation-cap me-2"></i>Education
                    </h6>
                    <p class="text-muted">${Utils.escapeHtml(lawyer.college || 'Not specified')}</p>
                </div>
                
                <div class="col-md-6">
                    <h6 class="text-cyan">
                        <i class="fas fa-gavel me-2"></i>Specializations
                    </h6>
                    <div>${specializations}</div>
                </div>
            </div>
            
            ${lawyer.qualifications ? `
                <div class="mt-4">
                    <h6 class="text-cyan">
                        <i class="fas fa-award me-2"></i>Qualifications & Experience
                    </h6>
                    <p class="text-muted">${Utils.escapeHtml(lawyer.qualifications)}</p>
                </div>
            ` : ''}
            
            <div class="row mt-4">
                <div class="col-4 text-center">
                    <div class="stat-number">${lawyer.total_connections || 0}</div>
                    <div class="stat-label">Connections</div>
                </div>
                <div class="col-4 text-center">
                    <div class="stat-number">${this.getExperienceYears(lawyer)}</div>
                    <div class="stat-label">Years Experience</div>
                </div>
                <div class="col-4 text-center">
                    <div class="stat-number">⭐⭐⭐⭐⭐</div>
                    <div class="stat-label">Rating</div>
                </div>
            </div>
        `;
    }
    
    showConnectionModal(lawyerId) {
        const modal = document.getElementById('connectionModal');
        const lawyerIdInput = document.getElementById('selectedLawyerId');
        
        if (!modal || !lawyerIdInput) return;
        
        lawyerIdInput.value = lawyerId;
        
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
    }
    
    async handleConnectionRequest(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const data = {
            lawyer_id: parseInt(formData.get('lawyer_id')),
            case_description: formData.get('case_description').trim(),
            urgent: formData.has('urgent')
        };
        
        if (!data.case_description) {
            Utils.showAlert('Please provide a case description.', 'warning');
            return;
        }
        
        try {
            const response = await API.connectWithLawyer(data);
            
            if (response.success) {
                Utils.showAlert('Connection request sent successfully!', 'success');
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('connectionModal'));
                modal.hide();
                
                // Reset form
                e.target.reset();
                
                // Refresh lawyers list
                this.loadLawyers(this.currentPage);
                
            } else {
                throw new Error(response.message || 'Failed to send connection request');
            }
            
        } catch (error) {
            console.error('Connection request error:', error);
            Utils.showAlert(`Failed to send request: ${error.message}`, 'error');
        }
    }
    
    renderPagination() {
        const container = document.getElementById('paginationContainer');
        if (!container || this.totalPages <= 1) {
            container.innerHTML = '';
            return;
        }
        
        let paginationHtml = '';
        
        // Previous button
        paginationHtml += `
            <li class="page-item ${this.currentPage <= 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${this.currentPage - 1}">
                    <i class="fas fa-chevron-left"></i>
                </a>
            </li>
        `;
        
        // Page numbers
        const startPage = Math.max(1, this.currentPage - 2);
        const endPage = Math.min(this.totalPages, this.currentPage + 2);
        
        if (startPage > 1) {
            paginationHtml += `<li class="page-item"><a class="page-link" href="#" data-page="1">1</a></li>`;
            if (startPage > 2) {
                paginationHtml += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
        }
        
        for (let i = startPage; i <= endPage; i++) {
            paginationHtml += `
                <li class="page-item ${i === this.currentPage ? 'active' : ''}">
                    <a class="page-link" href="#" data-page="${i}">${i}</a>
                </li>
            `;
        }
        
        if (endPage < this.totalPages) {
            if (endPage < this.totalPages - 1) {
                paginationHtml += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
            paginationHtml += `<li class="page-item"><a class="page-link" href="#" data-page="${this.totalPages}">${this.totalPages}</a></li>`;
        }
        
        // Next button
        paginationHtml += `
            <li class="page-item ${this.currentPage >= this.totalPages ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${this.currentPage + 1}">
                    <i class="fas fa-chevron-right"></i>
                </a>
            </li>
        `;
        
        container.innerHTML = paginationHtml;
        
        // Add click handlers
        container.addEventListener('click', (e) => {
            e.preventDefault();
            const pageLink = e.target.closest('[data-page]');
            if (pageLink && !pageLink.closest('.disabled')) {
                const page = parseInt(pageLink.dataset.page);
                if (page >= 1 && page <= this.totalPages) {
                    this.loadLawyers(page);
                }
            }
        });
    }
    
    updateResultsCount(total) {
        const element = document.getElementById('resultsCount');
        if (element) {
            element.innerHTML = `
                <i class="fas fa-users me-2"></i>
                Found ${total} lawyer${total !== 1 ? 's' : ''} 
                (Page ${this.currentPage} of ${this.totalPages})
            `;
        }
    }
    
    showLoading(show) {
        const spinner = document.getElementById('loadingSpinner');
        const grid = document.getElementById('lawyersGrid');
        
        if (spinner) {
            spinner.style.display = show ? 'block' : 'none';
        }
        
        if (grid && show) {
            grid.innerHTML = '';
        }
    }
}

// Initialize lawyer network when page loads
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('lawyersGrid')) {
        window.lawyerNetwork = new LawyerNetwork();
    }
});