import psycopg
import requests

# 1. Connect to local PostgreSQL
conn = psycopg.connect("dbname=vector_db user=nick")
cur = conn.cursor()

# 2. Define Query
user_query = "SCRAM-SHA-256"

# 3. Generate Query Embedding via Ollama
embed_response = requests.post(
    "http://localhost:11434/api/embeddings",
    json={"model": "nomic-embed-text", "prompt": user_query}
)
query_embedding = embed_response.json()["embedding"]

# 4. Execute RRF Hybrid Search
rrf_sql = """
WITH vector_search AS (
    SELECT 
        id, 
        content, 
        ROW_NUMBER() OVER (ORDER BY embedding <=> %s::vector) AS v_rank
    FROM document_embeddings
    LIMIT 10
),
text_search AS (
    SELECT 
        id, 
        content, 
        ROW_NUMBER() OVER (ORDER BY ts_rank_cd(fts_tokens, plainto_tsquery('english', %s)) DESC) AS t_rank
    FROM document_embeddings
    WHERE fts_tokens @@ plainto_tsquery('english', %s)
    LIMIT 10
)
SELECT 
    COALESCE(v.id, t.id) AS id,
    COALESCE(v.content, t.content) AS content,
    COALESCE(v.v_rank, 0) AS v_rank,
    COALESCE(t.t_rank, 0) AS t_rank,
    (COALESCE(1.0 / (60 + v.v_rank), 0.0) + COALESCE(1.0 / (60 + t.t_rank), 0.0)) AS rrf_score
FROM vector_search v
FULL OUTER JOIN text_search t ON v.id = t.id
ORDER BY rrf_score DESC
LIMIT 1;
"""

cur.execute(rrf_sql, (query_embedding, user_query, user_query))
result = cur.fetchone()

if result:
    doc_id, content, v_rank, t_rank, rrf_score = result
    print(f"\n[USER QUERY]: '{user_query}'")
    print(f"[RETRIEVED CONTEXT]: {content}")
    print(f"[VECTOR RANK]: {v_rank} | [TEXT RANK]: {t_rank} | [RRF SCORE]: {rrf_score:.4f}\n")

    # 5. Pass Context to Ollama (llama3)
    prompt = f"Answer the question based ONLY on the provided context below.\n\nContext: {content}\n\nQuestion: {user_query}"
    
    print("[GENERATING RESPONSE VIA LLM]...\n")
    llm_response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "llama3", "prompt": prompt, "stream": False}
    )
    print(f"[LLM RESPONSE]:\n{llm_response.json()['response']}")
else:
    print("No relevant context found.")

cur.close()
conn.close()

