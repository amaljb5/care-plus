from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime

app = Flask(__name__)

DATABASE = "database.db"


# ---------------- DATABASE ----------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():

    conn = get_db()
    cursor = conn.cursor()

    # Emergency requests
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emergencies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            emergency_type TEXT,
            latitude REAL,
            longitude REAL,
            status TEXT,
            created_at TEXT
        )
    """)

    # Emergency contacts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emergency_contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            phone TEXT
        )
    """)

    # Caregivers
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS caregivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            service TEXT,
            phone TEXT,
            available INTEGER
        )
    """)

    # Bookings
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            caregiver_id INTEGER,
            service TEXT,
            booking_date TEXT,
            status TEXT
        )
    """)

    # Volunteers
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS volunteers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            service TEXT,
            available INTEGER
        )
    """)

    # Blood donors
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blood_donors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            blood_group TEXT,
            location TEXT,
            available INTEGER
        )
    """)

    # Blood requests
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blood_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT,
            blood_group TEXT,
            hospital TEXT,
            location TEXT,
            status TEXT
        )
    """)

    conn.commit()
    conn.close()


# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- SOS ----------------

@app.route("/sos", methods=["POST"])
def sos():

    data = request.json

    user_id = data.get("user_id")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO emergencies
        (user_id, emergency_type, latitude, longitude, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        "SOS",
        latitude,
        longitude,
        "ACTIVE",
        datetime.now().isoformat()
    ))

    emergency_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Emergency request created",
        "emergency_id": emergency_id
    })


# ---------------- EMERGENCY STATUS ----------------

@app.route("/emergency/<int:emergency_id>")
def emergency_status(emergency_id):

    conn = get_db()

    emergency = conn.execute(
        "SELECT * FROM emergencies WHERE id = ?",
        (emergency_id,)
    ).fetchone()

    conn.close()

    if emergency is None:
        return jsonify({"error": "Emergency not found"})

    return jsonify(dict(emergency))


# ---------------- UPDATE EMERGENCY STATUS ----------------

@app.route("/emergency/<int:emergency_id>/status", methods=["POST"])
def update_status(emergency_id):

    data = request.json

    status = data.get("status")

    conn = get_db()

    conn.execute("""
        UPDATE emergencies
        SET status = ?
        WHERE id = ?
    """, (status, emergency_id))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Emergency status updated"
    })


# ---------------- CAREGIVER SEARCH ----------------

@app.route("/caregivers")
def caregivers():

    service = request.args.get("service")

    conn = get_db()

    if service:
        results = conn.execute("""
            SELECT * FROM caregivers
            WHERE service = ? AND available = 1
        """, (service,)).fetchall()
    else:
        results = conn.execute("""
            SELECT * FROM caregivers
            WHERE available = 1
        """).fetchall()

    conn.close()

    return jsonify([dict(row) for row in results])


# ---------------- BOOK CAREGIVER ----------------

@app.route("/booking", methods=["POST"])
def booking():

    data = request.json

    user_id = data.get("user_id")
    caregiver_id = data.get("caregiver_id")
    service = data.get("service")
    booking_date = data.get("booking_date")

    conn = get_db()

    conn.execute("""
        INSERT INTO bookings
        (user_id, caregiver_id, service, booking_date, status)
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        caregiver_id,
        service,
        booking_date,
        "PENDING"
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Booking request submitted"
    })


# ---------------- VOLUNTEER REGISTRATION ----------------

@app.route("/volunteer", methods=["POST"])
def volunteer():

    data = request.json

    name = data.get("name")
    phone = data.get("phone")
    service = data.get("service")

    conn = get_db()

    conn.execute("""
        INSERT INTO volunteers
        (name, phone, service, available)
        VALUES (?, ?, ?, ?)
    """, (
        name,
        phone,
        service,
        1
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Volunteer registered successfully"
    })


# ---------------- BLOOD DONOR ----------------

@app.route("/blood-donor", methods=["POST"])
def blood_donor():

    data = request.json

    conn = get_db()

    conn.execute("""
        INSERT INTO blood_donors
        (name, phone, blood_group, location, available)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data.get("name"),
        data.get("phone"),
        data.get("blood_group"),
        data.get("location"),
        1
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Blood donor registered"
    })


# ---------------- BLOOD SEARCH ----------------

@app.route("/blood-donors")
def blood_donors():

    blood_group = request.args.get("blood_group")

    conn = get_db()

    donors = conn.execute("""
        SELECT * FROM blood_donors
        WHERE blood_group = ? AND available = 1
    """, (blood_group,)).fetchall()

    conn.close()

    return jsonify([dict(donor) for donor in donors])


# ---------------- BLOOD REQUEST ----------------

@app.route("/blood-request", methods=["POST"])
def blood_request():

    data = request.json

    conn = get_db()

    conn.execute("""
        INSERT INTO blood_requests
        (patient_name, blood_group, hospital, location, status)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data.get("patient_name"),
        data.get("blood_group"),
        data.get("hospital"),
        data.get("location"),
        "ACTIVE"
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Blood request created"
    })


if __name__ == "__main__":

    create_tables()

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )






@app.route("/emergency/<int:emergency_id>/escalate",
           methods=["POST"])
def escalate_emergency(emergency_id):

    conn = get_db()

    conn.execute("""
        UPDATE emergencies
        SET status = ?
        WHERE id = ?
    """, (
        "ESCALATED",
        emergency_id
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Emergency escalated"
    })








@app.route("/emergency/<int:emergency_id>/verify",
           methods=["POST"])
def verify_emergency(emergency_id):

    data = request.json

    decision = data.get("decision")

    conn = get_db()

    if decision == "VERIFIED":

        status = "VERIFIED"

    else:

        status = "CANCELLED"

    conn.execute("""
        UPDATE emergencies
        SET status = ?
        WHERE id = ?
    """, (
        status,
        emergency_id
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "status": status
    })










@app.route("/notify-contact/<int:emergency_id>")
def notify_contact(emergency_id):

    conn = get_db()

    contacts = conn.execute("""
        SELECT * FROM emergency_contacts
    """).fetchall()

    conn.close()

    for contact in contacts:

        print(
            "NOTIFICATION SENT TO:",
            contact["name"],
            contact["phone"]
        )

    return jsonify({
        "success": True,
        "message": "Emergency contacts notified"
    })





