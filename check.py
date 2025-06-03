import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="pose_db",
    user="postgres",
    password="1234"
)

cur = conn.cursor()
cur.execute("SELECT * FROM pose_data LIMIT 5;")
rows = cur.fetchall()
for row in rows:
    print(row)
cur.close()
conn.close()

