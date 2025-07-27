"""
Content parsing utilities for the web crawler
"""
import re
import logging
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from pathlib import Path


def clean_text(s: str) -> str:
    """Clean and normalize text"""
    return re.sub(r"\s+", " ", s).strip()


def parse_html(url: str, html: str):
    """Parse HTML content and extract title, text, and links"""
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title else url
    text = clean_text(soup.get_text(" "))
    links = [urljoin(url, a.get("href")) for a in soup.find_all("a", href=True)]
    return title, text, links


def parse_pdf(path: Path):
    """Extract text from PDF file"""
    try:
        reader = PdfReader(path)
        text = " ".join(page.extract_text() or "" for page in reader.pages)
        return clean_text(text)
    except Exception as e:
        logging.error(f"PDF parse error {path}: {e}")
        return "" 