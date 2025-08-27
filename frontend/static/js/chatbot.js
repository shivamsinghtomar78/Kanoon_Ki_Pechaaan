/**
 * Chatbot JavaScript
 * Handles AI chat functionality and session management
 */

class ChatBot {
    constructor() {
        this.currentSessionId = null;
        this.sessions = [];
        this.isTyping = false;
        
        this.init();
    }
    
    async init() {
        // Load chat sessions
        await this.loadSessions();
        
        // Load legal categories
        await this.loadQuickCategories();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Auto-resize textarea
        this.setupAutoResize();
        
        // Check for category parameter
        this.checkCategoryParam();
    }
    
    setupEventListeners() {
        // Chat form submission
        const chatForm = document.getElementById('chatForm');
        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });
        
        // Enter key to send (Shift+Enter for new line)
        const messageInput = document.getElementById('messageInput');
        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Auto-focus on input
        messageInput.focus();
    }
    
    setupAutoResize() {
        const textarea = document.getElementById('messageInput');
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });
    }
    
    checkCategoryParam() {
        const urlParams = new URLSearchParams(window.location.search);
        const category = urlParams.get('category');
        if (category) {
            this.startCategoryChat(category);
        }
    }
    
    async loadSessions() {
        try {
            const response = await API.get('/chatbot/sessions');
            if (response.success) {
                this.sessions = response.sessions;
                this.renderSessions();
            }
        } catch (error) {
            console.error('Failed to load sessions:', error);
            document.getElementById('chatSessions').innerHTML = `
                <div class="text-center py-3">
                    <i class="fas fa-exclamation-triangle text-warning"></i>
                    <p class="text-muted small mt-2">Failed to load sessions</p>
                </div>
            `;
        }
    }
    
    renderSessions() {
        const container = document.getElementById('chatSessions');
        
        if (this.sessions.length === 0) {
            container.innerHTML = `
                <div class="text-center py-3">
                    <i class="fas fa-comments text-muted" style="font-size: 2rem;"></i>
                    <p class="text-muted small mt-2">No chat sessions yet</p>
                    <button class="btn btn-sm btn-primary" onclick="chatBot.createNewSession()">
                        <i class="fas fa-plus me-1"></i>Start First Chat
                    </button>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.sessions.map(session => `
            <div class="session-item ${session.id === this.currentSessionId ? 'active' : ''}" 
                 onclick="chatBot.loadSession(${session.id})">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <div class="fw-medium small">${Utils.truncateText(session.session_title, 25)}</div>
                        <div class="text-muted" style="font-size: 0.75rem;">
                            ${Utils.formatDate(session.updated_at)}
                        </div>
                    </div>
                    <div class="ms-2">
                        <button class="btn btn-sm btn-outline-danger" onclick="event.stopPropagation(); chatBot.deleteSession(${session.id})">
                            <i class="fas fa-trash" style="font-size: 0.7rem;"></i>
                        </button>
                    </div>
                </div>
                <div class="text-muted small mt-1">
                    <i class="fas fa-comments me-1"></i>${session.message_count || 0} messages
                </div>
            </div>
        `).join('');
    }
    
    async loadQuickCategories() {
        try {
            const response = await API.get('/chatbot/legal-categories');
            if (response.success) {
                const container = document.getElementById('quickCategories');
                container.innerHTML = response.categories.slice(0, 4).map(category => `
                    <button class="btn btn-sm btn-outline-secondary text-start" 
                            onclick="chatBot.startCategoryChat('${category.id}')">
                        <i class="fas fa-gavel me-2 text-cyan"></i>
                        <div>
                            <div class="fw-medium small">${category.name}</div>
                            <div class="text-muted" style="font-size: 0.7rem;">${category.description}</div>
                        </div>
                    </button>
                `).join('');
            }
        } catch (error) {
            console.error('Failed to load categories:', error);
        }
    }
    
    async createNewSession() {
        try {
            Utils.showLoading();
            const response = await API.post('/chatbot/sessions', {
                title: `Chat Session ${new Date().toLocaleString()}`
            });
            
            if (response.success) {
                this.sessions.unshift(response.session);
                this.renderSessions();
                this.loadSession(response.session.id);
                Utils.showAlert('New chat session created!', 'success', 2000);
            }
        } catch (error) {
            Utils.showAlert('Failed to create new session', 'danger');
        } finally {
            Utils.hideLoading();
        }
    }
    
    async loadSession(sessionId) {
        try {
            this.currentSessionId = sessionId;
            this.renderSessions(); // Update active session
            
            const response = await API.get(`/chatbot/sessions/${sessionId}/messages`);
            if (response.success) {
                this.renderMessages(response.messages);
                document.getElementById('chatTitle').textContent = response.session.session_title;
                document.getElementById('chatSubtitle').textContent = `${response.messages.length} messages`;
                
                // Show chat actions
                document.getElementById('clearChatBtn').style.display = 'inline-block';
                document.getElementById('exportChatBtn').style.display = 'inline-block';
            }
        } catch (error) {
            Utils.showAlert('Failed to load chat session', 'danger');
        }
    }
    
    renderMessages(messages) {
        const container = document.getElementById('chatMessages');
        
        if (messages.length === 0) {
            container.innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-robot text-cyan" style="font-size: 3rem;"></i>
                    <h5 class="mt-3 text-cyan">Start the conversation</h5>
                    <p class="text-muted">Ask me anything about Indian law</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = messages.map(message => this.renderMessage(message)).join('');
        this.scrollToBottom();
    }
    
    renderMessage(message) {
        const isUser = message.message_type === 'user';
        const time = Utils.formatDate(message.created_at);
        
        return `
            <div class="message ${message.message_type}">
                <div class="message-content">
                    <div class="message-text">${this.formatMessageContent(message.content)}</div>
                    <div class="message-time">${time}</div>
                    ${!isUser && message.metadata && message.metadata.sources ? 
                        `<div class="message-sources mt-2">
                            <small class="text-muted">
                                <i class="fas fa-book me-1"></i>
                                Sources: ${message.metadata.sources.join(', ')}
                            </small>
                        </div>` : ''}
                </div>
            </div>
        `;
    }
    
    formatMessageContent(content) {
        // Basic markdown-like formatting
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>')
            .replace(/Section (\d+)/g, '<span class="text-cyan">Section $1</span>')
            .replace(/Article (\d+)/g, '<span class="text-magenta">Article $1</span>');
    }
    
    async sendMessage() {
        const input = document.getElementById('messageInput');
        const message = input.value.trim();
        
        if (!message || this.isTyping) return;
        
        // Create session if none exists
        if (!this.currentSessionId) {
            await this.createNewSession();
            if (!this.currentSessionId) return;
        }
        
        // Clear input
        input.value = '';
        input.style.height = 'auto';
        
        // Add user message to UI
        this.addMessageToUI({
            message_type: 'user',
            content: message,
            created_at: new Date().toISOString()
        });
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            const response = await API.post(`/chatbot/sessions/${this.currentSessionId}/chat`, {
                message: message
            });
            
            this.hideTypingIndicator();
            
            if (response.success) {
                // Add AI response to UI
                this.addMessageToUI(response.ai_response);
                
                // Update session in sidebar
                await this.loadSessions();
            } else {
                this.addMessageToUI({
                    message_type: 'assistant',
                    content: 'I apologize, but I encountered an error processing your request. Please try again.',
                    created_at: new Date().toISOString()
                });
            }
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessageToUI({
                message_type: 'assistant',
                content: 'I apologize, but I\'m having trouble connecting right now. Please try again in a moment.',
                created_at: new Date().toISOString()
            });
        }
    }
    
    addMessageToUI(message) {
        const container = document.getElementById('chatMessages');
        
        // Remove welcome message if it exists
        const welcomeMessage = container.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
        
        container.insertAdjacentHTML('beforeend', this.renderMessage(message));
        this.scrollToBottom();
        
        // Update chat subtitle
        const messageCount = container.querySelectorAll('.message').length;
        document.getElementById('chatSubtitle').textContent = `${messageCount} messages`;
    }
    
    showTypingIndicator() {
        this.isTyping = true;
        document.getElementById('typingIndicator').style.display = 'block';
        document.getElementById('sendButton').disabled = true;
    }
    
    hideTypingIndicator() {
        this.isTyping = false;
        document.getElementById('typingIndicator').style.display = 'none';
        document.getElementById('sendButton').disabled = false;
    }
    
    scrollToBottom() {
        const container = document.getElementById('chatMessages');
        container.scrollTop = container.scrollHeight;
    }
    
    async deleteSession(sessionId) {
        if (!confirm('Are you sure you want to delete this chat session?')) return;
        
        try {
            await API.delete(`/chatbot/sessions/${sessionId}`);
            
            // Remove from local array
            this.sessions = this.sessions.filter(s => s.id !== sessionId);
            this.renderSessions();
            
            // Clear chat if it was the current session
            if (this.currentSessionId === sessionId) {
                this.currentSessionId = null;
                document.getElementById('chatMessages').innerHTML = `
                    <div class="welcome-message text-center py-5">
                        <i class="fas fa-robot text-cyan" style="font-size: 4rem;"></i>
                        <h3 class="text-cyan mt-3">Select a session or start a new chat</h3>
                    </div>
                `;
                document.getElementById('chatTitle').textContent = 'AI Legal Assistant';
                document.getElementById('chatSubtitle').textContent = 'Ask me anything about Indian law';
                document.getElementById('clearChatBtn').style.display = 'none';
                document.getElementById('exportChatBtn').style.display = 'none';
            }
            
            Utils.showAlert('Chat session deleted', 'success', 2000);
        } catch (error) {
            Utils.showAlert('Failed to delete session', 'danger');
        }
    }
    
    startCategoryChat(categoryId) {
        // Start a new session with a category-specific question
        const categoryQuestions = {
            'criminal': 'I have questions about criminal law. Can you help me understand my rights?',
            'civil': 'I need assistance with civil law matters. What should I know?',
            'family': 'I have questions about family law. Can you guide me?',
            'corporate': 'I need help with corporate legal matters. What are the basics?',
            'constitutional': 'I want to understand my constitutional rights. Can you explain?'
        };
        
        const question = categoryQuestions[categoryId] || 'Hello, I need legal assistance.';
        
        // Set the question in the input
        document.getElementById('messageInput').value = question;
        
        // Create new session and send the message
        this.createNewSession().then(() => {
            setTimeout(() => {
                this.sendMessage();
            }, 500);
        });
    }
    
    clearChat() {
        if (!confirm('Are you sure you want to clear this chat?')) return;
        
        // In a real app, this might archive the session instead of deleting
        this.deleteSession(this.currentSessionId);
    }
    
    exportChat() {
        if (!this.currentSessionId) return;
        
        const messages = document.querySelectorAll('#chatMessages .message');
        let exportText = `Kanoon Ki Pechaan - Chat Export\n`;
        exportText += `Session: ${document.getElementById('chatTitle').textContent}\n`;
        exportText += `Exported: ${new Date().toLocaleString()}\n`;
        exportText += `${'='.repeat(50)}\n\n`;
        
        messages.forEach(message => {
            const isUser = message.classList.contains('user');
            const content = message.querySelector('.message-text').textContent;
            const time = message.querySelector('.message-time').textContent;
            
            exportText += `${isUser ? 'You' : 'AI Assistant'} (${time}):\n${content}\n\n`;
        });
        
        // Create and download file
        const blob = new Blob([exportText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `kanoon-chat-${Date.now()}.txt`;
        a.click();
        URL.revokeObjectURL(url);
        
        Utils.showAlert('Chat exported successfully!', 'success', 2000);
    }
}

// Global functions for template
window.createNewSession = () => window.chatBot.createNewSession();
window.clearChat = () => window.chatBot.clearChat();
window.exportChat = () => window.chatBot.exportChat();
window.attachDocument = () => {
    Utils.showAlert('Document attachment feature coming soon!', 'info');
};

window.sendExampleQuestion = (button) => {
    const question = button.textContent;
    document.getElementById('messageInput').value = question;
    window.chatBot.sendMessage();
};

// Initialize chatbot when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.chatBot = new ChatBot();
});