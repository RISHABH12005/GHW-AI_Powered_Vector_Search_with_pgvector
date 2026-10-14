import os
from datetime import datetime, timedelta, timezone

import pandas as pd
import psycopg
import streamlit as st
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer

DB_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/vector_demo')
MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'
st.set_page_config(page_title='TigerData Vector Search', page_icon='🔎', layout='wide')
st.title('AI-Powered Vector Search')
st.caption('Semantic search with PostgreSQL, pgvector, timestamps, and JSON metadata.')

@st.cache_resource
def load_model():
    return SentenceTransformer(MODEL_NAME)

def connect_database():
    conn = psycopg.connect(DB_URL, connect_timeout=8)
    register_vector(conn)
    return conn

with st.sidebar:
    st.header('Search filters')
    days = st.slider('Look back (days)', min_value=1, max_value=180, value=90)
    category = st.selectbox('Category', ['all', 'ai', 'security', 'database', 'devops'])
    top_k = st.slider('Number of results', min_value=1, max_value=10, value=5)

query = st.text_input('Search by meaning', 'How can I secure an API?')
if st.button('Search documents', type='primary'):
    if not query.strip():
        st.warning('Enter a search query.')
        st.stop()
    with st.spinner('Embedding query and searching PostgreSQL...'):
        try:
            embedding = load_model().encode(query.strip(), normalize_embeddings=True).tolist()
            end = datetime.now(timezone.utc)
            start = end - timedelta(days=days)
            sql = '''
                SELECT id, created_at, content, metadata->>'category' AS category,
                       1 - (embedding <=> %s) AS cosine_similarity
                FROM documents
                WHERE created_at >= %s AND created_at < %s
                  AND (%s = 'all' OR metadata->>'category' = %s)
                ORDER BY embedding <=> %s
                LIMIT %s
            '''
            with connect_database() as conn:
                rows = conn.execute(sql, (embedding, start, end, category, category, embedding, top_k)).fetchall()
        except Exception as exc:
            st.error(f'Search failed: {exc}')
            st.caption('Check DATABASE_URL and SSL settings, enable pgvector, then run python init_db.py and python seed.py.')
            st.stop()
    if not rows:
        st.info('No matches found. Try a longer time range or choose another category.')
    else:
        st.success(f'Found {len(rows)} matching documents')
        df = pd.DataFrame(rows, columns=['ID', 'Timestamp', 'Content', 'Category', 'Cosine similarity'])
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], utc=True).dt.strftime('%Y-%m-%d %H:%M UTC')
        df['Cosine similarity'] = df['Cosine similarity'].astype(float).round(4)
        st.dataframe(df, use_container_width=True, hide_index=True)
        for row in rows:
            with st.expander(f'{row[3]} · similarity {float(row[4]):.3f} · {row[1].strftime('%Y-%m-%d')}'):
                st.write(row[2])
else:
    st.info('Click Search documents to query the database.')
    st.markdown('Try: How can I secure an API? · Explain vector search · How do hypertables work?')

with st.expander('Database status'):
    try:
        with connect_database() as conn:
            extensions = conn.execute("SELECT extname, extversion FROM pg_extension WHERE extname IN ('vector', 'timescaledb') ORDER BY extname").fetchall()
            count = conn.execute('SELECT count(*) FROM documents').fetchone()[0]
        st.write('Enabled extensions:', extensions)
        st.metric('Documents in database', count)
    except Exception as exc:
        st.error(f'Database unavailable: {exc}')
        st.caption('Start PostgreSQL or set DATABASE_URL, then run init_db.py and seed.py.')
