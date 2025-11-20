# encycloped.ai Documentation

Welcome to the encycloped.ai documentation! This directory contains comprehensive documentation for the AI Moderated Encyclopedia project.

## Documentation Overview

### 📚 [API Documentation](API.md)
Complete API reference with endpoints, request/response examples, and error handling.

**Key Topics:**
- Article generation endpoints
- User feedback endpoints
- Topic suggestion system
- Rate limiting and security
- Response codes and error handling

### 🔒 [Security Documentation](SECURITY.md)
Comprehensive security features, threat mitigation, and best practices.

**Key Topics:**
- Prompt injection protection
- XSS and injection prevention
- DoS protection and rate limiting
- Content poisoning prevention
- Review queue and admin tools
- Security best practices

### 🍔 [Hamburger Menu Documentation](HAMBURGER_MENU.md)
Complete guide to the hamburger menu feature and recent topics navigation.

**Key Topics:**
- User interface and interactions
- Local storage implementation
- JavaScript functionality
- CSS styling and animations
- Accessibility features
- Troubleshooting guide

### 🏗️ [Architecture Documentation](ARCHITECTURE.md)
Detailed system architecture, component relationships, and technical design.

**Key Topics:**
- System architecture overview
- Component descriptions
- Data flow diagrams
- Security architecture
- Scalability considerations
- Deployment strategies

### 🚀 [Setup and Installation Guide](SETUP.md)
Step-by-step instructions for setting up the development and production environments.

**Key Topics:**
- Prerequisites and requirements
- Quick start guide
- Platform-specific instructions
- Database setup
- Local LLM configuration
- Troubleshooting common issues

### 🤝 [Contributing Guidelines](CONTRIBUTING.md)
Guidelines for contributors, including code style, testing, and pull request process.

**Key Topics:**
- Development setup
- Code style guidelines
- Testing requirements
- Issue reporting
- Pull request process
- Areas for contribution

## Quick Links

### For Users
- [Main README](../README.md) - Project overview and features
- [Setup Guide](SETUP.md) - Get started quickly
- [API Documentation](API.md) - Use the API

### For Developers
- [Architecture Documentation](ARCHITECTURE.md) - Understand the system
- [Security Documentation](SECURITY.md) - Security implementation details
- [Contributing Guidelines](CONTRIBUTING.md) - Contribute to the project
- [Setup Guide](SETUP.md) - Development environment

### For System Administrators
- [Architecture Documentation](ARCHITECTURE.md) - System design
- [Security Documentation](SECURITY.md) - Security features and incident response
- [Setup Guide](SETUP.md) - Production deployment
- [API Documentation](API.md) - API monitoring

## Project Structure

```
encycloped.ai/
├── docs/                    # Documentation
│   ├── API.md              # API reference
│   ├── ARCHITECTURE.md     # System architecture
│   ├── HAMBURGER_MENU.md   # Hamburger menu documentation
│   ├── SETUP.md            # Setup instructions
│   ├── CONTRIBUTING.md     # Contributing guidelines
│   └── README.md           # This file
├── agents/                 # LLM integration
├── content/                # Content processing
├── security/               # Security features
├── utils/                  # Database utilities
├── templates/              # HTML templates
├── static/                 # CSS/JS assets
├── app.py                  # Main application
├── requirements.txt        # Dependencies
└── docker-compose.yml      # Database services
```

## Key Features

### 🤖 AI-Powered Content Generation
- Dynamic encyclopedia article generation
- Support for both OpenAI API and local LLMs
- Intelligent topic disambiguation
- Real-time content updates

### 🔒 Security and Validation
- XSS protection with HTML sanitization
- Rate limiting to prevent abuse
- Input validation and sanitization
- Secure session management

### 🌐 Interactive Features
- Topic suggestion system
- User feedback integration
- Cross-reference linking
- Responsive web interface
- Recent topics navigation (hamburger menu)

### 💾 Persistent Storage
- PostgreSQL database for articles
- Redis for rate limiting
- JSON metadata storage
- Data durability and reliability

## Technology Stack

### Backend
- **Flask**: Web framework
- **PostgreSQL**: Primary database
- **Redis**: Rate limiting cache
- **OpenAI API**: AI content generation
- **Ollama**: Local LLM support

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Responsive styling
- **JavaScript**: Interactive features
- **jQuery**: DOM manipulation

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Service orchestration
- **Python 3.8+**: Runtime environment

## Getting Started

### 1. Quick Start
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
- Access recently viewed topics via the hamburger menu

## Support and Community

### Getting Help
- **Documentation**: Check the relevant documentation files
- **Issues**: Report bugs or request features on GitHub
- **Discussions**: Join community discussions on GitHub

### Contributing
- Read the [Contributing Guidelines](CONTRIBUTING.md)
- Check open issues for areas to contribute
- Follow the code style and testing guidelines
- Submit pull requests for review

### License
This project is licensed under the [GNU General Public License v3 (GPL v3)](../LICENSE).

## Changelog

### Recent Updates
- Added comprehensive documentation
- Improved local LLM support
- Enhanced security features
- Better error handling and validation
- Added hamburger menu with recent topics navigation

### Upcoming Features
- User authentication system
- Advanced search functionality
- Content versioning
- API rate limiting per user

## Acknowledgments

- [Flask](https://flask.palletsprojects.com/) - Web framework
- [OpenAI](https://openai.com/) - AI content generation
- [PostgreSQL](https://www.postgresql.org/) - Database
- [Redis](https://redis.io/) - Caching and rate limiting
- [Docker](https://www.docker.com/) - Containerization
- The open-source community for inspiration and contributions

---

**Need help?** Check the [Setup Guide](SETUP.md) for installation instructions or the [API Documentation](API.md) for technical details.
