from flask import Flask, render_template, request
from urllib.parse import urlparse

app = Flask(__name__)

def valid_url(url):
    try:
        result = urlparse(url)

        return result.scheme in ["http", "https"] and bool(result.netloc)

    except Exception:
        return False

@app.route("/", methods=["GET" , "POST"])
def home():

    if request.method == "POST":
        url = request.form["url"].strip()

        if not url:
            return render_template("index.html", error="Please enter a URL.")

        if not valid_url(url):
            return render_template("index.html", error="Please enter a valid URL starting with https:// or http://.")

        print("Valid URL : ",url)
            
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug = True)