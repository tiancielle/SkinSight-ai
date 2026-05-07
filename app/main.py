# """
# SkinSight AI — app/main.py
# Dashboard Streamlit complet : analyse, routine, historique, fiches, webcam AR
# Palette : terracotta + mauve + nude + sage sur fond crème
# """

# import streamlit as st
# import numpy as np
# import cv2
# import pickle
# import sqlite3
# import os
# from datetime import datetime
# from PIL import Image

# # ── Config page ────────────────────────────────────────────────────────────────
# st.set_page_config(
#     page_title="SkinSight AI",
#     page_icon="🔬",
#     layout="wide",
#     initial_sidebar_state="expanded",
# )

# # ── CSS global ─────────────────────────────────────────────────────────────────
# st.markdown("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500&display=swap');

# html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

# :root {
#   --bg:#fdf9f6; --bg2:#ffffff; --bg3:#f5f0eb;
#   --terra:#c47c5a; --terra-l:#f7ede6; --terra-m:#e8b49a;
#   --mauve:#9b7fa6; --mauve-l:#f0eaf4; --mauve-m:#cdb8d6;
#   --nude:#d4a882;  --nude-l:#fdf3ec;
#   --sage:#7a9e87;  --sage-l:#eaf2ed;
#   --txt:#2a1f1a;   --txt2:#7a6860;   --txt3:#b5a89e;
#   --brd:#ece5de;   --brd2:#d8cfc6;
# }

# .stApp { background: var(--bg) !important; }
# .block-container { padding: 2rem !important; max-width: 100% !important; }

# [data-testid="stSidebar"] { background: var(--bg2) !important; border-right: 1px solid var(--brd); }
# [data-testid="stSidebar"] .block-container { padding: 1.5rem 1rem !important; }

# .stButton > button {
#   background: var(--terra) !important; color: white !important;
#   border: none !important; border-radius: 8px !important;
#   font-family: 'DM Sans', sans-serif !important; font-size: 0.85rem !important;
#   padding: 0.5rem 1.2rem !important; transition: all 0.18s !important;
# }
# .stButton > button:hover { background: #b06a48 !important; transform: translateY(-1px); }

# [data-testid="stMetricValue"] {
#   font-family: 'DM Serif Display', serif !important;
#   color: var(--terra) !important; font-size: 1.6rem !important;
# }
# [data-testid="stMetricLabel"] {
#   font-size: 0.65rem !important; letter-spacing: 0.7px;
#   text-transform: uppercase; color: var(--txt3) !important;
# }
# [data-testid="stMetric"] {
#   background: var(--bg2); border: 1px solid var(--brd); border-radius: 12px; padding: 0.75rem 1rem;
# }

# .sk-title { font-family: 'DM Serif Display', serif; font-size: 1.5rem; color: #2a1f1a; margin-bottom: 0.2rem; }
# .sk-sub   { font-size: 0.78rem; color: #7a6860; margin-bottom: 1.2rem; }
# .sk-label { font-size: 0.63rem; letter-spacing: 0.8px; text-transform: uppercase; color: #b5a89e; margin-bottom: 0.4rem; }

# .result-card { background: var(--bg2); border: 1px solid var(--brd); border-radius: 16px; padding: 1.2rem; margin-top: 1rem; }
# .badge-terra {
#   display:inline-block; padding:.28rem .8rem; border-radius:50px; font-size:.72rem;
#   font-weight:500; background:var(--terra-l); color:var(--terra); border:1px solid var(--terra-m);
# }
# .reco-box { background: var(--bg3); border-radius: 10px; padding: 0.7rem 0.85rem; margin-bottom: 0.4rem; }
# .reco-cat { font-size:.63rem; letter-spacing:.8px; text-transform:uppercase; color:var(--terra); font-weight:500; margin-bottom:.15rem; }
# .fiche-box { background:var(--bg2); border:1px solid var(--brd); border-radius:14px; padding:1rem; margin-bottom:.6rem; }
# .pill { display:inline-block; font-size:.63rem; letter-spacing:.6px; padding:.2rem .6rem; border-radius:50px; font-weight:500; margin-top:.4rem; }
# .hist-row { background:var(--bg2); border:1px solid var(--brd); border-radius:12px; padding:.8rem 1rem; margin-bottom:.5rem; display:flex; align-items:center; gap:.8rem; }
# .warn-box { background:var(--nude-l); border-left:2px solid var(--nude); border-radius:8px; padding:.6rem .85rem; font-size:.72rem; color:#7a6860; margin-top:.75rem; }
# .routine-step { background:var(--bg2); border:1px solid var(--brd); border-radius:12px; padding:.85rem 1rem; margin-bottom:.5rem; }
# .model-pill { font-size:.65rem; letter-spacing:.7px; padding:.28rem .75rem; border-radius:50px; background:var(--terra-l); color:var(--terra); border:1px solid var(--terra-m); font-weight:500; }
# .logo-text  { font-family:'DM Serif Display',serif; font-size:1.4rem; color:var(--terra); }
# </style>
# """, unsafe_allow_html=True)

# # ── Chemins ────────────────────────────────────────────────────────────────────
# BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# MODEL_DIR = os.path.join(BASE_DIR, "models")
# DB_PATH   = os.path.join(BASE_DIR, "data", "history.db")

# CLASSES = ["saine", "acne_inflammatoire", "acne_non_inflammatoire", "rosacee", "hyperpigmentation"]

# CLASSES_FR = {
#     "saine":                  "Peau saine",
#     "acne_inflammatoire":     "Acné inflammatoire",
#     "acne_non_inflammatoire": "Acné non inflammatoire",
#     "rosacee":                "Rosacée",
#     "hyperpigmentation":      "Hyperpigmentation",
# }

# COLORS = {
#     "saine":                  "#7a9e87",
#     "acne_inflammatoire":     "#c47c5a",
#     "acne_non_inflammatoire": "#d4a882",
#     "rosacee":                "#9b7fa6",
#     "hyperpigmentation":      "#7a9e87",
# }

# # ── Routines soins ─────────────────────────────────────────────────────────────
# ROUTINES = {
#     "acne_inflammatoire": {
#         "matin": [
#             ("Nettoyage",   "Gel nettoyant à l'acide salicylique 0.5%, eau tiède, mouvements doux", "Obligatoire"),
#             ("Sérum actif", "Niacinamide 10% — réduit sébum et rougeurs visibles",                  "Actif clé"),
#             ("Hydratation", "Gel hydratant non-comédogène, texture eau ou gel léger",               "Essentiel"),
#             ("Protection",  "SPF 50+ fluide, tous les jours même nuageux",                          "Indispensable"),
#         ],
#         "soir": [
#             ("Double nettoyage", "1. Huile démaquillante  2. Gel nettoyant doux sans savon",        "Obligatoire"),
#             ("Traitement",       "Acide azélaïque 10% ou rétinoïde 0.025% en fine couche",         "Actif clé"),
#             ("Hydratation",      "Crème à la centella asiatica ou aloe vera, texture réparatrice",  "Réparation"),
#             ("Règle d'or",       "Ne jamais toucher les lésions, changer la taie tous les 2 jours","Habitude"),
#         ],
#     },
#     "acne_non_inflammatoire": {
#         "matin": [
#             ("Nettoyage",   "Gel moussant doux, enlever l'excès de sébum sans agresser",           "Obligatoire"),
#             ("Exfoliant",   "BHA (acide salicylique 1%) 3× par semaine en sérum",                  "Actif clé"),
#             ("Hydratation", "Fluide hydratant léger sans huiles comédogènes",                       "Essentiel"),
#             ("Protection",  "SPF 50+ non gras, formule matifiante",                                "Indispensable"),
#         ],
#         "soir": [
#             ("Nettoyage",   "Gel nettoyant doux, insister sur la zone T",                          "Obligatoire"),
#             ("Traitement",  "Rétinoïde 0.025% pour déboucher les pores en douceur",                "Actif clé"),
#             ("Hydratation", "Crème légère non-comédogène, finition mate",                          "Réparation"),
#             ("Habitude",    "Nettoyer pinceaux maquillage chaque semaine",                         "Habitude"),
#         ],
#     },
#     "rosacee": {
#         "matin": [
#             ("Nettoyage",   "Eau micellaire ou lait nettoyant ultra-doux, sans friction",          "Obligatoire"),
#             ("Sérum",       "Niacinamide 5% ou sérum anti-rougeurs à l'azulène",                   "Actif clé"),
#             ("Hydratation", "Crème apaisante à la camomille ou à l'avoine colloïdale",             "Essentiel"),
#             ("Protection",  "SPF 50+ minéral (zinc oxyde), éviter filtres chimiques",              "Indispensable"),
#         ],
#         "soir": [
#             ("Nettoyage",    "Lait démaquillant doux, rincer à l'eau fraîche",                     "Obligatoire"),
#             ("Traitement",   "Acide azélaïque 10% — réduit rougeurs et inflammation",              "Actif clé"),
#             ("Hydratation",  "Crème barrière réparatrice, texture confort",                        "Réparation"),
#             ("Déclencheurs", "Éviter alcool, épices, soleil intense, chaleur excessive",           "Habitude"),
#         ],
#     },
#     "hyperpigmentation": {
#         "matin": [
#             ("Nettoyage",   "Gel nettoyant doux, ne pas frotter les taches",                       "Obligatoire"),
#             ("Sérum",       "Vitamine C 10–20% — éclaircit et protège du photovieillissement",     "Actif clé"),
#             ("Hydratation", "Crème hydratante légère, compatible vitamine C",                      "Essentiel"),
#             ("Protection",  "SPF 50+ INDISPENSABLE — le soleil aggrave toute pigmentation",        "Indispensable"),
#         ],
#         "soir": [
#             ("Nettoyage",   "Double nettoyage doux, bien enlever le SPF",                          "Obligatoire"),
#             ("Traitement",  "Rétinoïde 0.025–0.05% ou acide kojique pour estomper les taches",    "Actif clé"),
#             ("Hydratation", "Crème nourrissante à la niacinamide, nuit réparatrice",               "Réparation"),
#             ("Habitude",    "Éviter d'exposer les zones pigmentées au soleil sans SPF",            "Habitude"),
#         ],
#     },
#     "saine": {
#         "matin": [
#             ("Nettoyage",   "Gel nettoyant doux, 1× par jour suffit",                             "Entretien"),
#             ("Sérum",       "Sérum antioxydant à la vitamine C ou au resvératrol",                "Prévention"),
#             ("Hydratation", "Crème hydratante légère adaptée à ton type de peau",                 "Essentiel"),
#             ("Protection",  "SPF 30–50 tous les jours",                                           "Indispensable"),
#         ],
#         "soir": [
#             ("Nettoyage",   "Nettoyant doux pour enlever pollution et SPF",                       "Entretien"),
#             ("Traitement",  "Rétinoïde faible dosage 1× semaine (prévention)",                    "Prévention"),
#             ("Hydratation", "Crème de nuit nourrissante",                                         "Réparation"),
#             ("Habitude",    "Dormir 7–8h — le sommeil répare la peau en profondeur",              "Habitude"),
#         ],
#     },
# }

# RECOMMENDATIONS = {
#     "acne_inflammatoire":     [("Nettoyage","Gel doux sans savon 2× par jour"),("Actif ciblé","Acide salicylique 1–2% ou niacinamide"),("Hydratation","Gel non-comédogène, texture légère"),("Habitude","Changer taie d'oreiller, ne pas toucher")],
#     "acne_non_inflammatoire": [("Nettoyage","Gel moussant doux, 2× par jour"),("Exfoliant","BHA 1% en sérum, 3× par semaine"),("Hydratation","Fluide léger sans huiles comédogènes"),("Habitude","Nettoyer les pinceaux maquillage régulièrement")],
#     "rosacee":                [("Nettoyage","Eau micellaire ou lait ultra-doux"),("Actif ciblé","Niacinamide 5% ou sérum anti-rougeurs"),("Hydratation","Crème apaisante à la camomille"),("Déclencheurs","Éviter alcool, épices, chaleur")],
#     "hyperpigmentation":      [("Nettoyage","Gel doux, ne pas frotter les taches"),("Actif ciblé","Vitamine C matin, rétinoïde soir"),("Hydratation","Crème légère compatible vitamine C"),("Protection","SPF 50+ INDISPENSABLE")],
#     "saine":                  [("Nettoyage","Gel doux 1× par jour"),("Prévention","Sérum antioxydant vitamine C"),("Hydratation","Crème adaptée à ton type de peau"),("Protection","SPF 30–50 tous les jours")],
# }

# FICHES = {
#     "acne_inflammatoire":     {"emoji":"🔴","titre":"Acné inflammatoire","desc":"Papules et pustules rouges issues d'une infection bactérienne (C. acnes) du follicule pileux.","causes":"Excès de sébum, bactéries, hormones, stress","traitement":"Acide salicylique, niacinamide, peroxyde de benzoyle","tag":"Très fréquent","color":"#c47c5a","color_l":"#f7ede6"},
#     "acne_non_inflammatoire": {"emoji":"🟤","titre":"Acné non inflammatoire","desc":"Points noirs et blancs. Excès de sébum obstruant les pores sans infection active.","causes":"Hyperséborrhée, kératinisation excessive","traitement":"BHA, rétinoïdes, exfoliation douce","tag":"Courant","color":"#d4a882","color_l":"#fdf3ec"},
#     "rosacee":                {"emoji":"🌸","titre":"Rosacée","desc":"Affection chronique causant des rougeurs persistantes et des vaisseaux visibles.","causes":"Génétique, soleil, alcool, épices, chaleur","traitement":"Acide azélaïque, métronidazole, SPF minéral","tag":"Chronique","color":"#9b7fa6","color_l":"#f0eaf4"},
#     "hyperpigmentation":      {"emoji":"🟣","titre":"Hyperpigmentation","desc":"Taches sombres dues à un excès de mélanine : UV, hormones, cicatrices.","causes":"Soleil, hormones, inflammation, cicatrices","traitement":"Vitamine C, rétinoïdes, acide kojique, SPF 50+","tag":"Traitable","color":"#7a9e87","color_l":"#eaf2ed"},
#     "saine":                  {"emoji":"✨","titre":"Peau saine","desc":"Aucune pathologie détectée. Aspect uniforme, bonne hydratation, barrière cutanée intacte.","causes":"Bonne hygiène, hydratation, alimentation équilibrée","traitement":"Entretien préventif, SPF quotidien, antioxydants","tag":"Excellent","color":"#7a9e87","color_l":"#eaf2ed"},
# }

# # ── SQLite ─────────────────────────────────────────────────────────────────────
# def init_db():
#     os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
#     conn = sqlite3.connect(DB_PATH)
#     conn.execute("CREATE TABLE IF NOT EXISTS analyses (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, pathologie TEXT, confiance REAL, scores TEXT)")
#     conn.commit(); conn.close()

# def save_analysis(pathologie, confiance, scores):
#     conn = sqlite3.connect(DB_PATH)
#     conn.execute("INSERT INTO analyses (date,pathologie,confiance,scores) VALUES (?,?,?,?)",
#                  (datetime.now().strftime("%Y-%m-%d %H:%M"), pathologie, confiance, str(scores)))
#     conn.commit(); conn.close()

# def load_history(limit=20):
#     conn = sqlite3.connect(DB_PATH)
#     rows = conn.execute("SELECT date,pathologie,confiance FROM analyses ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
#     conn.close(); return rows

# def count_analyses():
#     conn = sqlite3.connect(DB_PATH)
#     n = conn.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]
#     conn.close(); return n

# def avg_confidence():
#     conn = sqlite3.connect(DB_PATH)
#     avg = conn.execute("SELECT AVG(confiance) FROM analyses").fetchone()[0]
#     conn.close(); return round(avg, 1) if avg else 0.0

# # ── Modèles ────────────────────────────────────────────────────────────────────
# @st.cache_resource
# def load_models():
#     try:
#         with open(os.path.join(MODEL_DIR, "lightgbm.pkl"), "rb") as f: model = pickle.load(f)
#         with open(os.path.join(MODEL_DIR, "pca_512.pkl"),  "rb") as f: pca   = pickle.load(f)
#         return model, pca
#     except FileNotFoundError:
#         return None, None

# @st.cache_resource
# def load_extractors():
#     try:
#         from tensorflow.keras.applications import MobileNetV2, DenseNet121, InceptionV3
#         from tensorflow.keras.applications.mobilenet_v2 import preprocess_input as pm
#         from tensorflow.keras.applications.densenet    import preprocess_input as pd
#         from tensorflow.keras.applications.inception_v3 import preprocess_input as pi
#         mob = MobileNetV2(weights="imagenet", include_top=False, pooling="avg")
#         den = DenseNet121(weights="imagenet", include_top=False, pooling="avg")
#         inc = InceptionV3(weights="imagenet", include_top=False, pooling="avg", input_shape=(299,299,3))
#         return (mob,pm),(den,pd),(inc,pi)
#     except Exception:
#         return None,None,None

# def predict(image: Image.Image):
#     from tensorflow.keras.preprocessing.image import img_to_array
#     model, pca = load_models()
#     exts = load_extractors()
#     if model is None or exts[0] is None: return None

#     (mob,pm),(den,pd),(inc,pi) = exts
#     def prep(img, size, fn):
#         arr = img_to_array(img.resize(size).convert("RGB"))
#         return fn(np.expand_dims(arr, 0))

#     feats = np.concatenate([
#         mob.predict(prep(image,(224,224),pm), verbose=0).flatten(),
#         den.predict(prep(image,(224,224),pd), verbose=0).flatten(),
#         inc.predict(prep(image,(299,299),pi), verbose=0).flatten(),
#     ]).reshape(1,-1)

#     reduced = pca.transform(feats)
#     proba   = model.predict_proba(reduced)[0]
#     idx     = np.argmax(proba)
#     return CLASSES[idx], float(proba[idx])*100, {c:float(p)*100 for c,p in zip(CLASSES,proba)}

# # ── Helpers ────────────────────────────────────────────────────────────────────
# def html(s): st.markdown(s, unsafe_allow_html=True)
# def divider(): html('<hr style="border:none;border-top:1px solid #ece5de;margin:.85rem 0">')
# def warn(s): html(f'<div class="warn-box">⚠ {s}</div>')

# init_db()
# # ── SIDEBAR ────────────────────────────────────────────────────────────────────
# with st.sidebar:
#     html('<div class="logo-text">SkinSight</div>')
#     html('<p style="font-size:.68rem;letter-spacing:.8px;color:#b5a89e;margin-top:2px;margin-bottom:1.5rem">Analyse cutanée · IA</p>')
#     page = st.radio("", ["Analyse","Ma routine","Historique","Fiches","Webcam AR"], label_visibility="collapsed")
#     st.markdown("---")
#     html(f"""<div style="background:#f5f0eb;border-radius:12px;padding:.85rem;border:1px solid #ece5de">
#       <p style="font-size:.63rem;letter-spacing:.8px;color:#b5a89e;text-transform:uppercase;margin-bottom:.3rem">Session</p>
#       <p style="font-size:.85rem;font-weight:500;color:#2a1f1a">{count_analyses()} analyse(s)</p>
#       <p style="font-size:.72rem;color:#7a6860;margin-top:.1rem">Précision moy. {avg_confidence()}%</p>
#     </div>""")
#     st.markdown("")
#     html('<span class="model-pill">LightGBM · actif</span>')



# # ══════════════════════════════════════════════════════════════════════════════
# # PAGE ANALYSE
# # ══════════════════════════════════════════════════════════════════════════════
# if page == "Analyse":
#     html('<div class="sk-title">Nouvelle analyse</div>')
#     html('<div class="sk-sub">Importe une photo pour un diagnostic instantané</div>')

#     c1,c2,c3 = st.columns(3)
#     with c1: st.metric("Analyses",      count_analyses())
#     with c2: st.metric("Précision moy.",f"{avg_confidence()}%")
#     with c3:
#         last = load_history(1)
#         st.metric("Dernière", f"{round(last[0][2])}%" if last else "—")

#     st.markdown("")
#     uploaded = st.file_uploader("Déposer ou cliquer pour importer", type=["jpg","jpeg","png"])

#     col_a, col_w = st.columns(2)
#     with col_a: analyse_btn = st.button("Analyser l'image", use_container_width=True)

#     if uploaded and analyse_btn:
#         image = Image.open(uploaded)
#         with st.spinner("Analyse en cours…"):
#             result = predict(image)

#         if result is None:
#             st.error("Modèles introuvables. Vérifie models/lightgbm.pkl et models/pca_512.pkl")
#         else:
#             pathologie, confiance, scores = result
#             st.session_state["derniere_pathologie"] = pathologie
#             save_analysis(pathologie, confiance, list(scores.values()))

#             col_img, col_res = st.columns([1, 1.8])
#             with col_img:
#                 st.image(image, use_container_width=True, caption="Image analysée")

#             with col_res:
#                 html('<div class="result-card">')
#                 html(f"""<div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:1rem">
#                   <div>
#                     <div class="sk-label">Résultat IA</div>
#                     <div style="font-family:'DM Serif Display',serif;font-size:1.15rem;color:#2a1f1a">{CLASSES_FR[pathologie]}</div>
#                   </div>
#                   <span class="badge-terra">{round(confiance)}% de confiance</span>
#                 </div>""")

#                 html('<div class="sk-label">Confiance principale</div>')
#                 st.progress(confiance / 100)
#                 divider()

#                 html('<div class="sk-label" style="margin-bottom:.5rem">Scores par classe</div>')
#                 for cls, score in sorted(scores.items(), key=lambda x: -x[1]):
#                     cn, cb, cp = st.columns([2,3,0.6])
#                     with cn: html(f'<span style="font-size:.71rem;color:#7a6860">{CLASSES_FR[cls]}</span>')
#                     with cb: st.progress(score/100)
#                     with cp: html(f'<span style="font-size:.7rem;color:#b5a89e">{round(score)}%</span>')

#                 divider()
#                 html('<div class="sk-label" style="margin-bottom:.5rem">Recommandations soins</div>')
#                 recos = RECOMMENDATIONS.get(pathologie, [])
#                 cr1, cr2 = st.columns(2)
#                 for i,(cat,texte) in enumerate(recos):
#                     with cr1 if i%2==0 else cr2:
#                         html(f'<div class="reco-box"><div class="reco-cat">{cat}</div><div style="font-size:.74rem;color:#2a1f1a;line-height:1.5">{texte}</div></div>')
#                 html('</div>')

#             # ── Routine résumé ──────────────────────────────────────────────
#             st.markdown("")
#             html('<div style="background:#f0eaf4;border:1px solid #cdb8d6;border-radius:12px;padding:1rem">')
#             ct, cs = st.columns([2,1])
#             with ct: html('<p style="font-size:.82rem;font-weight:500;color:#9b7fa6;margin-bottom:.6rem">Routine personnalisée</p>')
#             with cs:
#                 moment = st.radio("", ["☀️ Matin","🌙 Soir"], horizontal=True,
#                                   label_visibility="collapsed", key="moment_preview")

#             m_key = "matin" if "Matin" in moment else "soir"
#             for i,(nom,desc,_) in enumerate(ROUTINES.get(pathologie,{}).get(m_key,[])[:3], 1):
#                 html(f"""<div class="routine-step" style="display:flex;gap:.75rem;align-items:flex-start;margin-bottom:.4rem">
#                   <div style="width:24px;height:24px;border-radius:50%;background:#f0eaf4;border:1px solid #cdb8d6;
#                               color:#9b7fa6;font-size:.68rem;display:flex;align-items:center;justify-content:center;
#                               flex-shrink:0;font-weight:500">{i}</div>
#                   <div><div style="font-size:.78rem;font-weight:500;color:#2a1f1a">{nom}</div>
#                        <div style="font-size:.72rem;color:#7a6860;line-height:1.4">{desc}</div></div>
#                 </div>""")
#             html('</div>')
#             warn("Résultat indicatif — consulter un dermatologue pour un diagnostic médical.")

# # ══════════════════════════════════════════════════════════════════════════════
# # PAGE MA ROUTINE
# # ══════════════════════════════════════════════════════════════════════════════
# elif page == "Ma routine":
#     pathologie = st.session_state.get("derniere_pathologie", "acne_inflammatoire")
#     html('<div class="sk-title">Ma routine</div>')
#     html(f'<div class="sk-sub">Basée sur ton dernier diagnostic · {CLASSES_FR[pathologie]}</div>')

#     tab_m, tab_s = st.tabs(["☀️ Routine matin", "🌙 Routine soir"])
#     for tab, moment in [(tab_m,"matin"),(tab_s,"soir")]:
#         with tab:
#             f    = FICHES.get(pathologie, {})
#             col  = f.get("color","#c47c5a")
#             col_l= f.get("color_l","#f7ede6")
#             for i,(nom,desc,tag) in enumerate(ROUTINES.get(pathologie,{}).get(moment,[]), 1):
#                 html(f"""<div class="fiche-box" style="display:flex;gap:.9rem;align-items:flex-start">
#                   <div style="width:32px;height:32px;border-radius:50%;background:{col_l};border:1px solid {col}40;
#                               color:{col};font-size:.72rem;display:flex;align-items:center;justify-content:center;
#                               flex-shrink:0;font-weight:500">{i}</div>
#                   <div>
#                     <div style="font-size:.88rem;font-weight:500;color:#2a1f1a;margin-bottom:.2rem">{nom}</div>
#                     <div style="font-size:.76rem;color:#7a6860;line-height:1.55">{desc}</div>
#                     <span class="pill" style="background:{col_l};color:{col};border:1px solid {col}40">{tag}</span>
#                   </div>
#                 </div>""")
#     warn("Ces recommandations sont générées automatiquement. Consulte un dermatologue pour un suivi personnalisé.")

# # ══════════════════════════════════════════════════════════════════════════════
# # PAGE HISTORIQUE
# # ══════════════════════════════════════════════════════════════════════════════
# elif page == "Historique":
#     html('<div class="sk-title">Historique</div>')
#     html('<div class="sk-sub">Tes analyses récentes</div>')
#     rows = load_history()
#     if not rows:
#         st.info("Aucune analyse enregistrée. Lance ta première analyse !")
#     else:
#         for date, pathologie, confiance in rows:
#             col = COLORS.get(pathologie, "#b5a89e")
#             html(f"""<div class="hist-row">
#               <div style="width:6px;height:36px;border-radius:3px;background:{col};flex-shrink:0"></div>
#               <div style="flex:1">
#                 <div style="font-size:.83rem;font-weight:500;color:#2a1f1a">{CLASSES_FR.get(pathologie,pathologie)}</div>
#                 <div style="font-size:.7rem;color:#b5a89e;letter-spacing:.3px">{date}</div>
#               </div>
#               <span style="font-family:'DM Serif Display',serif;font-size:.95rem;color:{col}">{round(confiance)}%</span>
#             </div>""")

# # ══════════════════════════════════════════════════════════════════════════════
# # PAGE FICHES
# # ══════════════════════════════════════════════════════════════════════════════
# elif page == "Fiches":
#     html('<div class="sk-title">Fiches pathologies</div>')
#     html('<div class="sk-sub">Comprends chaque condition détectée par l\'IA</div>')
#     col1, col2 = st.columns(2)
#     for i,(key,f) in enumerate(FICHES.items()):
#         with col1 if i%2==0 else col2:
#             html(f"""<div class="fiche-box">
#               <div style="display:flex;align-items:center;gap:.6rem;margin-bottom:.5rem">
#                 <div style="width:30px;height:30px;border-radius:8px;background:{f['color_l']};
#                             display:flex;align-items:center;justify-content:center;font-size:14px">{f['emoji']}</div>
#                 <div style="font-family:'DM Serif Display',serif;font-size:.95rem;color:#2a1f1a">{f['titre']}</div>
#               </div>
#               <p style="font-size:.73rem;color:#7a6860;line-height:1.55;margin-bottom:.4rem">{f['desc']}</p>
#               <div style="font-size:.68rem;color:#b5a89e;margin-bottom:.2rem"><b style="color:{f['color']}">Causes :</b> {f['causes']}</div>
#               <div style="font-size:.68rem;color:#b5a89e;margin-bottom:.4rem"><b style="color:{f['color']}">Traitement :</b> {f['traitement']}</div>
#               <span class="pill" style="background:{f['color_l']};color:{f['color']};border:1px solid {f['color']}40">{f['tag']}</span>
#             </div>""")

# # ══════════════════════════════════════════════════════════════════════════════
# # PAGE WEBCAM AR
# # ══════════════════════════════════════════════════════════════════════════════
# elif page == "Webcam AR":
#     html('<div class="sk-title">Webcam AR</div>')
#     html('<div class="sk-sub">Overlay temps réel selon la pathologie détectée · MediaPipe FaceMesh</div>')

#     pathologie = st.session_state.get("derniere_pathologie", "acne_inflammatoire")
#     AR_COLORS_BGR = {
#         "saine":                  (135, 158, 122),
#         "acne_inflammatoire":     (90,  124, 196),
#         "acne_non_inflammatoire": (130, 168, 212),
#         "rosacee":                (166, 127, 155),
#         "hyperpigmentation":      (135, 158, 122),
#     }
#     ZONE_LANDMARKS = {
#         "front":  [10,338,297,332,284,251,389,356,454,323,361,288,397,365,379,378,400,377,152,148,176,149,150,136,172,58,132,93,234,127,162,21,54,103,67,109],
#         "joue_g": [234,93,132,58,172,136,150,149,176,148,152,377,400,378,379,365,397,288,361,323,454,356,389,251,284,332,297,338],
#         "joue_d": [454,323,361,288,397,365,379,378,400,377,152,148,176,149,150,136,172,58,132,93,234,127,162,21,54,103,67,109],
#         "menton": [152,148,176,149,150,136,172,58,132,93,234,127],
#         "nez":    [1,2,5,4,6,19,94,125,354,370,327,326,97,99,60,75],
#     }
#     ZONES_PAR_PATHOLOGIE = {
#         "acne_inflammatoire":     ["front","joue_g","joue_d","menton"],
#         "acne_non_inflammatoire": ["front","nez"],
#         "rosacee":                ["joue_g","joue_d","nez"],
#         "hyperpigmentation":      ["front","joue_g","joue_d"],
#         "saine":                  [],
#     }

#     col_info, col_ctrl = st.columns([2,1])
#     with col_info:
#         zones_str = ", ".join(ZONES_PAR_PATHOLOGIE.get(pathologie,[])) or "aucune (peau saine)"
#         html(f"""<div class="fiche-box">
#           <p style="font-size:.72rem;color:#c47c5a;font-weight:500;margin-bottom:.4rem">Pathologie active · {CLASSES_FR[pathologie]}</p>
#           <p style="font-size:.75rem;color:#7a6860;margin-bottom:.3rem">Zones ciblées : <b style="color:#2a1f1a">{zones_str}</b></p>
#           <p style="font-size:.72rem;color:#b5a89e">MediaPipe FaceMesh place 468 landmarks sur ton visage en temps réel. L'overlay suit précisément les zones anatomiques concernées.</p>
#         </div>""")
#     with col_ctrl:
#         opacity = st.slider("Opacité overlay", 0.1, 0.6, 0.3, 0.05)
#         activer = st.button("Activer la caméra", use_container_width=True)

#     warn("Le flux webcam tourne à ~10 fps dans Streamlit — suffisant pour une démo.")

#     if activer:
#         try:
#             import mediapipe as mp
#             mp_face      = mp.solutions.face_mesh
#             zones_actives = ZONES_PAR_PATHOLOGIE.get(pathologie, [])
#             couleur_bgr   = AR_COLORS_BGR.get(pathologie, (90,124,196))
#             frame_holder  = st.empty()
#             stop_btn      = st.button("⏹ Arrêter la caméra")
#             cap = cv2.VideoCapture(0)

#             if not cap.isOpened():
#                 st.error("Impossible d'ouvrir la caméra. Essaie VideoCapture(1) dans le code.")
#             else:
#                 with mp_face.FaceMesh(max_num_faces=1, refine_landmarks=True,
#                                       min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:
#                     while cap.isOpened() and not stop_btn:
#                         ret, frame = cap.read()
#                         if not ret: break
#                         frame = cv2.flip(frame, 1)
#                         rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#                         res   = face_mesh.process(rgb)

#                         if res.multi_face_landmarks and zones_actives:
#                             h, w  = frame.shape[:2]
#                             overlay = frame.copy()
#                             for zone in zones_actives:
#                                 indices = ZONE_LANDMARKS.get(zone, [])
#                                 pts = np.array([
#                                     (int(res.multi_face_landmarks[0].landmark[i].x * w),
#                                      int(res.multi_face_landmarks[0].landmark[i].y * h))
#                                     for i in indices if i < 468
#                                 ], dtype=np.int32)
#                                 if len(pts) >= 3:
#                                     hull = cv2.convexHull(pts)
#                                     cv2.fillConvexPoly(overlay, hull, couleur_bgr)
#                             frame = cv2.addWeighted(overlay, opacity, frame, 1-opacity, 0)

#                         frame_holder.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
#                                            channels="RGB", use_container_width=True)
#                 cap.release()

#         except ImportError:
#             st.error("MediaPipe non installé. Lance : pip install mediapipe")
#         except Exception as e:
#             st.error(f"Erreur webcam : {e}")