import psycopg2

def create_table():
    conn = None
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="pose_db",
            user="postgres",
            password="1234"
        )
        cur = conn.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS pose_api_posedata (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(100),
            timestamp TIMESTAMP,
            pose_json JSONB
        );
        """
        cur.execute(create_table_query)
        conn.commit()
        print("Table pose_api_posedata created successfully.")
        cur.close()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_table()

