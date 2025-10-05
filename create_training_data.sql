DROP TABLE IF EXISTS public.training_silver_halfdata;

CREATE TABLE public.training_silver_halfdata AS
SELECT *
FROM (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY neighborhood ORDER BY random()) AS rn,
           COUNT(*) OVER (PARTITION BY neighborhood) AS total_in_neighborhood
    FROM public.training_bronze
) t
WHERE rn <= total_in_neighborhood / 2
DISTRIBUTED RANDOMLY;

