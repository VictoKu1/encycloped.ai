# encycloped.ai (AI Moderated Encyclopedia)

**encycloped.ai** is an experimental, community-driven project that combines the power of ChatGPT 4.1 (or any other LLM with an API) with the collaborative spirit of Wikipedia. This platform dynamically generates encyclopedia-style articles with citations using the ChatGPT 4.1 (or any other LLM with an API) API, while allowing users to report inaccuracies and contribute missing information. AI moderation helps ensure that the content remains accurate and reliable, even as the community drives its evolution.

> **Note:** All article and topic data is stored in a persistent PostgreSQL database, ensuring data durability and multi-user support. No in-memory storage is used for articles or topics.

## Features

- **Dynamic Content Generation:**  
  Automatically generate encyclopedia articles on-the-fly using ChatGPT 4.1 (or any other LLM with an API) with full citations.

- **Topic and Subtopic Navigation:**  
  Access articles via URL paths (e.g., `/Python`) and subtopics using anchors (`#subtopic`) or paths (e.g., `/Python/libraries`).

- **User Feedback:**  
  Users can report issues or suggest additional information through intuitive modals. Feedback is sent to the ChatGPT 4.1 (or any other LLM with an API) API for validation and content updates.

- **AI Moderation:**  
  The system leverages AI (ChatGPT 4.1 or compatible) to review and integrate user contributions, ensuring that the content remains both accurate and reliable.

- **Community-Driven:**  
  Open-source and decentralized, contributions are welcome from anyone. However, final control and integration of contributions remain with the project maintainers, ensuring consistency and quality.

- **Persistent Database Storage:**  
  All articles and topics are stored in a PostgreSQL database for durability and reliability. This enables multi-user access, prevents data loss on server restarts, and supports future scalability.

## Security Features

- **Cross-Site Scripting (XSS) Protection:**
  - HTML sanitization using `bleach`
  - Strict tag and attribute whitelisting
  - Safe template rendering

- **Denial of Service (DoS) Protection:**
  - IP-based rate limiting (5 requests per minute for sensitive endpoints)
  - Request throttling per session
  - Input size restrictions

- **Content Security:**
  - Markdown sanitization
  - Path traversal prevention
  - Input validation and sanitization
  - Contributor metadata logging

- **API Security:**
  - JSON payload validation
  - Required field checking
  - Error handling and logging
  - Secure session management


- **Flask App**: Handles all web requests, user feedback, and article generation.
- **OpenAI API**: Used for generating and updating encyclopedia articles and topic suggestions.
- **PostgreSQL**: Stores all articles, markdown, topic suggestions, and logs—**persistent, durable storage**.
- **Redis**: Used **only for rate limiting** (not for article data)—ensures fair usage and protects against abuse, even in a distributed/multi-instance setup.

## Why Redis and PostgreSQL?

- **PostgreSQL** is a robust, persistent database for all encyclopedia content and logs.
- **Redis** is a fast, in-memory data store used for **rate limiting**.  
  - Rate limiting requires atomic, high-speed operations and must be shared across all app instances.
  - Redis is the industry standard for this use case; PostgreSQL is not suitable for distributed rate limiting.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/VictoKu1/encycloped.ai.git
   cd encycloped.ai
   ```

2. **Set Up a Virtual Environment (Recommended):**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. **Install Python Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**

   Create a `.env` file (or set the environment variables directly) to configure your API key, for example:
  
   Linux:
   
   ```bash
   export OPENAI_API_KEY=your_openai_api_key
   ```
  
   Windows:
   
   - Using CMD:
    ```cmd
    set OPENAI_API_KEY=your_openai_api_key
    ```
   
   - Using PowerShell:
   
    ```powershell
    $env:OPENAI_API_KEY="your_openai_api_key"
    ``` 

---

## Database & Project Setup (Step-by-Step)

Follow these steps to set up the PostgreSQL database and Redis for rate limiting, and run the project. You do NOT need to run all commands in the same terminal, but you may find it convenient to use multiple terminals for different steps.

### 1. Start Docker/PostgreSQL/Redis
Open any terminal and run:
```bash
docker-compose up -d
```
This starts the PostgreSQL database **and Redis** in the background. You can close this terminal or use it for other commands.

### 2. Set Environment Variables
Set the following environment variables in the terminal where you will run the app and the database initialization script. You can also use a `.env` file if your app loads it automatically.

**Linux/macOS:**
```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=encyclopedai
export DB_USER=encyclo_user
export DB_PASSWORD=encyclo_pass
export REDIS_HOST=localhost
```
**Windows PowerShell:**
```powershell
$env:DB_HOST="localhost"
$env:DB_PORT="5432"
$env:DB_NAME="encyclopedai"
$env:DB_USER="encyclo_user"
$env:DB_PASSWORD="encyclo_pass"
$env:REDIS_HOST="localhost"
```

- In production/Docker, set `REDIS_HOST=redis`.

### 3. Initialize the Database Schema (Run Once)
In any terminal (after Docker is running and dependencies are installed):
```bash
python utils/db.py --init
```
This creates the necessary tables for topics and logs. You only need to run this once (or after making schema changes).

### 4. Run the Flask App
In a new terminal (so you can keep it open while using the app):
```bash
python app.py
```
Leave this terminal open while you use the app in your browser.

---

### Optional: Restarting the Database with Docker Compose
If you need to restart the PostgreSQL database cleanly (for example, after making changes to the Docker configuration or to reset the container), you can use the following commands:

**Stop the database service:**
```bash
docker-compose down
```

**Remove all stopped containers and volumes (WARNING: this will delete all data!):**
```bash
docker-compose down -v
```

**Start the database service again:**
```bash
docker-compose up -d
```

## Usage

- **Home Page:**  
  Enter a topic in the search bar. If the topic already exists, you'll be directed to its page; otherwise, a new page is generated with a loading animation while content is created.

- **Topic Pages:**  
  View the generated article along with citations. Use the "Report an Issue" button to flag inaccuracies or the "Add Missing Information" button to contribute extra details or subtopics.

- **User Feedback:**  
  Feedback forms open in modals. Your input is sent via AJAX to the backend, where it is validated by the ChatGPT 4.1 (or any other LLM with an API) API before updating the article content.

## Security Considerations

- The application implements rate limiting to prevent abuse
- All user input is sanitized to prevent XSS attacks
- Content is validated and sanitized before storage
- Contributor actions are logged for accountability
- API endpoints are protected against common vulnerabilities

## Contributing

Contributions are welcome and encouraged! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to contribute to the project.

## License

This project is licensed under the [GNU General Public License v3 (GPL v3)](LICENSE).

## Acknowledgments

- [Flask](https://flask.palletsprojects.com/) – The web framework powering this project.
- [OpenAI](https://openai.com/) – For providing the ChatGPT 4.1 API.
- [PostgreSQL](https://www.postgresql.org/) – The database powering this project.
- [Redis](https://redis.io/) – The rate limiting database powering this project.
- [Docker](https://www.docker.com/) – The containerization platform powering this project.
- The open-source community – For their inspiration and continuous contributions.
- Wikipedia and other collaborative knowledge-sharing platforms – For inspiring a decentralized approach to knowledge.





