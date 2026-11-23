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

print("Connecting to vector_db on lab...")
DB_DSN = os.getenv(
    "VECTOR_DB_DSN",
    "host=localhost dbname=vector_db user=user",
)
conn = psycopg.connect(DB_DSN)
register_vector(conn)

with conn.cursor() as cur:
    cur.execute("CREATE TEMP TABLE knowledge_base (id serial PRIMARY KEY, content text, embedding vector(768));")
    
    print("[INGESTION] Generating local Ollama embeddings and writing to pgvector...")
    for doc in documents:
        vec = get_embedding(doc)
        cur.execute("INSERT INTO knowledge_base (content, embedding) VALUES (%s, %s);", (doc, vec))
    conn.commit()

    user_query = "How do I secure my database logins?"
    print(f"[QUERY]: '{user_query}'")
    
    query_vec = get_embedding(user_query)
    
    cur.execute("""
        SELECT content, embedding <=> %s::vector AS distance 
        FROM knowledge_base 
        ORDER BY distance ASC 
        LIMIT 1;
    """, (query_vec,))
    
    match, distance = cur.fetchone()
    print(f"[BEST MATCH]: {match}")
    print(f"[DISTANCE]: {distance:.4f} (Lower distance = higher conceptual similarity)")

conn.close()
