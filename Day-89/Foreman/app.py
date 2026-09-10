import os
import sqlite3
from datetime import datetime, timezone

from flask import Flask, render_template, request, jsonify

DB_PATH = os.path.join(os.path.dirname(__file__), "foreman.db")

app = Flask(__name__)

STATUSES = ("todo", "doing", "done")
PRIORITIES = ("low", "medium", "high")

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    task_key    TEXT NOT NULL,
    title       TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    status      TEXT NOT NULL DEFAULT 'todo',
    priority    TEXT NOT NULL DEFAULT 'medium',
    position    INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL
);
"""

DEMO_TASKS = [
    # title, description, status, priority
    ("Set up project repository", "Init git, add README, push to remote.", "todo", "medium"),
    ("Write onboarding docs", "So the next person doesn't have to ask.", "todo", "low"),
    ("Design the board schema", "Tasks table: status + priority + position.", "doing", "high"),
    ("Sketch wireframes", "Three columns, drag and drop between them.", "done", "medium"),
]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.execute(SCHEMA)
    count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    if count == 0:
        for i, (title, desc, status, priority) in enumerate(DEMO_TASKS):
            conn.execute(
                """INSERT INTO tasks (task_key, title, description, status, priority, position, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (f"TSK-{i + 1}", title, desc, status, priority, i, now_iso()),
            )
        conn.commit()
    conn.close()


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def row_to_dict(row):
    return {
        "id": row["id"],
        "key": row["task_key"],
        "title": row["title"],
        "description": row["description"],
        "status": row["status"],
        "priority": row["priority"],
        "position": row["position"],
        "created_at": row["created_at"],
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/tasks", methods=["GET"])
def list_tasks():
    conn = get_db()
    rows = conn.execute("SELECT * FROM tasks ORDER BY status, position").fetchall()
    conn.close()
    return jsonify([row_to_dict(r) for r in rows])


@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.get_json(force=True, silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "title is required"}), 400

    description = (data.get("description") or "").strip()
    status = data.get("status") if data.get("status") in STATUSES else "todo"
    priority = data.get("priority") if data.get("priority") in PRIORITIES else "medium"

    conn = get_db()
    max_pos = conn.execute(
        "SELECT COALESCE(MAX(position), -1) FROM tasks WHERE status = ?", (status,)
    ).fetchone()[0]

    cursor = conn.execute(
        """INSERT INTO tasks (task_key, title, description, status, priority, position, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        ("TEMP", title, description, status, priority, max_pos + 1, now_iso()),
    )
    new_id = cursor.lastrowid
    task_key = f"TSK-{new_id}"
    conn.execute("UPDATE tasks SET task_key = ? WHERE id = ?", (task_key, new_id))
    conn.commit()

    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (new_id,)).fetchone()
    conn.close()
    return jsonify(row_to_dict(row)), 201


@app.route("/api/tasks/<int:task_id>", methods=["PATCH"])
def update_task(task_id):
    data = request.get_json(force=True, silent=True) or {}

    conn = get_db()
    existing = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if existing is None:
        conn.close()
        return jsonify({"error": "not found"}), 404

    title = data.get("title", existing["title"])
    description = data.get("description", existing["description"])
    status = data.get("status", existing["status"])
    priority = data.get("priority", existing["priority"])
    position = data.get("position", existing["position"])

    if status not in STATUSES:
        status = existing["status"]
    if priority not in PRIORITIES:
        priority = existing["priority"]

    conn.execute(
        """UPDATE tasks SET title = ?, description = ?, status = ?, priority = ?, position = ?
           WHERE id = ?""",
        (title, description, status, priority, position, task_id),
    )
    conn.commit()

    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return jsonify(row_to_dict(row))


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_db()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return "", 204


@app.route("/api/reorder", methods=["POST"])
def reorder():
    """Body: {"status": "todo", "ordered_ids": [3, 1, 4]}
    Sets position = index in the list for each id, and forces their status
    to the given column (covers a card being dropped into a new column)."""
    data = request.get_json(force=True, silent=True) or {}
    status = data.get("status")
    ordered_ids = data.get("ordered_ids", [])

    if status not in STATUSES or not isinstance(ordered_ids, list):
        return jsonify({"error": "invalid payload"}), 400

    conn = get_db()
    for index, task_id in enumerate(ordered_ids):
        conn.execute(
            "UPDATE tasks SET status = ?, position = ? WHERE id = ?",
            (status, index, task_id),
        )
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
