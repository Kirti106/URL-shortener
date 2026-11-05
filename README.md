# 🔗 URL Shortener

A simple and lightweight URL Shortener web application built using Python and Flask. 
The application converts long URLs into short, unique links that redirect users to the original URL.

---

## 📌 Project Description

The URL Shortener allows users to enter a long URL and generate a unique short URL.

The original URL and its generated short code are stored in an SQLite database. 
When a user accesses the short URL, the application searches the database for the corresponding original URL and redirects the user to it.

---

## ✨ Features

- Enter a long URL
- Validate URL input
- Generate a unique 6-character short code
- Store URL mappings in SQLite
- Display the generated short URL
- Redirect short URLs to the original URL
- Handle invalid or empty URLs
- Handle unknown short URLs with a 404 response
- Copy generated short URL to clipboard
- Simple and responsive user interface

---

## 🛠️ Technologies Used

### Backend
- **Python** – Main programming language
- **Flask** – Web framework used to build the application

### Database
- **SQLite** – Stores the original URLs and their corresponding short codes

### Frontend
- **HTML** – Structure of the webpage
- **CSS** – Styling and responsive design

---

## 🧠 Approach

The application follows a simple URL mapping approach.

1. The user enters a long URL.
2. Flask receives the URL through a POST request.
3. The URL is validated to ensure that it uses HTTP or HTTPS.
4. A random 6-character alphanumeric short code is generated.
5. The application checks whether the generated code already exists.
6. The URL and short code are stored in the SQLite database.
7. The generated short URL is displayed to the user.
8. When the short URL is accessed, Flask searches the database using the short code.
9. The corresponding original URL is retrieved.
10. The user is redirected to the original URL.

---

## 🔄 Application Workflow

```text
User enters long URL
        ↓
URL validation
        ↓
Generate short code
        ↓
Check code uniqueness
        ↓
Store URL + code in SQLite
        ↓
Display short URL
        ↓
User opens short URL
        ↓
Search database
        ↓
Retrieve original URL
        ↓
Redirect to original URL

```
---

## 🚀 Future Improvements

Possible future improvements include:

- Short URLs directly copied 
- Custom short URLs
- URL expiration
- Click statistics
- QR code generation
- User authentication
- URL history
- Analytics dashboard
- Online deployment

---

## Author

Kirti
