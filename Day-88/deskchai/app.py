import os
import sqlite3
from urllib.parse import quote

from flask import Flask, render_template, request, redirect, url_for, flash

DB_PATH = os.path.join(os.path.dirname(__file__), "cafes.db")

app = Flask(__name__)
app.secret_key = "dev-only-secret-key-change-before-deploying"

# Filter keys must match column names in the cafes table.
FILTERS = ["has_wifi", "has_sockets", "has_toilet", "can_take_calls", "quiet_friendly", "veg_available"]
FILTER_LABELS = {
    "has_wifi": "Wi-Fi",
    "has_sockets": "Sockets",
    "has_toilet": "Restroom",
    "can_take_calls": "Calls okay",
    "quiet_friendly": "Quiet",
    "veg_available": "Veg food",
}


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us access columns by name, e.g. row["name"]
    return conn


@app.route("/")
def index():
    active_filters = [f for f in FILTERS if request.args.get(f) == "1"]

    query = "SELECT * FROM cafes"
    params = []
    if active_filters:
        conditions = " AND ".join(f"{f} = 1" for f in active_filters)
        query += f" WHERE {conditions}"
    query += " ORDER BY name"

    conn = get_db()
    cafes = conn.execute(query, params).fetchall()
    conn.close()

    return render_template(
        "index.html",
        cafes=cafes,
        filters=FILTERS,
        filter_labels=FILTER_LABELS,
        active_filters=active_filters,
        total=len(cafes),
    )


@app.route("/add", methods=["GET", "POST"])
def add_cafe():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        area = request.form.get("area", "").strip()
        city = request.form.get("city", "").strip() or "Bengaluru"
        opening_hours = request.form.get("opening_hours", "").strip()
        seats = request.form.get("seats", "").strip()
        coffee_price = request.form.get("coffee_price", "").strip()

        if not name or not area:
            flash("Please fill in at least the café name and area.")
            return redirect(url_for("add_cafe"))

        map_url = f"https://www.google.com/maps/search/?api=1&query={quote(f'{name} {area} {city}')}"

        conn = get_db()
        conn.execute(
            """INSERT INTO cafes
               (name, area, city, map_url, opening_hours, seats, coffee_price,
                has_wifi, has_sockets, has_toilet, can_take_calls, quiet_friendly, veg_available)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                name, area, city, map_url, opening_hours, seats, coffee_price,
                1 if request.form.get("has_wifi") else 0,
                1 if request.form.get("has_sockets") else 0,
                1 if request.form.get("has_toilet") else 0,
                1 if request.form.get("can_take_calls") else 0,
                1 if request.form.get("quiet_friendly") else 0,
                1 if request.form.get("veg_available") else 0,
            ),
        )
        conn.commit()
        conn.close()

        flash(f'"{name}" was added.')
        return redirect(url_for("index"))

    return render_template("add.html")


@app.route("/delete/<int:cafe_id>", methods=["POST"])
def delete_cafe(cafe_id):
    conn = get_db()
    cafe = conn.execute("SELECT name FROM cafes WHERE id = ?", (cafe_id,)).fetchone()
    conn.execute("DELETE FROM cafes WHERE id = ?", (cafe_id,))
    conn.commit()
    conn.close()

    if cafe:
        flash(f'"{cafe["name"]}" was removed.')
    return redirect(url_for("index"))


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print("cafes.db not found. Run `python seed_db.py` first, then start the app again.")
    else:
        app.run(debug=True)
