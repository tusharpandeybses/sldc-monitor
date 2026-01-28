import psycopg2

DB_URL = "postgresql://postgres.utjfbgmdgphfdgorvlvp:BsesYamuna%4012345%24@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"

conn = psycopg2.connect(DB_URL)
cur = conn.cursor()
cur.execute("select now();")
print("✅ Connected:", cur.fetchone())
conn.close()
