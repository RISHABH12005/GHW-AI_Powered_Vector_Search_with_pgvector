# AI-Powered Vector Search with pgvector

A demo project for the MLH Global Hack Week Open Source TigerData challenge. It stores text documents, semantic embeddings, timestamps, and JSON metadata in PostgreSQL, then ranks results by vector similarity while filtering by time and metadata.

## Features

- Semantic embeddings generated with `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions).
- PostgreSQL `pgvector` cosine-distance search, using the official Python adapter.
- Time filtering using `created_at`.
- JSONB metadata filters (category).
- Optional TimescaleDB hypertable support.
- Streamlit UI and SQL example.
- GitHub Codespaces configuration.

## Run in GitHub Codespaces

1. Open this repository and select **Code → Codespaces → Create codespace on main**.
2. For Neon, open the project SQL Editor and run `CREATE EXTENSION IF NOT EXISTS vector;`. In **Connect**, copy the pooled or direct connection string with SSL enabled.
4. In the Codespaces terminal, set the URL for the current terminal session: `read -s -p "Paste DATABASE_URL: " DATABASE_URL; echo; export DATABASE_URL`. Do not commit this value or paste it into public issues.
5. Run `pip install -r requirements.txt`, `python init_db.py`, `python seed.py`, then `streamlit run app.py`.
6. Open forwarded port `8501` from the **Ports** tab. Keep the same terminal open so `DATABASE_URL` remains set.

> Codespaces environments do not always support running Docker-in-Docker. If Docker Compose is unavailable (as in many Codespaces), use hosted PostgreSQL with `pgvector`. Neon supports pgvector; use its connection string with SSL enabled. For a persistent setup, add `DATABASE_URL` as a Codespaces repository or environment secret and load it into the terminal before running commands. TimescaleDB is optional for basic time filtering, but required to demonstrate a hypertable specifically.


## Run without Codespaces (GitHub Actions)

If your Codespaces free usage is exhausted, you can validate the project through the **Vector search smoke test** workflow. It starts a temporary PostgreSQL service with pgvector, installs dependencies, initializes the schema, generates sample embeddings, and runs a semantic search query. The database is temporary and is deleted when the workflow finishes.

1. Open **Actions → Vector search smoke test**.
2. Click **Run workflow** and choose `main`.
3. Open the run and inspect **Verify documents and vector search** for the seeded document count and top matches.

This workflow tests the application’s database/embedding/search path. It does not publish a permanent dashboard or use a remote Neon database. The Streamlit UI can be launched locally with `streamlit run app.py`, or deployed separately to a hosting provider with a secure `DATABASE_URL` secret.

## Run locally

Requirements: Python 3.10+, Docker Desktop, Docker Compose.

```bash
docker compose up -d
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python init_db.py
python seed.py
streamlit run app.py
```

The local-only default database URL is `postgresql://postgres:postgres@localhost:5432/vector_demo`. Do not use these credentials for a production/public database.

## SQL query pattern

```sql
SELECT id, created_at, content, metadata->>'category' AS category,
       1 - (embedding <=> :query_embedding::vector) AS cosine_similarity
FROM documents
WHERE created_at >= :start_time
  AND created_at < :end_time
  AND (:category = 'all' OR metadata->>'category' = :category)
ORDER BY embedding <=> :query_embedding::vector
LIMIT :top_k;
```

A lower cosine distance means a closer vector match; similarity is calculated as `1 - cosine_distance`.

## Repository files

- `app.py` — Streamlit search UI.
- `init_db.py` — extension, table, hypertable, and index setup.
- `seed.py` — sample documents and embeddings.
- `docker-compose.yml` — disposable local database.
- `requirements.txt` — Python dependencies.
- `.devcontainer/devcontainer.json` — Codespaces defaults.

## Troubleshooting

- **Extension missing:** Confirm the database supports `pgvector`; execute `CREATE EXTENSION vector;`.
- **Connection refused:** Check `DATABASE_URL`, database status, and port/SSL requirements.
- **Model download issue:** The first run downloads the Sentence Transformers model and needs internet access.
- **TimescaleDB not installed:** Basic filtering still works on PostgreSQL with pgvector; hypertable conversion requires TimescaleDB.
- **No search results:** Run `python seed.py` after initialization and widen the look-back filter. The seed script replaces its own sample rows, so rerunning it will not duplicate the sample dataset.

## Submission checklist

- [ ] Run against a real PostgreSQL/pgvector database.
- [ ] Confirm seeded rows and run semantic search.
- [ ] Demonstrate time and category filtering in the UI.
- [ ] Capture a screenshot of the running app and/or database query output.
- [ ] Submit this repository URL or screenshot on the MLH challenge page.

## References

- [Tiger Data: Refining vector search queries with time filters](https://www.tigerdata.com/blog/refining-vector-search-queries-with-time-filters-in-pgvector-a-tutorial)
- [Tiger Data documentation](https://www.tigerdata.com/docs)
- [pgvector](https://github.com/pgvector/pgvector)
- [MLH challenge](https://www.mlh.com/events/global-hack-week-open-source-90/challenges/ghwHF1026-tigerdata-pgvector)
