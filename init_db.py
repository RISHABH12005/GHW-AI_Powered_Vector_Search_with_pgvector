import os
import psycopg

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/vector_demo")

with psycopg.connect(DB_URL, autocommit=True) as conn:
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    has_timescale = conn.execute("SELECT EXISTS (SELECT 1 FROM pg_available_extensions WHERE name = 'timescaledb')").fetchone()[0]
    if has_timescale:
        conn.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id BIGSERIAL PRIMARY KEY,
            created_at TIMESTAMPTZ NOT NULL,
            content TEXT NOT NULL,
            metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
            embedding VECTOR(384) NOT NULL
        );
    """)
    if has_timescale:
        conn.execute("""
            SELECT create_hypertable(
                'documents', by_range('created_at', INTERVAL '7 days'),
                if_not_exists => TRUE, migrate_data => TRUE
            );
        """)
    conn.execute("CREATE INDEX IF NOT EXISTS documents_embedding_hnsw ON documents USING hnsw (embedding vector_cosine_ops);")
    conn.execute("CREATE INDEX IF NOT EXISTS documents_metadata_category ON documents ((metadata->>'category'));")
    conn.execute("CREATE INDEX IF NOT EXISTS documents_created_at ON documents (created_at DESC);")
    enabled = conn.execute("SELECT extname, extversion FROM pg_extension WHERE extname IN ('vector', 'timescaledb') ORDER BY extname").fetchall()
    print("Schema ready. Enabled extensions:", enabled)
