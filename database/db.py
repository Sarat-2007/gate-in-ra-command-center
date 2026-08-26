"""
SQLite Database Layer for GATE Preparation Command Center
Provides schema creation, automatic topic seeding, and CRUD operations.
"""
import sqlite3
import json
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from config import DB_PATH
from database.seed_data import SYLLABUS_SEED_DATA


def get_db_connection() -> sqlite3.Connection:
    """Creates a database connection with dictionary-like row factory and concurrency timeout."""
    conn = sqlite3.connect(str(DB_PATH), timeout=30.0)
    conn.row_factory = sqlite3.Row
    return conn


def _safe_json_loads(val: Any, default: Any = None) -> Any:
    """Safely deserializes JSON with fallback default to prevent crash on corrupt data."""
    if default is None:
        default = []
    if val is None or val == "":
        return default
    if isinstance(val, (list, dict)):
        return val
    try:
        return json.loads(val)
    except Exception:
        return default


def init_db() -> None:
    """Initializes the database schema and seeds initial syllabus topics."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")

    # 1. Daily Check-Ins Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_checkins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT UNIQUE NOT NULL,
        hours_logged REAL NOT NULL,
        completed_topics TEXT NOT NULL,      -- JSON array of topic IDs
        error_codes TEXT NOT NULL,           -- JSON array of error codes ['C', 'F', etc.]
        roadblocks_text TEXT,
        ai_generated_plan TEXT,              -- Cached JSON string of generated next-day plan
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Syllabus Topics Master Registry
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS syllabus_topics (
        id TEXT PRIMARY KEY,
        week_number INTEGER NOT NULL,
        domain TEXT NOT NULL,
        module_name TEXT NOT NULL,
        topic_name TEXT NOT NULL,
        priority TEXT DEFAULT 'High',
        weightage_approx_marks REAL DEFAULT 2.0,
        is_completed INTEGER DEFAULT 0,
        completed_date TEXT,
        yt_theory_title TEXT,
        yt_theory_url TEXT,
        yt_pyq_title TEXT,
        yt_pyq_url TEXT,
        pyq_practice_url TEXT,
        key_formula_latex TEXT,
        core_summary TEXT,
        pyq_question TEXT,
        pyq_type TEXT DEFAULT 'MCQ',
        pyq_options TEXT,
        pyq_correct_answer TEXT,
        pyq_explanation TEXT
    );
    """)

    # 3. Dedicated Weekend General Aptitude Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS aptitude_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        week_number INTEGER NOT NULL,
        hours_logged REAL NOT NULL,
        topic_category TEXT NOT NULL,
        pyqs_attempted INTEGER DEFAULT 0,
        pyqs_correct INTEGER DEFAULT 0,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 4. Spaced Repetition Formula Vault
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS formula_vault (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic_id TEXT UNIQUE NOT NULL,
        formula_title TEXT NOT NULL,
        formula_latex TEXT NOT NULL,
        domain TEXT NOT NULL,
        interval_days INTEGER DEFAULT 1,
        repetition_count INTEGER DEFAULT 0,
        ease_factor REAL DEFAULT 2.5,
        last_reviewed_date TEXT,
        next_review_date TEXT,
        mastery_status TEXT DEFAULT 'Learning', -- 'Learning', 'Reviewing', 'Mastered'
        FOREIGN KEY (topic_id) REFERENCES syllabus_topics (id)
    );
    """)

    # 5. Redo Mistakes Error Quarantine
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS error_quarantine (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date_logged TEXT NOT NULL,
        topic_id TEXT NOT NULL,
        topic_name TEXT NOT NULL,
        error_code TEXT NOT NULL,
        question_details TEXT NOT NULL,
        wrong_attempt_notes TEXT,
        correct_takeaway TEXT,
        attempts_count INTEGER DEFAULT 0,
        is_mastered INTEGER DEFAULT 0,
        mastered_date TEXT
    );
    """)

    # 6. Key-Value User Settings
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    );
    """)

    # Create Performance Indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_checkins_date ON daily_checkins(date);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_syllabus_week ON syllabus_topics(week_number);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_syllabus_completed ON syllabus_topics(is_completed);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_aptitude_week ON aptitude_sessions(week_number);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_formula_next_review ON formula_vault(next_review_date);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_error_quarantine_mastered ON error_quarantine(is_mastered);")

    conn.commit()

    # Seed syllabus data if table is empty
    today = date.today()
    today_str = today.strftime("%Y-%m-%d")

    # Seed or synchronize syllabus topics and formula vault
    for t in SYLLABUS_SEED_DATA:
        cursor.execute("""
        INSERT OR REPLACE INTO syllabus_topics (
            id, week_number, domain, module_name, topic_name, priority,
            weightage_approx_marks, is_completed, completed_date,
            yt_theory_title, yt_theory_url, yt_pyq_title, yt_pyq_url,
            pyq_practice_url, key_formula_latex, core_summary,
            pyq_question, pyq_type, pyq_options, pyq_correct_answer, pyq_explanation
        ) VALUES (
            ?, ?, ?, ?, ?, ?,
            ?,
            COALESCE((SELECT is_completed FROM syllabus_topics WHERE id = ?), 0),
            (SELECT completed_date FROM syllabus_topics WHERE id = ?),
            ?, ?, ?, ?,
            ?, ?, ?,
            ?, ?, ?, ?, ?
        )
        """, (
            t["id"], t["week_number"], t["domain"], t["module_name"], t["topic_name"],
            t["priority"], t["weightage_approx_marks"],
            t["id"], t["id"],
            t["yt_theory_title"], t["yt_theory_url"], t["yt_pyq_title"], t["yt_pyq_url"],
            t["pyq_practice_url"], t["key_formula_latex"], t["core_summary"],
            t.get("pyq_question", ""), t.get("pyq_type", "MCQ"),
            json.dumps(t.get("pyq_options", [])),
            t.get("pyq_correct_answer", ""), t.get("pyq_explanation", "")
        ))

        # Progressive initial review date (staggered by week so future cards don't flood Day 1)
        w_offset = max(0, t["week_number"] - 1) * 7
        staggered_date = (today + timedelta(days=w_offset)).strftime("%Y-%m-%d")

        cursor.execute("""
        INSERT OR IGNORE INTO formula_vault (
            topic_id, formula_title, formula_latex, domain,
            interval_days, repetition_count, ease_factor,
            last_reviewed_date, next_review_date, mastery_status
        ) VALUES (?, ?, ?, ?, 1, 0, 2.5, NULL, ?, 'Learning')
        """, (
            t["id"], t["topic_name"], t["key_formula_latex"], t["domain"], staggered_date
        ))

    # Default Settings (if not already present)
    cursor.execute("INSERT OR IGNORE INTO user_settings (key, value) VALUES ('target_paper', 'IN')")
    cursor.execute("INSERT OR IGNORE INTO user_settings (key, value) VALUES ('start_date', ?)", (today_str,))
    conn.commit()

    conn.close()


# =============================================================================
# CRUD Operations
# =============================================================================

def get_all_topics() -> List[Dict[str, Any]]:
    """Fetches all syllabus topics."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM syllabus_topics ORDER BY week_number, id")
    rows = []
    for r in cursor.fetchall():
        d = dict(r)
        d["pyq_options"] = _safe_json_loads(d.get("pyq_options"), [])
        rows.append(d)
    conn.close()
    return rows


def update_topic_completion(topic_id: str, is_completed: bool, completed_date: Optional[str] = None) -> None:
    """Updates completion status of a topic."""
    conn = get_db_connection()
    cursor = conn.cursor()
    c_date = completed_date if is_completed else None
    cursor.execute("""
    UPDATE syllabus_topics
    SET is_completed = ?, completed_date = ?
    WHERE id = ?
    """, (1 if is_completed else 0, c_date, topic_id))
    conn.commit()
    conn.close()


def log_daily_checkin(
    checkin_date: str,
    hours_logged: float,
    completed_topics: List[str],
    error_codes: List[str],
    roadblocks_text: str = "",
    ai_generated_plan: Optional[str] = None
) -> int:
    """Logs or updates a daily check-in."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Mark topics as completed in syllabus_topics
    for tid in completed_topics:
        cursor.execute("""
        UPDATE syllabus_topics
        SET is_completed = 1, completed_date = ?
        WHERE id = ?
        """, (checkin_date, tid))

    cursor.execute("""
    INSERT INTO daily_checkins (
        date, hours_logged, completed_topics, error_codes, roadblocks_text, ai_generated_plan
    ) VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(date) DO UPDATE SET
        hours_logged = excluded.hours_logged,
        completed_topics = excluded.completed_topics,
        error_codes = excluded.error_codes,
        roadblocks_text = excluded.roadblocks_text,
        ai_generated_plan = COALESCE(excluded.ai_generated_plan, daily_checkins.ai_generated_plan)
    """, (
        checkin_date,
        hours_logged,
        json.dumps(completed_topics),
        json.dumps(error_codes),
        roadblocks_text,
        ai_generated_plan
    ))
    cursor.execute("SELECT id FROM daily_checkins WHERE date = ?", (checkin_date,))
    checkin_row = cursor.fetchone()
    checkin_id = checkin_row[0] if checkin_row else 1
    conn.commit()
    conn.close()
    return checkin_id


def get_checkin_by_date(checkin_date: str) -> Optional[Dict[str, Any]]:
    """Retrieves check-in record for a specific date."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM daily_checkins WHERE date = ?", (checkin_date,))
    row = cursor.fetchone()
    conn.close()
    if row:
        data = dict(row)
        data["completed_topics"] = _safe_json_loads(data.get("completed_topics"), [])
        data["error_codes"] = _safe_json_loads(data.get("error_codes"), [])
        return data
    return None


def get_all_checkins() -> List[Dict[str, Any]]:
    """Retrieves all daily check-ins ordered by date."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM daily_checkins ORDER BY date ASC")
    rows = []
    for r in cursor.fetchall():
        d = dict(r)
        d["completed_topics"] = _safe_json_loads(d.get("completed_topics"), [])
        d["error_codes"] = _safe_json_loads(d.get("error_codes"), [])
        rows.append(d)
    conn.close()
    return rows


def log_aptitude_session(
    session_date: str,
    week_number: int,
    hours_logged: float,
    topic_category: str,
    pyqs_attempted: int,
    pyqs_correct: int,
    notes: str = ""
) -> int:
    """Logs a weekend General Aptitude study session."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO aptitude_sessions (
        date, week_number, hours_logged, topic_category, pyqs_attempted, pyqs_correct, notes
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (session_date, week_number, hours_logged, topic_category, pyqs_attempted, pyqs_correct, notes))
    sid = cursor.lastrowid
    conn.commit()
    conn.close()
    return sid


def get_aptitude_sessions() -> List[Dict[str, Any]]:
    """Fetches all General Aptitude study records."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM aptitude_sessions ORDER BY date DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def add_error_quarantine(
    date_logged: str,
    topic_id: str,
    topic_name: str,
    error_code: str,
    question_details: str,
    wrong_attempt_notes: str,
    correct_takeaway: str
) -> int:
    """Adds a problem to the Redo Mistakes quarantine queue."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO error_quarantine (
        date_logged, topic_id, topic_name, error_code, question_details,
        wrong_attempt_notes, correct_takeaway, attempts_count, is_mastered
    ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, 0)
    """, (
        date_logged, topic_id, topic_name, error_code,
        question_details, wrong_attempt_notes, correct_takeaway
    ))
    eid = cursor.lastrowid
    conn.commit()
    conn.close()
    return eid


def get_quarantined_errors(only_active: bool = True) -> List[Dict[str, Any]]:
    """Fetches problems from error quarantine."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if only_active:
        cursor.execute("SELECT * FROM error_quarantine WHERE is_mastered = 0 ORDER BY date_logged DESC")
    else:
        cursor.execute("SELECT * FROM error_quarantine ORDER BY date_logged DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def update_error_mastery(error_id: int, is_mastered: bool) -> None:
    """Marks a quarantined mistake as mastered after re-testing."""
    conn = get_db_connection()
    cursor = conn.cursor()
    m_date = datetime.now().strftime("%Y-%m-%d") if is_mastered else None
    cursor.execute("""
    UPDATE error_quarantine
    SET is_mastered = ?, mastered_date = ?, attempts_count = attempts_count + 1
    WHERE id = ?
    """, (1 if is_mastered else 0, m_date, error_id))
    conn.commit()
    conn.close()


def get_formula_vault(due_only: bool = False) -> List[Dict[str, Any]]:
    """Fetches formula flashcards from the vault."""
    conn = get_db_connection()
    cursor = conn.cursor()
    today_str = date.today().strftime("%Y-%m-%d")
    if due_only:
        cursor.execute("SELECT * FROM formula_vault WHERE next_review_date <= ? ORDER BY next_review_date ASC", (today_str,))
    else:
        cursor.execute("SELECT * FROM formula_vault ORDER BY domain, topic_id")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def update_formula_review(topic_id: str, quality_score: int) -> None:
    """
    Updates a formula's spaced repetition interval using modified SuperMemo-2.
    Quality score: 0 (forgot), 1 (hesitated), 2 (easy recall)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM formula_vault WHERE topic_id = ?", (topic_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return

    curr = dict(row)
    reps = curr.get("repetition_count") if curr.get("repetition_count") is not None else 0
    interval = curr.get("interval_days") if curr.get("interval_days") is not None else 1
    ease = curr.get("ease_factor") if curr.get("ease_factor") is not None else 2.5

    today = date.today()
    if quality_score >= 1:
        if reps == 0:
            interval = 1
        elif reps == 1:
            interval = 3
        else:
            interval = int(interval * ease)
        reps += 1
        ease = max(1.3, ease + (0.1 - (2 - quality_score) * 0.08))
    else:
        reps = 0
        interval = 1
        ease = max(1.3, ease - 0.2)

    interval = min(365, max(1, interval))
    status = "Mastered" if reps >= 4 else ("Reviewing" if reps >= 1 else "Learning")
    next_date = (today + timedelta(days=interval)).strftime("%Y-%m-%d")

    cursor.execute("""
    UPDATE formula_vault
    SET interval_days = ?, repetition_count = ?, ease_factor = ?,
        last_reviewed_date = ?, next_review_date = ?, mastery_status = ?
    WHERE topic_id = ?
    """, (interval, reps, ease, today.strftime("%Y-%m-%d"), next_date, status, topic_id))
    conn.commit()
    conn.close()


def get_setting(key: str, default: str = "") -> str:
    """Fetches a setting value."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM user_settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else default


def set_setting(key: str, value: str) -> None:
    """Sets a setting value."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO user_settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()
