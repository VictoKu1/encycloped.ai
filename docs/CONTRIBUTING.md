# Contributing Guidelines

Thank you for your interest in contributing to encycloped.ai! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Process](#contributing-process)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing](#testing)
- [Documentation](#documentation)
- [Issue Reporting](#issue-reporting)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- Python 3.8+ (recommended: Python 3.10)
- Docker and Docker Compose
- Git
- Basic knowledge of Flask, PostgreSQL, and LLM APIs

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/encycloped.ai.git
   cd encycloped.ai
   ```

3. **Set up development environment:**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Start database services
   docker-compose up -d
   
   # Initialize database
   export DB_HOST=localhost
   export DB_PORT=5432
   export DB_NAME=encyclopedai
   export DB_USER=encyclo_user
   export DB_PASSWORD=encyclo_pass
   export REDIS_HOST=localhost
   python utils/db.py --init
   ```

4. **Test the setup:**
   ```bash
   python app.py
   # Visit http://localhost:5000 to verify it works
   ```

## Contributing Process

### 1. Choose What to Work On

- **Bug fixes**: Fix issues reported in GitHub Issues
- **New features**: Implement features requested in Issues
- **Documentation**: Improve existing documentation
- **Code quality**: Refactor, optimize, or improve code
- **Tests**: Add or improve test coverage

### 2. Create a Branch

```bash
# Create and switch to a new branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number
```

**Branch naming conventions:**
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring
- `test/description` - Test improvements

### 3. Make Changes

- Write clean, readable code
- Follow the code style guidelines
- Add tests for new functionality
- Update documentation as needed
- Test your changes thoroughly

### 4. Test Your Changes

```bash
# Test the application
python app.py

# Test local LLM integration (if applicable)
python test_local_llm.py

# Run any existing tests
python -m pytest tests/  # If tests exist
```

### 5. Commit Your Changes

```bash
# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "Add: Brief description of changes

- Detailed description of what was changed
- Why the change was made
- Any relevant context"
```

**Commit message format:**
- Start with a type: `Add:`, `Fix:`, `Update:`, `Remove:`, `Refactor:`, `Docs:`
- Keep the first line under 50 characters
- Use the imperative mood ("Add feature" not "Added feature")
- Include details in the body if needed

### 6. Push and Create Pull Request

```bash
# Push your branch
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Code Style Guidelines

### Python Code Style

Follow PEP 8 with these additional guidelines:

```python
# Good
def generate_topic_content(topic: str) -> tuple[str, str]:
    """Generate encyclopedia content for a topic.
    
    Args:
        topic: The topic to generate content for
        
    Returns:
        Tuple of (reply_code, content)
    """
    # Implementation here
    pass

# Bad
def generate_topic_content(topic):
    # Generate content
    pass
```

**Key guidelines:**
- Use type hints for function parameters and return values
- Write descriptive docstrings for all functions and classes
- Use meaningful variable and function names
- Keep functions small and focused
- Use `snake_case` for variables and functions
- Use `UPPER_CASE` for constants

### HTML/CSS Guidelines

```html
<!-- Good: Semantic HTML -->
<article class="encyclopedia-article">
  <header class="article-header">
    <h1>{{ topic }}</h1>
  </header>
  <div class="article-content">
    {{ content|safe }}
  </div>
</article>

<!-- Bad: Non-semantic HTML -->
<div class="container">
  <div class="title">{{ topic }}</div>
  <div class="text">{{ content|safe }}</div>
</div>
```

**Key guidelines:**
- Use semantic HTML elements
- Include proper accessibility attributes
- Use consistent class naming (BEM methodology recommended)
- Keep CSS organized and modular

### JavaScript Guidelines

```javascript
// Good: Modern JavaScript with proper error handling
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('topic-suggestion-modal');
    if (!modal) {
        console.error('Topic suggestion modal not found');
        return;
    }
    
    // Implementation here
});

// Bad: jQuery without error handling
$(document).ready(function() {
    $('#topic-suggestion-modal').show();
});
```

**Key guidelines:**
- Use modern JavaScript (ES6+)
- Include proper error handling
- Use meaningful variable names
- Comment complex logic
- Avoid global variables

## Testing

### Manual Testing

Before submitting changes, test:

1. **Basic functionality:**
   - Article generation works
   - Search functionality works
   - Feedback forms work
   - Topic suggestions work

2. **Error handling:**
   - Invalid topic names
   - Network errors
   - Database connection issues
   - LLM API errors

3. **Browser compatibility:**
   - Chrome, Firefox, Safari, Edge
   - Mobile responsiveness
   - Accessibility features

### Automated Testing

If you add new features, consider adding tests:

```python
# Example test structure
def test_generate_topic_content():
    """Test topic content generation."""
    topic = "Python"
    reply_code, content = generate_topic_content(topic)
    
    assert reply_code == "1"
    assert content is not None
    assert len(content) > 0
    assert "Python" in content
```

## Documentation

### Code Documentation

- Write docstrings for all functions and classes
- Include type hints
- Add inline comments for complex logic
- Update README.md if you add new features

### API Documentation

- Update API.md if you modify endpoints
- Include request/response examples
- Document new parameters or return values

### User Documentation

- Update setup instructions if you change dependencies
- Add troubleshooting information for new features
- Update architecture documentation for significant changes

## Issue Reporting

### Before Creating an Issue

1. Check if the issue already exists
2. Search closed issues for similar problems
3. Try the latest version of the code
4. Test with both OpenAI API and local LLM modes

### Creating a Good Issue

**Bug Reports:**
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g. Ubuntu 20.04]
- Python version: [e.g. 3.10]
- LLM mode: [OpenAI API / Local LLM]
- Browser: [e.g. Chrome 91]

**Additional context**
Any other context about the problem.
```

**Feature Requests:**
```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
A clear description of any alternative solutions.

**Additional context**
Add any other context or screenshots.
```

## Pull Request Process

### Before Submitting

1. **Ensure your code works:**
   - Test all functionality
   - Check for errors in logs
   - Verify database operations

2. **Follow code style:**
   - Run linting tools if available
   - Check for typos and formatting
   - Ensure consistent naming

3. **Update documentation:**
   - Update relevant documentation
   - Add comments for complex code
   - Update README if needed

### Pull Request Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update
- [ ] Code refactoring

## Testing
- [ ] Manual testing completed
- [ ] All existing tests pass
- [ ] New tests added (if applicable)

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### Review Process

1. **Automated checks** (if configured)
2. **Code review** by maintainers
3. **Testing** by maintainers
4. **Approval** and merge

## Areas for Contribution

### High Priority

- **Bug fixes** for reported issues
- **Security improvements**
- **Performance optimizations**
- **Test coverage improvements**

### Medium Priority

- **New features** from issue requests
- **UI/UX improvements**
- **Documentation enhancements**
- **Code refactoring**

### Low Priority

- **Code style improvements**
- **Minor feature additions**
- **Cosmetic changes**

## Getting Help

### Communication Channels

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Pull Request Comments**: For code review discussions

### Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)
- [Ollama Documentation](https://ollama.ai/docs)

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to encycloped.ai! Your contributions help make this project better for everyone.
