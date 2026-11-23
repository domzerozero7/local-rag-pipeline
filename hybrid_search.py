import psycopg
from psycopg.rows import dict_row

# Database connection settings
DB_URI = 

def setup_hybrid_schema(conn):
    """Adds a tsvector column for native PostgreSQL full-text search."""
    with conn.cursor() as cur:
        # 1. Add generated tsvector column if it doesn't exist
        cur.execute("""
            ALTER TABLE documents 
            ADD COLUMN IF NOT EXISTS fts_content tsvector 
            GENERATED ALWAYS AS (to_tsvector('english', coalesce(content, ''))) STORED;
        """)
        
        # 2. Create a GIN index for lightning-fast keyword searches
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_fts_content ON documents USING gin(fts_content);
        """)
        conn.commit()
        print("Schema updated: Full-Text Search (tsvector + GIN index) ready.")

def hybrid_search(conn, query_text, query_vector, limit=5):
    """Blends Vector Cosine Similarity with Full-Text Keyword Search."""
    sql = """
    WITH vector_matches AS (
        SELECT id, content, 1 - (embedding <=> %s::vector) AS vector_score
        FROM documents
        ORDER BY embedding <=> %s::vector
        LIMIT 20
    ),
    text_matches AS (
        SELECT id, content, ts_rank_cd(fts_content, websearch_to_tsquery('english', %s)) AS text_score
        FROM documents
        WHERE fts_content @@ websearch_to_tsquery('english', %s)
        LIMIT 20
    )
    SELECT 
        COALESCE(v.id, t.id) AS id,
        COALESCE(v.content, t.content) AS content,
        COALESCE(v.vector_score, 0) AS vector_score,
        COALESCE(t.text_score, 0) AS text_score,
        (COALESCE(v.vector_score, 0) + COALESCE(t.text_score, 0)) AS combined_score
    FROM vector_matches v
    FULL OUTER JOIN text_matches t ON v.id = t.id
    ORDER BY combined_score DESC
    LIMIT %s;
    """
    
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(sql, (query_vector, query_vector, query_text, query_text, limit))
        return cur.fetchall()

if __name__ == "__main__":
    # Test connection and schema setup
    with psycopg.connect(DB_URI) as conn:
        setup_hybrid_schema(conn)
