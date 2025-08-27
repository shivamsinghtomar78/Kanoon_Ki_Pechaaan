# Kanoon Ki Pechaan - Legal AI Platform (Flask Version)

A comprehensive legal technology platform built with Flask, providing AI-powered legal assistance, document analysis, and lawyer networking capabilities.

## 🌟 Features

### 🤖 AI Legal Assistant
- Powered by Google Gemini AI
- Specialized legal knowledge base
- Real-time chat with legal context
- Session management and history

### 📄 Document Analysis
- PDF, DOC, DOCX, TXT file support
- AI-powered document summarization
- Legal document analysis
- Secure file upload and storage

### 👥 Lawyer Network
- Lawyer profile management
- Client-lawyer connection system
- Specialization-based search
- Professional networking features

### 🔐 Authentication & Security
- JWT-based authentication
- Secure password handling
- Session management
- Role-based access control

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask 3.0.0
- **Database**: MySQL with SQLAlchemy ORM
- **AI**: Google Gemini AI via LangChain
- **Authentication**: Flask-Login + JWT
- **API**: RESTful API design

### Frontend
- **Templates**: Jinja2 with Bootstrap 5
- **CSS**: Custom dark theme with modern styling
- **JavaScript**: Vanilla JS with modern ES6+ features
- **Icons**: Font Awesome 6
- **Animations**: CSS animations and transitions

### Database Schema
- **Users**: Authentication and profile management
- **Documents**: File storage and analysis results
- **Chat Sessions**: AI conversation history
- **Chat Messages**: Individual chat messages
- **Lawyer Connections**: Client-lawyer relationships

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- MySQL 5.7+ or MySQL 8.0+
- Git

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd Kanoon_Ki_Pechaaan
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration
Create a `.env` file in the project root:

```env
# Database Configuration
DB_HOST=localhost
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_NAME=kanoon_ki_pechaan
DB_PORT=3306

# Security Configuration
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Google AI Configuration
GOOGLE_API_KEY=your-google-ai-api-key

# Application Configuration
APP_DEBUG=True
APP_HOST=localhost
FLASK_PORT=5000
DEVELOPMENT_MODE=True

# File Upload Configuration
MAX_FILE_SIZE_MB=50
UPLOAD_FOLDER=uploads
ALLOWED_EXTENSIONS=pdf,doc,docx,txt

# Email Configuration (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_email_app_password

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=app.log
```

### Step 5: Database Setup
```bash
# Create MySQL database
mysql -u root -p
CREATE DATABASE kanoon_ki_pechaan;
exit;
```

### Step 6: Run the Application
```bash
python run_flask.py
```

The application will be available at `http://localhost:5000`

## 🚀 Quick Start

### Starting the Application
```bash
# Using the startup script (recommended)
python run_flask.py

# Or directly with Flask
python app.py
```

### First Time Setup
1. Visit `http://localhost:5000`
2. Click "Register" to create an account
3. Choose account type (Client or Lawyer)
4. Complete your profile
5. Start using the platform!

## 📱 Usage Guide

### For Clients
1. **Register/Login**: Create a client account
2. **AI Assistant**: Use the chatbot for legal queries
3. **Document Analysis**: Upload legal documents for AI analysis
4. **Find Lawyers**: Search and connect with legal professionals
5. **Profile Management**: Update your personal information

### For Lawyers
1. **Register/Login**: Create a lawyer account with professional details
2. **Profile Setup**: Add qualifications, specializations, and experience
3. **Client Connections**: Manage connection requests from clients
4. **Dashboard**: View statistics and recent activity
5. **Document Review**: Assist clients with document analysis

## 🏗️ Project Structure

```
Kanoon_Ki_Pechaaan/
├── app.py                     # Flask application entry point
├── run_flask.py              # Application startup script
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
├── .env.template            # Environment template
├── backend/                 # Backend API modules
│   ├── models.py           # Database models
│   ├── auth.py             # Authentication API
│   ├── chatbot.py          # AI chatbot API
│   ├── documents.py        # Document processing API
│   └── lawyers.py          # Lawyer network API
├── frontend/               # Frontend templates and assets
│   ├── templates/         # Jinja2 templates
│   │   ├── base.html      # Base template
│   │   ├── index.html     # Landing page
│   │   ├── auth/          # Authentication pages
│   │   ├── dashboard/     # Dashboard pages
│   │   ├── features/      # Feature pages
│   │   └── errors/        # Error pages
│   └── static/           # Static assets
│       ├── css/          # Stylesheets
│       ├── js/           # JavaScript files
│       └── images/       # Images and icons
└── uploads/              # File upload directory
```

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update user profile
- `PUT /api/auth/change-password` - Change password

### Chatbot
- `GET /api/chatbot/sessions` - Get chat sessions
- `POST /api/chatbot/sessions` - Create new session
- `GET /api/chatbot/sessions/{id}` - Get specific session
- `POST /api/chatbot/sessions/{id}/messages` - Send message
- `DELETE /api/chatbot/sessions/{id}` - Delete session

### Documents
- `GET /api/documents` - Get user documents
- `POST /api/documents/upload` - Upload document
- `GET /api/documents/{id}` - Get specific document
- `POST /api/documents/{id}/analyze` - Analyze document
- `DELETE /api/documents/{id}` - Delete document

### Lawyers
- `GET /api/lawyers/search` - Search lawyers
- `GET /api/lawyers/profile/{id}` - Get lawyer profile
- `GET /api/lawyers/specializations` - Get specializations
- `POST /api/lawyers/connect` - Send connection request
- `GET /api/lawyers/connections` - Get connections
- `PUT /api/lawyers/connections/{id}/respond` - Respond to connection

### Utility
- `GET /api/health` - Health check endpoint

## 🎨 Frontend Features

### Responsive Design
- Mobile-first approach
- Bootstrap 5 framework
- Custom dark theme
- Modern CSS animations

### Interactive Components
- Real-time chat interface
- File upload with progress
- Dynamic search and filtering
- Modal dialogs and forms

### User Experience
- Intuitive navigation
- Loading states and feedback
- Error handling and validation
- Accessibility considerations

## 🔒 Security Features

### Authentication
- JWT token-based authentication
- Secure password hashing with bcrypt
- Session management
- Password strength validation

### Data Protection
- SQL injection prevention with SQLAlchemy ORM
- XSS protection with template escaping
- CSRF protection
- Secure file upload handling

### API Security
- Input validation and sanitization
- Rate limiting (configurable)
- CORS configuration
- Secure headers

## 🧪 Testing

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-flask

# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html
```

### Test Structure
- Unit tests for API endpoints
- Integration tests for database operations
- Frontend JavaScript testing
- End-to-end testing scenarios

## 📊 Monitoring and Logging

### Application Logs
- Structured logging with Python logging module
- Log rotation and archival
- Error tracking and reporting
- Performance monitoring

### Health Monitoring
- `/api/health` endpoint for health checks
- Database connection monitoring
- AI service availability checks
- File system health verification

## 🚀 Deployment

### Production Setup
1. **Environment**: Set `DEVELOPMENT_MODE=False`
2. **Database**: Use production MySQL instance
3. **Web Server**: Deploy with Gunicorn + Nginx
4. **SSL**: Configure HTTPS certificates
5. **Monitoring**: Set up logging and monitoring

### Docker Deployment (Optional)
```dockerfile
# Dockerfile example
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"]
```

### Environment Variables for Production
```env
DEVELOPMENT_MODE=False
APP_DEBUG=False
SECRET_KEY=your-production-secret-key
DATABASE_URL=mysql://user:password@host:port/database
GOOGLE_API_KEY=your-production-api-key
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests for new features
5. Submit a pull request

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings for functions and classes
- Write comprehensive comments

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Gemini AI for powerful language models
- Flask community for the excellent web framework
- Bootstrap for responsive UI components
- Font Awesome for beautiful icons

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the FAQ section

---

**Kanoon Ki Pechaan** - Empowering legal access through technology 🏛️⚖️