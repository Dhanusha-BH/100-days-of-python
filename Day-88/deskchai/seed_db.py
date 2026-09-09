"""
Creates cafes.db and populates it with sample work-friendly cafés in Bengaluru.

Run this once before starting the app:
    python seed_db.py

If you already have your own cafes.db (e.g. from the Day 66 API project) with
a matching schema, you can skip this and just drop your file in this folder
instead — app.py doesn't care how the data got there.
"""

import os
import sqlite3
from urllib.parse import quote

DB_PATH = os.path.join(os.path.dirname(__file__), "cafes.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS cafes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    area            TEXT NOT NULL,
    city            TEXT NOT NULL DEFAULT 'Bengaluru',
    map_url         TEXT,
    opening_hours   TEXT,
    seats           TEXT,
    coffee_price    TEXT,
    has_wifi        INTEGER NOT NULL DEFAULT 0,
    has_sockets     INTEGER NOT NULL DEFAULT 0,
    has_toilet      INTEGER NOT NULL DEFAULT 0,
    can_take_calls  INTEGER NOT NULL DEFAULT 0,
    quiet_friendly  INTEGER NOT NULL DEFAULT 0,
    veg_available   INTEGER NOT NULL DEFAULT 0
);
"""

# (name, area, opening_hours, seats, coffee_price,
#  wifi, sockets, toilet, calls, quiet, veg)
CAFES = [
    ("Filter & Founders", "Indiranagar", "08:00 – 20:00", "30-40", "₹180", 1, 1, 1, 1, 0, 1),
    ("The Working Chai", "Koramangala", "09:00 – 22:00", "20-30", "₹120", 1, 1, 1, 0, 0, 1),
    ("Beans & Bytes", "HSR Layout", "08:30 – 21:00", "15-20", "₹200", 1, 1, 0, 1, 1, 0),
    ("Sunday Standard", "Jayanagar", "08:00 – 19:00", "10-15", "₹150", 1, 0, 1, 0, 1, 1),
    ("Two Owls Café", "Whitefield", "07:30 – 21:30", "40-50", "₹160", 1, 1, 1, 1, 0, 0),
    ("Paper Plane Coffee", "MG Road", "08:00 – 22:00", "25-30", "₹220", 1, 1, 1, 1, 0, 1),
    ("Kaapi Kada", "Malleswaram", "07:00 – 20:00", "15-20", "₹80", 0, 0, 1, 0, 1, 1),
    ("The Reading Room Café", "JP Nagar", "09:00 – 20:00", "10-15", "₹190", 1, 1, 1, 0, 1, 1),
    ("Mint & Mortar", "Basavanagudi", "08:00 – 19:30", "12-18", "₹140", 1, 0, 0, 0, 1, 1),
    ("Peppercorn Café", "Electronic City", "08:00 – 21:00", "30-35", "₹170", 1, 1, 1, 1, 0, 0),
    ("The Notebook Café", "Indiranagar", "09:00 – 23:00", "20-25", "₹210", 1, 1, 1, 1, 1, 0),
    ("Broadway Brew", "Koramangala", "08:00 – 22:00", "35-40", "₹190", 1, 1, 1, 0, 0, 1),
    ("Whitefield Workshop Café", "Whitefield", "08:00 – 20:00", "20-25", "₹150", 1, 1, 1, 1, 1, 0),
    ("One More Cup", "HSR Layout", "07:30 – 21:00", "15-20", "₹130", 1, 0, 1, 0, 0, 1),
    ("The Colony Café", "Jayanagar", "08:00 – 20:00", "18-22", "₹160", 1, 1, 0, 0, 1, 1),
    ("Bytes & Brew", "MG Road", "08:00 – 23:00", "25-30", "₹230", 1, 1, 1, 1, 0, 0),
    ("South Block Café", "Malleswaram", "07:30 – 19:00", "10-15", "₹100", 0, 1, 1, 0, 1, 1),
    ("The Long Table", "JP Nagar", "09:00 – 21:00", "30-35", "₹180", 1, 1, 1, 1, 0, 1),
    ("Third Quarter Coffee", "Basavanagudi", "08:00 – 20:00", "20-25", "₹150", 1, 1, 0, 0, 1, 0),
    ("Sunday Roast Café", "Electronic City", "08:30 – 21:30", "15-20", "₹170", 1, 0, 1, 1, 1, 1),
]

CITY = "Bengaluru"


def build_map_url(name, area, city):
    query = quote(f"{name} {area} {city}")
    return f"https://www.google.com/maps/search/?api=1&query={query}"


def main():
    fresh = not os.path.exists(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(SCHEMA)

    existing = conn.execute("SELECT COUNT(*) FROM cafes").fetchone()[0]
    if existing:
        print(f"cafes.db already has {existing} cafés — leaving it as is.")
        conn.close()
        return

    for row in CAFES:
        name, area, hours, seats, price, wifi, sockets, toilet, calls, quiet, veg = row
        conn.execute(
            """INSERT INTO cafes
               (name, area, city, map_url, opening_hours, seats, coffee_price,
                has_wifi, has_sockets, has_toilet, can_take_calls, quiet_friendly, veg_available)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, area, CITY, build_map_url(name, area, CITY), hours, seats, price,
             wifi, sockets, toilet, calls, quiet, veg),
        )

    conn.commit()
    conn.close()
    print(f"{'Created' if fresh else 'Updated'} cafes.db with {len(CAFES)} cafés.")


if __name__ == "__main__":
    main()
