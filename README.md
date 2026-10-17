# AI-Powered Document Search

This project helps you find useful information from documents by searching for their **meaning**, not just exact words.

For example, if a document talks about keeping the environment clean, you could search for “ways to reduce pollution” and still find it—even if those exact words are not in the document.

Built for the **MLH Global Hack Week Open Source challenge** using TigerData and PostgreSQL.

## What can it do?

- Find documents related to what you type.
- Narrow results to a particular time period.
- Filter results by category.
- Show results in a simple web interface.
- Run in GitHub Codespaces or on your own computer.

## How it works

1. The project loads a small collection of sample documents.
2. It prepares each document so the app can compare its meaning with your search.
3. You enter a question or phrase.
4. The app finds and displays the most relevant documents, with optional date and category filters.

## Getting started

The easiest way to try the project is to open it in **GitHub Codespaces**:

1. Open this repository on GitHub.
2. Select **Code → Codespaces → Create codespace on main**.
3. Connect the project to a PostgreSQL database that supports vector search. You can use a hosted option such as Neon.
4. Follow the setup steps below in the Codespaces terminal.

Install the required packages and prepare sample data:

```bash
pip install -r requirements.txt
python init_db.py
python seed.py
```

Start the app:

```bash
streamlit run app.py
```

When it starts, open port **8501** from the Codespaces **Ports** tab to view the web app.

**Note:** The database connection must be configured before running the setup commands. Keep it private—never publish your database password or connection string in your repository.

## Run it on your computer

You will need Python 3.10 or later and Docker Desktop with Docker Compose installed.

```bash
docker compose up -d
python -m venv .venv
```

Activate the environment:

- **Windows PowerShell:** `.venv\Scripts\Activate.ps1`
- **macOS/Linux:** `source .venv/bin/activate`

Then run:

```bash
pip install -r requirements.txt
python init_db.py
python seed.py
streamlit run app.py
```

## Main project files

- `app.py` — the web interface where you search.
- `init_db.py` — prepares the database.
- `seed.py` — adds sample documents.
- `docker-compose.yml` — starts the local database.
- `requirements.txt` — lists the software packages the project needs.

## Troubleshooting

- **The app cannot connect to the database:** Check that the database is running and the connection details are correct.
- **No results appear:** Run the setup commands again, including `python seed.py`, to add the sample documents.
- **The first search is slow:** The app may be downloading its language model for the first time.
- **Local setup is difficult:** Try GitHub Codespaces with a hosted PostgreSQL database instead.

## Learn more

- [TigerData tutorial on improving document search](https://www.tigerdata.com/blog/refining-vector-search-queries-with-time-filters-in-pgvector-a-tutorial)
- [TigerData documentation](https://www.tigerdata.com/docs)
- [pgvector project](https://github.com/pgvector/pgvector)
- [MLH Global Hack Week challenge](https://www.mlh.com/events/global-hack-week-open-source-90/challenges/ghwHF1026-tigerdata-pgvector)
