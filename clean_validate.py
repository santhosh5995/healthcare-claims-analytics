"""Data cleaning & validation for the synthetic claims files.

Checks: required columns, nulls, negative paid amounts, duplicate claim IDs,
invalid dates. Writes cleaned CSVs and loads them into a SQLite database
(claims.db) used by queries.sql.
"""
import sqlite3
import pandas as pd
from pathlib import Path

BASE = Path(__file__).parent
DATA = BASE / "data"

RX_COLS = ["claim_id", "member_id", "age_band", "service_date", "ndc", "drug_name",
           "is_generic", "quantity", "days_supply", "paid_amount", "pharmacy"]
DX_COLS = ["claim_id", "member_id", "age_band", "service_date", "icd10", "diagnosis",
           "category", "procedure_code", "provider_specialty", "paid_amount"]

def clean(df: pd.DataFrame, cols: list[str], name: str) -> pd.DataFrame:
    missing = [c for c in cols if c not in df.columns]
    assert not missing, f"{name}: missing columns {missing}"
    before = len(df)
    df["service_date"] = pd.to_datetime(df["service_date"], errors="coerce")
    bad_dates = int(df["service_date"].isna().sum())
    negatives = int((df["paid_amount"] < 0).sum())
    dupes = int(df.duplicated(subset="claim_id").sum())
    df = df.dropna(subset=["service_date"])
    df = df[df["paid_amount"] >= 0].drop_duplicates(subset="claim_id").copy()
    df["service_date"] = df["service_date"].dt.date.astype(str)
    print(f"{name}: {before} -> {len(df)} rows | removed: {negatives} negative-amount, "
          f"{dupes} duplicate claim_id, {bad_dates} bad dates, "
          f"{int(df[cols].isna().sum().sum())} null cells remaining")
    return df

if __name__ == "__main__":
    rx = clean(pd.read_csv(DATA / "pharmacy_claims.csv"), RX_COLS, "pharmacy_claims")
    dx = clean(pd.read_csv(DATA / "medical_claims.csv"), DX_COLS, "medical_claims")
    rx.to_csv(DATA / "pharmacy_claims_clean.csv", index=False)
    dx.to_csv(DATA / "medical_claims_clean.csv", index=False)
    with sqlite3.connect(BASE / "claims.db") as con:
        rx.to_sql("pharmacy_claims", con, if_exists="replace", index=False)
        dx.to_sql("medical_claims", con, if_exists="replace", index=False)
    print("Cleaned CSVs written; claims.db loaded (tables: pharmacy_claims, medical_claims).")
