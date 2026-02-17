WITH owner_lines AS (
    SELECT
        id,
        TRIM(COALESCE(owner_info, '')) AS owner_info,
        TRIM(split_part(COALESCE(owner_info, ''), E'\n', 1)) AS line1,
        TRIM(split_part(COALESCE(owner_info, ''), E'\n', 2)) AS line2
    FROM saved_estimates
),
to_fix AS (
    SELECT
        id,
        line1 AS phone_line,
        line2 AS name_line
    FROM owner_lines
    WHERE line1 ~* '^\(?\d{3}\)?[\s\-]*\d{3}[\-\s]*\d{4}(?:\s*(?:cell|work|home|mobile))?$'
      AND line2 <> ''
      AND line2 !~* '^\(?\d{3}\)?[\s\-]*\d{3}[\-\s]*\d{4}(?:\s*(?:cell|work|home|mobile))?$'
)
UPDATE saved_estimates se
SET
    owner_info = tf.name_line || E'\n' || tf.phone_line,
    phone_original = CASE
        WHEN COALESCE(TRIM(se.phone_original), '') = '' THEN tf.phone_line
        ELSE se.phone_original
    END
FROM to_fix tf
WHERE se.id = tf.id;
