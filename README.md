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

- **Flexible Topic Names:**
  Topic names now support most common symbols, including spaces, parentheses, periods, commas, colons, semicolons, exclamation marks, question marks, slashes, brackets, braces, quotes, ampersands, asterisks, percent, dollar, at, caret, equals, tilde, pipe, angle brackets, and more. This allows for accurate representation of real-world article titles and disambiguation (e.g., "Python (programming language)", "C++", "Mercury (planet)", etc.).

- **Local LLM Support:**
  Run the application with local LLMs using Ollama. Switch between OpenAI API and local models by using different startup commands. Supports any model available in Ollama, with DeepSeek-Coder as the recommended local option. Local LLM mode uses optimized prompts for better performance and includes improved error handling and timeout management.

- **Interactive Topic Suggestion:**
  Enhanced user engagement with intelligent text selection features. When you highlight text in an article, a lens icon (🔍) appears near your selection. Clicking the icon opens a modal that:
  - Extracts actual terms from your selected text as topic suggestions
  - Provides 3 relevant topic options based on the highlighted content
  - Allows custom topic input with real-time validation
  - Automatically converts selected text into clickable links to new articles
  - Creates an interconnected encyclopedia where new topics link back to original content
  - Features a blurred background modal with loading animations and accessibility support

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
- **LLM Integration**: Supports both OpenAI API and local LLMs via Ollama for generating and updating encyclopedia articles and topic suggestions. Local LLM mode includes optimized prompts, increased timeouts, and improved error handling for better reliability.
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

#### Option A: Using OpenAI API (Default)
In a new terminal (so you can keep it open while using the app):
```bash
python app.py
```
Leave this terminal open while you use the app in your browser.

#### Option B: Using Local LLM with Ollama
If you want to use a local LLM instead of OpenAI API:

1. **Install Ollama:**
   Visit [ollama.ai](https://ollama.ai) and follow the installation instructions for your platform.

2. **Start Ollama:**
   ```bash
   ollama serve
   ```
   **Note:** If you get an error about the port being in use, it means Ollama is already running. This is normal and you can proceed to the next step.

3. **Pull a model (e.g., DeepSeek-R1):**
   ```bash
   ollama pull deepseek-coder:6.7b
   ```
   This model is recommended for good performance and quality. You can also try other models like `llama3.2:3b` for faster responses.

4. **Configure local LLM settings:**
   
   **Option A: Interactive setup (Recommended):**
   ```bash
   python setup_local_llm.py
   ```
   
   **Option B: Manual configuration:**
   Edit the `local_llm.json` file to specify your preferred model:
   ```json
   {
       "model": "deepseek-coder:6.7b",
       "base_url": "http://localhost:11434"
   }
   ```

5. **Test the local LLM integration (Recommended):**
   ```bash
   python test_local_llm.py
   ```
   This will run a series of tests to verify that the local LLM integration is working correctly.

6. **Run the app in local LLM mode:**
   ```bash
   python app.py local
   ```

   The app will validate your Ollama setup and model availability before starting. Local LLM mode uses simplified prompts optimized for local models, providing faster responses while maintaining quality.

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
  Enter a topic in the search bar. Topic names can include most common symbols and punctuation, allowing for precise and disambiguated article titles (e.g., "Python (programming language)", "C++," "Mercury: The Planet"). If the topic already exists, you'll be directed to its page; otherwise, a new page is generated with a loading animation while content is created.

- **Topic Pages:**  
  View the generated article along with citations. Use the "Report an Issue" button to flag inaccuracies or the "Add Missing Information" button to contribute extra details or subtopics.

- **Interactive Topic Suggestion:**  
  **New Feature!** Select any text in an article (at least 10 characters) and a lens icon (🔍) will appear near your selection. Click the icon to:
  - See topic suggestions extracted from your selected text
  - Enter a custom topic with real-time validation
  - Generate new articles that automatically link back to the original content
  - Create an interconnected web of related topics

- **User Feedback:**  
  Feedback forms open in modals. Your input is sent via AJAX to the backend, where it is validated by the LLM (OpenAI API or local LLM) before updating the article content.

- **LLM Mode Switching:**  
  Easily switch between OpenAI API and local LLM modes by using different startup commands. The application validates your setup before starting to ensure everything works correctly. Local LLM mode provides offline capability and privacy while maintaining article quality.

## Interactive Topic Suggestion Feature

The Interactive Topic Suggestion feature enhances article exploration by allowing users to discover and create related topics directly from the content they're reading.

### How It Works

1. **Text Selection**: Select any text in an article (minimum 10 characters)
2. **Lens Icon**: A lens icon (🔍) appears near your selection
3. **Topic Extraction**: Click the icon to extract actual terms from your selected text
4. **Smart Suggestions**: The system provides 3 relevant topic suggestions based on the highlighted content
5. **Custom Topics**: Enter your own topic with real-time validation
6. **Automatic Linking**: Selected text becomes a clickable link to the new article
7. **Interconnected Content**: Creates a web of related topics that link back to original content

### Features

- **Intelligent Extraction**: Extracts actual terms from selected text, not generic suggestions
- **Real-time Validation**: Checks if custom topics are part of the selected text
- **Visual Feedback**: Button color changes based on validation status
- **Accessibility**: Keyboard navigation and screen reader support
- **Mobile-Friendly**: Responsive design works on all devices
- **Loading Animations**: Smooth loading states with progress indicators
- **Blur Effects**: Modal with blurred background for focus

### Example Workflow

1. **Select text**: "Python is an interpreted programming language"
2. **Click lens icon**: Opens modal with suggestions
3. **See suggestions**: "Python", "interpreted", "programming language"
4. **Click suggestion**: Creates new article and converts selected text to link
5. **Result**: "Python is an <a href="/programming%20language">interpreted programming language</a>"

### Benefits

- **Discoverability**: Helps users find related topics they might not know about
- **Content Creation**: Encourages creation of new articles from existing content
- **Interconnection**: Creates a network of related articles
- **User Engagement**: Makes article exploration more interactive and fun
- **Knowledge Discovery**: Reveals connections between different topics

## Troubleshooting Local LLM

### Common Issues

1. **"Ollama is not running or not accessible"**
   - Make sure Ollama is installed and running: `ollama serve`
   - Check if Ollama is accessible at `http://localhost:11434`
   - If you get a port binding error, Ollama is already running (this is normal)

2. **"Model is not available in Ollama"**
   - Pull the model first: `ollama pull deepseek-coder:6.7b`
   - Check available models: `ollama list`
   - Update the model name in `local_llm.json` if needed

3. **"Local LLM setup validation failed"**
   - Run the test script: `python test_local_llm.py`
   - Use the setup script to reconfigure: `python setup_local_llm.py`
   - Check the logs for specific error messages
   - Ensure your model has enough memory and resources

4. **"Error communicating with Ollama: Read timed out"**
   - Local LLMs are slower than OpenAI API
   - The timeout has been increased to 120 seconds
   - Consider using a smaller model for faster responses
   - Ensure your system has sufficient RAM (at least 8GB recommended)

5. **"OpenAI API error: local variable 'client' referenced before assignment"**
   - This error occurs when the OpenAI API key is not set but the app tries to use OpenAI mode
   - Set your OpenAI API key: `$env:OPENAI_API_KEY="your_key"`
   - Or use local LLM mode: `python app.py local`

### Performance Tips

- Local LLMs may be slower than OpenAI API (30-60 seconds for article generation)
- Consider using smaller models for faster responses:
  - `llama3.2:3b` - Faster, smaller model
  - `deepseek-coder:6.7b` - Good balance of speed and quality
  - `deepseek-coder:33b` - Higher quality, slower
- Ensure your system has sufficient RAM (8GB minimum, 16GB recommended)
- Local LLM mode uses optimized prompts for better performance

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





