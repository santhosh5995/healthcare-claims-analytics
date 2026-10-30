-- Healthcare Claims Analytics: headline queries against claims.db
-- (SQLite; tables loaded by clean_validate.py: pharmacy_claims, medical_claims)

-- 1) Top 10 drugs by total spend
SELECT drug_name, COUNT(*) AS claims, ROUND(SUM(paid_amount), 2) AS total_paid
FROM pharmacy_claims
GROUP BY drug_name ORDER BY total_paid DESC LIMIT 10;

-- 2) Cost per member per month (PMPM) trend, Rx + Dx combined
WITH monthly AS (
    SELECT substr(service_date, 1, 7) AS month, paid_amount, member_id FROM pharmacy_claims
    UNION ALL
    SELECT substr(service_date, 1, 7), paid_amount, member_id FROM medical_claims
),
members AS (SELECT COUNT(DISTINCT member_id) AS n FROM monthly)
SELECT month, ROUND(SUM(paid_amount), 2) AS total_paid,
       ROUND(SUM(paid_amount) / (SELECT n FROM members), 2) AS pmpm
FROM monthly GROUP BY month ORDER BY month;

-- 3) Most common diagnoses
SELECT diagnosis, category, COUNT(*) AS claims,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_claims
FROM medical_claims GROUP BY diagnosis, category ORDER BY claims DESC LIMIT 10;

-- 4) Generic vs brand: average paid per claim
SELECT CASE WHEN is_generic THEN 'Generic' ELSE 'Brand' END AS drug_type,
       COUNT(*) AS claims, ROUND(AVG(paid_amount), 2) AS avg_paid_per_claim
FROM pharmacy_claims GROUP BY drug_type;

-- 5) High-cost claimant concentration: spend share of the top 5% of members
WITH member_spend AS (
    SELECT member_id, SUM(paid_amount) AS spend FROM (
        SELECT member_id, paid_amount FROM pharmacy_claims
        UNION ALL SELECT member_id, paid_amount FROM medical_claims)
    GROUP BY member_id
),
ranked AS (
    SELECT spend, ROW_NUMBER() OVER (ORDER BY spend DESC) AS rn, COUNT(*) OVER () AS n
    FROM member_spend)
SELECT ROUND(100.0 * SUM(CASE WHEN rn <= 0.05 * n THEN spend END) / SUM(spend), 1)
       AS top5pct_spend_share_pct
FROM ranked;

-- 6) Spend by diagnosis category
SELECT category, COUNT(*) AS claims, ROUND(SUM(paid_amount), 2) AS total_paid
FROM medical_claims GROUP BY category ORDER BY total_paid DESC;
