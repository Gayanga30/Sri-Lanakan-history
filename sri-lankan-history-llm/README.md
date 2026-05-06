# Sri Lankan History LLM

A retrieval-augmented chatbot that answers questions about Sri Lankan history using sources you control. The model brain is Google Gemini (free tier). Embeddings, vector search, and the web UI all run locally with free tools.

## How it works

1. **You drop sources** (PDFs, HTML, text) into `sources/`.
2. `ingest.py` chunks the text, embeds it with a local model, and stores the result in a Chroma database under `vectorstore/`.
3. `app.py` runs a Streamlit chat. Each question is embedded, the closest chunks are pulled from Chroma, and the chunks plus the question go to Gemini, which writes the answer with citations.

## Setup (one-time)

You need Python 3.10 or newer.

```bash
# 1. Open a terminal in this folder
cd "/Users/gayangafernando/Desktop/Sri Lanaka/Sri Lankan history LLM"

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows PowerShell

# 3. Install dependencies (this takes a few minutes the first time)
pip install -r requirements.txt

# 4. Get a free Gemini API key from https://aistudio.google.com/apikey
#    Then copy the example env file and paste your key in
cp .env.example .env
# Open .env in a text editor and replace `your_key_here` with the real key
```

## Add sources and ingest

1. Open `sources/SOURCES.md` and download the starter set (Mahavamsa, Culavamsa, key Wikipedia pages).
2. Drop every file directly into `sources/`. PDFs, `.html`, and `.txt` all work.
3. Run the ingest script:

```bash
python ingest.py
```

You should see a `chunks` count for each file and a final summary. Re-run this any time you add or change source files.

## Run the chat

```bash
streamlit run app.py
```

A browser tab opens at `http://localhost:8501`. Ask a question. The first run downloads the embedding model (~80 MB) — later runs are instant.

## Share with others (free hosting)

Streamlit Community Cloud will host this for you for free.

1. Create a free GitHub account if you don't have one.
2. Push this folder to a new GitHub repo. Make sure `.gitignore` is in place so `.env` and `vectorstore/` don't get committed — but you DO want `sources/` and ingested files in the repo so the cloud build can re-ingest, OR commit the prebuilt `vectorstore/` (it can be large).
3. Sign in at https://streamlit.io/cloud with that GitHub account.
4. Click "New app", pick the repo, set the main file to `app.py`.
5. Under "Advanced settings → Secrets", paste:
   ```
   GEMINI_API_KEY = "your_real_key_here"
   ```
6. Deploy. You get a public URL like `your-app.streamlit.app` you can share.

If you commit `sources/` but not `vectorstore/`, add a build step that runs `python ingest.py` before `streamlit run`. The simplest path is committing the prebuilt `vectorstore/` once it's stable.

## Tuning the answers

- **Change tone or rules**: edit `system_prompt.txt`. The app re-reads it on each launch.
- **More or fewer source chunks per answer**: change `TOP_K` near the top of `app.py`. Higher = more thorough answers, slower, more tokens used.
- **Switch the LLM**: change `GEMINI_MODEL` in `app.py`. `gemini-1.5-flash` is fast and free; `gemini-1.5-pro` is smarter and still has a free tier with lower rate limits.
- **Better answer quality**: add more sources (academic papers especially) and re-run `ingest.py`.

## Troubleshooting

- **"Missing GEMINI_API_KEY"**: your `.env` file isn't being read. Make sure it sits next to `app.py` and the variable name matches exactly.
- **"Collection not found"**: you haven't run `python ingest.py` yet, or `vectorstore/` got deleted.
- **PDF ingests with no text**: it's probably a scanned image. Run OCR first — `ocrmypdf input.pdf output.pdf` works well.
- **Free-tier rate limit hit**: Gemini's free tier caps requests per minute. Wait a minute or upgrade.

## File map

```
.
|-- app.py              # Streamlit chat
|-- ingest.py           # Build the vector store from sources/
|-- system_prompt.txt   # Historian persona and rules
|-- requirements.txt    # Python deps
|-- .env.example        # Copy to .env and add your API key
|-- .gitignore
|-- sources/
|   |-- SOURCES.md      # List of starter sources to download
|   `-- (your files)
`-- vectorstore/        # Auto-created by ingest.py - do not edit by hand
```
