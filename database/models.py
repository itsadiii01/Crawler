"""
Database operations for the web crawler application
"""
import sqlite3
import datetime
import numpy as np
from pathlib import Path
from typing import List, Tuple
from config.settings import DB_PATH, EMB_SEP


def get_db():
    """Provide a single SQLite connection per request / thread"""
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def close_db(db):
    """Close database connection"""
    if db:
        db.close()


def init_db():
    """Create tables once"""
    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS documents(
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            url       TEXT UNIQUE,
            title     TEXT,
            text      TEXT,
            file_path TEXT,
            added_on  TEXT
        );
        CREATE TABLE IF NOT EXISTS vectors(
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id    INTEGER,
            dim       INTEGER,
            embedding_blob TEXT,
            FOREIGN KEY (doc_id) REFERENCES documents(id)
        );
        """
    )
    db.commit()
    db.close()


def _serialize(vec: np.ndarray) -> str:
    """Serialize numpy array to string"""
    return EMB_SEP.join(map("{:.6f}".format, vec.tolist()))


def _deserialize(blob: str) -> np.ndarray:
    """Deserialize string to numpy array"""
    return np.fromstring(blob, sep=EMB_SEP, dtype=np.float32)


def save_document(db, url: str, title: str, text: str, file_path: str = None):
    """Save document to database"""
    cur = db.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO documents(url, title, text, file_path, added_on) "
        "VALUES(?,?,?,?,?)",
        (url, title, text, file_path, datetime.datetime.utcnow().isoformat()),
    )
    db.commit()
    return cur.lastrowid or cur.execute("SELECT id FROM documents WHERE url=?", (url,)).fetchone()[0]


def upsert_embeddings(pairs: List[Tuple[int, np.ndarray]]):
    """
    Store embeddings in database
    pairs: list of (doc_id, vector)
    """
    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()
    for doc_id, vec in pairs:
        blob = _serialize(vec)
        dim = len(vec)
        cur.execute(
            "INSERT OR REPLACE INTO vectors(doc_id, dim, embedding_blob) "
            "VALUES(?,?,?)",
            (doc_id, dim, blob),
        )
    db.commit()
    db.close()


def query_vectors(vec: np.ndarray, top_k: int = 5):
    """
    Query vector database for similar documents
    Returns list of (row_dict, cosine_score)
    """
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    cur = db.cursor()
    cur.execute(
        "SELECT d.*, v.embedding_blob FROM documents d "
        "JOIN vectors v ON d.id = v.doc_id"
    )
    rows, scores = [], []
    for r in cur.fetchall():
        emb = _deserialize(r["embedding_blob"])
        score = float(vec @ emb / (np.linalg.norm(vec) * np.linalg.norm(emb) + 1e-8))
        rows.append(r)
        scores.append(score)
    db.close()
    
    if not rows:
        return []
    
    idx = np.argsort(scores)[::-1][:top_k]
    return [(rows[i], scores[i]) for i in idx]


def get_status():
    """Get application status and statistics"""
    try:
        db = sqlite3.connect(DB_PATH)
        cur = db.cursor()
        
        # Count documents
        cur.execute("SELECT COUNT(*) FROM documents")
        doc_count = cur.fetchone()[0]
        
        # Count vectors
        cur.execute("SELECT COUNT(*) FROM vectors")
        vector_count = cur.fetchone()[0]
        
        db.close()
        
        return {
            "status": "running",
            "documents": doc_count,
            "vectors": vector_count,
            "database_path": str(DB_PATH),
        }
    
    except Exception as e:
        return {"status": "error", "message": str(e)} 