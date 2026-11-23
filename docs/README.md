
# Local Production RAG Pipeline

A lightweight, production-grade Retrieval-Augmented Generation (RAG) system built with local tools. This project implements deterministic hybrid search (Vector + Full-Text Search) using PostgreSQL and `pgvector`, with zero high-level framework dependencies (no LangChain or LlamaIndex).

## Deep-Dive Documentation

For detailed specifications and step-by-step engineering breakdowns, refer to the phase documentation:

* [Phase 1: Environment & Storage Foundation (PDF)](./docs/Phase_1_Architecture.pdf) — Architectural overview, schema setup, and local LLM integration.
* [Phase 2: RRF Search & Auth Security (PDF)](./docs/Phase_2_RRF_Implementation.pdf) — Hybrid search query design, UNIX socket peer authentication, and rank fusion math.

---

## System Architecture & Engineering Decisions
### Key Technical Decisions

* **Hybrid Search via Reciprocal Rank Fusion (RRF):**
  Raw vector distance (`pgvector` cosine score) and Full-Text Search scores (`tsvector` term density) operate on incompatible mathematical scales. We execute an RRF query in a PostgreSQL CTE using window functions (`ROW_NUMBER()`):
  $$\text{RRF Score} = \frac{1}{60 + \text{Vector Rank}} + \frac{1}{60 + \text{Text Rank}}$$
  This normalizes disparate database outputs into a predictable position rank before context reaches the LLM.

* **Least-Privilege & Native UNIX Authentication:**
  The application runs under a dedicated, unprivileged database role (`nick`) bound to local UNIX domain socket peer authentication (`/var/run/postgresql/`), enforcing OS-level access controls without exposing network ports or hardcoding admin credentials.

* **Stored Generated TSVector Indexing:**
  Keyword search relies on an automated PostgreSQL generated column (`fts_tokens tsvector GENERATED ALWAYS AS ... STORED`) indexed via GIN. Token generation occurs at the storage layer upon row insertion.

* **Low-Latency Streaming Interface:**
  To optimize Time To First Token (TTFT), the pipeline consumes chunked HTTP response streams directly from the Ollama API, rendering real-time tokens to the console.

---

## Getting Started

### Prerequisites
* PostgreSQL 16+ with `pgvector` extension
* Python 3.12+
* Ollama (`llama3` and `nomic-embed-text` models)

### Setup & Running
1. Clone the repository and navigate to the root:
   ```bash
   cd ~/ai-lab
### Step 3: Save and Exit

1. Press **`Ctrl + O`**, then press **Enter** to save.
2. Press **`Ctrl + X`** to exit `nano`.

