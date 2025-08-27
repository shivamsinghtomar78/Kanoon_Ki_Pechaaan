/**
 * Documents Page JavaScript
 * Handles document upload, analysis, and management
 */

class DocumentManager {
    constructor() {
        this.currentDocuments = [];
        this.uploadInProgress = false;
        this.maxFileSize = 50 * 1024 * 1024; // 50MB
        this.allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadDocuments();
        this.setupDragAndDrop();
    }
    
    setupEventListeners() {
        // File input change
        const fileInput = document.getElementById('documentFile');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        }
        
        // Upload form submission
        const uploadForm = document.getElementById('uploadForm');
        if (uploadForm) {
            uploadForm.addEventListener('submit', (e) => this.handleUpload(e));
        }
        
        // Quick analysis buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('.btn-analyze')) {
                const docId = e.target.dataset.docId;
                this.analyzeDocument(docId);
            } else if (e.target.matches('.btn-view-doc')) {
                const docId = e.target.dataset.docId;
                this.viewDocument(docId);
            } else if (e.target.matches('.btn-delete-doc')) {
                const docId = e.target.dataset.docId;
                this.deleteDocument(docId);
            }
        });
        
        // Search functionality
        const searchInput = document.getElementById('documentSearch');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.filterDocuments(e.target.value));
        }
        
        // Filter by type
        const typeFilter = document.getElementById('typeFilter');
        if (typeFilter) {
            typeFilter.addEventListener('change', (e) => this.filterDocuments());
        }
    }
    
    setupDragAndDrop() {
        const dropZone = document.getElementById('uploadDropZone');
        if (!dropZone) return;
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, this.preventDefaults, false);
        });
        
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.add('drag-over');
            }, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.remove('drag-over');
            }, false);
        });
        
        dropZone.addEventListener('drop', (e) => this.handleDrop(e), false);
    }
    
    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    handleDrop(e) {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.processFiles(files);
        }
    }
    
    handleFileSelect(e) {
        const files = e.target.files;
        if (files.length > 0) {
            this.processFiles(files);
        }
    }
    
    processFiles(files) {
        Array.from(files).forEach(file => {
            if (this.validateFile(file)) {
                this.uploadFile(file);
            }
        });
    }
    
    validateFile(file) {
        // Check file size
        if (file.size > this.maxFileSize) {
            Utils.showAlert(`File "${file.name}" is too large. Maximum size is 50MB.`, 'error');
            return false;
        }
        
        // Check file type
        if (!this.allowedTypes.includes(file.type)) {
            Utils.showAlert(`File "${file.name}" type is not supported. Please upload PDF, DOC, DOCX, or TXT files.`, 'error');
            return false;
        }
        
        return true;
    }
    
    async uploadFile(file) {
        if (this.uploadInProgress) {
            Utils.showAlert('Another upload is in progress. Please wait.', 'warning');
            return;
        }
        
        this.uploadInProgress = true;
        this.showUploadProgress(true);
        
        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('title', file.name.replace(/\.[^/.]+$/, ""));
            formData.append('analyze', 'true');
            
            const response = await API.uploadDocument(formData, (progress) => {
                this.updateUploadProgress(progress);
            });
            
            if (response.success) {
                Utils.showAlert('Document uploaded and analyzed successfully!', 'success');
                this.loadDocuments();
                this.clearUploadForm();
            } else {
                throw new Error(response.message || 'Upload failed');
            }
            
        } catch (error) {
            console.error('Upload error:', error);
            Utils.showAlert(`Upload failed: ${error.message}`, 'error');
        } finally {
            this.uploadInProgress = false;
            this.showUploadProgress(false);
        }
    }
    
    handleUpload(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const fileInput = document.getElementById('documentFile');
        
        if (!fileInput.files.length) {
            Utils.showAlert('Please select a file to upload.', 'warning');
            return;
        }
        
        this.uploadFile(fileInput.files[0]);
    }
    
    async loadDocuments() {
        try {
            this.showDocumentsLoading(true);
            
            const response = await API.getDocuments();
            
            if (response.success) {
                this.currentDocuments = response.documents;
                this.renderDocuments(this.currentDocuments);
            } else {
                throw new Error(response.message || 'Failed to load documents');
            }
            
        } catch (error) {
            console.error('Load documents error:', error);
            Utils.showAlert(`Failed to load documents: ${error.message}`, 'error');
            this.renderDocuments([]);
        } finally {
            this.showDocumentsLoading(false);
        }
    }
    
    renderDocuments(documents) {
        const container = document.getElementById('documentsGrid');
        if (!container) return;
        
        if (documents.length === 0) {
            container.innerHTML = `
                <div class="col-12">
                    <div class="text-center py-5">
                        <i class="fas fa-folder-open text-muted" style="font-size: 4rem;"></i>
                        <h4 class="mt-3 text-muted">No Documents Found</h4>
                        <p class="text-muted">Upload your first legal document to get started.</p>
                    </div>
                </div>
            `;
            return;
        }
        
        container.innerHTML = documents.map(doc => this.createDocumentCard(doc)).join('');
    }
    
    createDocumentCard(doc) {
        const uploadDate = new Date(doc.created_at).toLocaleDateString();
        const fileSize = this.formatFileSize(doc.file_size || 0);
        const statusClass = this.getStatusClass(doc.analysis_status);
        const statusIcon = this.getStatusIcon(doc.analysis_status);
        
        return `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="glass-card h-100">
                    <div class="card-body d-flex flex-column">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <div class="flex-grow-1">
                                <h6 class="card-title mb-2">${Utils.escapeHtml(doc.title)}</h6>
                                <small class="text-muted">
                                    <i class="fas fa-calendar me-1"></i>${uploadDate}
                                </small>
                            </div>
                            <div class="dropdown">
                                <button class="btn btn-sm btn-outline-secondary" type="button" 
                                        data-bs-toggle="dropdown" aria-expanded="false">
                                    <i class="fas fa-ellipsis-v"></i>
                                </button>
                                <ul class="dropdown-menu">
                                    <li><a class="dropdown-item btn-view-doc" href="#" data-doc-id="${doc.id}">
                                        <i class="fas fa-eye me-2"></i>View
                                    </a></li>
                                    <li><a class="dropdown-item btn-analyze" href="#" data-doc-id="${doc.id}">
                                        <i class="fas fa-brain me-2"></i>Re-analyze
                                    </a></li>
                                    <li><hr class="dropdown-divider"></li>
                                    <li><a class="dropdown-item text-danger btn-delete-doc" href="#" data-doc-id="${doc.id}">
                                        <i class="fas fa-trash me-2"></i>Delete
                                    </a></li>
                                </ul>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <small class="text-muted">File Size: ${fileSize}</small>
                                <span class="badge ${statusClass}">
                                    <i class="${statusIcon} me-1"></i>${doc.analysis_status || 'pending'}
                                </span>
                            </div>
                        </div>
                        
                        ${doc.summary ? `
                            <div class="mb-3 flex-grow-1">
                                <small class="text-muted d-block mb-2">AI Summary:</small>
                                <p class="small text-truncate-3">${Utils.escapeHtml(doc.summary)}</p>
                            </div>
                        ` : ''}
                        
                        <div class="mt-auto">
                            <div class="btn-group w-100" role="group">
                                <button type="button" class="btn btn-sm btn-outline-primary btn-view-doc" 
                                        data-doc-id="${doc.id}">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button type="button" class="btn btn-sm btn-outline-success btn-analyze" 
                                        data-doc-id="${doc.id}">
                                    <i class="fas fa-brain"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    getStatusClass(status) {
        switch (status) {
            case 'completed': return 'bg-success';
            case 'processing': return 'bg-warning';
            case 'failed': return 'bg-danger';
            default: return 'bg-secondary';
        }
    }
    
    getStatusIcon(status) {
        switch (status) {
            case 'completed': return 'fas fa-check';
            case 'processing': return 'fas fa-spinner fa-spin';
            case 'failed': return 'fas fa-exclamation-triangle';
            default: return 'fas fa-clock';
        }
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    async analyzeDocument(docId) {
        try {
            const response = await API.analyzeDocument(docId);
            
            if (response.success) {
                Utils.showAlert('Document analysis started successfully!', 'success');
                this.loadDocuments(); // Refresh the list
            } else {
                throw new Error(response.message || 'Analysis failed');
            }
            
        } catch (error) {
            console.error('Analysis error:', error);
            Utils.showAlert(`Analysis failed: ${error.message}`, 'error');
        }
    }
    
    async viewDocument(docId) {
        try {
            const response = await API.getDocument(docId);
            
            if (response.success) {
                this.showDocumentModal(response.document);
            } else {
                throw new Error(response.message || 'Failed to load document');
            }
            
        } catch (error) {
            console.error('View document error:', error);
            Utils.showAlert(`Failed to load document: ${error.message}`, 'error');
        }
    }
    
    async deleteDocument(docId) {
        if (!confirm('Are you sure you want to delete this document? This action cannot be undone.')) {
            return;
        }
        
        try {
            const response = await API.deleteDocument(docId);
            
            if (response.success) {
                Utils.showAlert('Document deleted successfully!', 'success');
                this.loadDocuments();
            } else {
                throw new Error(response.message || 'Delete failed');
            }
            
        } catch (error) {
            console.error('Delete error:', error);
            Utils.showAlert(`Delete failed: ${error.message}`, 'error');
        }
    }
    
    showDocumentModal(document) {
        const modal = document.getElementById('documentModal');
        if (!modal) {
            this.createDocumentModal(document);
            return;
        }
        
        // Update modal content
        document.getElementById('modalDocumentTitle').textContent = document.title;
        document.getElementById('modalDocumentSummary').textContent = document.summary || 'No summary available';
        document.getElementById('modalDocumentAnalysis').textContent = document.analysis || 'No analysis available';
        
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
    }
    
    createDocumentModal(doc) {
        const modalHtml = `
            <div class="modal fade" id="documentModal" tabindex="-1" aria-labelledby="documentModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content bg-dark">
                        <div class="modal-header">
                            <h5 class="modal-title" id="documentModalLabel">
                                <i class="fas fa-file-alt me-2"></i>
                                <span id="modalDocumentTitle">${Utils.escapeHtml(doc.title)}</span>
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <div class="mb-4">
                                <h6 class="text-cyan">
                                    <i class="fas fa-file-text me-2"></i>AI Summary
                                </h6>
                                <p id="modalDocumentSummary" class="text-muted">
                                    ${Utils.escapeHtml(doc.summary || 'No summary available')}
                                </p>
                            </div>
                            
                            <div class="mb-4">
                                <h6 class="text-magenta">
                                    <i class="fas fa-brain me-2"></i>Legal Analysis
                                </h6>
                                <p id="modalDocumentAnalysis" class="text-muted">
                                    ${Utils.escapeHtml(doc.analysis || 'No analysis available')}
                                </p>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                            <button type="button" class="btn btn-primary btn-analyze" data-doc-id="${doc.id}">
                                <i class="fas fa-brain me-2"></i>Re-analyze
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        const modal = new bootstrap.Modal(document.getElementById('documentModal'));
        modal.show();
    }
    
    filterDocuments(searchTerm = '') {
        const typeFilter = document.getElementById('typeFilter')?.value || '';
        const searchInput = document.getElementById('documentSearch')?.value || searchTerm;
        
        let filteredDocs = this.currentDocuments;
        
        // Filter by search term
        if (searchInput) {
            filteredDocs = filteredDocs.filter(doc => 
                doc.title.toLowerCase().includes(searchInput.toLowerCase()) ||
                (doc.summary && doc.summary.toLowerCase().includes(searchInput.toLowerCase()))
            );
        }
        
        // Filter by type
        if (typeFilter) {
            filteredDocs = filteredDocs.filter(doc => 
                doc.analysis_status === typeFilter
            );
        }
        
        this.renderDocuments(filteredDocs);
    }
    
    showUploadProgress(show) {
        const progressContainer = document.getElementById('uploadProgress');
        if (progressContainer) {
            progressContainer.style.display = show ? 'block' : 'none';
        }
    }
    
    updateUploadProgress(percentage) {
        const progressBar = document.querySelector('#uploadProgress .progress-bar');
        if (progressBar) {
            progressBar.style.width = `${percentage}%`;
            progressBar.textContent = `${percentage}%`;
        }
    }
    
    showDocumentsLoading(show) {
        const container = document.getElementById('documentsGrid');
        if (!container) return;
        
        if (show) {
            container.innerHTML = `
                <div class="col-12">
                    <div class="text-center py-5">
                        <div class="spinner-border text-cyan" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p class="mt-2 text-muted">Loading documents...</p>
                    </div>
                </div>
            `;
        }
    }
    
    clearUploadForm() {
        const form = document.getElementById('uploadForm');
        if (form) {
            form.reset();
        }
    }
}

// Auto-resize textarea functionality
function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}

// Initialize document manager when page loads
document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('#documentsGrid')) {
        window.documentManager = new DocumentManager();
    }
    
    // Auto-resize textareas
    document.querySelectorAll('textarea[data-auto-resize]').forEach(textarea => {
        textarea.addEventListener('input', () => autoResizeTextarea(textarea));
        autoResizeTextarea(textarea); // Initial resize
    });
});