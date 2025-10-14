# API Documentation

## Overview

The encycloped.ai API provides endpoints for generating, updating, and managing encyclopedia articles using AI. The API supports both OpenAI API and local LLM modes.

## Base URL

```
http://localhost:5000
```

## Authentication

No authentication is required for basic operations. Rate limiting is applied to prevent abuse.

## Rate Limiting

- **General endpoints**: 200 requests per day, 50 per hour
- **Sensitive endpoints** (`/report`, `/add_info`): 5 requests per minute
- **Topic suggestions**: 10 requests per minute

## Endpoints

### 1. Generate Article

**GET** `/{topic}`

Generates or retrieves an encyclopedia article for the specified topic.

#### Parameters

- `topic` (string, required): The topic name for the article

#### Response

**Success (200)**
```html
<!DOCTYPE html>
<html>
  <!-- Rendered article page -->
</html>
```

**Error (400)**
```html
<!-- Error page with suggestions -->
```

#### Example

```bash
curl http://localhost:5000/Python
```

### 2. Report Issue

**POST** `/report`

Report an issue with an existing article.

#### Request Body

```json
{
  "topic": "Python",
  "report_details": "The section on history is outdated.",
  "sources": ["https://source1.com", "https://source2.com"]
}
```

#### Response

**Success (200)**
```json
{
  "reply": "1",
  "updated_content": "<html>Updated article content</html>"
}
```

**Error (400)**
```json
{
  "error": "Invalid topic name"
}
```

**Error (404)**
```json
{
  "reply": "0",
  "message": "Topic not found."
}
```

#### Example

```bash
curl -X POST http://localhost:5000/report \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python",
    "report_details": "The section on history is outdated.",
    "sources": ["https://python.org/history"]
  }'
```

### 3. Add Information

**POST** `/add_info`

Add missing information to an existing article.

#### Request Body

```json
{
  "topic": "Python",
  "subtopic": "Libraries",
  "info": "Python has many libraries for data science...",
  "sources": ["https://example.com"]
}
```

#### Response

**Success (200)**
```json
{
  "reply": "1",
  "updated_content": "<html>Updated article content</html>"
}
```

**Error (400)**
```json
{
  "error": "Missing required fields: ['topic', 'subtopic', 'info', 'sources']"
}
```

**Error (404)**
```json
{
  "reply": "0",
  "message": "Topic not found."
}
```

#### Example

```bash
curl -X POST http://localhost:5000/add_info \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python",
    "subtopic": "Libraries",
    "info": "Python has many libraries for data science...",
    "sources": ["https://pypi.org"]
  }'
```

### 4. Suggest Topics

**POST** `/suggest_topics`

Generate topic suggestions based on selected text.

#### Request Body

```json
{
  "selected_text": "Python is a programming language...",
  "current_topic": "Python"
}
```

#### Response

**Success (200)**
```json
{
  "suggestions": ["programming language", "Python", "interpreted"]
}
```

**Error (400)**
```json
{
  "error": "Selected text is too short. Please select more text."
}
```

#### Example

```bash
curl -X POST http://localhost:5000/suggest_topics \
  -H "Content-Type: application/json" \
  -d '{
    "selected_text": "Python is a programming language...",
    "current_topic": "Python"
  }'
```

### 5. Add Reference

**POST** `/add_reference`

Add a new reference (hyperlink) to an article.

#### Request Body

```json
{
  "article_topic": "Python",
  "selected_text": "interpreted programming language",
  "reference_topic": "Programming Language"
}
```

#### Response

**Success (200)**
```json
{
  "updated_content": "<html>Updated article with new reference</html>"
}
```

**Error (400)**
```json
{
  "error": "Invalid topic name"
}
```

**Error (404)**
```json
{
  "error": "Topic not found."
}
```

#### Example

```bash
curl -X POST http://localhost:5000/add_reference \
  -H "Content-Type: application/json" \
  -d '{
    "article_topic": "Python",
    "selected_text": "interpreted programming language",
    "reference_topic": "Programming Language"
  }'
```

## Response Codes

### Reply Codes

- `1`: Success - Content was generated/updated
- `0`: No change - Content was not modified
- `45`: Ambiguous topic - Multiple meanings found

### HTTP Status Codes

- `200`: Success
- `400`: Bad Request - Invalid input or missing required fields
- `404`: Not Found - Topic doesn't exist
- `429`: Too Many Requests - Rate limit exceeded
- `500`: Internal Server Error

## Error Handling

All API endpoints return appropriate HTTP status codes and error messages. JSON responses include an `error` field with details about what went wrong.

## Security

- All user input is sanitized to prevent XSS attacks
- HTML content is cleaned using bleach
- Rate limiting prevents abuse
- All contributions are logged for accountability

## Examples

### Complete Workflow

1. **Generate an article:**
   ```bash
   curl http://localhost:5000/Machine%20Learning
   ```

2. **Report an issue:**
   ```bash
   curl -X POST http://localhost:5000/report \
     -H "Content-Type: application/json" \
     -d '{
       "topic": "Machine Learning",
       "report_details": "The section on deep learning needs updating.",
       "sources": ["https://arxiv.org/abs/2023.12345"]
     }'
   ```

3. **Add information:**
   ```bash
   curl -X POST http://localhost:5000/add_info \
     -H "Content-Type: application/json" \
     -d '{
       "topic": "Machine Learning",
       "subtopic": "Applications",
       "info": "Machine learning is used in autonomous vehicles...",
       "sources": ["https://example.com/autonomous-vehicles"]
     }'
   ```

4. **Get topic suggestions:**
   ```bash
   curl -X POST http://localhost:5000/suggest_topics \
     -H "Content-Type: application/json" \
     -d '{
       "selected_text": "neural networks and deep learning algorithms",
       "current_topic": "Machine Learning"
     }'
   ```

## Rate Limiting Headers

When rate limits are applied, the following headers are included in the response:

- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Time when the rate limit resets

## Content Types

- **HTML responses**: `text/html` (for article pages)
- **JSON responses**: `application/json` (for API endpoints)
- **Request bodies**: `application/json` (for POST requests)
