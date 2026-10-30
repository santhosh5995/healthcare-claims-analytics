# Findings Summary — Healthcare Claims Analytics

All figures below are computed by `analysis.py` / `queries.sql` from the
**synthetic** dataset generated for this project (seed 42; 4,199 pharmacy and
6,000 medical claims after cleaning; 1,199 members with at least one claim;
service dates in calendar 2025).

## Headline numbers

| Metric | Value |
|---|---|
| Total paid (Rx + Dx) | $7,156,804 |
| Medical (Dx) paid | $4,230,151 |
| Pharmacy (Rx) paid | $2,926,653 |
| PMPM — Jan 2025 | $490.02 |
| PMPM — Dec 2025 | $541.82 (+10.6% YoY trend) |
| Top 5% members' share of total spend | 17.4% |

## Insights

1. **One specialty drug drives pharmacy spend.** Humira (adalimumab) totals
   $1,316,571 — 45.0% of all pharmacy paid — from only 286 claims. The top 5
   drugs by spend (Humira, Trulicity $412.8K, Ozempic $411.9K, Eliquis $304.7K,
   Jardiance $282.3K) are all brand specialty products and together account for
   roughly 93% of Rx spend. Any pharmacy-cost initiative has to start with
   specialty drug management, not generics.

2. **Brand/generic economics are extreme.** Brand claims average $1,566.22 paid
   per claim vs $19.00 for generics (~82×). Generics are 56% of Rx claim volume
   (2,359 of 4,199) but a small fraction of spend, so generic-substitution
   programs would move volume metrics far more than cost metrics here.

3. **Medical spend is led by circulatory conditions.** Essential hypertension
   is the most common diagnosis (950 claims, 15.8% of medical claims), and the
   Circulatory category is the largest by paid amount at $1,253,119, followed by
   Neoplasm ($721,977) and Musculoskeletal ($676,332).

4. **Costs trend upward through the year.** PMPM rose from $490.02 in January
   to $541.82 in December (+10.6%). With claim mix held roughly constant by the
   generator, this reflects the modeled utilization/price drift — in a real
   book of business this is the signal that would trigger a deeper drill-down
   into which category and drug classes drive the trend.

5. **Spend is concentrated, but not extremely.** The top 5% of members (60
   members) account for 17.4% of total paid. That is meaningful concentration
   worth care-management attention, though lower than the ~50% often cited for
   real commercial populations — a reminder that this is synthetic data with a
   deliberately simplified cost distribution.
