# Creating NPC Data for EQ Map Editor NPC Match Tools

The **NPC Match** tools require a combined NPC/map data file. This file tells EQ Map Editor which NPCs exist in each zone, what their map coordinates should be, what expansion they belong to, and whether they already appear on your current map labels.

The recommended workflow is:

```text
NPC database/export CSV
        ↓
EQMapEditor NPC Label List.csv
        ↓
extract_eq_map_points.py + your map folder
        ↓
[Map Folder Name] Combined Map Data.xlsx
        ↓
EQ Map Editor NPC Match tools
```

## Recommended generated file

The recommended file used by EQ Map Editor is:

```text
[Map Folder Name] Combined Map Data.xlsx
```

Example:

```text
Project Miragul Darkmode Maps Combined Map Data.xlsx
```

This file is created by the helper script:

```text
extract_eq_map_points.py
```

The script compares your current EverQuest map `.txt` files against an NPC list CSV named:

```text
EQMapEditor NPC Label List.csv
```

## Required files to include

If you want other users to create their own NPC data, include these files with the project or release package:

```text
extract_eq_map_points.py
apply_combined_map_data.py
EQMapEditor NPC Label List.csv
requirements.txt
```

You should also include a short example map folder or sample output workbook if possible:

```text
sample_maps/
  poknowledge.txt

sample_output/
  sample Combined Map Data.xlsx
```

The sample files make it much easier for users to confirm that Python, `openpyxl`, and the scripts are working correctly before they run the workflow on their own map folder.

## Required Python package

The helper scripts require Python and `openpyxl`.

Install dependencies with:

```bash
pip install openpyxl
```

If you already have a `requirements.txt`, make sure it includes:

```text
openpyxl
```

## Required input files

To create the combined NPC data, the user needs:

1. A folder containing EverQuest map `.txt` files.

   Example:

   ```text
   C:\EverQuest\maps\Project Miragul Darkmode Maps\
   ```

2. The NPC list CSV:

   ```text
   EQMapEditor NPC Label List.csv
   ```

   This file should be placed in the same folder as `extract_eq_map_points.py`, unless the script path is changed.

3. The helper script:

   ```text
   extract_eq_map_points.py
   ```

## Creating `EQMapEditor NPC Label List.csv`

`EQMapEditor NPC Label List.csv` is an export of NPC data from the server/database. It should include one row per NPC/spawn.

At minimum, include these columns:

```text
zone_short_name
npc_name
npc_role
spawn_x
spawn_y
spawn_z
is_merchant
min_expansion_number
min_expansion
max_expansion_number
max_expansion
scripted_npc
spawned_npc
```

### Column meanings

| Column | Purpose |
|---|---|
| `zone_short_name` | EQ zone shortname, such as `poknowledge`, `qeynos`, or `gfaydark`. |
| `npc_name` | The NPC name used for matching and generated map labels. |
| `npc_role` | Optional role text, such as `Banker`, `Information`, `Wizard Spells`, or `Quest NPC`. |
| `spawn_x` | NPC database X coordinate. |
| `spawn_y` | NPC database Y coordinate. |
| `spawn_z` | NPC database Z coordinate. |
| `is_merchant` | Whether the NPC is a merchant. Common values are `yes`/`no` or `1`/`0`. |
| `min_expansion_number` | First expansion where the NPC should exist. Use `-1` or blank if unknown/no minimum. |
| `min_expansion` | Expansion name for the minimum expansion. |
| `max_expansion_number` | Last expansion where the NPC should exist. Use `-1` or blank if unknown/no maximum. |
| `max_expansion` | Expansion name for the maximum expansion. |
| `scripted_npc` | Optional flag for scripted/special NPCs. |
| `spawned_npc` | Optional flag for normally spawned NPCs. |

The exact SQL/export process may vary by server database. Once exported, place the CSV beside `extract_eq_map_points.py` and run the extraction script against your map folder.

## Expansion number reference

Use consistent expansion numbers in `min_expansion_number` and `max_expansion_number`.

| Number | Expansion |
|---:|---|
| 0 | Classic |
| 1 | The Ruins of Kunark |
| 2 | The Scars of Velious |
| 3 | The Shadows of Luclin |
| 4 | The Planes of Power |
| 5 | The Legacy of Ykesha |
| 6 | Lost Dungeons of Norrath |
| 7 | Gates of Discord |
| 8 | Omens of War |
| 9 | Dragons of Norrath |
| 10 | Depths of Darkhollow |
| 11 | Prophecy of Ro |
| 12 | The Serpent's Spine |
| 13 | The Buried Sea |
| 14 | Secrets of Faydwer |
| 15 | Seeds of Destruction |
| 16 | Underfoot |
| 17 | House of Thule |
| 18 | Veil of Alaris |
| 19 | Rain of Fear |
| 20 | Call of the Forsaken |
| 21 | The Darkened Sea |
| 22 | The Broken Mirror |
| 23 | Empires of Kunark |
| 24 | Ring of Scale |
| 25 | The Burning Lands |
| 26 | Torment of Velious |
| 27 | Claws of Veeshan |
| 28 | Terror of Luclin |
| 29 | Night of Shadows |
| 30 | Laurion's Song |
| 31 | The Outer Brood |

## Running the extraction script

From a command prompt, run:

```bash
python extract_eq_map_points.py "C:\Path\To\Your\MapFolder"
```

Example:

```bash
python extract_eq_map_points.py "C:\EverQuest\maps\Project Miragul Darkmode Maps"
```

The script creates an output workbook beside the script:

```text
[Map Folder Name] Combined Map Data.xlsx
```

Example:

```text
Project Miragul Darkmode Maps Combined Map Data.xlsx
```

The output name is based on the selected map folder name.

## What the extraction script does

The script reads every map `.txt` file in the selected map folder and extracts all point labels from `P` records.

It then compares those map labels against the NPC list and creates combined rows with statuses such as:

| Status | Meaning |
|---|---|
| `Yes` | The NPC name matches the map label exactly after normalization. |
| `Possible` | The NPC name appears to be an alias/fuzzy match to the map label. |
| `Coordinate Match` | The row was already a possible name match and is also within 20 units of the NPC coordinate. |
| `NPC only` | The NPC exists in the NPC data but does not appear to be on the map. |
| `Map only` | The map label exists but does not appear to match an NPC row. |

Important: `Coordinate Match` is only assigned after a name/alias/fuzzy match is already found. The script does not match unrelated nearby labels by coordinates alone.

## Coordinate conversion

EverQuest map coordinates and database spawn coordinates use different X/Y orientation.

The script converts NPC database spawn coordinates into map coordinates using:

```text
npc_map_x = -spawn_x
npc_map_y = -spawn_y
npc_map_z = spawn_z
```

The editor uses the generated `npc_map_x`, `npc_map_y`, and `npc_map_z` fields when previewing or applying NPC Match changes.

## Generated NPC labels

NPC labels are generated in this format:

```text
npc_name_(npc_role)
```

Examples:

```text
Scholar_Awerrin_(Information)
Celent_Newmist_(Wizard_Spells)
Dogle_Pitt_(Banker)
Acomar_Lothwol
```

If `npc_role` is blank or `\N`, the label uses only the NPC name.

The script also cleans role values before creating labels. For example:

```text
\N
```

is treated as blank.

## Required columns in the combined data file

The editor expects the combined workbook or CSV to include columns such as:

```text
source_status
npc_matched
zone_shortname
npc_name
npc_role
npc_map_label
spawn_x
spawn_y
spawn_z
npc_map_x
npc_map_y
npc_map_z
is_merchant
min_expansion_number
min_expansion
max_expansion_number
max_expansion
scripted_npc
spawned_npc
map_label
map_match_label
map_x
map_y
map_z
map_db_x
map_db_y
map_db_z
map_r
map_g
map_b
map_size
map_source_file
match_distance
match_distance_x
match_distance_y
match_distance_z
```

## Using the generated data in EQ Map Editor

After the workbook is created:

1. Open EQ Map Editor.
2. Load a map zone.
3. Open the **NPC Match** tab.
4. Click **Choose NPC Data**.
5. Select the generated workbook:

   ```text
   [Map Folder Name] Combined Map Data.xlsx
   ```

6. Use one of the NPC Match workflows:
   - **NPC Match & Swap**
   - **Expansion / Era Cleanup**
   - **Add Missing NPCs for Current Era**

The editor filters the combined data to the currently loaded zone only. For example, if `poknowledge.txt` is loaded, the editor only uses rows where:

```text
zone_shortname = poknowledge
```

## Regenerating NPC data

Regenerate the combined NPC data whenever you:

- change many map labels manually;
- add or remove map files;
- update `EQMapEditor NPC Label List.csv`;
- change the NPC expansion data;
- want the NPC Match tab to reflect a newer version of your maps.

After regenerating the workbook, use **Choose NPC Data** again in the editor or reload the same file if it was overwritten.

## Optional: applying the combined data outside the editor

The editor is intended for interactive preview and review. If you want to batch-apply the combined workbook to an entire map folder, use:

```text
apply_combined_map_data.py
```

That script can replace matched labels/coordinates and remove labels that do not fit the selected expansion. The editor is safer for manual review because it lets you preview changes zone-by-zone before saving.

## Recommended release package contents for NPC data creation

To let other users create their own NPC data, include this folder or equivalent in your release:

```text
npc_data_tools/
  README_NPC_DATA.md
  extract_eq_map_points.py
  apply_combined_map_data.py
  EQMapEditor NPC Label List.csv
  requirements.txt
  sample_maps/
    poknowledge.txt
  sample_output/
    sample Combined Map Data.xlsx
```

At minimum, include:

```text
extract_eq_map_points.py
EQMapEditor NPC Label List.csv
requirements.txt
```

For users who want to batch-apply data outside the editor, also include:

```text
apply_combined_map_data.py
```

For users who want to rebuild the NPC CSV from their own server/database, include either:

```text
NPC export SQL
```

or clear documentation explaining which database fields are needed and how to export them to `EQMapEditor NPC Label List.csv`.
