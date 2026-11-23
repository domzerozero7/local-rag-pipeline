HEAD
# local-rag-pipeline
Local AI RAG pipeline 

# Local Production RAG Pipeline

A local Retrieval-Augmented Generation (RAG) system built without heavy orchestration frameworks across two Ubuntu nodes, combining vector similarity and full-text search in PostgreSQL with local Ollama inference.

## Deep-Dive Documentation

For detailed specifications and step-by-step engineering breakdowns, refer to the project documentation:

* [Phase 1: Environment & Storage Foundation (PDF)](./docs/Phase_1_Architecture.pdf)[cite: 11]
* [Phase 2: RRF Search & Auth Security (PDF)](./docs/Phase_2_RRF_Implementation.pdf)[cite: 11]

---

## System Architecture & Engineering Decisions

```text
+-------------------------------------------------------------------+
| Node01 (HP 15-bs234wm, Pentium N5000, 4GB)                        |
|  Document Ingest (Chunker + SHA-256 + nomic-embed-text)           |
+---------------------------------+---------------------------------+
                                  | Tailscale Mesh + UFW
                                  v
+-------------------------------------------------------------------+
| Node00 (HP Pavilion x360, i5, 8GB)                                |
|  PostgreSQL 16 (pgvector HNSW + fts_tokens GIN + RRF CTE k=60)    |
+---------------------------------+---------------------------------+
                                  | Pooled Connection / Context Cap
                                  v
+-------------------------------------------------------------------+
| Node01 (Ollama / llama3.2:3b + Streaming Output)                  |
|  Local Query & Response Generation                                |
+-------------------------------------------------------------------+
(Initial commit: local RAG pipeline scripts and docs)
