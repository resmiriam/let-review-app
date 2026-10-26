
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path(__file__).resolve().parent / "let_review.db"


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def now_datetime():
    return datetime.now().replace(microsecond=0)


def initialize_database():
    with connect() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS learners (
                learner_id INTEGER PRIMARY KEY AUTOINCREMENT,
                display_name TEXT NOT NULL DEFAULT 'Learner',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS questions (
                question_id TEXT PRIMARY KEY,
                subject TEXT NOT NULL,
                topic TEXT NOT NULL,
                question_text TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                explanation TEXT NOT NULL DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS attempts (
                attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
                learner_id INTEGER NOT NULL,
                question_id TEXT NOT NULL,
                selected_answer TEXT NOT NULL,
                is_correct INTEGER NOT NULL,
                was_guessed INTEGER NOT NULL DEFAULT 0,
                attempted_at TEXT NOT NULL,
                FOREIGN KEY (learner_id)
                    REFERENCES learners(learner_id),
                FOREIGN KEY (question_id)
                    REFERENCES questions(question_id)
            );

            CREATE TABLE IF NOT EXISTS topic_reviews (
                learner_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                topic TEXT NOT NULL,
                total_attempts INTEGER NOT NULL DEFAULT 0,
                total_mistakes INTEGER NOT NULL DEFAULT 0,
                consecutive_correct INTEGER NOT NULL DEFAULT 0,
                next_review_at TEXT,
                last_reviewed_at TEXT,
                PRIMARY KEY (learner_id, subject, topic),
                FOREIGN KEY (learner_id)
                    REFERENCES learners(learner_id)
            );

            CREATE TABLE IF NOT EXISTS question_reviews (
                learner_id INTEGER NOT NULL,
                question_id TEXT NOT NULL,
                mistake_count INTEGER NOT NULL DEFAULT 0,
                guess_count INTEGER NOT NULL DEFAULT 0,
                correct_streak INTEGER NOT NULL DEFAULT 0,
                next_review_at TEXT,
                last_reviewed_at TEXT,
                needs_review INTEGER NOT NULL DEFAULT 1,
                PRIMARY KEY (learner_id, question_id),
                FOREIGN KEY (learner_id)
                    REFERENCES learners(learner_id),
                FOREIGN KEY (question_id)
                    REFERENCES questions(question_id)
            );

            CREATE TABLE IF NOT EXISTS completed_lessons (
                learner_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                topic TEXT NOT NULL,
                completed_at TEXT NOT NULL,
                PRIMARY KEY (learner_id, subject, topic),
                FOREIGN KEY (learner_id)
                    REFERENCES learners(learner_id)
            );
        """)


def create_learner(display_name="Learner"):
    initialize_database()
    with connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO learners (display_name, created_at)
            VALUES (?, ?)
            """,
            (display_name, now_datetime().isoformat())
        )
        return cursor.lastrowid


def save_question(
    question_id,
    subject,
    topic,
    question_text,
    correct_answer,
    explanation=""
):
    initialize_database()
    with connect() as conn:
        conn.execute("""
            INSERT INTO questions (
                question_id, subject, topic,
                question_text, correct_answer, explanation
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(question_id) DO UPDATE SET
                subject = excluded.subject,
                topic = excluded.topic,
                question_text = excluded.question_text,
                correct_answer = excluded.correct_answer,
                explanation = excluded.explanation
        """, (
            question_id, subject, topic,
            question_text, correct_answer, explanation
        ))


def record_attempt(
    learner_id,
    question_id,
    selected_answer,
    was_guessed=False
):
    initialize_database()
    now = now_datetime()
    now_text = now.isoformat()

    with connect() as conn:
        question = conn.execute("""
            SELECT subject, topic, correct_answer
            FROM questions
            WHERE question_id = ?
        """, (question_id,)).fetchone()

        if question is None:
            raise ValueError("Question not found. Save it first.")

        learner = conn.execute(
            "SELECT learner_id FROM learners WHERE learner_id = ?",
            (learner_id,)
        ).fetchone()

        if learner is None:
            raise ValueError("Learner not found. Create a learner first.")

        correct = (
            str(selected_answer).strip().casefold()
            == str(question["correct_answer"]).strip().casefold()
        )
        guessed = bool(was_guessed)

        conn.execute("""
            INSERT INTO attempts (
                learner_id, question_id, selected_answer,
                is_correct, was_guessed, attempted_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            learner_id, question_id, str(selected_answer),
            int(correct), int(guessed), now_text
        ))

        # Update topic-level learning history.
        old_topic = conn.execute("""
            SELECT total_attempts, total_mistakes, consecutive_correct
            FROM topic_reviews
            WHERE learner_id = ? AND subject = ? AND topic = ?
        """, (learner_id, question["subject"], question["topic"])).fetchone()

        attempts = old_topic["total_attempts"] if old_topic else 0
        mistakes = old_topic["total_mistakes"] if old_topic else 0
        streak = old_topic["consecutive_correct"] if old_topic else 0

        attempts += 1

        if not correct:
            mistakes += 1
            streak = 0
        elif guessed:
            streak = 0
        else:
            streak += 1

        if not correct or guessed:
            topic_days = 1
        elif streak == 1:
            topic_days = 1
        elif streak == 2:
            topic_days = 3
        elif streak == 3:
            topic_days = 7
        else:
            topic_days = 14

        topic_next = (now + timedelta(days=topic_days)).isoformat()

        conn.execute("""
            INSERT INTO topic_reviews (
                learner_id, subject, topic, total_attempts,
                total_mistakes, consecutive_correct,
                next_review_at, last_reviewed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(learner_id, subject, topic) DO UPDATE SET
                total_attempts = excluded.total_attempts,
                total_mistakes = excluded.total_mistakes,
                consecutive_correct = excluded.consecutive_correct,
                next_review_at = excluded.next_review_at,
                last_reviewed_at = excluded.last_reviewed_at
        """, (
            learner_id, question["subject"], question["topic"],
            attempts, mistakes, streak, topic_next, now_text
        ))

        # Update question-level adaptive review history.
        old_question = conn.execute("""
            SELECT mistake_count, guess_count, correct_streak
            FROM question_reviews
            WHERE learner_id = ? AND question_id = ?
        """, (learner_id, question_id)).fetchone()

        mistake_count = old_question["mistake_count"] if old_question else 0
        guess_count = old_question["guess_count"] if old_question else 0
        question_streak = old_question["correct_streak"] if old_question else 0

        if not correct:
            mistake_count += 1
            question_streak = 0
            question_days = 1
            needs_review = 1
        elif guessed:
            guess_count += 1
            question_streak = 0
            question_days = 1
            needs_review = 1
        else:
            question_streak += 1
            if question_streak == 1:
                question_days = 1
            elif question_streak == 2:
                question_days = 3
            elif question_streak == 3:
                question_days = 7
            else:
                question_days = 14
            needs_review = 0

        question_next = (now + timedelta(days=question_days)).isoformat()

        conn.execute("""
            INSERT INTO question_reviews (
                learner_id, question_id, mistake_count, guess_count,
                correct_streak, next_review_at, last_reviewed_at,
                needs_review
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(learner_id, question_id) DO UPDATE SET
                mistake_count = excluded.mistake_count,
                guess_count = excluded.guess_count,
                correct_streak = excluded.correct_streak,
                next_review_at = excluded.next_review_at,
                last_reviewed_at = excluded.last_reviewed_at,
                needs_review = excluded.needs_review
        """, (
            learner_id, question_id, mistake_count, guess_count,
            question_streak, question_next, now_text, needs_review
        ))


def get_attempt_history(learner_id):
    initialize_database()
    with connect() as conn:
        rows = conn.execute("""
            SELECT a.*, q.subject, q.topic, q.question_text,
                   q.correct_answer, q.explanation
            FROM attempts a
            JOIN questions q ON q.question_id = a.question_id
            WHERE a.learner_id = ?
            ORDER BY a.attempt_id DESC
        """, (learner_id,)).fetchall()
        return [dict(row) for row in rows]


def get_weak_topics(learner_id):
    initialize_database()
    with connect() as conn:
        rows = conn.execute("""
            SELECT * FROM topic_reviews
            WHERE learner_id = ?
            ORDER BY total_mistakes DESC, consecutive_correct ASC
        """, (learner_id,)).fetchall()
        return [dict(row) for row in rows]


def get_due_reviews(learner_id):
    initialize_database()
    now_text = now_datetime().isoformat()
    with connect() as conn:
        rows = conn.execute("""
            SELECT tr.*
            FROM topic_reviews tr
            WHERE tr.learner_id = ?
              AND tr.next_review_at IS NOT NULL
              AND tr.next_review_at <= ?
            ORDER BY tr.total_mistakes DESC, tr.next_review_at ASC
        """, (learner_id, now_text)).fetchall()
        return [dict(row) for row in rows]


def get_questions_for_review(learner_id, limit=20, due_only=False):
    """Return questions needing practice, prioritizing mistakes and guesses."""
    initialize_database()
    now_text = now_datetime().isoformat()

    with connect() as conn:
        query = """
            SELECT
                q.question_id,
                q.subject,
                q.topic,
                q.question_text,
                q.correct_answer,
                q.explanation,
                qr.mistake_count,
                qr.guess_count,
                qr.correct_streak,
                qr.next_review_at,
                qr.needs_review,
                qr.last_reviewed_at
            FROM question_reviews qr
            JOIN questions q ON q.question_id = qr.question_id
            WHERE qr.learner_id = ?
        """
        params = [learner_id]

        if due_only:
            query += """
                AND qr.next_review_at IS NOT NULL
                AND qr.next_review_at <= ?
            """
            params.append(now_text)
        else:
            query += " AND (qr.needs_review = 1 OR qr.next_review_at <= ?)"
            params.append(now_text)

        query += """
            ORDER BY
                qr.needs_review DESC,
                qr.mistake_count DESC,
                qr.guess_count DESC,
                qr.next_review_at ASC
            LIMIT ?
        """
        params.append(max(1, min(int(limit), 100)))

        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]


def get_question_review_status(learner_id, question_id):
    initialize_database()
    with connect() as conn:
        row = conn.execute("""
            SELECT *
            FROM question_reviews
            WHERE learner_id = ? AND question_id = ?
        """, (learner_id, question_id)).fetchone()
        return dict(row) if row else None


if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully.")
    print(f"Database location: {DB_PATH}")


def mark_lesson_completed(learner_id, subject, topic):
    initialize_database()
    with connect() as conn:
        learner = conn.execute(
            "SELECT learner_id FROM learners WHERE learner_id = ?",
            (learner_id,)
        ).fetchone()
        if learner is None:
            raise ValueError("Learner not found.")

        conn.execute("""
            INSERT INTO completed_lessons
                (learner_id, subject, topic, completed_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(learner_id, subject, topic)
            DO UPDATE SET completed_at = excluded.completed_at
        """, (
            learner_id, subject, topic, now_datetime().isoformat()
        ))


def get_completed_lessons(learner_id):
    initialize_database()
    with connect() as conn:
        rows = conn.execute("""
            SELECT subject, topic
            FROM completed_lessons
            WHERE learner_id = ?
            ORDER BY completed_at
        """, (learner_id,)).fetchall()
        return [f"{row['subject']}: {row['topic']}" for row in rows]
