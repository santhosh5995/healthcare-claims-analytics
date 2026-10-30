"""Synthetic healthcare claims data generator.

Produces realistic-but-clearly-FAKE pharmacy (Rx) and medical (Dx) claims.
No real patient data is used anywhere. Seeded RNG for reproducibility.
Outputs: data/pharmacy_claims.csv, data/medical_claims.csv
"""
import numpy as np
import pandas as pd
from pathlib import Path

rng = np.random.default_rng(42)
DATES = np.array(pd.date_range("2025-01-01", "2025-12-31").strftime("%Y-%m-%d"))
OUT = Path(__file__).parent / "data"
OUT.mkdir(exist_ok=True)

N_MEMBERS = 1200
member_ids = [f"M{100000 + i}" for i in range(N_MEMBERS)]
age_bands = rng.choice(["0-17", "18-34", "35-49", "50-64", "65+"], N_MEMBERS,
                       p=[0.15, 0.25, 0.25, 0.22, 0.13])
member_age = dict(zip(member_ids, age_bands))
# A few members are high-cost (chronic conditions) -> spend concentration.
high_cost = set(rng.choice(member_ids, size=48, replace=False))  # top ~4%

DRUGS = [  # ndc-like, name, is_generic, base unit cost
    ("00093-1045", "Atorvastatin 20mg", True, 0.42), ("00093-1046", "Metformin 500mg", True, 0.18),
    ("00173-0659", "Amlodipine 5mg", True, 0.25), ("00002-8214", "Lisinopril 10mg", True, 0.21),
    ("00054-0177", "Omeprazole 20mg", True, 0.35), ("00093-3420", "Levothyroxine 50mcg", True, 0.30),
    ("00002-4460", "Humira 40mg (Adalimumab)", False, 2900.0), ("00088-2220", "Ozempic 1mg (Semaglutide)", False, 880.0),
    ("00056-0175", "Eliquis 5mg (Apixaban)", False, 540.0), ("00597-0153", "Jardiance 25mg (Empagliflozin)", False, 560.0),
    ("00093-7211", "Sertraline 50mg", True, 0.38), ("00024-5812", "Trulicity 1.5mg (Dulaglutide)", False, 830.0),
    ("00093-0058", "Gabapentin 300mg", True, 0.28), ("00186-1095", "Symbicort 160/4.5 Inhaler", False, 310.0),
]
PHARMACIES = ["CVS Pharmacy", "Walgreens", "Walmart Pharmacy", "Express Scripts Mail", "Local Care Rx"]

def pharmacy_claims(n=4200):
    rows = []
    for i in range(n):
        mid = rng.choice(member_ids, p=None if rng.random() > 0 else None)
        if mid in high_cost and rng.random() < 0.7:  # chronic members refill brands more
            idx = rng.integers(6, 10)
        else:
            idx = rng.integers(0, len(DRUGS))
        ndc, name, generic, unit = DRUGS[idx]
        qty = int(rng.integers(28, 91)) if unit < 10 else int(rng.integers(1, 3))
        paid = round(qty * unit * rng.uniform(0.9, 1.25), 2)
        rows.append(dict(claim_id=f"RX{700000 + i}", member_id=mid, age_band=member_age[mid],
                         service_date=rng.choice(DATES),
                         ndc=ndc, drug_name=name, is_generic=generic, quantity=qty,
                         days_supply=int(rng.choice([30, 30, 30, 90])), paid_amount=paid,
                         pharmacy=rng.choice(PHARMACIES)))
    return pd.DataFrame(rows)

DIAGNOSES = [  # icd10-like, description, category, base cost
    ("E11.9", "Type 2 diabetes mellitus", "Endocrine", 420), ("I10", "Essential hypertension", "Circulatory", 260),
    ("E78.5", "Hyperlipidemia", "Endocrine", 210), ("M54.5", "Low back pain", "Musculoskeletal", 320),
    ("J45.909", "Asthma, unspecified", "Respiratory", 300), ("F32.9", "Major depressive disorder", "Mental Health", 280),
    ("K21.9", "GERD without esophagitis", "Digestive", 290), ("M17.9", "Osteoarthritis of knee", "Musculoskeletal", 900),
    ("N18.3", "Chronic kidney disease stage 3", "Genitourinary", 1100), ("C50.919", "Malignant neoplasm of breast", "Neoplasm", 5200),
    ("I25.10", "Atherosclerotic heart disease", "Circulatory", 2400), ("J06.9", "Acute upper respiratory infection", "Respiratory", 160),
]
SPECIALTIES = ["Internal Medicine", "Family Practice", "Cardiology", "Endocrinology", "Orthopedics", "Psychiatry"]
DX_WEIGHTS = [0.12, 0.16, 0.12, 0.11, 0.08, 0.08, 0.08, 0.06, 0.04, 0.02, 0.05, 0.08]  # common conditions dominate
PROCS = ["99213", "99214", "99203", "80053", "36415", "97110", "93000"]

def medical_claims(n=6000):
    rows = []
    for i in range(n):
        mid = rng.choice(member_ids)
        idx = rng.choice([0, 8, 10]) if (mid in high_cost and rng.random() < 0.4) else rng.choice(len(DIAGNOSES), p=DX_WEIGHTS)
        icd, desc, cat, base = DIAGNOSES[idx]
        paid = round(base * rng.uniform(0.7, 1.6) * (4.5 if (mid in high_cost and rng.random() < 0.5) else 1.0), 2)
        rows.append(dict(claim_id=f"DX{300000 + i}", member_id=mid, age_band=member_age[mid],
                         service_date=rng.choice(DATES),
                         icd10=icd, diagnosis=desc, category=cat,
                         procedure_code=rng.choice(PROCS), provider_specialty=rng.choice(SPECIALTIES),
                         paid_amount=paid))
    return pd.DataFrame(rows)

if __name__ == "__main__":
    rx, dx = pharmacy_claims(), medical_claims()
    # Inject a few known data-quality issues so the validator has something to find.
    rx.loc[5, "paid_amount"] = -12.50
    dx = pd.concat([dx, dx.iloc[[10]]], ignore_index=True)  # duplicate claim row
    rx.to_csv(OUT / "pharmacy_claims.csv", index=False)
    dx.to_csv(OUT / "medical_claims.csv", index=False)
    print(f"pharmacy_claims: {len(rx)} rows | medical_claims: {len(dx)} rows -> {OUT}")
