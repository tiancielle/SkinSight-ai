"""
SkinSight AI — app/api/main.py
FastAPI backend : /predict + /history + /stats
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import numpy as np
import pickle
import joblib
import sqlite3
import os
from datetime import datetime
from PIL import Image
import io

app = FastAPI(title="SkinSight AI API", version="1.0.0")

# ── CORS : autorise le frontend HTML à appeler l'API ──────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Chemins ────────────────────────────────────────────────────────────────────
# Chemin absolu vers la racine — fonctionne peu importe depuis où uvicorn est lancé
BASE_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODEL_DIR = os.path.join(BASE_DIR, "models")
DB_PATH   = os.path.join(BASE_DIR, "data", "history.db")

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app.mount("/static", StaticFiles(directory=os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")), "app")), name="static")

@app.get("/ui")
def ui():
    return FileResponse(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")), "app", "index.html"))

print(f"[SkinSight] BASE_DIR  = {BASE_DIR}")
print(f"[SkinSight] MODEL_DIR = {MODEL_DIR}")
print(f"[SkinSight] lightgbm  = {os.path.exists(os.path.join(MODEL_DIR, 'lightgbm.pkl'))}")
print(f"[SkinSight] pca_512   = {os.path.exists(os.path.join(MODEL_DIR, 'pca_512.pkl'))}")

CLASSES = ["saine", "acne_inflammatoire", "acne_non_inflammatoire", "rosacee", "hyperpigmentation"]

CLASSES_FR = {
    "saine":                  "Peau saine",
    "acne_inflammatoire":     "Acné inflammatoire",
    "acne_non_inflammatoire": "Acné non inflammatoire",
    "rosacee":                "Rosacée",
    "hyperpigmentation":      "Hyperpigmentation",
}

RECOMMENDATIONS = {
    "acne_inflammatoire": [
        {"cat": "Nettoyage",   "texte": "Gel doux sans savon 2× par jour, eau tiède"},
        {"cat": "Actif ciblé", "texte": "Acide salicylique 1–2% ou niacinamide 5–10%"},
        {"cat": "Hydratation", "texte": "Gel non-comédogène, texture légère"},
        {"cat": "Habitude",    "texte": "Changer la taie d'oreiller, ne pas toucher"},
    ],
    "acne_non_inflammatoire": [
        {"cat": "Nettoyage",   "texte": "Gel moussant doux, 2× par jour"},
        {"cat": "Exfoliant",   "texte": "BHA (acide salicylique 1%) 3× par semaine"},
        {"cat": "Hydratation", "texte": "Fluide léger sans huiles comédogènes"},
        {"cat": "Habitude",    "texte": "Nettoyer les pinceaux maquillage régulièrement"},
    ],
    "rosacee": [
        {"cat": "Nettoyage",      "texte": "Eau micellaire ou lait ultra-doux, sans friction"},
        {"cat": "Actif ciblé",    "texte": "Niacinamide 5% ou sérum anti-rougeurs"},
        {"cat": "Hydratation",    "texte": "Crème apaisante à la camomille ou avoine"},
        {"cat": "Déclencheurs",   "texte": "Éviter alcool, épices, chaleur excessive"},
    ],
    "hyperpigmentation": [
        {"cat": "Nettoyage",   "texte": "Gel doux, ne pas frotter les taches"},
        {"cat": "Actif ciblé", "texte": "Vitamine C 10–20% matin, rétinoïde soir"},
        {"cat": "Hydratation", "texte": "Crème légère compatible vitamine C"},
        {"cat": "Protection",  "texte": "SPF 50+ INDISPENSABLE tous les jours"},
    ],
    "saine": [
        {"cat": "Nettoyage",   "texte": "Gel doux 1× par jour"},
        {"cat": "Prévention",  "texte": "Sérum antioxydant à la vitamine C"},
        {"cat": "Hydratation", "texte": "Crème adaptée à ton type de peau"},
        {"cat": "Protection",  "texte": "SPF 30–50 tous les jours"},
    ],
}

ROUTINES = {
    "acne_inflammatoire": {
        "matin": [
            {"nom": "Nettoyage",   "desc": "Gel nettoyant à l'acide salicylique 0.5%, eau tiède, mouvements doux", "tag": "Obligatoire"},
            {"nom": "Sérum actif", "desc": "Niacinamide 10% — réduit le sébum et les rougeurs visibles",          "tag": "Actif clé"},
            {"nom": "Hydratation", "desc": "Gel hydratant non-comédogène, texture eau ou gel léger",              "tag": "Essentiel"},
            {"nom": "Protection",  "desc": "SPF 50+ fluide, tous les jours même nuageux",                         "tag": "Indispensable"},
        ],
        "soir": [
            {"nom": "Double nettoyage", "desc": "1. Huile démaquillante  2. Gel nettoyant doux sans savon",       "tag": "Obligatoire"},
            {"nom": "Traitement",       "desc": "Acide azélaïque 10% ou rétinoïde 0.025% en fine couche",        "tag": "Actif clé"},
            {"nom": "Hydratation",      "desc": "Crème à la centella asiatica ou aloe vera, texture réparatrice", "tag": "Réparation"},
            {"nom": "Règle d'or",       "desc": "Ne jamais toucher les lésions, changer la taie tous les 2 jours","tag": "Habitude"},
        ],
    },
    "acne_non_inflammatoire": {
        "matin": [
            {"nom": "Nettoyage",   "desc": "Gel moussant doux, enlever l'excès de sébum sans agresser",          "tag": "Obligatoire"},
            {"nom": "Exfoliant",   "desc": "BHA (acide salicylique 1%) 3× par semaine en sérum",                 "tag": "Actif clé"},
            {"nom": "Hydratation", "desc": "Fluide hydratant léger sans huiles comédogènes",                     "tag": "Essentiel"},
            {"nom": "Protection",  "desc": "SPF 50+ non gras, formule matifiante",                               "tag": "Indispensable"},
        ],
        "soir": [
            {"nom": "Nettoyage",   "desc": "Gel nettoyant doux, insister sur la zone T",                         "tag": "Obligatoire"},
            {"nom": "Traitement",  "desc": "Rétinoïde 0.025% pour déboucher les pores en douceur",               "tag": "Actif clé"},
            {"nom": "Hydratation", "desc": "Crème légère non-comédogène, finition mate",                         "tag": "Réparation"},
            {"nom": "Habitude",    "desc": "Nettoyer pinceaux maquillage chaque semaine",                        "tag": "Habitude"},
        ],
    },
    "rosacee": {
        "matin": [
            {"nom": "Nettoyage",   "desc": "Eau micellaire ou lait nettoyant ultra-doux, sans friction",         "tag": "Obligatoire"},
            {"nom": "Sérum",       "desc": "Niacinamide 5% ou sérum anti-rougeurs à l'azulène",                  "tag": "Actif clé"},
            {"nom": "Hydratation", "desc": "Crème apaisante à la camomille ou à l'avoine colloïdale",            "tag": "Essentiel"},
            {"nom": "Protection",  "desc": "SPF 50+ minéral (zinc oxyde), éviter filtres chimiques",             "tag": "Indispensable"},
        ],
        "soir": [
            {"nom": "Nettoyage",    "desc": "Lait démaquillant doux, rincer à l'eau fraîche",                    "tag": "Obligatoire"},
            {"nom": "Traitement",   "desc": "Acide azélaïque 10% — réduit rougeurs et inflammation",             "tag": "Actif clé"},
            {"nom": "Hydratation",  "desc": "Crème barrière réparatrice, texture confort",                       "tag": "Réparation"},
            {"nom": "Déclencheurs", "desc": "Éviter alcool, épices, soleil intense, chaleur excessive",          "tag": "Habitude"},
        ],
    },
    "hyperpigmentation": {
        "matin": [
            {"nom": "Nettoyage",   "desc": "Gel nettoyant doux, ne pas frotter les taches",                      "tag": "Obligatoire"},
            {"nom": "Sérum",       "desc": "Vitamine C 10–20% — éclaircit et protège du photovieillissement",    "tag": "Actif clé"},
            {"nom": "Hydratation", "desc": "Crème hydratante légère, compatible vitamine C",                     "tag": "Essentiel"},
            {"nom": "Protection",  "desc": "SPF 50+ INDISPENSABLE — le soleil aggrave toute pigmentation",       "tag": "Indispensable"},
        ],
        "soir": [
            {"nom": "Nettoyage",   "desc": "Double nettoyage doux, bien enlever le SPF",                         "tag": "Obligatoire"},
            {"nom": "Traitement",  "desc": "Rétinoïde 0.025–0.05% ou acide kojique pour estomper les taches",   "tag": "Actif clé"},
            {"nom": "Hydratation", "desc": "Crème nourrissante à la niacinamide, nuit réparatrice",              "tag": "Réparation"},
            {"nom": "Habitude",    "desc": "Éviter d'exposer les zones pigmentées au soleil sans SPF",           "tag": "Habitude"},
        ],
    },
    "saine": {
        "matin": [
            {"nom": "Nettoyage",   "desc": "Gel nettoyant doux, 1× par jour suffit",                            "tag": "Entretien"},
            {"nom": "Sérum",       "desc": "Sérum antioxydant à la vitamine C ou au resvératrol",               "tag": "Prévention"},
            {"nom": "Hydratation", "desc": "Crème hydratante légère adaptée à ton type de peau",                "tag": "Essentiel"},
            {"nom": "Protection",  "desc": "SPF 30–50 tous les jours",                                          "tag": "Indispensable"},
        ],
        "soir": [
            {"nom": "Nettoyage",   "desc": "Nettoyant doux pour enlever pollution et SPF",                      "tag": "Entretien"},
            {"nom": "Traitement",  "desc": "Rétinoïde faible dosage 1× semaine (prévention)",                   "tag": "Prévention"},
            {"nom": "Hydratation", "desc": "Crème de nuit nourrissante",                                        "tag": "Réparation"},
            {"nom": "Habitude",    "desc": "Dormir 7–8h — le sommeil répare la peau en profondeur",             "tag": "Habitude"},
        ],
    },
}

# ── SQLite ─────────────────────────────────────────────────────────────────────
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS analyses
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         date TEXT, pathologie TEXT, confiance REAL, scores TEXT)""")
    conn.commit(); conn.close()

def save_analysis(pathologie, confiance, scores):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO analyses (date,pathologie,confiance,scores) VALUES (?,?,?,?)",
                 (datetime.now().strftime("%Y-%m-%d %H:%M"), pathologie, confiance, str(scores)))
    conn.commit(); conn.close()

def load_history(limit=20):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT date,pathologie,confiance FROM analyses ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [{"date": r[0], "pathologie": r[1], "pathologie_fr": CLASSES_FR.get(r[1], r[1]), "confiance": round(r[2], 1)} for r in rows]

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    n   = conn.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]
    avg = conn.execute("SELECT AVG(confiance) FROM analyses").fetchone()[0]
    conn.close()
    return {"total": n, "avg_confiance": round(avg, 1) if avg else 0.0}

# ── Modèles ────────────────────────────────────────────────────────────────────
_model, _pca = None, None
_extractors  = None

def get_models():
    global _model, _pca
    if _model is None:
        _model = joblib.load(os.path.join(MODEL_DIR, "lightgbm.pkl"))
        _pca   = joblib.load(os.path.join(MODEL_DIR, "pca_512.pkl"))
        print(f"[SkinSight] ✅ LightGBM chargé  : {type(_model).__name__}")
        print(f"[SkinSight] ✅ PCA chargé        : n_components={_pca.n_components_}")
    return _model, _pca

def get_extractors():
    global _extractors
    if _extractors is None:
        from tensorflow.keras.applications import MobileNetV2, DenseNet121, InceptionV3
        from tensorflow.keras.applications.mobilenet_v2 import preprocess_input as pm
        from tensorflow.keras.applications.densenet    import preprocess_input as pd
        from tensorflow.keras.applications.inception_v3 import preprocess_input as pi
        mob = MobileNetV2(weights="imagenet", include_top=False, pooling="avg")
        den = DenseNet121(weights="imagenet", include_top=False, pooling="avg")
        inc = InceptionV3(weights="imagenet", include_top=False, pooling="avg", input_shape=(299,299,3))
        _extractors = (mob,pm),(den,pd),(inc,pi)
    return _extractors

def run_prediction(image: Image.Image):
    from tensorflow.keras.preprocessing.image import img_to_array
    model, pca   = get_models()
    (mob,pm),(den,pd),(inc,pi) = get_extractors()

    def prep(img, size, fn):
        arr = img_to_array(img.resize(size).convert("RGB"))
        return fn(np.expand_dims(arr, 0))

    feats = np.concatenate([
        mob.predict(prep(image,(224,224),pm), verbose=0).flatten(),
        den.predict(prep(image,(224,224),pd), verbose=0).flatten(),
        inc.predict(prep(image,(299,299),pi), verbose=0).flatten(),
    ]).reshape(1,-1)

    reduced = pca.transform(feats)
    proba   = model.predict_proba(reduced)[0]
    idx     = np.argmax(proba)
    return CLASSES[idx], float(proba[idx])*100, {c: round(float(p)*100, 2) for c,p in zip(CLASSES, proba)}

# ── Startup ────────────────────────────────────────────────────────────────────
@app.on_event("startup")
def startup():
    init_db()

# ── Endpoints ──────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "ok", "app": "SkinSight AI", "version": "1.0.0"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "Le fichier doit être une image (JPG, PNG).")
    try:
        contents = await file.read()
        image    = Image.open(io.BytesIO(contents))
        pathologie, confiance, scores = run_prediction(image)
        save_analysis(pathologie, confiance, scores)
        return {
            "pathologie":    pathologie,
            "pathologie_fr": CLASSES_FR[pathologie],
            "confiance":     round(confiance, 1),
            "scores":        {CLASSES_FR[c]: round(v, 1) for c, v in scores.items()},
            "scores_raw":    scores,
            "recommandations": RECOMMENDATIONS.get(pathologie, []),
            "routine": {
                "matin": ROUTINES.get(pathologie, {}).get("matin", []),
                "soir":  ROUTINES.get(pathologie, {}).get("soir",  []),
            }
        }
    except Exception as e:
        raise HTTPException(500, f"Erreur de prédiction : {str(e)}")

@app.get("/history")
def history(limit: int = 20):
    return {"history": load_history(limit)}

@app.get("/stats")
def stats():
    return get_stats()

@app.delete("/history")
def clear_history():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM analyses")
    conn.commit(); conn.close()
    return {"status": "cleared"}

# ── Lancement ──────────────────────────────────────────────────────────────────
# uvicorn app.api.main:app --reload --port 8000