from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app = FastAPI(
    title="Vedic Time Machine API",
    description="API for exploring the linguistic and thematic evolution of the Rig Veda."
)


origins = [
    "http://localhost:3000",            # dev
    "http://127.0.0.1:5173",            # Vite dev (if used)
    "https://lov-rigveda.vercel.app/"  # <--- replace with your actual Vercel URL
]

# Allow CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

def load_data(filename):
    try:
        with open(f'../data/{filename}', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"FATAL: Could not load '{filename}'. Run preprocess.py first.")
        return {}

# Load data once at startup
# MANDALA_DATA_PATH = os.path.join(os.path.dirname(__file__), "mandala_stats.json")
mandala_stats = load_data("mandala_summary.json")

corpus = load_data("rigveda_corpus.json")

@app.get("/api/mandala/{mandala_id}")
def get_mandala(mandala_id: str):
    mandala = load_data(f"sukta_summary_{mandala_id}.json")
    if not mandala:
        return {"error": "Mandala not found"}, 404
    return mandala

@app.get("/api/all_mandalas")
def get_mandalas():
    return mandala_stats

@app.get("/api/deity_trends")
def get_deity_trends():
    trends = load_data("deity_trends.json")
    if not trends:
        return {"error": "Deity trends data not found"}, 404
    return trends

@app.get("/api/sukta/{mandala_id}/{sukta_id}")
def get_specific_sukta(mandala_id: int, sukta_id: int):
    """Retrieves the full data for a single, specific sukta."""
    verse_stats = []
    for sukta in corpus:
        if (sukta['mandala'] == mandala_id and 
            sukta['sukta'] == sukta_id):
            id = sukta['verse']
            sanskrit_text = sukta['text_translit']
            translation = sukta['translation_en']
            meter = sukta['meter']
            grammar = [token for token in sukta['tokens']]
            verse_stats.append({
                "id": id,
                "sanskrit_text": sanskrit_text,
                "translation": translation,
                "meter": meter,
                "grammar": grammar
            })
    if not verse_stats:
        raise HTTPException(status_code=404, detail="Sukta not found")
    return verse_stats

@app.get("/")
def read_root():
    return {"message": "Welcome to the Vedic Time Machine API"}