# AI-Powered Vector Search with pgvector

A demo project for the MLH Global Hack Week Open Source TigerData challenge. It stores text documents, semantic embeddings, timestamps, and JSON metadata in PostgreSQL, then ranks results by vector similarity while filtering by time and metadata.

## Features

- Semantic embeddings generated with `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions).
- PostgreSQL `pgvector` cosine-distance search.
- Time filtering using `created_at`.
- JSONB metadata filters (category).
- Optional TimescaleDB hypertable support.
- Streamlit UI and SQL example.
- GitHub Codespaces configuration.

## Run in GitHub Codespaces

1. Open this repository and select **Code → Codespaces → Create codespace on main**.
2. In the Codespaces terminal, install dependencies: `pip install -r requirements.txt`.
3. Set `DATABASE_URL` to a PostgreSQL database that has `pgvector` enabled. The default points at the local Docker Compose service.
4. If Docker is available in the Codespace, run `docker compose up -d`, then `python init_db.py`, `python seed.py`, and `streamlit run app.py`.
5. Open forwarded port `8501` from the **Ports** tab.

> Codespaces environments do not always support running Docker-in-Docker. If Docker Compose is unavailable, use hosted PostgreSQL with `pgvector`; set `DATABASE_URL` in your Codespaces secrets. TimescaleDB is optional for basic time filtering, but required to demonstrate a hypertable specifically.

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
- **No search results:** Run `python seed.py` after initialization and widen the look-back filter.

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
