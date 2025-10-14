# Setup and Installation Guide

## Prerequisites

Before setting up encycloped.ai, ensure you have the following installed:

- **Python 3.8+** (recommended: Python 3.10)
- **Docker and Docker Compose** (for database and Redis)
- **Git** (for cloning the repository)
- **pip** (Python package manager)

### Optional Prerequisites

- **Ollama** (for local LLM support)
- **OpenAI API Key** (for OpenAI API mode)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/VictoKu1/encycloped.ai.git
cd encycloped.ai
```

### 2. Set Up Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# .\venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start Database Services

```bash
# Start PostgreSQL and Redis using Docker Compose
docker-compose up -d
```

### 5. Initialize Database

```bash
# Set environment variables
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=encyclopedai
export DB_USER=encyclo_user
export DB_PASSWORD=encyclo_pass
export REDIS_HOST=localhost

# Initialize database schema
python utils/db.py --init
```

### 6. Run the Application

#### Option A: OpenAI API Mode (Default)

```bash
# Set your OpenAI API key
export OPENAI_API_KEY=your_openai_api_key_here

# Run the application
python app.py
```

#### Option B: Local LLM Mode

```bash
# Install and start Ollama
# Visit https://ollama.ai for installation instructions
ollama serve

# Pull a model (in another terminal)
ollama pull deepseek-coder:6.7b

# Configure local LLM
python setup_local_llm.py

# Test the setup
python test_local_llm.py

# Run in local LLM mode
python app.py local
```

### 7. Access the Application

Open your web browser and navigate to:
```
http://localhost:5000
```

## Detailed Setup Instructions

### Database Setup

#### Using Docker Compose (Recommended)

1. **Start services:**
   ```bash
   docker-compose up -d
   ```

2. **Verify services are running:**
   ```bash
   docker-compose ps
   ```

3. **Check logs if needed:**
   ```bash
   docker-compose logs db
   docker-compose logs redis
   ```

#### Manual PostgreSQL Setup

If you prefer to install PostgreSQL manually:

1. **Install PostgreSQL:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # macOS (with Homebrew)
   brew install postgresql
   
   # Windows
   # Download from https://www.postgresql.org/download/windows/
   ```

2. **Create database and user:**
   ```sql
   CREATE DATABASE encyclopedai;
   CREATE USER encyclo_user WITH PASSWORD 'encyclo_pass';
   GRANT ALL PRIVILEGES ON DATABASE encyclopedai TO encyclo_user;
   ```

3. **Install Redis:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install redis-server
   
   # macOS (with Homebrew)
   brew install redis
   
   # Windows
   # Download from https://github.com/microsoftarchive/redis/releases
   ```

### Environment Configuration

Create a `.env` file in the project root:

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

### Local LLM Setup

#### Install Ollama

1. **Download and install Ollama:**
   - Visit [ollama.ai](https://ollama.ai)
   - Follow installation instructions for your platform

2. **Start Ollama service:**
   ```bash
   ollama serve
   ```

3. **Pull a model:**
   ```bash
   # Recommended model
   ollama pull deepseek-coder:6.7b
   
   # Alternative models
   ollama pull llama3.2:3b  # Faster, smaller
   ollama pull deepseek-coder:33b  # Slower, higher quality
   ```

#### Configure Local LLM

1. **Interactive setup (recommended):**
   ```bash
   python setup_local_llm.py
   ```

2. **Manual configuration:**
   Edit `local_llm.json`:
   ```json
   {
     "model": "deepseek-coder:6.7b",
     "base_url": "http://localhost:11434"
   }
   ```

3. **Test the setup:**
   ```bash
   python test_local_llm.py
   ```

## Platform-Specific Instructions

### Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install Python and pip
sudo apt install python3 python3-pip python3-venv

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose

# Clone and setup
git clone https://github.com/VictoKu1/encycloped.ai.git
cd encycloped.ai
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### macOS

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and Docker
brew install python docker docker-compose

# Clone and setup
git clone https://github.com/VictoKu1/encycloped.ai.git
cd encycloped.ai
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Windows

1. **Install Python:**
   - Download from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH"

2. **Install Docker Desktop:**
   - Download from [docker.com](https://www.docker.com/products/docker-desktop)

3. **Install Git:**
   - Download from [git-scm.com](https://git-scm.com/download/win)

4. **Setup in PowerShell:**
   ```powershell
   # Clone repository
   git clone https://github.com/VictoKu1/encycloped.ai.git
   cd encycloped.ai
   
   # Create virtual environment
   python -m venv venv
   .\venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

## Verification

### Check Database Connection

```bash
# Test PostgreSQL connection
psql -h localhost -U encyclo_user -d encyclopedai -c "SELECT version();"

# Test Redis connection
redis-cli ping
```

### Test Application

1. **Start the application:**
   ```bash
   python app.py
   ```

2. **Test basic functionality:**
   - Navigate to `http://localhost:5000`
   - Search for a topic (e.g., "Python")
   - Verify article generation
   - Test feedback forms

3. **Test local LLM (if configured):**
   ```bash
   python app.py local
   ```

## Troubleshooting

### Common Issues

#### Database Connection Errors

**Error**: `psycopg2.OperationalError: could not connect to server`

**Solutions**:
1. Ensure PostgreSQL is running:
   ```bash
   docker-compose ps
   # or
   sudo systemctl status postgresql
   ```

2. Check environment variables:
   ```bash
   echo $DB_HOST $DB_PORT $DB_NAME $DB_USER
   ```

3. Verify database exists:
   ```bash
   psql -h localhost -U encyclo_user -d encyclopedai -c "\l"
   ```

#### Redis Connection Errors

**Error**: `redis.exceptions.ConnectionError`

**Solutions**:
1. Ensure Redis is running:
   ```bash
   docker-compose ps
   # or
   redis-cli ping
   ```

2. Check Redis configuration:
   ```bash
   echo $REDIS_HOST
   ```

#### Local LLM Issues

**Error**: `Ollama is not running or not accessible`

**Solutions**:
1. Start Ollama:
   ```bash
   ollama serve
   ```

2. Check if model is available:
   ```bash
   ollama list
   ```

3. Pull the model:
   ```bash
   ollama pull deepseek-coder:6.7b
   ```

#### OpenAI API Issues

**Error**: `OpenAI API error: local variable 'client' referenced before assignment`

**Solutions**:
1. Set API key:
   ```bash
   export OPENAI_API_KEY=your_key_here
   ```

2. Use local LLM mode instead:
   ```bash
   python app.py local
   ```

### Performance Issues

#### Slow Article Generation

**Local LLM Mode**:
- Use smaller models for faster responses
- Ensure sufficient RAM (8GB+ recommended)
- Consider using OpenAI API for better performance

**OpenAI API Mode**:
- Check internet connection
- Verify API key is valid
- Check rate limits

#### Memory Issues

**Solutions**:
1. Use smaller local LLM models
2. Increase system RAM
3. Close other applications
4. Use OpenAI API instead

## Development Setup

### Code Structure

```
encycloped.ai/
├── agents/           # LLM integration
├── content/          # Markdown processing
├── security/         # Input validation
├── utils/            # Database utilities
├── templates/        # HTML templates
├── static/           # CSS/JS assets
├── docs/             # Documentation
├── app.py            # Main application
├── requirements.txt  # Python dependencies
└── docker-compose.yml # Database services
```

### Running in Development Mode

```bash
# Enable debug mode
export FLASK_DEBUG=1

# Run with auto-reload
python app.py
```

### Testing

```bash
# Test local LLM setup
python test_local_llm.py

# Test database connection
python -c "from utils import db; print('DB OK' if db.get_connection() else 'DB Error')"
```

## Production Deployment

### Environment Variables

```bash
# Production environment
export FLASK_ENV=production
export DB_HOST=your_db_host
export REDIS_HOST=your_redis_host
export OPENAI_API_KEY=your_production_key
export FLASK_SECRET_KEY=your_production_secret
```

### Security Considerations

1. **Change default passwords**
2. **Use environment variables for secrets**
3. **Enable HTTPS in production**
4. **Configure firewall rules**
5. **Regular security updates**

### Monitoring

1. **Application logs**: `app.log`
2. **Database monitoring**: PostgreSQL logs
3. **Redis monitoring**: Redis logs
4. **System metrics**: CPU, memory, disk usage

## Support

If you encounter issues:

1. Check the [troubleshooting section](#troubleshooting)
2. Review application logs: `tail -f app.log`
3. Check database logs: `docker-compose logs db`
4. Open an issue on GitHub
5. Check the [API documentation](API.md)
6. Review the [architecture documentation](ARCHITECTURE.md)
