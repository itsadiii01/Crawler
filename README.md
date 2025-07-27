# Intelligent Web-Crawler and Query Engine

A Flask-based web application for crawling AP Agriculture websites and performing semantic search using OpenAI embeddings.

## Features

- 🌐 Web crawling of AP Agriculture websites
- 📄 PDF document processing
- 🔍 Semantic search using OpenAI embeddings
- 💾 SQLite database storage
- 🎨 Modern web interface
- ⚡ Caching for improved performance

## Setup Instructions

1. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create a .env file with your OpenAI API key:**
   ```
   OPENAI_API_KEY=sk-your-actual-openai-key-here
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Visit the application:**
   Open your browser and go to `http://127.0.0.1:8080`

## Project Structure

```
crawler2/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .env                  # Environment variables (create this)
├── config/
│   └── settings.py       # Configuration settings
├── database/
│   ├── __init__.py
│   └── models.py         # Database operations
├── crawler/
│   ├── __init__.py
│   ├── crawler.py        # Web crawling logic
│   └── parser.py         # Content parsing utilities
├── search/
│   ├── __init__.py
│   └── vector_store.py   # Vector search operations
├── static/
│   ├── css/
│   │   └── style.css     # Stylesheets
│   └── js/
│       └── main.js       # JavaScript functionality
├── templates/
│   └── index.html        # Main HTML template
└── downloads/            # Downloaded files (auto-created)
```

## Usage

1. **Initial Setup:** Click "Re-crawl Websites" to populate the database with content from AP Agriculture websites
2. **Search:** Use the search bar to find information about crops, schemes, policies, etc.
3. **Results:** View relevant documents with relevance scores and direct links to sources

## Configuration

Key settings can be modified in `config/settings.py`:
- Seed URLs for crawling
- Maximum pages to crawl
- Thread count for parallel processing
- Timeout settings

## API Endpoints

- `GET /` - Main application interface
- `POST /crawl` - Trigger web crawling
- `GET /search?query=<text>` - Perform semantic search
- `GET /status` - Application status and statistics

## Technologies Used

- **Backend:** Flask, SQLite
- **Crawling:** Requests, BeautifulSoup, PyPDF2
- **AI:** OpenAI Embeddings API
- **Frontend:** HTML5, CSS3, JavaScript
- **Caching:** Flask-Caching # Crawler
