# AI-Powered Vector Search with pgvector

A hands-on demo for the **MLH Global Hack Week Open Source TigerData challenge**. The project stores documents and their semantic embeddings in PostgreSQL, then retrieves relevant results using vector similarity, time ranges, and JSONB metadata filters.

## Features

- **Semantic search:** Generate 384-dimensional embeddings with `sentence-transformers/all-MiniLM-L6-v2`.
- **Vector similarity:** Rank documents using PostgreSQL's `pgvector` cosine distance.
- **Time filtering:** Narrow results by `created_at`.
- **Metadata filtering:** Filter by document category stored in JSONB.
- **Streamlit interface:** Search documents through a simple UI.
- **Optional TimescaleDB support:** Demonstrate hypertables where TimescaleDB is available.
- **Codespaces and CI support:** Run in GitHub Codespaces or use the smoke-test workflow.

## How it works

1. Initialize the PostgreSQL schema and required vector extension.
2. Seed sample documents and generate embeddings.
3. Convert the query text into an embedding.
4. Retrieve the closest vectors, applying optional time and category filters.
5. Display the matching documents in the Streamlit app.

## Run in GitHub Codespaces

1. Open this repository on GitHub and select **Code → Codespaces → Create codespace on main**.
2. Use a PostgreSQL database that supports `pgvector`. For Neon, open the SQL Editor and run:

   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

3. Copy your database connection string from the provider. Use SSL where required.
4. In the Codespaces terminal, set `DATABASE_URL` for the current session:

   ```bash
   read -s -p "Paste DATABASE_URL: " DATABASE_URL; echo
   export DATABASE_URL
   ```

5. Install dependencies, initialize the schema, and seed sample data:

   ```bash
   pip install -r requirements.txt
   python init_db.py
   python seed.py
   ```

6. Start the app:

   ```bash
   streamlit run app.py
   ```

7. Open forwarded port `8501` from the Codespaces **Ports** tab.

Keep the terminal session open while using the app so the environment variable remains available. Do not commit your connection string or paste it into public issues. For repeat use, store it as a Codespaces secret and load it securely into the terminal.

> **Note:** Some Codespaces environments cannot run Docker-in-Docker. Using a hosted PostgreSQL service with `pgvector` avoids that dependency. TimescaleDB is optional for ordinary time filtering; it is only required for the hypertable demonstration.

## Validate with GitHub Actions

When Codespaces usage is unavailable, you can run the **Vector search smoke test** workflow:

1. Open **Actions → Vector search smoke test**.
2. Select **Run workflow** and choose the `main` branch.
3. Open the workflow run and inspect **Verify documents and vector search**.

The workflow starts a temporary PostgreSQL service with `pgvector`, initializes the schema, creates sample embeddings, and runs a semantic search query. Its database is temporary and is removed when the run finishes. This workflow does not publish a permanent dashboard or connect to a remote Neon database.

## Run locally

### Requirements

- Python 3.10 or later
- Docker Desktop with Docker Compose
- A working internet connection for the first model download

### Start the database and application

```bash
docker compose up -d
python -m venv .venv
```

Activate the virtual environment:

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

Then install dependencies and launch the app:

```bash
pip install -r requirements.txt
python init_db.py
python seed.py
streamlit run app.py
```

The local Compose setup uses this development connection string by default:

```text
postgresql://postgres:postgres@localhost:5432/vector_demo
```

Use these credentials only for the local demo. For a hosted or public deployment, configure a secure database URL through environment variables or your hosting provider's secret manager.

## SQL query pattern

The core search pattern combines cosine distance with time and category filters:

```sql
SELECT
    id,
    created_at,
    content,
    metadata->>'category' AS category,
    1 - (embedding <=> :query_embedding::vector) AS cosine_similarity
FROM documents
WHERE created_at >= :start_time
  AND created_at < :end_time
  AND (:category = 'all' OR metadata->>'category' = :category)
ORDER BY embedding <=> :query_embedding::vector
LIMIT :top_k;
```

The `<=>` operator returns cosine distance. Lower distance means a closer vector match; the example converts distance to a similarity-style score using `1 - cosine_distance`.

## Project structure

| File | Purpose |
| --- | --- |
| `app.py` | Streamlit search interface |
| `init_db.py` | Creates the extension, tables, hypertable where supported, and indexes |
| `seed.py` | Inserts sample documents and their embeddings |
| `docker-compose.yml` | Defines the local database service |
| `requirements.txt` | Python dependencies |
| `.devcontainer/devcontainer.json` | GitHub Codespaces configuration |

## Troubleshooting

- **`vector` extension is missing:** Confirm the database supports `pgvector`, then run `CREATE EXTENSION IF NOT EXISTS vector;`.
- **Database connection fails:** Check `DATABASE_URL`, database status, SSL requirements, and network access.
- **The embedding model fails to download:** Ensure the environment has internet access; the model is downloaded on first use.
- **TimescaleDB is unavailable:** Standard PostgreSQL with `pgvector` still supports the basic time-filtered search. Only the hypertable feature requires TimescaleDB.
- **No results appear:** Run `python seed.py` after initializing the schema, then widen the selected time range. The seed script replaces its own sample rows rather than duplicating them.

## Submission checklist

- [ ] Connect to a working PostgreSQL database with `pgvector`.
- [ ] Initialize the schema and confirm the sample rows are present.
- [ ] Test semantic search and time/category filters.
- [ ] Capture a screenshot of the running app or query results.
- [ ] Submit the repository or screenshot on the MLH challenge page.

## References

- [Tiger Data: Refining vector search queries with time filters](https://www.tigerdata.com/blog/refining-vector-search-queries-with-time-filters-in-pgvector-a-tutorial)
- [Tiger Data documentation](https://www.tigerdata.com/docs)
- [pgvector on GitHub](https://github.com/pgvector/pgvector)
- [MLH Global Hack Week challenge](https://www.mlh.com/events/global-hack-week-open-source-90/challenges/ghwHF1026-tigerdata-pgvector)
