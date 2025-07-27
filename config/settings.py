"""
Configuration settings for the web crawler application
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_PATH = Path("crawler_meta.db").resolve()
EMB_SEP = ","  # separator for embedding serialization

# File storage
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

# Crawler parameters
SEED_URLS = [
    "https://angrau.ac.in",
    "https://apagrisnet.gov.in/",
    "https://apcooperation.nic.in/",
    "https://drysrhu.ap.gov.in/",
]
MAX_PAGES = 120
TIMEOUT = 10
THREADS = 6

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBED_MODEL = "text-embedding-ada-002"

# Flask configuration
FLASK_CONFIG = {
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "DEBUG": True,
    "HOST": "0.0.0.0",
    "PORT": 8080
}

# Search configuration
SEARCH_TOP_K = 5
CACHE_TIMEOUT = 180  # seconds

# User agent for web requests
USER_AGENT = "CrawlerBot/1.0" 