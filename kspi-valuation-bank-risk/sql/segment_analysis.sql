-- Reported FY2024 to FY2025; KZT millions. Not organic growth.
-- Marketplace includes acquisition effects; revenue is before eliminations.
-- Growth from zero/negative prior income is undefined, so return NULL.
SELECT cur.segment,
       cur.revenue / NULLIF(prior.revenue, 0) - 1 AS revenue_growth,
       CASE WHEN prior.net_income > 0
            THEN cur.net_income / prior.net_income - 1 END AS net_income_growth,
       cur.net_income - prior.net_income AS net_income_change_kzt_mn,
       cur.net_income / NULLIF(cur.revenue, 0) AS net_margin
FROM segments AS cur
JOIN segments AS prior
  ON cur.segment = prior.segment AND cur.year = prior.year + 1
WHERE cur.year = 2025
ORDER BY cur.segment;
