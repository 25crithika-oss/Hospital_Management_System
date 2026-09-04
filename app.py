from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


# ================= DATABASE CONNECTION =================

def get_db_connection():
    conn = sqlite3.connect("hospital.db")
    conn.row_factory = sqlite3.Row
    return conn


# ================= CREATE DATABASE TABLES =================

def create_table():

    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            phone TEXT NOT NULL,
            blood_group TEXT NOT NULL,
            address TEXT NOT NULL,
            symptoms TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization TEXT NOT NULL,
            phone TEXT NOT NULL,
            experience INTEGER NOT NULL,
            available_days TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            reason TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)
    conn.execute("""CREATE TABLE IF NOT EXISTS bills (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id INTEGER NOT NULL, amount REAL NOT NULL, payment_method TEXT NOT NULL, payment_status TEXT NOT NULL, description TEXT, bill_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    conn.commit()
    conn.close()


# ================= HOME PAGE =================

@app.route("/")
def home():

    conn = get_db_connection()

    patient_count = conn.execute(
        "SELECT COUNT(*) FROM patients"
    ).fetchone()[0]

    doctor_count = conn.execute(
        "SELECT COUNT(*) FROM doctors"
    ).fetchone()[0]

    appointment_count = conn.execute(
        "SELECT COUNT(*) FROM appointments"
    ).fetchone()[0]

    bill_count = conn.execute(
        "SELECT COUNT(*) FROM bills"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        patient_count=patient_count,
        doctor_count=doctor_count,
        appointment_count=appointment_count,
        bill_count=bill_count
    )

# ================= PATIENT PAGE =================

@app.route("/patients")
def patients():

    search = request.args.get("search", "").strip()

    conn = get_db_connection()

    if search:
        patients = conn.execute("""
            SELECT * FROM patients
            WHERE name LIKE ?
            OR phone LIKE ?
            ORDER BY id DESC
        """, (
            f"%{search}%",
            f"%{search}%"
        )).fetchall()
    else:
        patients = conn.execute("""
            SELECT * FROM patients
            ORDER BY id DESC
        """).fetchall()

    conn.close()

    return render_template(
        "patients.html",
        patients=patients,
        search=search
    )


# ================= REGISTER PATIENT =================

@app.route("/register-patient", methods=["POST"])
def register_patient():

    name = request.form["name"]
    age = request.form["age"]
    gender = request.form["gender"]
    phone = request.form["phone"]
    blood_group = request.form["blood_group"]
    address = request.form["address"]
    symptoms = request.form["symptoms"]

    conn = get_db_connection()

    conn.execute("""
        INSERT INTO patients
        (name, age, gender, phone, blood_group, address, symptoms)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        age,
        gender,
        phone,
        blood_group,
        address,
        symptoms
    ))

    conn.commit()
    conn.close()

    return redirect("/patients")


# ================= DOCTOR PAGE =================

@app.route("/doctors")
def doctors():

    search = request.args.get("search", "").strip()

    conn = get_db_connection()

    if search:
        doctors = conn.execute("""
            SELECT * FROM doctors
            WHERE name LIKE ?
            OR specialization LIKE ?
            ORDER BY id DESC
        """, (
            f"%{search}%",
            f"%{search}%"
        )).fetchall()
    else:
        doctors = conn.execute("""
            SELECT * FROM doctors
            ORDER BY id DESC
        """).fetchall()

    conn.close()

    return render_template(
        "doctors.html",
        doctors=doctors,
        search=search
    )


# ================= REGISTER DOCTOR =================

@app.route("/register-doctor", methods=["POST"])
def register_doctor():

    name = request.form["name"]
    specialization = request.form["specialization"]
    phone = request.form["phone"]
    experience = request.form["experience"]
    available_days = request.form["available_days"]

    conn = get_db_connection()

    conn.execute("""
        INSERT INTO doctors
        (name, specialization, phone, experience, available_days)
        VALUES (?, ?, ?, ?, ?)
    """, (
        name,
        specialization,
        phone,
        experience,
        available_days
    ))

    conn.commit()
    conn.close()

    return redirect("/doctors")


# ================= APPOINTMENT PAGE =================

@app.route("/appointments")
def appointments():

    search = request.args.get("search", "").strip()

    conn = get_db_connection()

    patients = conn.execute("""
        SELECT id, name
        FROM patients
        ORDER BY name
    """).fetchall()

    doctors = conn.execute("""
        SELECT id, name, specialization
        FROM doctors
        ORDER BY name
    """).fetchall()

    if search:

        appointment_list = conn.execute("""
            SELECT
                appointments.id,
                patients.name AS patient_name,
                doctors.name AS doctor_name,
                doctors.specialization,
                appointments.appointment_date,
                appointments.appointment_time,
                appointments.reason,
                appointments.status
            FROM appointments
            JOIN patients
                ON appointments.patient_id = patients.id
            JOIN doctors
                ON appointments.doctor_id = doctors.id
            WHERE patients.name LIKE ?
            OR doctors.name LIKE ?
            ORDER BY appointments.id DESC
        """, (
            f"%{search}%",
            f"%{search}%"
        )).fetchall()

    else:

        appointment_list = conn.execute("""
            SELECT
                appointments.id,
                patients.name AS patient_name,
                doctors.name AS doctor_name,
                doctors.specialization,
                appointments.appointment_date,
                appointments.appointment_time,
                appointments.reason,
                appointments.status
            FROM appointments
            JOIN patients
                ON appointments.patient_id = patients.id
            JOIN doctors
                ON appointments.doctor_id = doctors.id
            ORDER BY appointments.id DESC
        """).fetchall()

    conn.close()

    return render_template(
        "appointments.html",
        patients=patients,
        doctors=doctors,
        appointments=appointment_list,
        search=search
    )


# ================= REGISTER APPOINTMENT =================

@app.route("/register-appointment", methods=["POST"])
def register_appointment():

    patient_id = request.form["patient_id"]
    doctor_id = request.form["doctor_id"]
    appointment_date = request.form["appointment_date"]
    appointment_time = request.form["appointment_time"]
    reason = request.form["reason"]
    status = request.form["status"]

    conn = get_db_connection()

    conn.execute("""
        INSERT INTO appointments
        (
            patient_id,
            doctor_id,
            appointment_date,
            appointment_time,
            reason,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        patient_id,
        doctor_id,
        appointment_date,
        appointment_time,
        reason,
        status
    ))

    conn.commit()
    conn.close()

    return redirect("/appointments")
# ================= BILLING PAGE =================

@app.route("/billing")
def billing():

    conn = get_db_connection()

    patients = conn.execute("""
        SELECT id, name
        FROM patients
        ORDER BY name
    """).fetchall()

    bills = conn.execute("""
        SELECT
            bills.id,
            patients.name AS patient_name,
            bills.amount,
            bills.payment_method,
            bills.payment_status,
            bills.description,
            bills.bill_date
        FROM bills
        JOIN patients
            ON bills.patient_id = patients.id
        ORDER BY bills.id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "billing.html",
        patients=patients,
        bills=bills
    )

# ================= REGISTER BILL =================

@app.route("/register-bill", methods=["POST"])
def register_bill():

    patient_id = request.form["patient_id"]
    amount = request.form["amount"]
    payment_method = request.form["payment_method"]
    payment_status = request.form["payment_status"]
    description = request.form["description"]

    conn = get_db_connection()

    conn.execute("""
        INSERT INTO bills
        (
            patient_id,
            amount,
            payment_method,
            payment_status,
            description
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        patient_id,
        amount,
        payment_method,
        payment_status,
        description
    ))

    conn.commit()
    conn.close()

    return redirect("/billing")


# ================= RUN APPLICATION =================

create_table()

if __name__ == "__main__":
    app.run(debug=True)

    