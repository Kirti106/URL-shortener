from flask import Flask, render_template, request, redirect
from urllib.parse import urlparse

import random
import string

import sqlite3


app = Flask(__name__)

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

def save_url(original_url, short_code):
    connection = sqlite3.connect("urls.db")

    connection.execute(
        "INSERT INTO urls (original_url , short_code) VALUES (?,?)", (original_url, short_code)
    )

    connection.commit()
    connection.close()

def short_code_exists(short_code):
    connection = sqlite3.connect("urls.db")

    result = connection.execute("SELECT id FROM urls WHERE short_code = ?", (short_code,)).fetchone()

    connection.close()
    return result is not None


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

        save_url(url, short_code)

        short_url = f"http://127.0.0.1:5000/{short_code}"

        return render_template("index.html", short_url=short_url)

        print("Valid URL : ",url)
        print("Short Code : ", short_code)
            
    return render_template("index.html")

@app.route("/<short_code>")
def redirect_url(short_code):
    connection = sqlite3.connect("urls.db")

    result = connection.execute("SELECT original_url FROM urls WHERE short_code = ?", (short_code,)).fetchone()

    connection.close()

    if result:
        return redirect(result[0])

    return "Short URL not found." , 404

init_db()

if __name__ == "__main__":
    app.run(debug = True)