# Kanoon Ki Pechaan - Your Legal AI Assistant

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green)](https://palletsprojects.com/p/flask/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Welcome to **Kanoon Ki Pechaan** - a comprehensive legal technology platform that bridges the gap between legal professionals and clients through the power of AI. Our platform provides intelligent legal assistance, document analysis, and professional networking capabilities.

## 🌟 Why Kanoon Ki Pechaan?

Navigating the legal system can be overwhelming. Whether you're an individual seeking legal advice or a lawyer looking to expand your practice, Kanoon Ki Pechaan simplifies the process with:

- **AI-Powered Legal Assistance**: Get instant answers to your legal questions
- **Smart Document Analysis**: Upload and analyze legal documents with AI
- **Professional Networking**: Connect with qualified lawyers based on your needs
- **Secure & Confidential**: Your data is protected with enterprise-grade security

## 🚀 Key Features

### 🤖 AI Legal Assistant
Powered by Google's Gemini AI, our chatbot understands legal contexts and provides accurate information about:
- Indian Penal Code (IPC)
- Code of Criminal Procedure (CrPC)
- Constitution of India
- Civil laws and procedures
- Legal precedents and case studies

### 📄 Document Intelligence
Upload your legal documents and get:
- **Smart Summarization**: Key points extracted in seconds
- **Clause Analysis**: Detailed breakdown of important clauses
- **Risk Assessment**: Potential legal risks identified
- **Comparison Tools**: Compare similar documents side-by-side

### 👥 Lawyer Network
Find the right legal professional for your needs:
- **Specialization-Based Search**: Filter lawyers by expertise
- **Verified Profiles**: Authentic professional information
- **Client Reviews**: Make informed decisions with real feedback
- **Direct Communication**: Secure messaging with your chosen lawyer

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask 3.0.0
- **Database**: MySQL with SQLAlchemy ORM
- **AI Engine**: Google Gemini AI via LangChain
- **Authentication**: JWT + Flask-Login
- **API Design**: RESTful architecture

### Frontend
- **Templates**: Jinja2 with Bootstrap 5
- **Styling**: Modern dark theme with neon accents
- **Interactivity**: Vanilla JavaScript (ES6+)
- **Icons**: Font Awesome 6
- **Animations**: CSS transitions and effects

## 📦 Getting Started

### Prerequisites
Before you begin, ensure you have:
- Python 3.8 or higher
- MySQL 5.7+ or MySQL 8.0+
- Git (for cloning the repository)

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/shivamsinghtomar78/Kanoon_Ki_Pechaaan.git
   cd Kanoon_Ki_Pechaaan
   ```

2. **Set Up Virtual Environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   Create a `.env` file in the project root with the following:
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
   ```

5. **Set Up Database**
   ```bash
   # Create MySQL database
   mysql -u root -p
   CREATE DATABASE kanoon_ki_pechaan;
   exit;
   ```

6. **Run the Application**
   ```bash
   python run_flask.py
   ```

   The application will be available at `http://localhost:5000`

## 🎯 How to Use

### For Clients
1. **Register/Login**: Create your account
2. **Ask Legal Questions**: Use our AI chatbot for instant legal advice
3. **Analyze Documents**: Upload legal documents for smart analysis
4. **Find Lawyers**: Search and connect with qualified legal professionals
5. **Manage Profile**: Keep your information up-to-date

### For Lawyers
1. **Professional Profile**: Showcase your expertise and experience
2. **Client Connections**: Manage requests from potential clients
3. **Document Review**: Assist clients with document analysis
4. **Dashboard Insights**: Track your activity and performance
5. **Secure Communication**: Connect with clients through our platform

## 🏗️ Project Structure

```
Kanoon_Ki_Pechaaan/
├── app.py                     # Flask application entry point
├── run_flask.py              # Application startup script
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (not in repo)
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

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

If you need help or have questions:
- Open an issue on GitHub
- Contact our team at [support@kanoonkiprechaan.com](mailto:support@kanoonkiprechaan.com)

## 🙏 Acknowledgments

- Thanks to Google for providing the Gemini AI platform
- Inspired by the need to make legal services more accessible
- Built with ❤️ by the Kanoon Ki Pechaan team