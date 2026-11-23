import os
import psycopg
from pgvector.psycopg import register_vector
import urllib.request
import json

def get_embedding(text):
    url = "http://127.0.0.1:11434/api/embeddings"
    payload = json.dumps({"model": "nomic-embed-text", "prompt": text}).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        return result['embedding']

documents = [
    "PostgreSQL utilizes SCRAM-SHA-256 password hashing for secure database authentication.",
    "BJJ and martial arts training demand high physical conditioning and technical precision.",
    "Enterprise HRIS platforms streamline payroll processing and employee onboarding workflows.",
    "Tailscale constructs secure, zero-trust WireGuard mesh networks across distributed hosts."
]

print("Connecting to vector_db on lab-host...")
DB_DSN = os.getenv(
    "VECTOR_DB_DSN",
    "host=localhost dbname=vector_db user=ai_user",
)
conn = psycopg.connect(DB_DSN)
register_vector(conn)
with conn.cursor() as cur:
    # 1. Create permanent table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS document_embeddings (
            id serial PRIMARY KEY,
            content text UNIQUE,
            embedding vector(768)
        );
    """)
    
    # 2. Create HNSW index for ultra-fast vector similarity search
    print("Ensuring HNSW index exists on vector column...")
    cur.execute("""
        CREATE INDEX IF NOT EXISTS document_embeddings_hnsw_idx 
        ON document_embeddings 
        USING hnsw (embedding vector_cosine_ops);
    """)
    conn.commit()

    # 3. Populate persistent database
    print("[PERSISTENCE] Checking and inserting document embeddings...")
    for doc in documents:
        vec = get_embedding(doc)
        cur.execute("""
            INSERT INTO document_embeddings (content, embedding) 
            VALUES (%s, %s) 
            ON CONFLICT (content) DO NOTHING;
        """, (doc, vec))
    conn.commit()

conn.close()
