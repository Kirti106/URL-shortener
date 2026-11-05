
import sqlite3

connection = sqlite3.connect("urls.db")

try:
    connection.execute("PRAGMA foreign_keys = ON")

    # Check the columns that already exist
    existing_columns = {
        column[1]
        for column in connection.execute(
            "PRAGMA table_info(urls)"
        ).fetchall()
    }

    # Add creation timestamp
    if "created_at" not in existing_columns:
        connection.execute("""
            ALTER TABLE urls
            ADD COLUMN created_at TEXT
        """)
        print("Added created_at column.")

    # Add optional expiry timestamp
    if "expires_at" not in existing_columns:
        connection.execute("""
            ALTER TABLE urls
            ADD COLUMN expires_at TEXT
        """)
        print("Added expires_at column.")

    # Give existing links a creation timestamp
    connection.execute("""
        UPDATE urls
        SET created_at = CURRENT_TIMESTAMP
        WHERE created_at IS NULL
    """)

    # Create a table to track link visits
    connection.execute("""
        CREATE TABLE IF NOT EXISTS click_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url_id INTEGER NOT NULL,
            clicked_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            referrer TEXT,
            user_agent TEXT,
            FOREIGN KEY (url_id)
                REFERENCES urls(id)
                ON DELETE CASCADE
        )
    """)

    # Make analytics queries faster
    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_click_events_url_id
        ON click_events(url_id)
    """)

    connection.commit()

    print("\nDatabase migration successful!")

except Exception as error:
    connection.rollback()
    print("Migration failed:", error)

finally:
    connection.close()