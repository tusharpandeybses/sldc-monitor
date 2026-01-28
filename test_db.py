import psycopg2, os
conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()
cur.execute("SELECT now()")
print("✅ Connected:", cur.fetchone())
conn.close()
