# SkinSight AI -EN

AI-powered dermatological analysis tool using computer vision.  
Automatically detects skin pathologies from an uploaded image or live webcam feed.

---

## Quick Start

```bash
conda activate skinsight
cd Path_To\SkinSightAI

# Terminal 1 — FastAPI backend (required)
uvicorn app.api.main:app --reload --port 8000

# Terminal 2 — MediaPipe WebSocket server (optional, for AR webcam)
python app/webcam_ar.py

# Open in browser
http://localhost:8000/ui
```

---

## Detected Pathologies

| Class | Description |
|---|---|
| `saine` | Healthy skin, no pathology |
| `acne_inflammatoire` | Papules, pustules, red lesions |
| `acne_non_inflammatoire` | Open/closed comedones (blackheads/whiteheads) |
| `rosacee` | Persistent vascular redness |
| `hyperpigmentation` | Melanic spots, post-inflammatory hyperpigmentation |

---

## Technical Architecture

```
Image (224×224 / 299×299)
  ↓
MobileNetV2  → 1280D ┐
DenseNet121  → 1024D ├─ Concatenation (4352D) → PCA (512D)
InceptionV3  → 2048D ┘
  ↓
LightGBM (86.3% F1-macro)
  ↓
Severity Score (Mild / Moderate / Severe)
  ↓
Recommendation Engine (skincare + morning/evening routine)
```

---

## Installation

```bash
git clone https://github.com/tiancielle/skinsight-ai.git
cd skinsight-ai
pip install -r requirements.txt
```

---

## Project Structure

```
SkinSightAI/
├── app/
│   ├── index.html              Main web interface
│   ├── webcam_ar.py            MediaPipe WebSocket server (real-time AR)
│   ├── api/
│   │   └── main.py             FastAPI (/predict, /history, /stats, /patients)
│   └── static/
│       ├── css/
│       │   └── style.css       Global styles
│       └── js/
│           ├── config.js       Shared constants (API, COLORS, FICHES, ROUTINES)
│           ├── app.js          Navigation, stats, pathology cards, profile
│           ├── analyse.js      Upload, prediction, result rendering, PDF report
│           ├── modules.js      History, before/after, AR webcam
│           └── patients.js     Patient CRUD, patient file, patient PDF
├── models/
│   ├── lightgbm.pkl            Trained LightGBM model
│   └── pca_512.pkl             PCA 512 components
├── data/
│   ├── history.db              SQLite database (analyses + patients)
│   └── splits/
│       ├── train/              Training images by class
│       ├── val/                Validation images
│       └── test/               Test images
├── notebooks/                  6 documented notebooks (EDA, features, models)
├── requirements.txt
└── README.md
```

---

## Features

### AI Analysis
- Image upload (JPG, PNG) or drag & drop
- Multi-class prediction with per-pathology confidence scores
- Automatic severity scoring (Mild / Moderate / Severe)
- Personalized skincare recommendations
- Auto-generated morning/evening skincare routine
- Full PDF report export (image + diagnosis + scores + recommendations)

### Patient Records
- Create and manage patient files (name, age, sex, phototype)
- Link each analysis to a patient
- Patient file with 3 tabs: Record / Routine / Before-After
- Confidence evolution chart over time
- Dominant pathology badge + evolution index (Stable / Improving / Worsening)
- Full patient PDF export

### AR Webcam
- Real-time camera feed with anatomical zone overlay
- MediaPipe integration via WebSocket (ws://localhost:8765)
- Simulation mode if Python server is unavailable
- 4 visualizable pathologies with zone legend

### History & Pathology Cards
- Global history of all analyses with associated patient
- Detailed pathology cards (description, causes, treatments)
- CSV export of full history

---

## Technical Notes

- Models `.pkl` are in `models/` (loaded with `joblib.load()`)
- Dataset images are in `data/splits/train|val|test/class/`
- `patient_id` is optional in `/predict?patient_id=X`
- SQLite: `analyses` table + `patients` table with `LEFT JOIN`
- jsPDF loaded via CDN in `index.html`
- Model trained on ISIC dermatoscopic images — possible domain shift with regular photos

---

## FastAPI Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/ui` | GET | Web interface |
| `/predict` | POST | Analyze an image |
| `/history` | GET | Analysis history |
| `/stats` | GET | Global statistics |
| `/patients` | GET / POST | List / create a patient |
| `/patients/{id}` | GET / DELETE | Patient file / delete patient |

---

## Tech Stack

| Component | Technology |
|---|---|
| Feature extraction | TensorFlow / Keras (MobileNetV2, DenseNet121, InceptionV3) |
| Classification | LightGBM |
| Dimensionality reduction | PCA 512D (Scikit-learn) |
| API backend | FastAPI + Uvicorn |
| Database | SQLite |
| AR webcam | MediaPipe + WebSocket |
| Frontend | Vanilla HTML / CSS / JS |
| PDF export | jsPDF (CDN) |

---

## Model Performance

| Metric | LightGBM |
|---|---|
| F1-macro | 86.3% |
| Pipeline | MobileNetV2 + DenseNet121 + InceptionV3 → PCA-512 |
| Classes | 5 (healthy, inflammatory acne, non-inflammatory acne, rosacea, hyperpigmentation) |

---

## Datasets

- **Acne04** — 4,000 images, 4 acne severity levels
- **ISIC 2020** — Diverse dermatological lesions
- **DermNet** — 23 categories of skin pathologies

---

## Disclaimer

SkinSight AI is a detection assistance tool, **not a substitute for medical advice**.  
When in doubt, consult a certified dermatologist.

----
----

# SkinSight AI - FR

Outil d'analyse dermatologique par intelligence artificielle.  
Détecte automatiquement les pathologies cutanées depuis une image ou la webcam en temps réel.

---

## Lancement rapide

```bash
conda activate skinsight
cd Path_To\SkinSightAI

# Terminal 1 — API FastAPI (obligatoire)
uvicorn app.api.main:app --reload --port 8000

# Terminal 2 — Serveur WebSocket MediaPipe (optionnel, pour la webcam AR)
python app/webcam_ar.py

# Navigateur
http://localhost:8000/ui
```

---

## Pathologies détectées

| Classe | Description |
|---|---|
| `saine` | Peau saine, aucune pathologie |
| `acne_inflammatoire` | Papules, pustules, lésions rouges |
| `acne_non_inflammatoire` | Comédons ouverts/fermés (points noirs/blancs) |
| `rosacee` | Rougeurs vasculaires persistantes |
| `hyperpigmentation` | Taches mélaniques, hyperpigmentation post-inflammatoire |

---

## Architecture technique

```
Image (224×224 / 299×299)
  ↓
MobileNetV2  → 1280D ┐
DenseNet121  → 1024D ├─ Concatenation (4352D) → PCA (512D)
InceptionV3  → 2048D ┘
  ↓
LightGBM (86.3% F1-macro)
  ↓
Score de sévérité (Léger / Modéré / Sévère)
  ↓
Module Recommandation (soins + routine matin/soir)
```

---

## Installation

```bash
git clone https://github.com/tiancielle/skinsight-ai.git
cd skinsight-ai
pip install -r requirements.txt
```

---

## Structure du projet

```
SkinSightAI/
├── app/
│   ├── index.html              Interface web principale
│   ├── webcam_ar.py            Serveur WebSocket MediaPipe (AR temps réel)
│   ├── api/
│   │   └── main.py             API FastAPI (/predict, /history, /stats, /patients)
│   └── static/
│       ├── css/
│       │   └── style.css       Styles globaux
│       └── js/
│           ├── config.js       Constantes partagées (API, COLORS, FICHES, ROUTINES)
│           ├── app.js          Navigation, stats, fiches, profil
│           ├── analyse.js      Upload, prédiction, rendu résultat, PDF rapport
│           ├── modules.js      Historique, avant/après, webcam AR
│           └── patients.js     Dossiers patients CRUD, fiche, PDF patient
├── models/
│   ├── lightgbm.pkl            Modèle LightGBM entraîné
│   └── pca_512.pkl             PCA 512 composantes
├── data/
│   ├── history.db              Base SQLite (analyses + patients)
│   └── splits/
│       ├── train/              Images d'entraînement par classe
│       ├── val/                Images de validation
│       └── test/               Images de test
├── notebooks/                  6 notebooks documentés (EDA, features, modèles)
├── requirements.txt
└── README.md
```

---

## Fonctionnalités

### Analyse IA
- Upload d'image (JPG, PNG) ou drag & drop
- Prédiction multi-classe avec scores de confiance par pathologie
- Score de sévérité automatique (Léger / Modéré / Sévère)
- Recommandations de soins personnalisées
- Protocole de soins matin/soir généré automatiquement
- Export rapport PDF complet (image + diagnostic + scores + recommandations)

### Dossiers patients
- Création et gestion de dossiers patients (nom, âge, sexe, phototype)
- Association analyse ↔ patient
- Fiche patient avec 3 onglets : Dossier / Routine / Avant-Après
- Graphique d'évolution de la confiance dans le temps
- Badge pathologie dominante + indice évolutif (Stable / Amélioration / Aggravation)
- Export PDF du dossier patient complet

### Webcam AR
- Flux caméra temps réel avec overlay des zones anatomiques
- Intégration MediaPipe via WebSocket (ws://localhost:8765)
- Mode simulation si le serveur Python est absent
- 4 pathologies visualisables avec légende des zones

### Historique & Fiches
- Historique global de toutes les analyses avec patient associé
- Fiches pathologies détaillées (description, causes, traitements)

---

## Points techniques importants

- Les modèles `.pkl` sont dans `models/` (chargés avec `joblib.load()`)
- Les images dataset sont dans `data/splits/train|val|test/classe/`
- `patient_id` optionnel dans `/predict?patient_id=X`
- SQLite : table `analyses` + table `patients` avec `LEFT JOIN`
- jsPDF chargé via CDN dans `index.html`
- Le modèle est entraîné sur images dermatoscopiques ISIC — domain shift possible avec photos grand public

---

## API FastAPI

| Endpoint | Méthode | Description |
|---|---|---|
| `/ui` | GET | Interface web |
| `/predict` | POST | Analyse une image |
| `/history` | GET | Historique des analyses |
| `/stats` | GET | Statistiques globales |
| `/patients` | GET / POST | Liste / créer un patient |
| `/patients/{id}` | GET / DELETE | Fiche / supprimer un patient |

---

## Stack technologique

| Composant | Technologie |
|---|---|
| Extraction features | TensorFlow / Keras (MobileNetV2, DenseNet121, InceptionV3) |
| Classification | LightGBM |
| Réduction dimensionnelle | PCA 512D (Scikit-learn) |
| API backend | FastAPI + Uvicorn |
| Base de données | SQLite |
| Interface webcam AR | MediaPipe + WebSocket |
| Frontend | HTML / CSS / JS vanilla |
| Export PDF | jsPDF (CDN) |

---

## Métriques du modèle

| Métrique | LightGBM |
|---|---|
| F1-macro | 86.3% |
| Pipeline | MobileNetV2 + DenseNet121 + InceptionV3 → PCA-512 |
| Classes | 5 (saine, acné inflammatoire, acné non inflammatoire, rosacée, hyperpigmentation) |

---

## Datasets utilisés

- **Acne04** — 4 000 images, 4 niveaux de sévérité d'acné
- **ISIC 2020** — Lésions dermatologiques diverses
- **DermNet** — 23 catégories de pathologies cutanées

---

## Avertissement

SkinSight AI est un outil d'aide à la détection, **pas un substitut à un avis médical**.  
En cas de doute, consultez un dermatologue certifié.