"""
Main Flask application for the Intelligent Web-Crawler and Query Engine
"""
import logging
from flask import Flask, request, jsonify, render_template, g
from flask_caching import Cache

from config.settings import FLASK_CONFIG, CACHE_TIMEOUT, SEARCH_TOP_K
from database.models import init_db, get_status
from crawler.crawler import crawl
from search.vector_store import search

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize Flask app
app = Flask(__name__)
app.config.update(FLASK_CONFIG)
cache = Cache(app)

# Database teardown
@app.teardown_appcontext
def close_db(exc=None):
    """Close database connection when context ends"""
    db = g.pop("db", None)
    if db:
        db.close()

# Initialize database on startup
with app.app_context():
    init_db()

@app.route("/")
def index():
    """Serve the main page"""
    return render_template("index.html")

@app.route("/crawl", methods=["POST"])
def trigger_crawl():
    """Start crawling process"""
    try:
        pages = crawl()
        return jsonify({"status": "completed", "pages_crawled": pages})
    except Exception as e:
        logging.error(f"Crawl error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@cache.cached(timeout=CACHE_TIMEOUT, query_string=True)
@app.route("/search")
def search_endpoint():
    """Perform semantic search"""
    q = request.args.get("query", "").strip()
    if not q:
        return jsonify({"error": "Query parameter missing"}), 400
    
    try:
        results = search(q, top_k=SEARCH_TOP_K)
        return jsonify(results)
    
    except Exception as e:
        logging.error(f"Search error: {e}")
        return jsonify({"error": "Search failed"}), 500

@app.route("/status")
def status_endpoint():
    """Get application status"""
    try:
        status_data = get_status()
        return jsonify(status_data)
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    print("🌾 Starting Andhra Pradesh Agriculture Knowledge Base")
    print("📚 Make sure to:")
    print("   1. Set your OPENAI_API_KEY in .env file")
    print("   2. Click 'Re-crawl Websites' to populate the database")
    print("   3. Start searching for agriculture information!")
    print("🌐 Visit: http://127.0.0.1:8080")
    
    app.run(
        debug=FLASK_CONFIG["DEBUG"], 
        host=FLASK_CONFIG["HOST"], 
        port=FLASK_CONFIG["PORT"]
    ) 