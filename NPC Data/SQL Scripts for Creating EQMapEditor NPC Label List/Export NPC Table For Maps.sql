WITH single_npc_spawngroups AS (
    SELECT
        spawngroupID
    FROM spawnentry
    GROUP BY spawngroupID
    HAVING COUNT(DISTINCT npcID) = 1
)

SELECT
    npc_name,

    CASE
        WHEN npc_name LIKE '%#%' THEN 'Yes'
        ELSE 'No'
    END AS scripted_npc,

    lastname AS npc_role,

    zone_short_name,
    zone_long_name,

    zone_expansion,
    zone_expansion_name,

    ROUND(x, 2) AS spawn_x,
    ROUND(y, 2) AS spawn_y,
    ROUND(z, 2) AS spawn_z,

    CASE
        WHEN is_merchant = 1 THEN 'Yes'
        ELSE 'No'
    END AS is_merchant,

    CASE
        WHEN spawn_min_expansion = -1
             AND zone_expansion IS NOT NULL
             AND zone_expansion >= 0
        THEN zone_expansion
        ELSE spawn_min_expansion
    END AS min_expansion_number,

    CASE
        WHEN spawn_min_expansion = -1
             AND zone_expansion IS NOT NULL
             AND zone_expansion >= 0
        THEN zone_expansion_name
        ELSE spawn_min_expansion_name
    END AS min_expansion,

    spawn_max_expansion AS max_expansion_number,
    spawn_max_expansion_name AS max_expansion

FROM vw_npc_spawn_listing_one_spawn_per_zone v

JOIN single_npc_spawngroups sng
    ON sng.spawngroupID = v.spawngroupID

WHERE
    npc_name NOT LIKE 'a\_%' ESCAPE '\\'
    AND npc_name NOT LIKE 'A\_%' ESCAPE '\\'
    AND npc_name NOT LIKE 'an\_%' ESCAPE '\\'
    AND npc_name NOT LIKE 'An\_%' ESCAPE '\\'

GROUP BY
    npc_name,

    CASE
        WHEN npc_name LIKE '%#%' THEN 'Yes'
        ELSE 'No'
    END,

    lastname,

    zone_short_name,
    zone_long_name,

    zone_expansion,
    zone_expansion_name,

    ROUND(x, 2),
    ROUND(y, 2),
    ROUND(z, 2),

    CASE
        WHEN is_merchant = 1 THEN 'Yes'
        ELSE 'No'
    END,

    CASE
        WHEN spawn_min_expansion = -1
             AND zone_expansion IS NOT NULL
             AND zone_expansion >= 0
        THEN zone_expansion
        ELSE spawn_min_expansion
    END,

    CASE
        WHEN spawn_min_expansion = -1
             AND zone_expansion IS NOT NULL
             AND zone_expansion >= 0
        THEN zone_expansion_name
        ELSE spawn_min_expansion_name
    END,

    spawn_max_expansion,
    spawn_max_expansion_name

ORDER BY
    zone_expansion,
    zone_short_name,
    npc_name;