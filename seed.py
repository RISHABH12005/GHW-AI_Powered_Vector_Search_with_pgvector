import os
from datetime import datetime, timedelta, timezone
import psycopg
from psycopg.types.json import Jsonb
from sentence_transformers import SentenceTransformer

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/vector_demo")
SAMPLES = [
    ("Use parameterized queries and least-privilege credentials to secure an API.", "security", 1),
    ("A vector database ranks documents by embedding distance to a query embedding.", "ai", 2),
    ("Use Docker Compose to run PostgreSQL locally with repeatable configuration.", "devops", 4),
    ("Rate limiting and request validation reduce abuse of public APIs.", "security", 7),
    ("Time-series hypertables partition records into chunks based on time.", "database", 12),
    ("Cosine distance compares the direction of two embedding vectors.", "ai", 18),
    ("Store event timestamps in UTC and filter with an explicit time window.", "database", 24),
    ("Continuous integration runs tests automatically when code changes.", "devops", 30),
    ("Retrieval augmented generation grounds language model responses in retrieved context.", "ai", 45),
    ("Rotate database passwords and never commit secrets to source control.", "security", 60),
    ("PostgreSQL JSONB supports flexible metadata filters in SQL queries.", "database", 90),
    ("Monitor latency, errors, and resource usage after deployment.", "devops", 120),
]

def main():
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    vectors = model.encode([item[0] for item in SAMPLES], normalize_embeddings=True).tolist()
    now = datetime.now(timezone.utc)
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            for (content, category, days_ago), vector in zip(SAMPLES, vectors):
                cur.execute("INSERT INTO documents (created_at, content, metadata, embedding) VALUES (%s, %s, %s, %s::vector)", (now - timedelta(days=days_ago), content, Jsonb({"category": category, "source": "sample"}), vector))
        conn.commit()
    print(f"Inserted {len(SAMPLES)} sample documents.")

if __name__ == "__main__":
    main()
