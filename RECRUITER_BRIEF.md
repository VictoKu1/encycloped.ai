# Recruiter Brief: encycloped.ai

## One-minute summary

encycloped.ai is a Flask-based AI knowledge platform that generates encyclopedia-style articles, stores them in PostgreSQL, and protects user contribution flows with rate limiting, validation, sanitization, and prompt-injection defenses. It demonstrates backend engineering, LLM integration, application security thinking, and practical deployment with Docker-managed infrastructure.

## What it demonstrates

- Backend development with Flask routes, persistent PostgreSQL storage, Redis-backed rate limiting, and Docker Compose infrastructure.
- AI/LLM product engineering with OpenAI-compatible generation, local Ollama support, topic suggestion workflows, and feedback-driven content updates.
- Security-aware design with HTML sanitization, JSON validation, prompt-injection heuristics, abuse throttling, and a contributor review queue.
- Product sense through an article creation flow, topic/subtopic navigation, reporting modals, and interactive text-selection topic discovery.

## Architecture at a glance

```text
Browser UI
  -> Flask app
  -> Topic generation and feedback workflows
  -> OpenAI-compatible API or local Ollama model
  -> PostgreSQL for article/topic persistence
  -> Redis for shared rate limiting
```

Important files:

- `app.py` - main Flask routes and user workflows.
- `agents/topic_generator.py` - LLM-backed article generation, update, and topic suggestion logic.
- `agents/local_llm.py` - local Ollama integration.
- `utils/db.py` and `utils/data_store.py` - PostgreSQL persistence.
- `security/` - prompt-injection detection, sanitization, validation, and review-queue helpers.
- `docs/ARCHITECTURE.md`, `docs/API.md`, and `docs/SECURITY.md` - deeper technical documentation.

## How to verify locally

```bash
docker-compose up -d
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python utils/db.py --init
python app.py
```

For local LLM mode, configure Ollama with `python setup_local_llm.py`, validate with `python test_local_llm.py`, and run `python app.py local`.

## Role positioning

Best aligned roles:

- Backend Developer
- Python Developer
- Software Engineer
- AI/LLM Application Developer
- Application Security / AI Security Engineer

Suggested portfolio phrasing:

> Built an AI-assisted encyclopedia prototype with Flask, PostgreSQL, Redis, Docker, OpenAI-compatible LLMs, local Ollama support, prompt-injection defenses, and user feedback moderation.

## Responsible claims

This is an experimental project, not a replacement for professional editorial review. When presenting it, emphasize the engineering and safety architecture rather than claiming guaranteed factual accuracy.
