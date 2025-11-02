#!/usr/bin/env python3
"""
Generate demo presets from a filtered CSV (nouvelle_donnee_predite_filtre.csv).

Features:
- Validates required columns
- Buckets by probability_default: Low (<0.3), Medium (0.3-0.7), High (>=0.7)
- Picks a balanced set: top-N high, N closest to 0.5 for medium, bottom-N low
- Writes JSON list suitable for use in the web app (public/presets.json)

Usage:
  python Data/generate_presets.py \
    --csv Data/nouvelle_donnee_predite_filtre.csv \
    --out web/public/presets.json

Optional:
  --n-high 4 --n-mid 3 --n-low 3  # adjust counts
  --stdout                        # print to stdout instead of file
  --dry-run                       # validate and show counts only
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from typing import Dict, List, Any


REQUIRED_COLS = [
    "Total_Amount",
    "Total_Amount_to_Repay",
    "duration",
    "Lender_portion_to_be_repaid",
    "New_versus_Repeat",
    "loan_type",
    "probability_default",
]


def coerce_row(raw: Dict[str, str]) -> Dict[str, Any] | None:
    try:
        return {
            "Total_Amount": float(raw["Total_Amount"]),
            "Total_Amount_to_Repay": float(raw["Total_Amount_to_Repay"]),
            "duration": int(float(raw["duration"])),
            "Lender_portion_to_be_repaid": float(raw["Lender_portion_to_be_repaid"]),
            "New_versus_Repeat": str(raw["New_versus_Repeat"]),
            "loan_type": str(raw["loan_type"]).strip(),
            "probability_default": float(raw["probability_default"]),
        }
    except Exception:
        return None


def load_rows(csv_path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    rows: List[Dict[str, Any]] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLS if c not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        for r in reader:
            coerced = coerce_row(r)
            if coerced is not None:
                # drop NaNs or invalid numerics
                if any(
                    v is None or (isinstance(v, float) and (v != v))  # NaN check
                    for k, v in coerced.items()
                    if k != "loan_type"
                ):
                    continue
                rows.append(coerced)
    return rows


def _sig(r: Dict[str, Any]) -> tuple:
    return (
        round(float(r["Total_Amount"]), 6),
        round(float(r["Total_Amount_to_Repay"]), 6),
        int(r["duration"]),
        round(float(r["Lender_portion_to_be_repaid"]), 6),
        str(r["New_versus_Repeat"]),
        str(r["loan_type"]),
        round(float(r["probability_default"]), 6),
    )


def _pick_unique(sorted_rows: List[Dict[str, Any]], target: int) -> List[Dict[str, Any]]:
    seen = set()
    out: List[Dict[str, Any]] = []
    for r in sorted_rows:
        s = _sig(r)
        if s in seen:
            continue
        seen.add(s)
        out.append(r)
        if len(out) >= target:
            break
    return out


def select_presets(rows: List[Dict[str, Any]], n_high=4, n_mid=3, n_low=3) -> List[Dict[str, Any]]:
    hi_all = [r for r in rows if r["probability_default"] >= 0.7]
    mid_all = [r for r in rows if 0.3 <= r["probability_default"] < 0.7]
    lo_all = [r for r in rows if r["probability_default"] < 0.3]

    hi_sorted = sorted(hi_all, key=lambda r: -r["probability_default"])  # highest first
    mid_sorted = sorted(mid_all, key=lambda r: abs(r["probability_default"] - 0.5))  # closest to 0.5
    lo_sorted = sorted(lo_all, key=lambda r: r["probability_default"])  # lowest first

    hi = _pick_unique(hi_sorted, n_high)
    mid = _pick_unique(mid_sorted, n_mid)
    lo = _pick_unique(lo_sorted, n_low)

    # If a bucket has fewer unique rows than target, try to fill from remaining of same bucket
    if len(hi) < n_high:
        hi = _pick_unique(hi_sorted, n_high)
    if len(mid) < n_mid:
        mid = _pick_unique(mid_sorted, n_mid)
    if len(lo) < n_low:
        lo = _pick_unique(lo_sorted, n_low)

    sel = hi + mid + lo
    return sel[: n_high + n_mid + n_low]


def to_items(selected: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for r in selected:
        p = float(r["probability_default"])
        bucket = "Low" if p < 0.3 else ("Medium" if p < 0.7 else "High")
        name = f"{bucket} — {r['loan_type']} — p={p:.2f}"
        items.append(
            {
                "name": name,
                "data": {
                    "Total_Amount": r["Total_Amount"],
                    "Total_Amount_to_Repay": r["Total_Amount_to_Repay"],
                    "duration": int(r["duration"]),
                    "Lender_portion_to_be_repaid": r["Lender_portion_to_be_repaid"],
                    "New_versus_Repeat": r["New_versus_Repeat"],
                    "loan_type": r["loan_type"],
                },
            }
        )
    return items


def detect_default_out() -> str:
    # Prefer web/public if it exists
    web_pub = os.path.join("web", "public")
    if os.path.isdir(web_pub):
        return os.path.join(web_pub, "presets.json")
    return "presets.json"


def main(argv: List[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Generate demo presets JSON from CSV")
    p.add_argument("--csv", dest="csv_path", default=os.path.join("Data", "nouvelle_donnee_predite_filtre.csv"))
    p.add_argument("--n-high", type=int, default=4)
    p.add_argument("--n-mid", type=int, default=3)
    p.add_argument("--n-low", type=int, default=3)
    p.add_argument("--out", dest="out_path", default=None, help="Output file path; defaults to web/public/presets.json if exists, else presets.json")
    p.add_argument("--stdout", action="store_true", help="Print JSON to stdout instead of writing to a file")
    p.add_argument("--dry-run", action="store_true", help="Validate and show bucket counts without writing output")
    args = p.parse_args(argv)

    try:
        rows = load_rows(args.csv_path)
    except Exception as e:
        print(json.dumps({"error": "load_failed", "message": str(e)}))
        return 1

    selected = select_presets(rows, n_high=args.n_high, n_mid=args.n_mid, n_low=args.n_low)
    items = to_items(selected)

    if args.dry_run:
        hi = sum(1 for r in selected if r["probability_default"] >= 0.7)
        mid = sum(1 for r in selected if 0.3 <= r["probability_default"] < 0.7)
        lo = sum(1 for r in selected if r["probability_default"] < 0.3)
        print(json.dumps({
            "total_rows": len(rows),
            "selected": len(selected),
            "buckets": {"high": hi, "medium": mid, "low": lo},
        }, ensure_ascii=False))
        return 0

    if args.stdout:
        print(json.dumps(items, ensure_ascii=False))
        return 0

    out_path = args.out_path or detect_default_out()
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
