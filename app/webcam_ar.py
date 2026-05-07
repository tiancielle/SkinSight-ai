"""
SkinSight AI — app/webcam_ar.py
Serveur WebSocket : reçoit frames JPEG → MediaPipe Face Mesh → retourne landmarks JSON

Lancement :
    conda activate skinsight
    python app/webcam_ar.py
    → ws://localhost:8765
"""

import asyncio
import base64
import json
import os

import numpy as np
import cv2
import websockets

# ── MediaPipe — Compatibilité toutes versions ────────────────────────────────
try:
    import mediapipe as mp
    # Compatibilité toutes versions MediaPipe
    _fm = __import__('mediapipe.python.solutions.face_mesh', fromlist=['FaceMesh'])
    FaceMesh = _fm.FaceMesh
    MEDIAPIPE_OK = True
    print("[webcam_ar] ✅ MediaPipe chargé")
except Exception as e:
    MEDIAPIPE_OK = False
    print(f"[webcam_ar] ⚠️  MediaPipe indisponible : {e}")

# ── Zones anatomiques (indices landmarks MediaPipe Face Mesh) ──────────────────
ZONES = {
    "Front":       [10, 67, 109, 338, 297, 332, 333, 334, 296, 336],
    "JoueGauche":  [234, 93, 132, 58, 172, 136, 150, 149, 176, 148],
    "JoueDroite":  [454, 323, 361, 288, 397, 365, 379, 378, 400, 377],
    "Nez":         [1, 2, 4, 5, 6, 19, 20, 94, 125, 354],
    "Menton":      [18, 200, 199, 175, 152, 171, 148, 176, 149, 150],
}

# Zones actives par pathologie
ZONE_MAP = {
    "acne_inflammatoire":     ["Front", "JoueGauche", "JoueDroite", "Menton"],
    "acne_non_inflammatoire": ["Front", "Nez"],
    "rosacee":                ["JoueGauche", "JoueDroite", "Nez"],
    "hyperpigmentation":      ["Front", "JoueGauche", "JoueDroite"],
    "saine":                  [],
}

ZONE_COLORS = {
    "acne_inflammatoire":     [196, 124, 90],
    "acne_non_inflammatoire": [212, 168, 130],
    "rosacee":                [155, 127, 166],
    "hyperpigmentation":      [122, 158, 135],
    "saine":                  [122, 158, 135],
}

# ── WebSocket handler ──────────────────────────────────────────────────────────
async def handle(websocket):
    print(f"[webcam_ar] Client connecté : {websocket.remote_address}")

    # ── Initialisation FaceMesh (ancienne API compatible) ───────────────────
    face_mesh = FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) if MEDIAPIPE_OK else None

    try:
        async for message in websocket:
            try:
                # Message JSON : { "frame": "<base64 jpeg>", "pathologie": "acne_inflammatoire" }
                data       = json.loads(message)
                pathologie = data.get("pathologie", "acne_inflammatoire")
                frame_b64  = data.get("frame", "")

                # Décoder la frame JPEG
                img_bytes = base64.b64decode(frame_b64.split(",")[-1])
                nparr     = np.frombuffer(img_bytes, np.uint8)
                frame     = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if frame is None:
                    await websocket.send(json.dumps({"landmarks": [], "error": "frame invalide"}))
                    continue

                h, w = frame.shape[:2]

                if not MEDIAPIPE_OK or face_mesh is None:
                    # Fallback : retourner zones simulées
                    await websocket.send(json.dumps({
                        "landmarks": [],
                        "simulated": True,
                        "width": w,
                        "height": h,
                    }))
                    continue

                # ── Détection avec MediaPipe FaceMesh ───────────────────────
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results   = face_mesh.process(frame_rgb)

                if not results.multi_face_landmarks:
                    await websocket.send(json.dumps({
                        "landmarks": [],
                        "face_detected": False,
                        "width": w,
                        "height": h,
                    }))
                    continue

                lms = results.multi_face_landmarks[0].landmark

                # Extraire les coordonnées pixel des zones actives
                active_zones = ZONE_MAP.get(pathologie, [])
                zones_data   = {}

                for zone_name in active_zones:
                    if zone_name not in ZONES:
                        continue
                    pts = []
                    for idx in ZONES[zone_name]:
                        if idx < len(lms):
                            lm = lms[idx]
                            pts.append([
                                round(lm.x * w),
                                round(lm.y * h),
                            ])
                    if pts:
                        zones_data[zone_name] = pts

                color = ZONE_COLORS.get(pathologie, [196, 124, 90])

                response = {
                    "face_detected": True,
                    "zones":         zones_data,
                    "color":         color,
                    "pathologie":    pathologie,
                    "width":         w,
                    "height":        h,
                }
                await websocket.send(json.dumps(response))

            except Exception as e:
                print(f"[webcam_ar] Erreur traitement frame : {e}")
                await websocket.send(json.dumps({"error": str(e)}))

    except websockets.exceptions.ConnectionClosedOK:
        print("[webcam_ar] Client déconnecté proprement")
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"[webcam_ar] Connexion fermée avec erreur : {e}")
    finally:
        if face_mesh:
            face_mesh.close()

# ── Main ───────────────────────────────────────────────────────────────────────
async def main():
    print("[webcam_ar] Serveur WebSocket démarré sur ws://localhost:8765")
    print("[webcam_ar] En attente de connexions...")
    async with websockets.serve(handle, "localhost", 8765):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())