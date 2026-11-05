from flask import Flask, render_template, request, redirect
from urllib.parse import urlparse

from functools import wraps

from flask import session
from werkzeug.security import generate_password_hash , check_password_hash

import random
import string

import sqlite3


app = Flask(__name__)
app.secret_key = "dev-only-change-this-secret-key"

def login_required(route_function):

    @wraps(route_function)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            return redirect("/login")

        return route_function(*args, **kwargs)

    return wrapper

def valid_url(url):
    try:
        result = urlparse(url)

        return result.scheme in ["http", "https"] and bool(result.netloc)

    except Exception:
        return False

def gen_short_code():
    characters = string.ascii_letters + string.digits
    short_code = ''.join(random.choices(characters, k=6))

    return short_code

def init_db():
    connection = sqlite3.connect("urls.db")

    connection.execute("""
        CREATE TABLE IF NOT EXISTS urls(
        id INTEGER PRIMARY KEY AUTOINCREMENT, original_url TEXT NOT NULL, short_code TEXT NOT NULL UNIQUE)
        """)

    connection.commit()
    connection.close()

def save_url(original_url, short_code, user_id=None):

    connection = sqlite3.connect("urls.db")

    connection.execute("""
        INSERT INTO urls (original_url, short_code, user_id)
        VALUES (?, ?, ?)
    """, (original_url, short_code, user_id))

    connection.commit()
    connection.close()

def short_code_exists(short_code):
    connection = sqlite3.connect("urls.db")

    result = connection.execute("SELECT id FROM urls WHERE short_code = ?", (short_code,)).fetchone()

    connection.close()
    return result is not None


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # Validate empty fields
        if not username or not email or not password:
            return render_template(
                "register.html",
                error="All fields are required."
            )

        # Validate password length
        if len(password) < 8:
            return render_template(
                "register.html",
                error="Password must contain at least 8 characters."
            )

        # Hash the password before storing it
        password_hash = generate_password_hash(password)

        connection = sqlite3.connect("urls.db")

        try:
            connection.execute("""
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            """, (username, email, password_hash))

            connection.commit()

            user = connection.execute("""
                SELECT id, username
                FROM users
                WHERE email = ?
            """, (email,)).fetchone()

            session["user_id"] = user[0]
            session["username"] = user[1]

            return redirect("/")

        except sqlite3.IntegrityError:
            return render_template(
                "register.html",
                error="Username or email already exists."
            )

        finally:
            connection.close()

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            return render_template(
                "login.html",
                error="Please enter your email and password."
            )

        connection = sqlite3.connect("urls.db")

        user = connection.execute("""
            SELECT id, username, email, password_hash
            FROM users
            WHERE email = ?
        """, (email,)).fetchone()

        connection.close()

        # Check whether the account exists
        if user is None:
            return render_template(
                "login.html",
                error="Invalid email or password."
            )

        # Verify the password
        if not check_password_hash(user[3], password):
            return render_template(
                "login.html",
                error="Invalid email or password."
            )

        # Create login session
        session.clear()
        session["user_id"] = user[0]
        session["username"] = user[1]

        return redirect("/")

    return render_template("login.html")

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

@app.route("/dashboard")
@login_required
def dashboard():

    user_id = session["user_id"]

    connection = sqlite3.connect("urls.db")

    # Get the user's URLs and individual click counts
    urls = connection.execute("""
        SELECT
            urls.id,
            urls.original_url,
            urls.short_code,
            urls.created_at,
            urls.expires_at,
            COUNT(click_events.id) AS total_clicks

        FROM urls

        LEFT JOIN click_events
        ON urls.id = click_events.url_id

        WHERE urls.user_id = ?

        GROUP BY
            urls.id,
            urls.original_url,
            urls.short_code,
            urls.created_at,
            urls.expires_at

        ORDER BY urls.id DESC
    """, (user_id,)).fetchall()

    # Calculate total clicks across this user's URLs
    total_clicks = sum(url[5] for url in urls)

    total_links = len(urls)

    connection.close()

    return render_template(
        "dashboard.html",
        urls=urls,
        total_clicks=total_clicks,
        total_links=total_links,
        base_url=request.host_url.rstrip("/")
    )

@app.route("/delete/<int:url_id>", methods=["POST"])
@login_required
def delete_url(url_id):

    user_id = session["user_id"]

    connection = sqlite3.connect("urls.db")

    # Delete only if the URL belongs to the logged-in user
    connection.execute("""
        DELETE FROM urls
        WHERE id = ? AND user_id = ?
    """, (url_id, user_id))

    connection.commit()
    connection.close()

    return redirect("/dashboard")


@app.route("/", methods=["GET" , "POST"])
def home():

    if request.method == "POST":
        url = request.form["url"].strip()

        if not url:
            return render_template("index.html", error="Please enter a URL.")

        if not valid_url(url):
            return render_template("index.html", error="Please enter a valid URL starting with https:// or http://.")

        short_code = gen_short_code()

        while short_code_exists(short_code):
            short_code = gen_short_code()

        user_id = session.get("user_id")
        save_url(url, short_code, user_id)

        short_url = f"http://127.0.0.1:5000/{short_code}"

        return render_template("index.html", short_url=short_url)

        print("Valid URL : ",url)
        print("Short Code : ", short_code)
            
    return render_template("index.html")


@app.route("/<short_code>")
def redirect_url(short_code):

    connection = sqlite3.connect("urls.db")

    # Find the original URL and its database ID
    result = connection.execute("""
        SELECT id, original_url
        FROM urls
        WHERE short_code = ?
    """, (short_code,)).fetchone()

    if result:

        url_id = result[0]
        original_url = result[1]

        # Record this visit
        connection.execute("""
            INSERT INTO click_events
            (url_id, referrer, user_agent)
            VALUES (?, ?, ?)
        """, (
            url_id,
            request.referrer,
            request.user_agent.string
        ))

        connection.commit()
        connection.close()

        return redirect(original_url)

    connection.close()

    return "Short URL not found.", 404

init_db()

if __name__ == "__main__":
    app.run(debug = True)