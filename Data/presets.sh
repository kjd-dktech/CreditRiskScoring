#!/usr/bin/env bash
set -euo pipefail

# Generate presets JSON using the Python helper. Prefer web/public if present.
CSV_PATH="Data/nouvelle_donnee_predite_filtre.csv"
OUT_DEFAULT="web/public/presets.json"

if [ -d "web/public" ]; then
    OUT_PATH="$OUT_DEFAULT"
else
    OUT_PATH="presets.json"
fi

python Data/generate_presets.py --csv "$CSV_PATH" --out "$OUT_PATH"
echo "Presets written to $OUT_PATH"