from flask import Flask, render_template, request, redirect
import sqlite3, os
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.secret_key = "secret"

socketio = SocketIO(app)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ================== БАЗА ==================
def init_db():
    conn = sqlite3.connect("db.sqlite3")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS ads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        lat REAL,
        lng REAL,
        image TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()


# ================== ГЛАВНАЯ ==================
@app.route("/", methods=["GET", "POST"])
def index():
    conn = sqlite3.connect("db.sqlite3")
    c = conn.cursor()

    # ДОБАВЛЕНИЕ ОБЪЯВЛЕНИЯ
    if request.method == "POST":
        title = request.form["title"]
        desc = request.form["description"]
        lat = request.form["lat"]
        lng = request.form["lng"]

        file = request.files["image"]
        filename = ""

        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        c.execute("""
        INSERT INTO ads (title, description, lat, lng, image)
        VALUES (?, ?, ?, ?, ?)
        """, (title, desc, lat, lng, filename))

        conn.commit()

    ads = c.execute("SELECT * FROM ads").fetchall()
    conn.close()

    return render_template("index.html", ads=ads)


# ================== ЧАТ ==================
@socketio.on("message")
def handle_message(msg):
    send(msg, broadcast=True)


# ================== ЗАПУСК ==================
if __name__ == "__main__":
    socketio.run(app, debug=True)
  
