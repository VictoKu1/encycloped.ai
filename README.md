# encycloped.ai

**encycloped.ai** is an experimental, community-driven project that combines the power of ChatGPT (or any other LLM with an API) with the collaborative spirit of Wikipedia. This platform dynamically generates encyclopedia-style articles with citations using the ChatGPT (or any other LLM with an API) API, while allowing users to report inaccuracies and contribute missing information. AI moderation helps ensure that the content remains accurate and reliable, even as the community drives its evolution.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Running Locally](#running-locally)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Features

- **Dynamic Content Generation:**  
  Automatically generate encyclopedia articles on-the-fly using ChatGPT (or any other LLM with an API) with full citations.

- **Topic and Subtopic Navigation:**  
  Access articles via URL paths (e.g., `/Python`) and subtopics using anchors (`#subtopic`) or paths (e.g., `/Python/libraries`).

- **User Feedback:**  
  Users can report issues or suggest additional information through intuitive modals. Feedback is sent to the ChatGPT (or any other LLM with an API) API for validation and content updates.

- **AI Moderation:**  
  The system leverages AI to review and integrate user contributions, ensuring that the content remains both accurate and reliable.

- **Community-Driven:**  
  Open-source and decentralized, contributions are welcome from anyone. However, final control and integration of contributions remain with the project maintainers, ensuring consistency and quality.

## Project Structure

```plaintext
encycloped.ai/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── CONTRIBUTING.md         # Guidelines for contributing
├── CODE_OF_CONDUCT.md      # Code of conduct for contributors
├── LICENSE                 # Project license (GPL v3)
├── templates/
│   ├── base.html           # Base HTML template
│   ├── index.html          # Homepage with search functionality
│   └── topic.html          # Template for displaying topics and subtopics
└── static/
    ├── css/
    │   └── style.css       # CSS styling for the project
    └── js/
        └── main.js         # JavaScript for interactivity and AJAX calls
```

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/VictoKu1/encycloped.ai.git
   cd encycloped.ai
   ```

2. **Set Up a Virtual Environment (Recommended):**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**

   Create a `.env` file (or set the environment variables directly) to configure your API key, for example:

   ```bash
   export OPENAI_API_KEY=your_openai_api_key
   ```

## Running Locally

To run the Flask application locally, execute:

```bash
python app.py
```

By default, the application runs in debug mode on `http://127.0.0.1:5000/`. Open your browser and navigate to that URL to start exploring topics.

## Usage

- **Home Page:**  
  Enter a topic in the search bar. If the topic already exists, you'll be directed to its page; otherwise, a new page is generated with a loading animation while content is created.

- **Topic Pages:**  
  View the generated article along with citations. Use the "Report an Issue" button to flag inaccuracies or the "Add Missing Information" button to contribute extra details or subtopics.

- **User Feedback:**  
  Feedback forms open in modals. Your input is sent via AJAX to the backend, where it is validated by the ChatGPT (or any other LLM with an API) API before updating the article content.

## Contributing

Contributions are welcome and encouraged! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to contribute to the project.

## License

This project is licensed under the [GNU General Public License v3 (GPL v3)](LICENSE).

## Acknowledgments

- [Flask](https://flask.palletsprojects.com/) – The web framework powering this project.
- [OpenAI](https://openai.com/) – For providing the ChatGPT API.
- The open-source community – For their inspiration and continuous contributions.
- Wikipedia and other collaborative knowledge-sharing platforms – For inspiring a decentralized approach to knowledge.







