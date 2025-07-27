"""
Web crawling logic for the application
"""
import time
import logging
import threading
import queue
from urllib.parse import urldefrag
import requests
from pathlib import Path

from config.settings import (
    SEED_URLS, MAX_PAGES, TIMEOUT, THREADS, 
    DOWNLOAD_DIR, USER_AGENT
)
from database.models import get_db, save_document, upsert_embeddings
from search.vector_store import embed
from .parser import parse_html, parse_pdf


def worker(url_q: queue.Queue, seen: set, lock: threading.Lock):
    """Worker thread for crawling URLs"""
    db = get_db()
    while True:
        try:
            url = url_q.get_nowait()
        except queue.Empty:
            break
        
        try:
            # Skip unwanted URLs
            if any(bad in url for bad in ("mailto:", "javascript:", "#")):
                continue
            
            with lock:
                if url in seen or len(seen) > MAX_PAGES:
                    continue
                seen.add(url)
            
            # Fetch URL
            r = requests.get(
                url, 
                timeout=TIMEOUT, 
                headers={"User-Agent": USER_AGENT},
                verify=False  # Skip SSL verification for government sites
            )
            
            content_type = r.headers.get("content-type", "").lower()
            
            if "text/html" in content_type:
                # Process HTML
                title, text, links = parse_html(url, r.text)
                if text.strip():  # Only save if there's actual content
                    doc_id = save_document(db, url, title, text)
                    embedding = embed(text)
                    upsert_embeddings([(doc_id, embedding)])
                
                # Add new links to queue
                for link in links:
                    clean_link = urldefrag(link)[0]
                    if clean_link and clean_link.startswith('http'):
                        url_q.put(clean_link)
            
            elif "application/pdf" in content_type or url.lower().endswith(".pdf"):
                # Process PDF
                fname = DOWNLOAD_DIR / f"{hash(url)}.pdf"
                fname.write_bytes(r.content)
                text = parse_pdf(fname)
                if text.strip():  # Only save if there's actual content
                    doc_id = save_document(db, url, fname.name, text, str(fname))
                    embedding = embed(text)
                    upsert_embeddings([(doc_id, embedding)])
        
        except Exception as e:
            logging.warning(f"Error processing {url}: {e}")
        finally:
            url_q.task_done()
    
    db.close()


def crawl():
    """Main crawling function"""
    from database.models import init_db
    init_db()
    
    q, seen, lock = queue.Queue(), set(), threading.Lock()
    
    # Add seed URLs
    for u in SEED_URLS:
        q.put(u)
    
    # Start worker threads
    threads = [
        threading.Thread(target=worker, args=(q, seen, lock), daemon=True) 
        for _ in range(THREADS)
    ]
    for t in threads:
        t.start()
    
    # Wait for completion
    q.join()
    return len(seen) 