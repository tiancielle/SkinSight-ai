// ── SkinSight AI — config.js ──────────────────────────────────────────────────
// Constantes partagées entre tous les fichiers JS

const API = 'http://localhost:8000';

const COLORS = {
  saine:                  '#7a9e87',
  acne_inflammatoire:     '#c47c5a',
  acne_non_inflammatoire: '#d4a882',
  rosacee:                '#9b7fa6',
  hyperpigmentation:      '#7a9e87',
};

const CLASSES_FR = {
  saine:                  'Peau saine',
  acne_inflammatoire:     'Acné inflammatoire',
  acne_non_inflammatoire: 'Acné non inflammatoire',
  rosacee:                'Rosacée',
  hyperpigmentation:      'Hyperpigmentation',
};

const FICHES = [
  { key:'acne_inflammatoire',     titre:'Acné inflammatoire',
    desc:"Papules et pustules rouges issues d'une infection bactérienne (C. acnes) du follicule pileux.",
    causes:'Excès de sébum, bactéries, hormones, stress',
    traitement:'Acide salicylique, niacinamide, peroxyde de benzoyle',
    tag:'Très fréquent', color:'#c47c5a', colorL:'#f7ede6' },
  { key:'acne_non_inflammatoire', titre:'Acné non inflammatoire',
    desc:"Points noirs et blancs. Excès de sébum obstruant les pores sans infection active.",
    causes:'Hyperséborrhée, kératinisation excessive',
    traitement:'BHA, rétinoïdes, exfoliation douce',
    tag:'Courant', color:'#d4a882', colorL:'#fdf3ec' },
  { key:'rosacee',                titre:'Rosacée',
    desc:"Affection chronique causant des rougeurs persistantes et des vaisseaux visibles.",
    causes:'Génétique, soleil, alcool, épices, chaleur',
    traitement:'Acide azélaïque, métronidazole, SPF minéral',
    tag:'Chronique', color:'#9b7fa6', colorL:'#f0eaf4' },
  { key:'hyperpigmentation',      titre:'Hyperpigmentation',
    desc:"Taches sombres dues à un excès de mélanine : exposition UV, hormones, cicatrices.",
    causes:'Soleil, hormones, inflammation, cicatrices',
    traitement:'Vitamine C, rétinoïdes, acide kojique, SPF 50+',
    tag:'Traitable', color:'#7a9e87', colorL:'#eaf2ed' },
  { key:'saine',                  titre:'Peau saine',
    desc:"Aucune pathologie détectée. Aspect uniforme, bonne hydratation, barrière cutanée intacte.",
    causes:'Bonne hygiène, hydratation, alimentation équilibrée',
    traitement:'Entretien préventif, SPF quotidien, antioxydants',
    tag:'Excellent', color:'#7a9e87', colorL:'#eaf2ed' },
];

const ROUTINES = {
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
