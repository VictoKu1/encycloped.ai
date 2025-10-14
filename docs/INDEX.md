# encycloped.ai Documentation Index

Welcome to the comprehensive documentation for encycloped.ai, an AI-powered encyclopedia platform. This index provides quick access to all documentation resources.

## 📚 Documentation Overview

### For Users
- **[Main README](../README.md)** - Project overview, features, and quick start
- **[Setup Guide](SETUP.md)** - Step-by-step installation instructions
- **[API Documentation](API.md)** - API reference for developers

### For Developers
- **[Developer Guide](DEVELOPER_GUIDE.md)** - Comprehensive development information
- **[Architecture Documentation](ARCHITECTURE.md)** - System design and components
- **[Contributing Guidelines](CONTRIBUTING.md)** - How to contribute to the project

### For System Administrators
- **[Architecture Documentation](ARCHITECTURE.md)** - System design and deployment
- **[Setup Guide](SETUP.md)** - Production deployment instructions
- **[API Documentation](API.md)** - API monitoring and management

## 🚀 Quick Start

### 1. Get Started
```bash
# Clone the repository
git clone https://github.com/VictoKu1/encycloped.ai.git
cd encycloped.ai

# Set up environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start services
docker-compose up -d
python utils/db.py --init

# Run the application
python app.py
```

### 2. Access the Application
Open your browser and navigate to `http://localhost:5000`

### 3. Explore Features
- Search for topics (e.g., "Python", "Machine Learning")
- Select text to generate topic suggestions
- Use feedback forms to improve articles
- Explore the interconnected topic network

## 📖 Documentation Structure

### Core Documentation

| Document                                 | Purpose                        | Audience                  |
| ---------------------------------------- | ------------------------------ | ------------------------- |
| [README](../README.md)                   | Project overview and features  | All users                 |
| [API.md](API.md)                         | API reference and endpoints    | Developers, API users     |
| [ARCHITECTURE.md](ARCHITECTURE.md)       | System design and components   | Developers, System admins |
| [SETUP.md](SETUP.md)                     | Installation and configuration | All users                 |
| [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) | Development information        | Developers                |
| [CONTRIBUTING.md](CONTRIBUTING.md)       | Contribution guidelines        | Contributors              |

### Quick Reference

#### API Endpoints
- `GET /{topic}` - Generate/retrieve article
- `POST /report` - Report article issues
- `POST /add_info` - Add missing information
- `POST /suggest_topics` - Generate topic suggestions
- `POST /add_reference` - Add cross-references

#### Key Features
- **AI Content Generation**: OpenAI API and local LLM support
- **Interactive Features**: Topic suggestions, user feedback
- **Security**: XSS protection, rate limiting, input validation
- **Persistent Storage**: PostgreSQL database, Redis caching

#### Technology Stack
- **Backend**: Flask, PostgreSQL, Redis
- **AI/ML**: OpenAI API, Ollama (local LLMs)
- **Frontend**: HTML5, CSS3, JavaScript, jQuery
- **Infrastructure**: Docker, Docker Compose

## 🔧 Development

### Prerequisites
- Python 3.8+ (recommended: Python 3.10)
- Docker and Docker Compose
- Git
- Basic knowledge of Flask, PostgreSQL, and LLM APIs

### Development Setup
1. Follow the [Setup Guide](SETUP.md) for installation
2. Read the [Developer Guide](DEVELOPER_GUIDE.md) for detailed information
3. Check [Contributing Guidelines](CONTRIBUTING.md) for contribution process

### Code Structure
```
encycloped.ai/
├── agents/           # LLM integration
├── content/          # Content processing
├── security/         # Security features
├── utils/            # Database utilities
├── templates/        # HTML templates
├── static/           # CSS/JS assets
├── docs/             # Documentation
└── app.py            # Main application
```

## 🛠️ Configuration

### Environment Variables
```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=encyclopedai
DB_USER=encyclo_user
DB_PASSWORD=encyclo_pass

# Redis Configuration
REDIS_HOST=localhost

# OpenAI API (optional)
OPENAI_API_KEY=your_openai_api_key_here

# Flask Configuration
FLASK_SECRET_KEY=your_secret_key_here
```

### Local LLM Configuration
```json
{
  "model": "deepseek-coder:6.7b",
  "base_url": "http://localhost:11434"
}
```

## 🔒 Security

### Security Features
- **XSS Protection**: HTML sanitization with bleach
- **Rate Limiting**: IP-based rate limiting using Redis
- **Input Validation**: Comprehensive input validation and sanitization
- **Content Security**: Path traversal prevention, SQL injection protection

### Security Best Practices
- Validate all inputs before processing
- Sanitize HTML content before rendering
- Use parameterized queries to prevent SQL injection
- Implement rate limiting to prevent abuse
- Log security events for monitoring

## 📊 Monitoring and Logging

### Application Logs
- Structured logging to `app.log`
- Contribution tracking
- Error logging with stack traces

### Database Monitoring
- Query performance monitoring
- Connection monitoring
- Data integrity checks

### System Metrics
- Rate limiting statistics
- LLM response times
- Database query performance
- System resource usage

## 🚀 Deployment

### Development Deployment
```bash
# Start services
docker-compose up -d

# Set environment variables
export DB_HOST=localhost DB_PORT=5432 DB_NAME=encyclopedai DB_USER=encyclo_user DB_PASSWORD=encyclo_pass REDIS_HOST=localhost

# Initialize database
python utils/db.py --init

# Run application
python app.py
```

### Production Deployment
- Use environment variables for configuration
- Enable HTTPS in production
- Set secure session cookies
- Configure proper CORS headers
- Regular security updates

## 🤝 Contributing

### How to Contribute
1. Read the [Contributing Guidelines](CONTRIBUTING.md)
2. Check open issues for areas to contribute
3. Follow the code style and testing guidelines
4. Submit pull requests for review

### Areas for Contribution
- **Bug fixes** for reported issues
- **Security improvements**
- **Performance optimizations**
- **Test coverage improvements**
- **New features** from issue requests
- **UI/UX improvements**
- **Documentation enhancements**

## 📞 Support

### Getting Help
- **Documentation**: Check the relevant documentation files
- **Issues**: Report bugs or request features on GitHub
- **Discussions**: Join community discussions on GitHub

### Resources
- [Flask Documentation](https://flask.palletsprojects.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)
- [Ollama Documentation](https://ollama.ai/docs)

## 📄 License

This project is licensed under the [GNU General Public License v3 (GPL v3)](../LICENSE).

## 🙏 Acknowledgments

- [Flask](https://flask.palletsprojects.com/) - Web framework
- [OpenAI](https://openai.com/) - AI content generation
- [PostgreSQL](https://www.postgresql.org/) - Database
- [Redis](https://redis.io/) - Caching and rate limiting
- [Docker](https://www.docker.com/) - Containerization
- The open-source community for inspiration and contributions

---

**Need help?** Check the [Setup Guide](SETUP.md) for installation instructions or the [API Documentation](API.md) for technical details.
