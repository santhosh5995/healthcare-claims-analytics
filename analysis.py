"""Healthcare claims analysis: headline metrics + charts.

Reads the cleaned CSVs produced by clean_validate.py, prints the headline
insights (also written up in ANALYSIS.md) and saves 3 charts to charts/.
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

BASE = Path(__file__).parent
DATA, CHARTS = BASE / "data", BASE / "charts"
CHARTS.mkdir(exist_ok=True)

rx = pd.read_csv(DATA / "pharmacy_claims_clean.csv", parse_dates=["service_date"])
dx = pd.read_csv(DATA / "medical_claims_clean.csv", parse_dates=["service_date"])
all_claims = pd.concat([rx[["member_id", "service_date", "paid_amount"]],
                        dx[["member_id", "service_date", "paid_amount"]]])
n_members = all_claims["member_id"].nunique()
total_spend = all_claims["paid_amount"].sum()

print(f"Members: {n_members} | Total paid (Rx+Dx): ${total_spend:,.0f}")

top_drugs = rx.groupby("drug_name")["paid_amount"].sum().sort_values(ascending=False)
print("\nTop 5 drugs by spend:")
print((top_drugs.head(5) / 1000).round(1).to_string())

monthly = (all_claims.assign(month=all_claims["service_date"].dt.to_period("M"))
             .groupby("month")["paid_amount"].sum())
monthly.index = monthly.index.to_timestamp()
pmpm = monthly / n_members
print(f"\nPMPM: first month ${pmpm.iloc[0]:,.2f} -> last month ${pmpm.iloc[-1]:,.2f} "
      f"({(pmpm.iloc[-1] / pmpm.iloc[0] - 1) * 100:+.1f}%)")

dx_counts = dx["diagnosis"].value_counts()
print(f"\nMost common diagnosis: {dx_counts.index[0]} ({dx_counts.iloc[0]} claims, "
      f"{dx_counts.iloc[0] / len(dx) * 100:.1f}% of medical claims)")

gb = rx.groupby("is_generic")["paid_amount"].agg(["mean", "count"])
print(f"\nAvg paid per claim — brand: ${gb.loc[False, 'mean']:,.2f} ({int(gb.loc[False, 'count'])} claims) "
      f"vs generic: ${gb.loc[True, 'mean']:,.2f} ({int(gb.loc[True, 'count'])} claims) "
      f"= brand costs {gb.loc[False, 'mean'] / gb.loc[True, 'mean']:.0f}x more per claim")

member_spend = all_claims.groupby("member_id")["paid_amount"].sum().sort_values(ascending=False)
top5_share = member_spend.head(int(0.05 * n_members)).sum() / total_spend * 100
print(f"Top 5% of members account for {top5_share:.1f}% of total spend")

# --- Charts ---
monthly.plot(marker="o", figsize=(9, 4), title="Total Claims Spend by Month (2025)")
plt.ylabel("Paid amount ($)"); plt.tight_layout()
plt.savefig(CHARTS / "monthly_spend_trend.png", dpi=120); plt.close()

top_drugs.head(10).iloc[::-1].plot.barh(figsize=(9, 5), title="Top 10 Drugs by Total Spend")
plt.xlabel("Paid amount ($)"); plt.tight_layout()
plt.savefig(CHARTS / "top_drugs_by_spend.png", dpi=120); plt.close()

cat_share = dx.groupby("category")["paid_amount"].sum().sort_values(ascending=False)
cat_share.plot.pie(autopct="%1.1f%%", figsize=(7, 7), title="Medical Spend Share by Diagnosis Category")
plt.ylabel(""); plt.tight_layout()
plt.savefig(CHARTS / "diagnosis_category_share.png", dpi=120); plt.close()
print(f"\nCharts saved to {CHARTS}: monthly_spend_trend.png, top_drugs_by_spend.png, diagnosis_category_share.png")
