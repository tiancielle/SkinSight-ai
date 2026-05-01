"""
SkinSight AI — Moteur de recommandation dermatologique
Prend la classe prédite + score de confiance → retourne un diagnostic structuré.
"""
from dataclasses import dataclass, asdict
from typing import Optional
import json


# ─── Règles de recommandation ─────────────────────────────────────────────────

RECOMMANDATIONS = {
    "saine": {
        "diagnostic": "Peau saine",
        "description": "Aucune pathologie détectée. La peau présente un aspect sain.",
        "traitements": [],
        "routine": [
            "Nettoyant doux quotidien",
            "Hydratant adapté au type de peau",
            "SPF 30+ le matin"
        ],
        "urgence": "Aucune — continuer la routine de soin préventive.",
        "emoji": "✅"
    },
    "acne_inflammatoire": {
        "diagnostic": "Acné inflammatoire (papules / pustules)",
        "description": "Présence de lésions rouges, gonflées ou contenant du pus.",
        "traitements": [
            "Peroxyde de benzoyle 5% (matin)",
            "Trétinoïne 0.025% (soir — introduire progressivement)",
            "Clindamycine topique si surinfection"
        ],
        "routine": [
            "Nettoyant à l'acide salicylique",
            "Sérum anti-bactérien (niacinamide 10%)",
            "Hydratant non-comédogène",
            "SPF 50 (la trétinoïne photosensibilise)"
        ],
        "urgence": "Consulter un dermatologue si absence d'amélioration après 6 semaines.",
        "emoji": "⚠️"
    },
    "acne_non_inflammatoire": {
        "diagnostic": "Acné rétentionnelle (comédons ouverts / fermés)",
        "description": "Points noirs (comédons ouverts) ou points blancs (comédons fermés) sans inflammation.",
        "traitements": [
            "Acide salicylique 2% (exfoliation keratolytique)",
            "Rétinol 0.1–0.3% (accélère le renouvellement cellulaire)"
        ],
        "routine": [
            "Exfoliant doux 2×/semaine",
            "Sérum pores serrés (niacinamide)",
            "Hydratant léger non-comédogène",
            "SPF 30+"
        ],
        "urgence": "Non urgent — amélioration attendue en 8–12 semaines.",
        "emoji": "ℹ️"
    },
    "rosacee": {
        "diagnostic": "Rosacée (rougeurs vasculaires diffuses)",
        "description": "Rougeurs persistantes, vaisseaux visibles, parfois papules sur joues/nez.",
        "traitements": [
            "Métronidazole topique 0.75–1%",
            "Acide azélaïque 15% (anti-inflammatoire doux)"
        ],
        "routine": [
            "Nettoyant ultra-doux sans parfum ni alcool",
            "Sérum apaisant anti-rougeur (centella asiatica)",
            "SPF minéral (ZnO ou TiO2 — pas de filtres chimiques)",
            "Éviter chaleur, alcool, épices"
        ],
        "urgence": "Consultation recommandée — traitement médical souvent nécessaire.",
        "emoji": "⚠️"
    },
    "hyperpigmentation": {
        "diagnostic": "Hyperpigmentation (taches mélaniques)",
        "description": "Zones de peau plus foncées liées à une surproduction de mélanine.",
        "traitements": [
            "Vitamine C stabilisée 15–20% (matin)",
            "Niacinamide 10% (inhibe le transfert de mélanine)",
            "Acide kojique ou arbutine (dépigmentants)"
        ],
        "routine": [
            "Exfoliant chimique (AHA — acide glycolique 5–10%)",
            "Sérum éclaircissant (2×/jour)",
            "SPF 50+ impératif (le soleil aggrave les taches)"
        ],
        "urgence": "Non urgent — résultats visibles en 3–6 mois avec SPF strict.",
        "emoji": "ℹ️"
    }
}


# ─── Dataclass de sortie ───────────────────────────────────────────────────────

@dataclass
class DiagnosticResult:
    classe: str
    confiance: float          # score 0–1
    diagnostic: str
    description: str
    traitements: list
    routine: list
    urgence: str
    emoji: str
    avertissement: Optional[str] = None


# ─── Moteur ───────────────────────────────────────────────────────────────────

class RecommandationEngine:
    SEUIL_CONFIANCE_BAS = 0.55

    def predict(self, classe_predite: str, confiance: float) -> DiagnosticResult:
        """
        classe_predite : str (ex: 'acne_inflammatoire')
        confiance      : float (ex: 0.87)
        """
        if classe_predite not in RECOMMANDATIONS:
            raise ValueError(f"Classe inconnue : {classe_predite}")

        regles = RECOMMANDATIONS[classe_predite]
        avertissement = None

        if confiance < self.SEUIL_CONFIANCE_BAS:
            avertissement = (
                f"Confiance faible ({confiance:.0%}). "
                "L'analyse n'est pas certaine — consultation dermatologique recommandée."
            )

        return DiagnosticResult(
            classe=classe_predite,
            confiance=round(confiance, 3),
            diagnostic=regles["diagnostic"],
            description=regles["description"],
            traitements=regles["traitements"],
            routine=regles["routine"],
            urgence=regles["urgence"],
            emoji=regles["emoji"],
            avertissement=avertissement
        )

    def to_dict(self, result: DiagnosticResult) -> dict:
        return asdict(result)

    def to_json(self, result: DiagnosticResult) -> str:
        return json.dumps(self.to_dict(result), ensure_ascii=False, indent=2)


# ─── Usage direct ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    engine = RecommandationEngine()
    result = engine.predict("acne_inflammatoire", confiance=0.83)
    print(engine.to_json(result))
