-- Main NPC spawn listing view.
-- Keeps NPCs that have exactly one spawn2 point in a given zone.
-- This is useful for excluding many common monsters while keeping static/unique NPCs.
-- Includes zone expansion, spawn minimum expansion, spawn maximum expansion, and readable expansion names.

CREATE OR REPLACE VIEW vw_npc_spawn_listing_one_spawn_per_zone AS
WITH npc_zone_spawn_counts AS (
    SELECT
        se.npcID AS npc_id,
        s.zone AS zone_short_name,
        COUNT(DISTINCT s.id) AS spawnpoint_count
    FROM spawnentry se
    JOIN spawn2 s
        ON s.spawngroupID = se.spawngroupID
    GROUP BY
        se.npcID,
        s.zone
)
SELECT
    nt.id AS npc_id,
    nt.name AS npc_name,

    CASE
        WHEN nt.merchant_id IS NOT NULL AND nt.merchant_id <> 0 THEN 1
        ELSE 0
    END AS is_merchant,

    CASE
        WHEN nt.merchant_id IS NOT NULL AND nt.merchant_id <> 0 THEN 'Yes'
        ELSE 'No'
    END AS is_merchant_name,

    nt.merchant_id,

    z.zoneidnumber,
    z.short_name AS zone_short_name,
    z.long_name AS zone_long_name,

    z.expansion AS zone_expansion,
    COALESCE(zexp.expansion_name, CONCAT('Unknown / Expansion ', z.expansion)) AS zone_expansion_name,

    COALESCE(s.min_expansion, z.expansion) AS spawn_min_expansion,
    COALESCE(smin.expansion_name, zexp.expansion_name, CONCAT('Unknown / Expansion ', COALESCE(s.min_expansion, z.expansion))) AS spawn_min_expansion_name,

    s.max_expansion AS spawn_max_expansion,
    CASE
        WHEN s.max_expansion IS NULL OR s.max_expansion < 0 THEN 'Not specified / no maximum'
        ELSE COALESCE(smax.expansion_name, CONCAT('Unknown / Expansion ', s.max_expansion))
    END AS spawn_max_expansion_name,

    s.id AS spawn2_id,
    s.spawngroupID,
    s.x,
    s.y,
    s.z,
    s.heading,
    s.respawntime,
    s.variance,
    s.pathgrid,

    sg.name AS spawngroup_name,

    nt.level,
    nt.maxlevel,
    nt.race,
    nt.class,
    nt.bodytype,
    nt.lastname,
    nt.npc_faction_id,
    nt.loottable_id,

    nzsc.spawnpoint_count

FROM npc_types nt
JOIN spawnentry se
    ON se.npcID = nt.id
JOIN spawn2 s
    ON s.spawngroupID = se.spawngroupID
JOIN zone z
    ON z.short_name = s.zone
LEFT JOIN spawngroup sg
    ON sg.id = s.spawngroupID
LEFT JOIN vw_eqemu_expansion_lookup zexp
    ON zexp.expansion_id = z.expansion
LEFT JOIN vw_eqemu_expansion_lookup smin
    ON smin.expansion_id = COALESCE(s.min_expansion, z.expansion)
LEFT JOIN vw_eqemu_expansion_lookup smax
    ON smax.expansion_id = s.max_expansion
JOIN npc_zone_spawn_counts nzsc
    ON nzsc.npc_id = nt.id
   AND nzsc.zone_short_name = s.zone

WHERE
    nzsc.spawnpoint_count = 1
    AND z.min_status = 0
    AND nt.race NOT IN (127, 240);
