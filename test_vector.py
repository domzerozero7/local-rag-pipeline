import psycopg
from pgvector.psycopg import register_vector
import numpy as np

# Connect using ai_user credentials on lab-host
conn = psycopg.connect("host=localhost dbname=vector_db user=ai_user password=Password123")
register_vector(conn)

with conn.cursor() as cur:
    # Set up temporary schema
    cur.execute("CREATE TEMP TABLE py_vectors (id serial PRIMARY KEY, embedding vector(3));")
    
    # Insert a sample numpy vector
    sample_vec = np.array([1.5, 2.5, 3.5])
    cur.execute("INSERT INTO py_vectors (embedding) VALUES (%s);", (sample_vec,))
    
    # Query vector back
    cur.execute("SELECT embedding FROM py_vectors;")
    result = cur.fetchone()[0]
    
    print(f"\n[SUCCESS] Successfully written and retrieved vector via Python: {result}\n")

conn.close()
