# Developer Guide

This guide provides detailed information for developers working on encycloped.ai, including code structure, development workflows, and advanced topics.

## Table of Contents

- [Codebase Overview](#codebase-overview)
- [Development Workflow](#development-workflow)
- [Code Structure](#code-structure)
- [Key Components](#key-components)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
- [Frontend Architecture](#frontend-architecture)
- [LLM Integration](#llm-integration)
- [Security Implementation](#security-implementation)
- [Testing Strategy](#testing-strategy)
- [Debugging](#debugging)
- [Performance Optimization](#performance-optimization)
- [Deployment](#deployment)

## Codebase Overview

### Project Structure

```
encycloped.ai/
├── agents/                 # LLM integration and content generation
│   ├── __init__.py
│   ├── topic_generator.py  # Main LLM interaction logic
│   └── local_llm.py        # Local LLM (Ollama) integration
├── content/                # Content processing and formatting
│   ├── __init__.py
│   └── markdown_processor.py
├── security/               # Security and validation
│   ├── __init__.py
│   └── validators.py
├── utils/                  # Database and utility functions
│   ├── __init__.py
│   ├── db.py              # Database operations
│   └── data_store.py      # Data management layer
├── templates/              # HTML templates
│   ├── base.html
│   ├── index.html
│   └── topic.html
├── static/                 # Static assets
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── docs/                   # Documentation
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── docker-compose.yml      # Database services
├── local_llm.json         # Local LLM configuration
└── setup_local_llm.py     # Local LLM setup script
```

### Technology Stack

- **Backend**: Flask, PostgreSQL, Redis
- **AI/ML**: OpenAI API, Ollama (local LLMs)
- **Frontend**: HTML5, CSS3, JavaScript, jQuery
- **Infrastructure**: Docker, Docker Compose
- **Security**: Bleach, Flask-Limiter, Werkzeug

## Development Workflow

### 1. Environment Setup

```bash
# Clone and setup
git clone https://github.com/VictoKu1/encycloped.ai.git
cd encycloped.ai
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start services
docker-compose up -d
export DB_HOST=localhost DB_PORT=5432 DB_NAME=encyclopedai DB_USER=encyclo_user DB_PASSWORD=encyclo_pass REDIS_HOST=localhost
python utils/db.py --init
```

### 2. Development Mode

```bash
# Run with debug mode
export FLASK_DEBUG=1
python app.py

# Or with local LLM
python app.py local
```

### 3. Code Organization

- **Modular design**: Each module has a specific responsibility
- **Separation of concerns**: UI, business logic, and data access are separated
- **Configuration management**: Environment variables for different settings
- **Error handling**: Comprehensive error handling throughout

## Code Structure

### Main Application (`app.py`)

The main Flask application handles routing, request processing, and response generation.

**Key Functions:**
- `index()`: Home page and topic search
- `topic_page()`: Article generation and display
- `report_issue()`: User feedback processing
- `add_information()`: Content addition
- `suggest_topics()`: Topic suggestion generation
- `add_reference()`: Cross-reference creation

**Request Flow:**
```
Request → Validation → Business Logic → Database → Response
```

### Agents Module (`agents/`)

Handles all LLM interactions and content generation.

#### Topic Generator (`agents/topic_generator.py`)

**Core Functions:**
```python
def generate_topic_content(topic: str) -> tuple[str, str]:
    """Generate encyclopedia article for a topic."""
    
def update_topic_content(topic: str, current_content: str) -> tuple[str, str]:
    """Update existing article content."""
    
def extract_topic_suggestions(article_text: str) -> list[str]:
    """Extract related topics from article text."""
    
def process_user_feedback(topic: str, current_content: str, 
                         feedback_type: str, feedback_details: str, 
                         sources: list[str]) -> tuple[str, str]:
    """Process user reports and additions."""
```

**LLM Integration:**
- Unified interface for OpenAI API and local LLMs
- Optimized prompts for different model types
- Error handling and fallback mechanisms
- Timeout management for local models

#### Local LLM (`agents/local_llm.py`)

**Key Classes:**
```python
class OllamaClient:
    """Client for interacting with Ollama API."""
    
    def is_available(self) -> bool:
        """Check if Ollama is running."""
        
    def generate(self, model: str, messages: list, 
                max_tokens: int = 800, 
                temperature: float = 0.7) -> Optional[str]:
        """Generate response using specified model."""
```

### Content Processing (`content/`)

Handles markdown processing, HTML conversion, and content formatting.

#### Markdown Processor (`content/markdown_processor.py`)

**Key Functions:**
```python
def convert_markdown(content: str) -> str:
    """Convert Markdown to HTML with security sanitization."""
    
def linkify_topics(markdown_content: str, topic_suggestions: list[str]) -> str:
    """Create internal links between articles."""
    
def remove_duplicate_header(html: str, topic: str) -> str:
    """Remove redundant headers from content."""
```

**Features:**
- Math equation support (LaTeX/MathJax)
- Reference linking system
- HTML sanitization
- Topic suggestion integration

### Security Module (`security/`)

Implements security measures and input validation.

#### Validators (`security/validators.py`)

**Security Functions:**
```python
def validate_topic_slug(topic: str) -> str:
    """Validate topic names against allowed patterns."""
    
def sanitize_html(html_content: str) -> str:
    """Sanitize HTML content using bleach."""
    
def sanitize_text(text_content: str) -> str:
    """Sanitize plain text content."""
    
def validate_json_payload(data: dict, required_fields: list) -> bool:
    """Validate JSON payload has required fields."""
```

**Security Features:**
- XSS protection with HTML sanitization
- Input validation and sanitization
- Path traversal prevention
- Rate limiting support

### Data Layer (`utils/`)

Handles database operations and data management.

#### Database (`utils/db.py`)

**Database Schema:**
```sql
CREATE TABLE topics (
    id SERIAL PRIMARY KEY,
    topic_key TEXT UNIQUE NOT NULL,
    content TEXT NOT NULL,
    markdown TEXT,
    generated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    topic_suggestions JSONB
);

CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    event_time TIMESTAMP NOT NULL DEFAULT NOW(),
    event_type TEXT NOT NULL,
    details TEXT
);
```

**Key Functions:**
```python
def init_db():
    """Initialize database schema."""
    
def save_topic(topic_key: str, content: str, markdown: str, 
               topic_suggestions: Optional[str] = None):
    """Save or update topic data."""
    
def get_topic(topic_key: str) -> Optional[dict]:
    """Retrieve topic data."""
```

#### Data Store (`utils/data_store.py`)

**Data Management Functions:**
```python
def is_topic_outdated(generated_at_str: str) -> bool:
    """Check if topic content is older than 30 days."""
    
def get_topic_data(topic_key: str) -> Optional[dict]:
    """Get formatted topic data from database."""
    
def save_topic_data(topic_key: str, content: str, 
                   markdown_content: str, 
                   topic_suggestions: Optional[list] = None):
    """Save topic data with metadata."""
```

## Database Schema

### Topics Table

| Column              | Type                 | Description                  |
| ------------------- | -------------------- | ---------------------------- |
| `id`                | SERIAL PRIMARY KEY   | Unique identifier            |
| `topic_key`         | TEXT UNIQUE NOT NULL | Lowercase topic name         |
| `content`           | TEXT NOT NULL        | HTML content                 |
| `markdown`          | TEXT                 | Original markdown content    |
| `generated_at`      | TIMESTAMP            | Creation/update timestamp    |
| `topic_suggestions` | JSONB                | Related topics as JSON array |

### Logs Table

| Column       | Type               | Description       |
| ------------ | ------------------ | ----------------- |
| `id`         | SERIAL PRIMARY KEY | Unique identifier |
| `event_time` | TIMESTAMP          | Event timestamp   |
| `event_type` | TEXT               | Type of event     |
| `details`    | TEXT               | Event details     |

## API Endpoints

### GET `/{topic}`

**Purpose**: Generate or retrieve encyclopedia article

**Parameters**:
- `topic` (string): Topic name

**Response**: HTML page with article content

**Process**:
1. Validate topic name
2. Check if topic exists in database
3. Check if content is outdated (>30 days)
4. Generate new content if needed
5. Process and format content
6. Save to database
7. Return HTML page

### POST `/report`

**Purpose**: Report issues with articles

**Request Body**:
```json
{
  "topic": "Python",
  "report_details": "The section on history is outdated.",
  "sources": ["https://source1.com"]
}
```

**Response**:
```json
{
  "reply": "1",
  "updated_content": "<html>Updated content</html>"
}
```

### POST `/add_info`

**Purpose**: Add missing information to articles

**Request Body**:
```json
{
  "topic": "Python",
  "subtopic": "Libraries",
  "info": "Python has many libraries...",
  "sources": ["https://example.com"]
}
```

### POST `/suggest_topics`

**Purpose**: Generate topic suggestions from selected text

**Request Body**:
```json
{
  "selected_text": "Python is a programming language...",
  "current_topic": "Python"
}
```

**Response**:
```json
{
  "suggestions": ["programming language", "Python", "interpreted"]
}
```

## Frontend Architecture

### HTML Templates

#### Base Template (`templates/base.html`)
- Common HTML structure
- CSS and JavaScript includes
- Footer and header elements

#### Index Template (`templates/index.html`)
- Home page with search functionality
- Invalid topic modal
- Search form handling

#### Topic Template (`templates/topic.html`)
- Article display page
- Feedback modals (report, add info)
- Topic suggestion modal
- Interactive features

### CSS Architecture (`static/css/style.css`)

**Key Components**:
- **Layout**: Flexbox and Grid for responsive design
- **Components**: Reusable UI components
- **Modals**: Overlay and modal styling
- **Forms**: Input and button styling
- **Responsive**: Mobile-first design

### JavaScript (`static/js/main.js`)

**Key Features**:
- **Text Selection**: Handle text selection for topic suggestions
- **Modal Management**: Open/close modals and handle interactions
- **AJAX Requests**: Send feedback and suggestions to backend
- **Form Validation**: Client-side validation
- **Event Handling**: User interaction management
- **Hamburger Menu**: Recent topics navigation and local storage

### Hamburger Menu Implementation

The hamburger menu provides users with quick access to their recently viewed topics, stored locally in the browser.

#### HTML Structure

**Base Template (`templates/base.html`)**:
```html
<!-- Hamburger Menu Button -->
<button id="hamburger-menu" class="hamburger-menu" title="Recent Topics">
  <span></span>
  <span></span>
  <span></span>
</button>

<!-- Sidebar for Recent Topics -->
<div id="sidebar" class="sidebar">
  <div class="sidebar-header">
    <h3>Recent Topics</h3>
    <button id="close-sidebar" class="close-sidebar">&times;</button>
  </div>
  <div class="sidebar-content">
    <div id="recent-topics-list" class="recent-topics-list">
      <p class="no-topics">No recent topics yet</p>
    </div>
  </div>
</div>

<!-- Overlay for sidebar -->
<div id="sidebar-overlay" class="sidebar-overlay"></div>
```

#### CSS Styling

**Key CSS Classes**:
```css
.hamburger-menu {
    background-color: #f2f2f2;
    border: none;
    cursor: pointer;
    padding: 8px;
    margin-right: 15px;
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    width: 30px;
    height: 30px;
    z-index: 1001;
    position: relative;
    border-radius: 4px;
}

.sidebar {
    position: fixed;
    top: 0;
    left: -300px;
    width: 300px;
    height: 100vh;
    background-color: #2c3e50;
    color: white;
    transition: left 0.3s ease;
    z-index: 1003;
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
}

.sidebar.open {
    left: 0;
}
```

#### JavaScript Functionality

**Core Functions**:
```javascript
// Recent topics storage key
const RECENT_TOPICS_KEY = 'encycloped_ai_recent_topics';
const MAX_RECENT_TOPICS = 20;

// Save topic to recent topics
function saveTopicToRecent(topic) {
    if (!topic) return;
    
    let recentTopics = JSON.parse(localStorage.getItem(RECENT_TOPICS_KEY) || '[]');
    
    // Remove if already exists (to move to top)
    recentTopics = recentTopics.filter(t => t.topic !== topic);
    
    // Add to beginning
    recentTopics.unshift({
        topic: topic,
        timestamp: Date.now(),
        url: window.location.href
    });
    
    // Keep only the most recent topics
    if (recentTopics.length > MAX_RECENT_TOPICS) {
        recentTopics = recentTopics.slice(0, MAX_RECENT_TOPICS);
    }
    
    localStorage.setItem(RECENT_TOPICS_KEY, JSON.stringify(recentTopics));
    updateRecentTopicsDisplay();
}

// Toggle sidebar
function toggleSidebar() {
    const $sidebar = $('#sidebar');
    const $overlay = $('#sidebar-overlay');
    const $hamburger = $('#hamburger-menu');
    
    $sidebar.toggleClass('open');
    $overlay.toggleClass('open');
    $hamburger.toggleClass('active');
    $('body').toggleClass('sidebar-open');
}
```

#### Features

1. **Local Storage**: Topics are stored in browser's localStorage
2. **Automatic Tracking**: Topics are automatically added when visited
3. **Sorting**: Topics are sorted by most recent first
4. **Persistence**: Data persists across browser sessions
5. **Responsive**: Works on desktop and mobile devices
6. **Accessibility**: Keyboard navigation (Escape to close)

#### Data Structure

**Recent Topics Storage**:
```javascript
[
    {
        "topic": "Python (Programming Language)",
        "timestamp": 1703123456789,
        "url": "http://localhost:5000/python%20%28programming%20language%29"
    },
    {
        "topic": "Machine Learning",
        "timestamp": 1703123400000,
        "url": "http://localhost:5000/machine%20learning"
    }
]
```

#### Event Handlers

```javascript
// Hamburger menu click
$('#hamburger-menu').click(function(e) {
    e.preventDefault();
    e.stopPropagation();
    toggleSidebar();
});

// Close sidebar
$('#close-sidebar').click(function(e) {
    e.preventDefault();
    closeSidebar();
});

// Overlay click to close
$('#sidebar-overlay').click(function(e) {
    e.preventDefault();
    closeSidebar();
});

// Escape key to close
$(document).keydown(function(e) {
    if (e.key === 'Escape' && $('#sidebar').hasClass('open')) {
        closeSidebar();
    }
});
```

## LLM Integration

### OpenAI API Integration

**Configuration**:
```python
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
```

**Usage**:
```python
response = client.chat.completions.create(
    model="gpt-4.1",
    messages=messages,
    max_tokens=max_tokens,
    temperature=temperature,
)
```

### Local LLM Integration (Ollama)

**Configuration**:
```json
{
  "model": "deepseek-coder:6.7b",
  "base_url": "http://localhost:11434"
}
```

**Usage**:
```python
client = OllamaClient(base_url="http://localhost:11434")
response = client.generate(model, messages, max_tokens, temperature)
```

### Prompt Engineering

**Topic Generation Prompt**:
```
Write an encyclopedia-style article about '{topic}' using Markdown formatting, UNLESS the topic is ambiguous (has multiple common meanings or interpretations). If the topic is ambiguous, do NOT generate an article. Instead, return a short intro sentence (for example: 'The topic <topic> may have several meanings, did you mean:'), then a numbered list, one per line, where each line is in the format '1. topic (option1)', '2. topic (option2)', etc. Do not add any extra explanations or formatting. Return the special code 45 as the reply code on the first line.
```

**Topic Suggestion Prompt**:
```
EXTRACT ONLY terms that are ACTUALLY MENTIONED in the selected text below. Do NOT generate related concepts or interpretations. Look for specific words, phrases, or terms that appear in the text and could be encyclopedia topics.
```

## Security Implementation

### Input Validation

**Topic Name Validation**:
```python
TOPIC_SLUG_REGEX = re.compile(r'^[a-zA-Z0-9_\-\s\+#\(\)\.,:;!\?/\[\]\{\}\'\"&\*%\$@\^=~\|<>]{1,100}$')
```

**HTML Sanitization**:
```python
ALLOWED_TAGS = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'li', 'strong', 'em', 'a', 'blockquote', 'code']
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'h1': ['id'], 'h2': ['id'], 'h3': ['id'], 'h4': ['id'], 'h5': ['id'], 'h6': ['id']
}
```

### Rate Limiting

**Configuration**:
```python
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

**Endpoint-Specific Limits**:
```python
@limiter.limit("5 per minute")
def report_issue():
    # Implementation
```

### Content Security

- **XSS Protection**: HTML sanitization with bleach
- **CSRF Protection**: Flask-WTF integration
- **Path Traversal**: Input validation and sanitization
- **SQL Injection**: Parameterized queries

## Testing Strategy

### Manual Testing

**Test Cases**:
1. **Basic Functionality**:
   - Article generation works
   - Search functionality works
   - Feedback forms work
   - Topic suggestions work

2. **Error Handling**:
   - Invalid topic names
   - Network errors
   - Database connection issues
   - LLM API errors

3. **Security**:
   - XSS prevention
   - Input validation
   - Rate limiting
   - SQL injection prevention

### Automated Testing

**Test Structure**:
```python
def test_generate_topic_content():
    """Test topic content generation."""
    topic = "Python"
    reply_code, content = generate_topic_content(topic)
    
    assert reply_code == "1"
    assert content is not None
    assert len(content) > 0
    assert "Python" in content

def test_validate_topic_slug():
    """Test topic slug validation."""
    valid_topic = "Python Programming"
    invalid_topic = "Python<script>alert('xss')</script>"
    
    assert validate_topic_slug(valid_topic) == "python programming"
    with pytest.raises(BadRequest):
        validate_topic_slug(invalid_topic)
```

## Debugging

### Logging

**Application Logs**:
```python
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

**Debug Information**:
```python
logging.info(f"[DEBUG] Will call OpenAI: topic_data is None (topic not in DB)")
logging.info(f"[OPENAI RAW GENERATION] Topic: {topic}\n{text}")
```

### Common Debug Scenarios

1. **Database Connection Issues**:
   - Check environment variables
   - Verify PostgreSQL is running
   - Test connection manually

2. **LLM API Issues**:
   - Check API key validity
   - Verify network connectivity
   - Check rate limits

3. **Frontend Issues**:
   - Check browser console for errors
   - Verify JavaScript is loading
   - Test AJAX requests

## Performance Optimization

### Database Optimization

**Indexing**:
```sql
CREATE INDEX idx_topics_topic_key ON topics(topic_key);
CREATE INDEX idx_topics_generated_at ON topics(generated_at);
```

**Query Optimization**:
- Use parameterized queries
- Limit result sets
- Use appropriate data types

### Caching Strategy

**Redis Usage**:
- Rate limiting data
- Session data (if implemented)
- Frequently accessed data

**Application-Level Caching**:
- Topic data caching
- LLM response caching
- Static content caching

### LLM Optimization

**Prompt Optimization**:
- Shorter prompts for local LLMs
- Optimized prompts for specific use cases
- Fallback mechanisms

**Response Handling**:
- Timeout management
- Error handling
- Retry logic

## Deployment

### Development Deployment

```bash
# Start services
docker-compose up -d

# Set environment variables
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=encyclopedai
export DB_USER=encyclo_user
export DB_PASSWORD=encyclo_pass
export REDIS_HOST=localhost

# Initialize database
python utils/db.py --init

# Run application
python app.py
```

### Production Deployment

**Environment Variables**:
```bash
export FLASK_ENV=production
export DB_HOST=your_production_db_host
export REDIS_HOST=your_production_redis_host
export OPENAI_API_KEY=your_production_api_key
export FLASK_SECRET_KEY=your_production_secret_key
```

**Security Considerations**:
- Use HTTPS in production
- Set secure session cookies
- Configure proper CORS headers
- Use environment variables for secrets
- Regular security updates

**Monitoring**:
- Application logs
- Database performance
- Redis metrics
- System resources

## Best Practices

### Code Quality

1. **Follow PEP 8** for Python code style
2. **Use type hints** for function parameters and return values
3. **Write docstrings** for all functions and classes
4. **Use meaningful variable names**
5. **Keep functions small and focused**

### Security

1. **Validate all inputs** before processing
2. **Sanitize HTML content** before rendering
3. **Use parameterized queries** to prevent SQL injection
4. **Implement rate limiting** to prevent abuse
5. **Log security events** for monitoring

### Performance

1. **Optimize database queries** and use appropriate indexes
2. **Cache frequently accessed data**
3. **Use connection pooling** for database connections
4. **Implement proper error handling** to prevent crashes
5. **Monitor performance metrics** in production

### Maintenance

1. **Keep dependencies updated** regularly
2. **Monitor logs** for errors and issues
3. **Backup database** regularly
4. **Test changes** thoroughly before deployment
5. **Document changes** in commit messages and release notes
