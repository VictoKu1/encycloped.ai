# Architecture Documentation

## Overview

encycloped.ai is a Flask-based web application that generates AI-powered encyclopedia articles with community feedback integration. The system supports both OpenAI API and local LLM modes for content generation.

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │    │   Flask App     │    │   PostgreSQL    │
│                 │◄──►│                 │◄──►│   Database      │
│  - Search UI    │    │  - Routes       │    │  - Topics       │
│  - Article View │    │  - LLM Agents   │    │  - Logs         │
│  - Modals       │    │  - Validation   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Redis Cache   │
                       │  - Rate Limiting│
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   LLM Service   │
                       │  - OpenAI API   │
                       │  - Local Ollama │
                       └─────────────────┘
```

## Core Components

### 1. Flask Application (`app.py`)

**Purpose**: Main web application entry point and request routing.

**Key Features**:
- Route handling for article generation and management
- Rate limiting using Flask-Limiter
- AJAX support for dynamic content updates
- Error handling and validation

**Main Routes**:
- `GET /`: Home page with search functionality
- `GET /{topic}`: Generate/display article for topic
- `POST /report`: Report issues with articles
- `POST /add_info`: Add missing information
- `POST /suggest_topics`: Generate topic suggestions
- `POST /add_reference`: Add cross-references

### 2. Agents Module (`agents/`)

**Purpose**: Handles all LLM interactions and content generation.

#### Topic Generator (`agents/topic_generator.py`)

**Key Functions**:
- `generate_topic_content()`: Creates new encyclopedia articles
- `update_topic_content()`: Updates existing articles
- `extract_topic_suggestions()`: Extracts related topics from content
- `process_user_feedback()`: Processes user reports and additions
- `validate_topic_name_with_llm()`: Validates topic names using AI

**LLM Integration**:
- Unified interface for OpenAI API and local LLMs
- Optimized prompts for different LLM types
- Error handling and fallback mechanisms

#### Local LLM (`agents/local_llm.py`)

**Key Features**:
- Ollama client integration
- Model validation and setup
- Configuration management
- Timeout handling for local models

**Supported Models**:
- DeepSeek-Coder (recommended)
- Llama 3.2
- Other Ollama-compatible models

### 3. Content Processing (`content/`)

#### Markdown Processor (`content/markdown_processor.py`)

**Key Functions**:
- `convert_markdown()`: Converts Markdown to HTML
- `linkify_topics()`: Creates internal links between articles
- `remove_duplicate_header()`: Cleans up redundant headers
- `linkify_references()`: Creates clickable reference links

**Features**:
- Math equation support (LaTeX/MathJax)
- Reference linking system
- HTML sanitization
- Topic suggestion integration

### 4. Security Module (`security/`)

#### Validators (`security/validators.py`)

**Security Features**:
- Input sanitization using bleach
- XSS protection
- Path traversal prevention
- JSON payload validation
- Rate limiting support

**Validation Functions**:
- `validate_topic_slug()`: Validates topic names
- `sanitize_html()`: Sanitizes HTML content
- `sanitize_text()`: Sanitizes plain text
- `validate_json_payload()`: Validates API requests

### 5. Data Layer (`utils/`)

#### Database (`utils/db.py`)

**Database Schema**:
```sql
-- Topics table
CREATE TABLE topics (
    id SERIAL PRIMARY KEY,
    topic_key TEXT UNIQUE NOT NULL,
    content TEXT NOT NULL,
    markdown TEXT,
    generated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    topic_suggestions JSONB
);

-- Logs table
CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    event_time TIMESTAMP NOT NULL DEFAULT NOW(),
    event_type TEXT NOT NULL,
    details TEXT
);
```

**Key Functions**:
- `init_db()`: Initialize database schema
- `save_topic()`: Save/update topic data
- `get_topic()`: Retrieve topic data
- `log_event()`: Log system events

#### Data Store (`utils/data_store.py`)

**Key Functions**:
- `is_topic_outdated()`: Check if content needs updating
- `get_topic_data()`: Retrieve formatted topic data
- `save_topic_data()`: Save topic with metadata
- `topic_exists()`: Check topic existence

### 6. Frontend (`templates/`, `static/`)

#### Templates
- `index.html`: Home page with search
- `topic.html`: Article display page
- `base.html`: Base template (if used)

#### Static Assets
- `css/style.css`: Styling and responsive design
- `js/main.js`: JavaScript functionality

**Frontend Features**:
- Interactive topic suggestion system
- Modal-based feedback forms
- AJAX-powered content updates
- Responsive design
- Accessibility support

## Data Flow

### 1. Article Generation Flow

```
User Input → Topic Validation → LLM Generation → Content Processing → Database Storage → HTML Rendering
```

1. **User enters topic** in search form
2. **Topic validation** checks if name is valid
3. **LLM generates content** (OpenAI API or local LLM)
4. **Content processing** converts Markdown to HTML
5. **Database storage** saves article and metadata
6. **HTML rendering** displays formatted article

### 2. User Feedback Flow

```
User Feedback → Validation → LLM Processing → Content Update → Database Update → UI Refresh
```

1. **User submits feedback** via modal
2. **Input validation** sanitizes and validates data
3. **LLM processes feedback** and generates updates
4. **Content update** applies changes to article
5. **Database update** saves new content
6. **UI refresh** shows updated article

### 3. Topic Suggestion Flow

```
Text Selection → LLM Analysis → Topic Extraction → Validation → Link Creation → UI Update
```

1. **User selects text** in article
2. **LLM analyzes text** to extract terms
3. **Topic extraction** identifies potential topics
4. **Validation** ensures topics are relevant
5. **Link creation** converts text to clickable links
6. **UI update** shows new links

## Configuration

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
OPENAI_API_KEY=your_api_key

# Flask Configuration
FLASK_SECRET_KEY=your_secret_key
```

### Local LLM Configuration

```json
{
  "model": "deepseek-coder:6.7b",
  "base_url": "http://localhost:11434"
}
```

## Security Architecture

### Input Validation
- All user inputs are sanitized using bleach
- Topic names are validated against regex patterns
- JSON payloads are validated for required fields

### XSS Protection
- HTML content is sanitized before rendering
- Only whitelisted HTML tags and attributes are allowed
- User-generated content is escaped

### Rate Limiting
- IP-based rate limiting using Redis
- Different limits for different endpoint types
- Prevents abuse and DoS attacks

### Content Security
- Path traversal prevention
- SQL injection protection via parameterized queries
- CSRF protection through Flask-WTF

## Scalability Considerations

### Database
- PostgreSQL provides ACID compliance
- JSONB columns for flexible metadata storage
- Indexed topic keys for fast lookups

### Caching
- Redis used for rate limiting
- Database queries are optimized
- Static content served efficiently

### LLM Integration
- Supports both cloud and local LLMs
- Timeout handling for reliability
- Fallback mechanisms for errors

## Deployment Architecture

### Development
```
Flask App (localhost:5000) → PostgreSQL (localhost:5432) → Redis (localhost:6379)
```

### Production (Docker)
```
Flask App → PostgreSQL Container → Redis Container
```

### Docker Compose Services
- **PostgreSQL**: Database service
- **Redis**: Rate limiting service
- **Flask App**: Web application (not containerized by default)

## Monitoring and Logging

### Application Logs
- Structured logging to `app.log`
- Contribution tracking
- Error logging with stack traces

### Database Logs
- Query logging (if enabled)
- Connection monitoring
- Performance metrics

### System Metrics
- Rate limiting statistics
- LLM response times
- Database query performance

## Future Enhancements

### Planned Features
- User authentication system
- Content versioning
- Advanced search functionality
- API rate limiting per user
- Content moderation tools

### Technical Improvements
- Microservices architecture
- Kubernetes deployment
- Advanced caching strategies
- Real-time collaboration
- Mobile app support
