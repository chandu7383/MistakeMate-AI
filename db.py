import sqlite3
import json
from datetime import datetime

DB_NAME = "mistakemate.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            score INTEGER,
            status TEXT,
            mistake_count INTEGER,
            result_json TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_analysis(question, answer, result):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO analyses
        (question, answer, score, status, mistake_count, result_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        question,
        answer,
        result.get("score", 0),
        result.get("overall_status", "Unknown"),
        len(result.get("mistakes", [])),
        json.dumps(result, ensure_ascii=False),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

def get_history(limit=20):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT question, answer, score, status, mistake_count, created_at
        FROM analyses
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()

    return [
        {
            "question": r[0],
            "answer": r[1],
            "score": r[2],
            "status": r[3],
            "mistake_count": r[4],
            "created_at": r[5]
        }
        for r in rows
    ]