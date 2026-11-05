import sqlite3

connection = sqlite3.connect("urls.db")

users = connection.execute("""
    SELECT id, username, email, password_hash, created_at
    FROM users
""").fetchall()

print("REGISTERED USERS:")

for user in users:
    print("\nUser ID:", user[0])
    print("Username:", user[1])
    print("Email:", user[2])
    print("Password Hash:", user[3])
    print("Created At:", user[4])

connection.close()