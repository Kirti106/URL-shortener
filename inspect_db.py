
import sqlite3

connection = sqlite3.connect("urls.db")

print("DATABASE TABLES:")

tables = connection.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
""").fetchall()

for table in tables:
    print("-", table[0])

print("\nUSERS TABLE:")
print(connection.execute(
    "PRAGMA table_info(users)"
).fetchall())

print("\nURL TABLE:")
print(connection.execute(
    "PRAGMA table_info(urls)"
).fetchall())

print("\nEXISTING URL COUNT:")
print(connection.execute(
    "SELECT COUNT(*) FROM urls"
).fetchone()[0])

print("\nUNASSIGNED EXISTING URLS:")
print(connection.execute(
    "SELECT COUNT(*) FROM urls WHERE user_id IS NULL"
).fetchone()[0])

connection.close()