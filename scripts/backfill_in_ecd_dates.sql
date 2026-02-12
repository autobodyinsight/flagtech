ALTER TABLE saved_estimates
ADD COLUMN IF NOT EXISTS in_date DATE DEFAULT CURRENT_DATE;

ALTER TABLE saved_estimates
ADD COLUMN IF NOT EXISTS ecd_date DATE;

WITH computed AS (
    SELECT
        se.id,
        COALESCE(se.in_date, se.saved_at::date, CURRENT_DATE) AS computed_in_date,
        (
            COALESCE(
                (
                    SELECT SUM(
                        CASE
                            WHEN NULLIF(REGEXP_REPLACE(COALESCE(item->>'value', ''), '[^0-9.\-]', '', 'g'), '') IS NULL THEN 0
                            ELSE NULLIF(REGEXP_REPLACE(COALESCE(item->>'value', ''), '[^0-9.\-]', '', 'g'), '')::numeric
                        END
                    )
                    FROM jsonb_array_elements(COALESCE(se.labor_repairs, '[]'::jsonb)) AS item
                ),
                0
            )
            +
            COALESCE(
                (
                    SELECT SUM(
                        CASE
                            WHEN NULLIF(REGEXP_REPLACE(COALESCE(item->>'value', ''), '[^0-9.\-]', '', 'g'), '') IS NULL THEN 0
                            ELSE NULLIF(REGEXP_REPLACE(COALESCE(item->>'value', ''), '[^0-9.\-]', '', 'g'), '')::numeric
                        END
                    )
                    FROM jsonb_array_elements(COALESCE(se.paint_repairs, '[]'::jsonb)) AS item
                ),
                0
            )
        ) AS total_hours
    FROM saved_estimates se
),
with_days AS (
    SELECT
        c.id,
        c.computed_in_date,
        GREATEST(0, CEIL((c.total_hours / 4.0) + 3.0))::int AS ecd_weekdays
    FROM computed c
),
final_dates AS (
    SELECT
        wd.id,
        wd.computed_in_date,
        CASE
            WHEN wd.ecd_weekdays <= 0 THEN wd.computed_in_date
            ELSE (
                SELECT g.day_value::date
                FROM generate_series(
                    wd.computed_in_date + INTERVAL '1 day',
                    wd.computed_in_date + ((wd.ecd_weekdays * 3 + 14) || ' days')::interval,
                    INTERVAL '1 day'
                ) AS g(day_value)
                WHERE EXTRACT(ISODOW FROM g.day_value) < 6
                ORDER BY g.day_value
                LIMIT 1 OFFSET (wd.ecd_weekdays - 1)
            )
        END AS computed_ecd_date
    FROM with_days wd
)
UPDATE saved_estimates se
SET
    in_date = fd.computed_in_date,
    ecd_date = COALESCE(se.ecd_date, fd.computed_ecd_date)
FROM final_dates fd
WHERE se.id = fd.id
  AND (
      se.in_date IS NULL
      OR se.ecd_date IS NULL
  );
