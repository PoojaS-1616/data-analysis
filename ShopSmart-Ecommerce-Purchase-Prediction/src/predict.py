"""Reusable batch prediction module and CLI using the saved Logistic Regression pipeline."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
import joblib
import pandas as pd

# Ensure project root is importable when run directly as a script
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import CAT_COLS, ID_COL, MODEL_PATH, NUM_COLS
from src.preprocessing import assign_marketing_segment


def predict_dataframe(
    df: pd.DataFrame,
    model_path: Path | str = MODEL_PATH,
    threshold: float = 0.50,
) -> pd.DataFrame:
    """Score a DataFrame with the saved pipeline and return predictions + marketing segments."""
    required = set(CAT_COLS + NUM_COLS)
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Input DataFrame missing required feature columns: {sorted(missing)}")

    pipe = joblib.load(model_path)
    X = df[CAT_COLS + NUM_COLS]
    probs = pipe.predict_proba(X)[:, 1]
    preds = (probs >= threshold).astype(int)

    out = pd.DataFrame(index=df.index)
    if ID_COL in df.columns:
        out[ID_COL] = df[ID_COL]
    out["Purchase_Probability"] = probs.round(6)
    out["Predicted_Purchase"] = preds
    out["Marketing_Segment"] = [assign_marketing_segment(float(p)) for p in probs]
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Run batch purchase prediction on a CSV file.")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--output", required=True, help="Path to write predictions CSV")
    parser.add_argument("--model", default=str(MODEL_PATH), help="Path to saved joblib pipeline")
    parser.add_argument("--threshold", type=float, default=0.50, help="Decision threshold (default 0.50)")
    args = parser.parse_args()

    in_df = pd.read_csv(args.input)
    res = predict_dataframe(in_df, model_path=args.model, threshold=args.threshold)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    res.to_csv(args.output, index=False)
    print(f"Scored {len(res):,} rows -> saved to {args.output}")


if __name__ == "__main__":
    main()
