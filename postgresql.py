import psycopg2

from pipeline import fetch_data


# Database connection parameters
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="mydb",
    user="ray",
    password="abc"
)

cur = conn.cursor()

# Create table
cur.execute("""
    CREATE TABLE IF NOT EXISTS people (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL
    );
""")

# Insert sample data
cur.execute("INSERT INTO people (name) VALUES (%s), (%s)", ("Alice", "Bob"))

# Query data
cur.execute("SELECT * FROM people")
rows = cur.fetchall()

print("Data in 'people' table:")
for row in rows:
    print(row)

# Cleanup
conn.commit()
cur.close()
conn.close()



df = fetch_data()