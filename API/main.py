#!/usr/bin/env python
import os
import sys
import joblib
import warnings
from pathlib import Path
from fastapi import FastAPI, HTTPException
import math
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd

# Suppression des warnings de compatibilité
warnings.filterwarnings("ignore")

# Ajout du chemin pour les imports
CURRENT_FILE_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_FILE_DIR.parent
sys.path.append(str(REPO_ROOT))

from API.processing_elements.preprocess import preprocessor, loan_type_dtype

# Chargement des modèles avec gestion d'erreur (paths relatifs au fichier)
MODEL_PATH = REPO_ROOT / "API/ml_models/Stacking_model.pkl"
#ENCODER_PATH = 
EXPLAINER_PATH = REPO_ROOT / "API/shap_explainer/explainer.pkl"

try:
    model = joblib.load(MODEL_PATH)
    print("✅ Modèle principal chargé")
except Exception as e:
    print(f"❌ Erreur chargement modèle: {e}")
    model = None

try:
    explainer = joblib.load(EXPLAINER_PATH)
    print("✅ Explainer SHAP chargé")
except Exception as e:
    print(f"❌ Erreur chargement explainer: {e}")
    explainer = None

# Configuration FastAPI
app = FastAPI(
    title="Credit Risk Scoring API - Demo",
    description="API simplifiée pour prédiction du risque de crédit",
    version="1.0.0"
)

# Configuration CORS pour Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Demo: autoriser toute origine
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèle de données d'entrée
class LoanProfile(BaseModel):
    Total_Amount: float
    Total_Amount_to_Repay: float
    duration: int
    Lender_portion_to_be_repaid: float
    New_versus_Repeat: str
    loan_type: str

    class Config:
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

# Endpoint racine
@app.get("/")
def root():
    return {
        "message": "Credit Risk Scoring API - Ready for demo",
        "status": "online",
        "endpoints": ["/predict", "/proba", "/explain", "/metadata", "/health"]
    }

# Endpoint de santé
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "explainer_loaded": explainer is not None,
    }

# Endpoint metadata (valeurs de référence)
@app.get("/metadata")
def metadata():
    try:
        loan_types = [str(x) for x in getattr(loan_type_dtype, 'categories', [])].sort()
        new_repeat_loan = ['New Loan', 'Repeat Loan']
        return {"loan_types": loan_types, "new_repeat_loan" : new_repeat_loan}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur metadata: {str(e)}")

# Endpoint de prédiction
@app.post("/predict")
def predict(profile: LoanProfile):
    """
    Prédire le risque de défaut pour un profil de prêt
    
    Returns:
        - probability: Probabilité de défaut (0-1)
        - prediction: Classe prédite (0=pas de défaut, 1=défaut)
        - risk_level: Niveau de risque (Low/Medium/High)
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Modèle non disponible")
        
    try:
        # Conversion en DataFrame
        df = pd.DataFrame([profile.model_dump()])
        # Preprocessing
        df_preprocessed = preprocessor(df)
        # Prédiction
        proba = float(model.predict_proba(df_preprocessed)[0][1])
        pred = int(proba >= 0.5)
        # Calcul du niveau de risque
        if proba < 0.3:
            risk_level = "Low"
        elif proba < 0.7:
            risk_level = "Medium"
        else:
            risk_level = "High"

        # Confiance basée sur l'entropie (plus informatif que max(p,1-p))
        # H(p) = -[p log2 p + (1-p) log2 (1-p)] ; certitude = 1 - H(p), bornée dans [0,1]
        p = min(max(proba, 1e-12), 1 - 1e-12)
        entropy = -(p * math.log(p, 2) + (1 - p) * math.log(1 - p, 2))
        confidence = max(0.0, min(1.0, 1.0 - entropy))
        return {
            "probability": round(proba, 4),
            "prediction": pred,
            "risk_level": risk_level,
            "confidence": round(confidence, 4),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la prédiction: {str(e)}")

# Endpoint probabilité seule
@app.post("/proba")
def proba(profile: LoanProfile):
    if model is None:
        raise HTTPException(status_code=503, detail="Modèle non disponible")
    try:
        df = pd.DataFrame([profile.model_dump()])
        df_preprocessed = preprocessor(df)
        proba_val = float(model.predict_proba(df_preprocessed)[0][1])
        return {"probability": round(proba_val, 4)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul de probabilité: {str(e)}")

# Endpoint d'explication
@app.post("/explain")
def explain(profile: LoanProfile):
    """
    Expliquer la prédiction avec SHAP values
    
    Returns:
        - prediction: Classe prédite
        - probability: Probabilité de défaut
        - base_value: Valeur de base du modèle
        - contributions: Contribution de chaque feature
        - top_features: Top 5 des features les plus importantes
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Modèle non disponible")
    
    if explainer is None:
        # Fallback sans SHAP - juste les prédictions
        df = pd.DataFrame([profile.model_dump()])
        df_preprocessed = preprocessor(df)
        proba = float(model.predict_proba(df_preprocessed)[0][1])
        pred = int(proba >= 0.5)
        
        return {
            "prediction": pred,
            "probability": round(float(proba), 4),
            "base_value": 0.5,
            "contributions": {"message": "Explainer SHAP non disponible"},
            "top_features": [{"feature": "N/A", "contribution": 0, "impact": "unknown"}]
        }
        
    try:
        # Conversion en DataFrame
        df = pd.DataFrame([profile.model_dump()])
        # Preprocessing
        df_preprocessed = preprocessor(df)
        # Prédiction
        proba = float(model.predict_proba(df_preprocessed)[0][1])
        pred = int(proba >= 0.5)
        # SHAP values
        shap_values = explainer.shap_values(df_preprocessed)
        # Gestion du format des SHAP values
        if isinstance(shap_values, list):
            shap_vector = shap_values[1][0]  # Classe positive
        else:
            shap_vector = shap_values[0]
        # Base value
        base_value = explainer.expected_value
        if isinstance(base_value, list):
            base_value = float(base_value[1])
        else:
            base_value = float(base_value)
        # Contributions par feature
        #feature_names = df_preprocessed.columns.tolist()
        feature_names = ["Montant à rembourser", "Durée", "Part prêteur à rembourser", "Statut du client", "Type de prêt"]
        contributions = {str(feature): float(shap_val) for feature, shap_val in zip(feature_names, shap_vector)}
        # Top 5 des features les plus importantes (valeur absolue)
        sorted_contributions = sorted(contributions.items(), key=lambda x: abs(x[1]), reverse=True)
        top_features = [
            {"feature": feature, "contribution": contrib, "impact": "increases_risk" if contrib > 0 else "decreases_risk"}
            for feature, contrib in sorted_contributions[:5]
        ]
        return {
            "prediction": pred,
            "probability": round(float(proba), 4),
            "base_value": round(base_value, 4),
            "contributions": {k: round(v, 4) for k, v in contributions.items()},
            "top_features": top_features,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'explication: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
