import os
import psycopg
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer

url = os.environ["DATABASE_URL"]
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
query = "How can I secure an API?"
vector = model.encode(query, normalize_embeddings=True).tolist()
with psycopg.connect(url) as conn:
    register_vector(conn)
    total = conn.execute("SELECT count(*) FROM documents").fetchone()[0]
    rows = conn.execute(
        """
        SELECT content, metadata->>'category' AS category,
               1 - (embedding <=> %s) AS similarity
        FROM documents
        ORDER BY embedding <=> %s
        LIMIT 5
        """,
        (vector, vector)
    ).fetchall()
print(f"Seeded document count: {total}")
print("Top semantic matches:")
for content, category, score in rows:
    print(f"- [{category}] similarity={float(score):.4f}: {content}")
if total < 10 or not rows:
    raise SystemExit("Smoke test failed: expected at least 10 documents and search results.")
print("PASS: pgvector semantic search returned results.")
