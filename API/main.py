#!/usr/bin/env python
import os
import sys
import time
import math
import warnings
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from collections import defaultdict, deque
from typing import Optional, Dict

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Chargement des variables d'environnement
load_dotenv()

# Suppression des warnings
warnings.filterwarnings("ignore")

# --- Logger Configuration ---
try:
    # Tentative d'import absolu (cas lancement depuis root 'python -m uvicorn API.main:app')
    from API.logger_config import logger
except ImportError:
    try:
        # Tentative d'import relatif (cas lancement depuis API/ 'python main.py')
        from logger_config import logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("API")
        logger.warning("Logger Loguru non chargé, pas de logs fichier.")

# --- Configuration des chemins et imports ---
CURRENT_FILE_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_FILE_DIR.parent

# Ajout du root au path pour permettre les imports absolus 'API.processing_elements...'
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

# Tentative d'import du préprocesseur
try:
    from API.processing_elements.preprocess import preprocessor, loan_type_dtype
except Exception as e:
    logger.error(f"Erreur CRITIQUE d'import du preprocessing : {e}")
    preprocessor = None
    loan_type_dtype = None

# --- Chargement des artefacts ML ---
MODEL_PATH = CURRENT_FILE_DIR / "ml_models/Stacking_model.pkl"
EXPLAINER_PATH = CURRENT_FILE_DIR / "shap_explainer/explainer.pkl"

def load_artifact(path: Path, label: str):
    if not path.exists():
        logger.warning(f"⚠️ Artefact absent : {path} ({label})")
        return None
    try:
        obj = joblib.load(path)
        logger.info(f"✅ {label} chargé")
        return obj
    except Exception as e:
        logger.error(f"❌ Erreur chargement {label} : {e}")
        return None

model = load_artifact(MODEL_PATH, "Modèle Stacking")
explainer = load_artifact(EXPLAINER_PATH, "Explainer SHAP")

# --- Configuration FastAPI ---
app = FastAPI(
    title="Credit Risk Scoring API",
    description="API de prédiction de risque de crédit avec explicabilité SHAP.",
    version="1.1.0"
)

# Sécurité & CORS
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")
origins_list = ["*"] if ALLOWED_ORIGINS == "*" else [o.strip() for o in ALLOWED_ORIGINS.split(",") if o]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Rate Limiting & Auth ---
RATE_LIMIT_PER_MIN = int(os.getenv("RATE_LIMIT_PER_MIN", "60"))
API_KEY_EXPECTED = os.getenv("API_KEY") # Peut être None (mode ouvert)

# Store simple avec nettoyage
_rate_store: Dict[str, deque] = defaultdict(deque)

def _clean_rate_store():
    """Nettoyage simple pour éviter fuite mémoire"""
    if len(_rate_store) > 1000:
        _rate_store.clear()

def _check_rate_limit(key: str) -> bool:
    now = time.time()
    dq = _rate_store[key]
    
    # Retirer les requêtes plus vieilles que 60s
    while dq and dq[0] < now - 60:
        dq.popleft()
    
    if len(dq) >= RATE_LIMIT_PER_MIN:
        return False
    
    dq.append(now)
    _clean_rate_store() # Nettoyage occasionnel
    return True

async def verify_api_key(
    x_api_key: Optional[str] = Header(None), 
    authorization: Optional[str] = Header(None)
) -> str:
    """
    Vérifie la clé API. 
    Si API_KEY n'est pas défini dans l'env, l'accès est public (warning).
    """
    if not API_KEY_EXPECTED:
        return "public"
        
    token = x_api_key
    if not token and authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
    
    if not token:
        raise HTTPException(status_code=401, detail="API Key manquante")
    if token != API_KEY_EXPECTED:
        raise HTTPException(status_code=403, detail="API Key invalide")
        
    return token

async def rate_limiter_dependency(request: Request, api_ident: str = Depends(verify_api_key)):
    # Identifiant pour le rate limit : clé API ou IP si public
    key = api_ident if api_ident != "public" else (request.client.host or "unknown")
    if not _check_rate_limit(key):
        raise HTTPException(status_code=429, detail="Too Many Requests")

# --- Modèles Pydantic ---
class LoanProfile(BaseModel):
    Total_Amount: float
    Total_Amount_to_Repay: float
    duration: int
    Lender_portion_to_be_repaid: float
    New_versus_Repeat: str
    loan_type: str

    class Config:
        # Compatible Pydantic v1/v2 (selon version installée)
        schema_extra = {
            "example": {
                "Total_Amount": 1000.0,
                "Total_Amount_to_Repay": 1200.0,
                "duration": 90,
                "Lender_portion_to_be_repaid": 1200.0,
                "New_versus_Repeat": "Repeat Loan",
                "loan_type": "Type_7"
            }
        }

# --- Routes ---

@app.get("/")
def root():
    return {
        "message": "Credit Risk Scoring API - Ready",
        "status": "online",
        "auth_enabled": bool(API_KEY_EXPECTED),
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "explainer_loaded": explainer is not None,
        "preprocessing_loaded": preprocessor is not None
    }

@app.get("/metadata", dependencies=[Depends(rate_limiter_dependency)])
def metadata():
    if not loan_type_dtype:
        raise HTTPException(status_code=503, detail="Preprocessing non disponible")
    try:
        # Gestion safe de loan_type_dtype
        cats = getattr(loan_type_dtype, 'categories', [])
        return {
            "loan_types": sorted([str(x) for x in cats]),
            "new_repeat_loan": ['New Loan', 'Repeat Loan']
        }
    except Exception as e:
        logger.error(f"Metadata error: {e}")
        raise HTTPException(status_code=500, detail="Erreur metadata")

@app.post("/predict", dependencies=[Depends(rate_limiter_dependency)])
def predict(profile: LoanProfile):
    if not model or not preprocessor:
        raise HTTPException(status_code=503, detail="Modèle non disponible")
        
    try:
        df = pd.DataFrame([profile.model_dump()])
        # Appel preprocessor
        X = preprocessor(df)
        
        # Prédiction (proba classe 1)
        proba = float(model.predict_proba(X)[0][1])
        prediction = 1 if proba >= 0.5 else 0
        
        # Risk Level
        if proba < 0.3: level = "Low"
        elif proba < 0.7: level = "Medium"
        else: level = "High"
        
        # Confiance (Entropie)
        # Évite log(0)
        p_safe = max(min(proba, 1 - 1e-9), 1e-9)
        entropy = -(p_safe * math.log2(p_safe) + (1 - p_safe) * math.log2(1 - p_safe))
        confidence = max(0.0, 1.0 - entropy)

        return {
            "probability": round(proba, 4),
            "prediction": prediction,
            "risk_level": level,
            "confidence": round(confidence, 4),
        }
    except Exception as e:
        logger.error(f"Predict error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/proba", dependencies=[Depends(rate_limiter_dependency)])
def proba(profile: LoanProfile):
    if not model or not preprocessor:
        raise HTTPException(status_code=503, detail="Modèle non disponible")
    try:
        df = pd.DataFrame([profile.model_dump()])
        X = preprocessor(df)
        val = float(model.predict_proba(X)[0][1])
        return {"probability": round(val, 4)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/explain", dependencies=[Depends(rate_limiter_dependency)])
def explain(profile: LoanProfile):
    """
    Retourne les contributions SHAP.
    Mode dégradé si explainer non disponible ou erreur.
    """
    if not model or not preprocessor:
        raise HTTPException(status_code=503, detail="Modèle non disponible")

    # Prédiction de base (toujours nécessaire)
    try:
        df = pd.DataFrame([profile.model_dump()])
        X = preprocessor(df)
        proba = float(model.predict_proba(X)[0][1])
        pred = 1 if proba >= 0.5 else 0
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur prédiction: {e}")

    # Fallback si pas d'explainer
    if not explainer:
        return {
            "prediction": pred,
            "probability": round(proba, 4),
            "status": "warning_no_explainer",
            "base_value": 0.5,
            "contributions": {},
            "top_features": []
        }

    try:
        # Calcul SHAP
        shap_values = explainer.shap_values(X)
        
        # Extraction vecteur importance (pour classe 1)
        if isinstance(shap_values, list):
            # Classification binaire -> liste de 2 arrays
            shap_vector = shap_values[1][0]
        else:
            shap_vector = shap_values[0]

        # Base value
        bv = explainer.expected_value
        if isinstance(bv, (list, np.ndarray)):
            base_value = float(bv[1]) if len(bv) > 1 else float(bv[0])
        else:
            base_value = float(bv)

        # Mapping features (Noms en français pour l'UI actuel)
        feature_names = ["Montant à rembourser", "Durée", "Part prêteur à rembourser", "Statut du client", "Type de prêt"]
        
        contributions = {}
        for i, val in enumerate(shap_vector):
            # On mappe sur les noms tant qu'il y en a, sinon Feature_X
            fname = feature_names[i] if i < len(feature_names) else f"Feature_{i}"
            contributions[fname] = float(val)

        # Top 5
        sorted_contribs = sorted(contributions.items(), key=lambda x: abs(x[1]), reverse=True)
        top_features = [
            {"feature": k, "contribution": v, "impact": "increases_risk" if v > 0 else "decreases_risk"}
            for k, v in sorted_contribs[:5]
        ]

        return {
            "prediction": pred,
            "probability": round(proba, 4),
            "base_value": round(base_value, 4),
            "contributions": {k: round(v, 4) for k, v in contributions.items()},
            "top_features": top_features
        }

    except Exception as e:
        logger.error(f"SHAP Explainer Error: {e}")
        # Retourne tout de même la prédiction correcte
        return {
            "prediction": pred,
            "probability": round(proba, 4),
            "error": "Erreur explication", 
            "details": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    # Permet de lancer le fichier directement pour tester
    uvicorn.run(app, host="0.0.0.0", port=8000)