
import sqlite3

connection = sqlite3.connect("urls.db")

try:
    connection.execute("PRAGMA foreign_keys = ON")

    # 1. Create the users table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. Check existing URL columns
    existing_columns = {
        column[1]
        for column in connection.execute(
            "PRAGMA table_info(urls)"
        ).fetchall()
    }

    # 3. Add an optional owner to each URL
    if "user_id" not in existing_columns:
        connection.execute("""
            ALTER TABLE urls
            ADD COLUMN user_id INTEGER
            REFERENCES users(id)
            ON DELETE SET NULL
        """)
        print("Added user_id column to urls.")

    # 4. Make user URL lookups faster
    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_urls_user_id
        ON urls(user_id)
    """)

    connection.commit()
    print("\nAuthentication database setup successful!")

except Exception as error:
    connection.rollback()
    print("Migration failed:", error)

finally:
    connection.close()