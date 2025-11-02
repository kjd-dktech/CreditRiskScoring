"""_summary_

    Produit pour le test (démo), un csv avec des transactions prédites ayant des probas audessus d'un certains seuil, ici : 0.2. 
"""


import sys
from pathlib import Path
import pandas as pd

REQUIRED_COLS = [
    "Total_Amount",
    "Total_Amount_to_Repay",
    "duration",
    "Lender_portion_to_be_repaid",
    "New_versus_Repeat",
    "loan_type",
    "probability_default",
]

def main(input_csv: str = "nouvelle_donnee_predite.csv",
         output_csv: str = "nouvelle_donnee_predite_filtre.csv",
         threshold: float = 0.2) -> None:
    input_path = Path(input_csv)
    if not input_path.exists():
        raise FileNotFoundError(f"Fichier introuvable: {input_path}")

    df = pd.read_csv(input_path)

    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes dans le CSV: {missing}")

    # Convertir les colonnes numériques si besoin
    numeric_cols = [
        "Total_Amount",
        "Total_Amount_to_Repay",
        "duration",
        "Lender_portion_to_be_repaid",
        "probability_default",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Masques: probabilité > seuil et champs requis non nuls
    mask_prob = df["probability_default"].fillna(0) > float(threshold)
    mask_valid = df[[
        "Total_Amount",
        "Total_Amount_to_Repay",
        "duration",
        "Lender_portion_to_be_repaid",
        "New_versus_Repeat",
        "loan_type",
    ]].notna().all(axis=1)

    df2 = df.loc[mask_prob & mask_valid].copy()

    output_path = Path(output_csv)
    if not output_path.is_absolute():
        output_path = input_path.with_name(output_csv)

    df2.to_csv(output_path, index=False)
    print(f"Lignes initiales: {len(df)} | Conservées: {len(df2)} | Seuil: {threshold}")
    print(f"Fichier écrit: {output_path}")


if __name__ == "__main__":
    # Usage: python test.py [input_csv] [output_csv] [threshold]
    args = sys.argv[1:]
    inp = args[0] if len(args) > 0 else "nouvelle_donnee_predite.csv"
    out = args[1] if len(args) > 1 else "nouvelle_donnee_predite_filtre.csv"
    thr = float(args[2]) if len(args) > 2 else 0.2
    main(inp, out, thr)