# EQ Map Editor

A desktop PySide6 editor for EverQuest map `.txt` files, including visual editing, point/line management, colour tools, zone browsing, and NPC-data assisted cleanup.

## NPC Match Tools Guide

The **NPC Match** tab is a set of three related tools for comparing the currently loaded map zone against an NPC data source, usually `Combined Map Data.xlsx` or an exported CSV from the map/NPC extraction workflow.

The tools are designed around the same workflow used by the helper scripts:

- `extract_eq_map_points.py` builds the combined NPC/map data and assigns `Yes`, `Possible`, `Coordinate Match`, `NPC only`, and `Map only` statuses.
- `apply_combined_map_data.py` applies selected workbook actions back to map files while preserving point colour and size.

Inside the editor, the same ideas are applied interactively to the **currently loaded zone only**. This keeps the workflow fast and lets you preview changes before saving.

![NPC Match filters and delete tools](docs/screenshots/npc_match_filters_delete.png)

### NPC data source

Use **Choose NPC Data** to select an NPC data workbook or CSV. The expected data columns are the same columns produced by the combined data workflow, including:

```text
source_status
npc_matched
zone_shortname
npc_name
npc_role
npc_map_label
npc_map_x
npc_map_y
npc_map_z
min_expansion_number
min_expansion
max_expansion_number
max_expansion
map_label
map_x
map_y
map_z
map_source_file
match_distance
```

The app filters this data to the currently loaded zone shortname. For example, if `poknowledge.txt` is open, only rows where `zone_shortname` is `poknowledge` are considered.

### Matching rules

The editor follows the same match assignment pattern as `extract_eq_map_points.py`:

| Match status | Meaning |
|---|---|
| `Yes` | The NPC name is an exact normalized match to the map label or cleaned map label. |
| `Possible` | The NPC name is an alias/fuzzy match to the map label. This includes common role-prefix patterns and close spelling matches. |
| `Coordinate Match` | The row was already a possible name/alias/fuzzy match and the NPC/map distance is within 20 units. The app does not coordinate-match unrelated nearby labels. |
| `NPC only` | The NPC exists in the NPC data for this zone but does not appear to match a loaded map point. |
| `Map only` | The loaded map point does not appear to match an NPC row. |

Default checked rows are limited to `Yes` and `Coordinate Match`, matching the safer apply-script behavior.

### Generated NPC labels

NPC labels are generated as:

```text
npc_name_(npc_role)
```

Examples:

```text
Celent_Newmist_(Wizard_Spells)
Scholar_Awerrin_(Information)
Acomar_Lothwol
```

If `npc_role` is blank or `\N`, the label is just the NPC name. Spaces in roles are replaced with underscores.

## NPC Match tab layout

The NPC Match tab contains three collapsible workflow boxes:

1. **NPC Match & Swap**
2. **Expansion / Era Cleanup**
3. **Add Missing NPCs for Current Era**

Each box can be expanded or collapsed from its checkbox/header. A collapsed box shrinks to a single line. When one box collapses, the available height is redistributed to the open boxes: one open box gets all of the available height, and two open boxes split the available height.

![Collapsible NPC workflow boxes](docs/screenshots/npc_collapsible_workflows.png)

The whole NPC Match tab is scrollable, and each workflow table supports manually resizable columns. Drag a table header divider left or right to widen or shrink a column.

## Workflow 1: NPC Match & Swap

Use **NPC Match & Swap** when you want to replace existing map labels and coordinates with the matched NPC-data label and NPC map coordinates.

![NPC Match and Swap overview](docs/screenshots/npc_match_swap_overview.png)

### Steps

1. Load a zone map.
2. Open **NPC Match**.
3. Click **Choose NPC Data** and select the combined NPC/map workbook or CSV.
4. Click **Compare Current Zone**.
5. Review the table.
6. Edit the **NPC Label** field if needed.
7. Use the filters/search tools to narrow the list.
8. Check the rows you want to update.
9. Click **Preview Selected**.
10. Click **Apply Selected** when the preview looks correct.
11. Click **Save Edits** to write the map file.

### Filters and search

The NPC Match & Swap section includes:

| Control | Purpose |
|---|---|
| Match Type | Shows all rows or only `Yes`, `Coordinate Match`, `Possible`, `NPC only`, or `Map only`. |
| Presence | Shows all rows, only rows already present on the map, or only rows missing from the map. |
| Search | Finds text across the current map label, NPC label, NPC name, NPC role, coordinates, and expansion text. |

![NPC Match filters and delete tools](docs/screenshots/npc_match_filters_delete.png)

### Table columns

Common columns include:

| Column | Meaning |
|---|---|
| Use | Whether the row is selected for preview/apply/delete. |
| Match Type | `Yes`, `Coordinate Match`, `Possible`, `NPC only`, or `Map only`. |
| Current Label | The label currently present in the loaded map. |
| NPC Label | The generated replacement label. This cell is editable. |
| Map XYZ | Current loaded map point coordinates. |
| NPC XYZ | NPC-derived replacement map coordinates. |
| Distance | Distance between map point and NPC spawn after coordinate conversion. |
| NPC Role | Role from the NPC data, if present. |

### Preview and apply

**Preview Selected** shows the proposed replacement labels/positions on the map without changing the file. **Apply Selected** updates the selected loaded map points in memory.

Applying a swap changes:

```text
label
x
y
z
```

It preserves:

```text
RGB colour
point size
source layer/file
```

The operation is undoable and the map is not written until **Save Edits** is clicked.

### Delete selected NPCs from map

Use **Delete Selected From Map** to remove selected rows that are already present on the loaded map. This is useful when the filters identify labels you do not want to keep.

Important behavior:

- `NPC only` rows are ignored because they are not currently on the map.
- The deletion is undoable.
- The map is marked dirty/unsaved.
- The map file is not changed until **Save Edits** is clicked.

## Workflow 2: Expansion / Era Cleanup

Use **Expansion / Era Cleanup** to find labels on the loaded map that do not belong in the selected expansion era.

![Expansion and Era Cleanup](docs/screenshots/npc_era_cleanup.png)

### Expansion setting

Choose your current expansion from the dropdown, then click **Save Expansion Setting** to store it in:

```text
app/settings/eq_map_editor_settings.json
```

The saved expansion is reloaded automatically when the editor starts and reused when changing maps.

### Era scan rules

A loaded map label is flagged when the matched NPC row has either:

```text
min_expansion_number > selected_expansion_number
```

or:

```text
max_expansion_number is known and max_expansion_number < selected_expansion_number
```

Blank, missing, or `-1` min/max values are treated as no known limit and are not automatically flagged.

### Steps

1. Load a map.
2. Choose NPC data if it has not already been loaded.
3. Select the current expansion.
4. Optionally click **Save Expansion Setting**.
5. Click **Scan Era Labels**.
6. Review the flagged labels.
7. Use **Preview Removals** to highlight them on the map.
8. Click **Remove Selected Labels** to remove the checked labels from the loaded map.
9. Click **Save Edits** when ready.

The removal is one undoable action and does not write to disk until the map is saved.

## Workflow 3: Add Missing NPCs for Current Era

Use **Add Missing NPCs for Current Era** when you want to add NPCs from the NPC data that fit the selected expansion and are not already present on the loaded map.

![Add Missing NPCs for Current Era](docs/screenshots/npc_add_missing.png)

### What counts as addable

An NPC is shown in this workflow when:

- it belongs to the currently loaded zone;
- it fits the selected expansion using `min_expansion_number` and `max_expansion_number`; and
- the matching logic does not find it already present on the loaded map.

### Steps

1. Load a map.
2. Choose NPC data if needed.
3. Confirm the current expansion.
4. Click **Find Missing NPCs**.
5. Edit any **NPC Label** cells that need cleanup.
6. Check the NPCs you want to add.
7. Choose the RGB/size style for new labels.
8. Click **Preview Adds**.
9. Click **Add Selected NPCs**.
10. Click **Save Edits** when ready.

New NPCs are appended as new map `P` records using the NPC map XYZ coordinates, the editable table label, and the selected RGB/size values.

### RGB, size, and matching an existing label style

The Add Missing NPCs workflow has a compact style row:

```text
Style: [new colour preview] R [value] G [value] B [value] Size [value] [Match existing label style...] [source swatch] [Match]
```

Use this when you want added NPCs to match an existing label type, such as merchants, trainers, quest NPCs, or standard white labels.

![Existing label style dropdown swatches](docs/screenshots/npc_style_dropdown_swatches.png)

The dropdown contains the loaded map labels and shows a colour swatch for each label. Select a label and click **Match** to copy that label's:

```text
red
green
blue
size
```

The source swatch beside **Match** previews the currently selected existing label before copying.

## NPC Match safety notes

- All changes are preview-first where practical.
- Apply/add/remove operations change the loaded map in memory and mark it dirty.
- Nothing is written to the map file until **Save Edits** is clicked.
- Undo/Redo works for NPC Match changes as grouped actions.
- Keep backups of map folders before large cleanup operations.
- Review `Possible`, `Map only`, and era-cleanup rows before deleting or applying them.

## Changelog

## v1.1.19 SVG toolbar icons

This build replaces the problematic hand-drawn bottom toolbar action icons with real SVG resources.

### Changed

```text
Undo:
- now loaded from app/resources/icons/undo.svg

Redo:
- now loaded from app/resources/icons/redo.svg

Save:
- now loaded from app/resources/icons/save.svg

Revert:
- now loaded from app/resources/icons/revert.svg

Why:
- The previous undo/redo icons were drawn with tiny QPainter arcs/paths and separate arrowheads.
- At toolbar size, those pieces scaled poorly and looked broken.
- SVG icons scale more cleanly and consistently.
```

## v1.1.18 toolbar icon style refresh

This build refreshes the bottom toolbar icons to use clearer, heavier symbols inspired by the provided references.

### Changed

```text
Undo:
- replaced with a bold standard undo arrow

Redo:
- replaced with a bold standard redo arrow

Save:
- simplified into a chunkier floppy-disk icon

Revert:
- redrawn as a document/page with a heavy return arrow
```

## v1.1.17 new undo redo icons

This build replaces the previous undo/redo symbols with clearer bent-arrow icons.

### Changed

```text
Undo:
- replaced with a bent left-pointing arrow icon

Redo:
- replaced with a bent right-pointing arrow icon

Both icons now use simpler shapes intended to read better at small sizes.
```

## v1.1.16 arrow tip fix

This build refines the Undo and Redo toolbar icons.

### Changed

```text
Undo:
- moved the arrow head to the true end of the curved line

Redo:
- moved the arrow head to the true end of the curved line

This makes both icons read more clearly at small sizes.
```

## v1.1.15 clear bottom toolbar icons

This build improves the readability of the bottom toolbar action icons.

### Changed

```text
Undo:
- Replaced with a bolder, more standard curved left arrow

Redo:
- Replaced with a bolder, more standard curved right arrow

Save:
- Replaced with a clearer floppy-disk save symbol

Revert:
- Replaced with a document/page plus restore arrow symbol

General:
- Increased icon drawing clarity
- Slightly enlarged toolbar icon size for better readability
```

## v1.1.14 map icon and bottom actions

This build updates the app icon and improves the bottom canvas toolbar.

### Changed

```text
Icon:
- Replaced the old small-text EQ Maps icon
- New icon uses the selected full-space golden windrose over parchment map
- Rebuilt app/resources/eq_maps_icon.png and app/resources/eq_maps_icon.ico

Startup:
- Removed the beta safety popup from startup
- The normal welcome / quick-start dialog remains available

Bottom canvas toolbar:
- Added Undo
- Added Redo
- Added Save Edits
- Added Revert Unsaved / reload from disk
```

## v1.1.13 icon resource fix

This build fixes icon lookup for the packaged EXE.

### Changed

```text
The app now looks for bundled resources in:
- the EXE folder
- the PyInstaller _internal folder
- the PyInstaller _MEIPASS bundle folder
- the source app folder

The app prefers eq_maps_icon.ico on Windows.
The build script now deletes old build/dist folders before building.
The PyInstaller spec uses an absolute path to the .ico file.
```

### Why this matters

```text
In PyInstaller one-folder builds, resources are often placed under:
dist/EQMapEditor/_internal/resources/

Earlier builds looked mainly beside the EXE:
dist/EQMapEditor/resources/

So the app could miss the icon at runtime, even though the icon file existed in the package.
```

## v1.1.12 icon and canvas toolbar refinement

This build addresses app icon display and makes the bottom canvas overlay controls functional.

### Changed

```text
App icon:
- Uses the .ico file first on Windows
- Sets a Windows AppUserModelID so the taskbar is more likely to show the EQ Maps icon
- Sets the same icon on QApplication and the main window

Canvas overlay:
- Removed the non-functional pan button
- Replaced single zoom button with Zoom Out and Zoom In buttons
- Split the selector button into edit-mode buttons:
  - Select Only
  - Move Points
  - Move Lines
  - Move Line Endpoints
- Overlay buttons stay in sync with the Inspector Edit Mode dropdown
```


## v1.1.11 beta prep

This build focuses on first-run usability, safer saving, and release polish.

### Added

```text
Integrated app icon assets:
- app/resources/eq_maps_icon.png
- app/resources/eq_maps_icon.ico
- PyInstaller spec now uses the .ico for the Windows EXE

First-run welcome / quick-start dialog
File > Quick Start
File > Keyboard Shortcuts
File > Open Logs Folder
File > About
Real Ctrl+O / Ctrl+S / Ctrl+F / Esc shortcuts for common commands
```

### Safer saving

```text
The editor now records file modified-times when map files are loaded.
Before Save Edits, it checks whether any target file changed externally.
If a file changed on disk after loading, the editor warns before overwriting.
```


## v1.1.10 pan beyond map edges

This build makes the map canvas easier to navigate near the outer edges.

### Changed

```text
Expanded the QGraphicsScene pan area beyond the map bounds
Users can now pan past the edge of the loaded map
Left/right/top/bottom map edges can be centered in the view
Fit Map still fits to the actual map content, not the padded pan area
Mini overview still shows the actual map content and current viewport rectangle
```


## v1.1.9 palette mapping preview

This build replaces blind nearest-colour conversion with a visible mapping preview.

### Added

```text
Mapping Preview table in Bulk Colours > Palette Conversion

The preview groups visible map colours separately by:
- Point colours
- Line colours

Each group shows:
- RGB swatch
- RGB value
- Count
- Sample point labels, when available
- A dropdown to choose the palette role
```

### Why this matters

```text
The same RGB colour might mean different things in different maps.
Lines could be water, walls, paths, or zone boundaries.
Points could be vendors, bankers, portals, monsters, or generic labels.
```

So v1.1.9 lets the user decide:

```text
Current map colour → palette role → target light/dark colour
```

### Buttons

```text
Build Mapping Preview
- Rebuilds the detected colour groups

Auto-map
- Uses label clues for point colours where possible
- Falls back to nearest RGB match

Apply Mapping
- Applies only the preview rows that are mapped to a role
- Skips rows set to Skip

Quick Apply Nearest
- Keeps the old v1.1.8 behaviour for fast simple conversions
```


## v1.1.8 map colour palettes

This build adds light/dark colour palettes for map files.

### Added

```text
Palette Conversion section in Bulk Colours
Built-in palettes:
- EQ Map Standard
- High Contrast

User palette support:
- Custom palettes are saved as JSON files in app/palettes/
- Use Edit / Save Palette to save your own paired light/dark palette entries
- Open Palettes Folder opens the palette folder

Palette conversion:
- Choose a palette
- Choose target: Dark or Light
- Click Apply Palette to Visible Records
- The app maps each current colour to the nearest palette entry
- It then applies that entry's matching light or dark RGB value
```


## v1.1.7 toolbar and canvas button cleanup

This build fixes clipping/alignment issues in the top toolbar and bottom canvas overlay.

### Changes

```text
Top toolbar buttons now render as full rectangles again
Search Labels text and search box are vertically aligned with the toolbar buttons
Bottom canvas overlay buttons now render as full rectangles and are centered in the overlay bar
Canvas overlay icons are now drawn icons instead of hard-to-see text/emoji glyphs
```


## v1.1.6 inspector cleanup

This build removes the non-functional thumb tack / pin icon from the Inspector header.

### Changes

```text
Removed the placeholder Inspector pin button
Kept the Inspector close / hide button
No behavior changes to the Inspector itself
```


## v1.1.5 canvas overlay / explorer simplification

This build removes the left Explorer tool panel and moves useful context into the map canvas.

### Changes

```text
Removed the left Explorer rail/tools from the main layout
Center map canvas now expands to use the freed space
Added a bottom-left canvas control/status overlay:
- Select mode shortcut
- Pan hint
- Zoom hint
- Fit map shortcut
- Cursor X/Y/Z readout
- Zoom percentage

Added a bottom-right mini overview map
- Shows the full loaded map
- Draws a viewport rectangle showing the current visible area

Aligned the Search Labels text box with the rest of the top toolbar controls
Zone search now filters while typing instead of requiring Search/Enter
```


## v1.1.4 left explorer refinement

This build updates the left Explorer panel to better match the Option 1 concept.

### Changes

```text
Added a vertical navigation rail for:
- Zones
- Layers
- Bulk Colours
- Points
- Pending Changes

Added stacked Explorer pages instead of a single long stacked column
Zones page now includes a searchable zone preview list
Layers page now summarizes loaded files and visibility
Bulk Colours, Points, and Pending pages each have clearer focused summaries
Explorer width and styling updated to better match the mockup
```


## v1.1.3 inspector refinement

This build updates the right-side Inspector to better match the Option 1 concept.

### Changes

```text
Inspector header with utility buttons
Selection Summary card with Delete Selected action
Card-style grouped sections for Label, Point Coordinates, Line Endpoints, Color (RGB), and Point Size
Full-width primary Apply Changes button
Cleaner helper text and footer summary
Wider right-side inspector area
```


# EQ Map Editor

A standalone desktop editor for EverQuest map `.txt` files.

EQ Map Editor can load, inspect, edit, recolour, search, and safely save EverQuest map line/point records.

![Main editor window](docs/screenshots/main_window_overview.png)

## Current version

```text
v1.1.19-svg-toolbar-icons
```

## Beta 12 fix

This build applies the same explicit inverted arrow images to the main editor spin boxes, not just the colour picker dialog.

Changes:

```text
Main Selected Item RGB/coordinate/size spin boxes now use explicit light arrow PNGs in dark mode
Colour picker dialog keeps the Beta 11 explicit arrow image fix
Dark spin-box buttons retain the larger clickable area
```

## Beta 11 fix

This build keeps the colour picker dialog in dark mode while restoring visible up/down arrows.

Changes:

```text
QColorDialog now uses explicit light arrow PNGs on dark spin-box buttons
The arrows visually match the light-mode arrow shape, but inverted for dark mode
Runtime resources are created in the local resources/ folder
APP_ROOT now points beside the EXE in PyInstaller builds
```

## Beta 10 fix

This build fixes the QColorDialog RGB/Hue/Sat/Val spin-box arrows in dark mode.

Changes:

```text
Removed all QSpinBox/QDoubleSpinBox subcontrol styling from the dark app stylesheet
Added a local light/native stylesheet for QColorDialog
Replaced static QColorDialog.getColor calls with a helper dialog that keeps spin-box arrows visible
```

## Beta 9 fix

This build fixes the spin-box arrow rendering issue where the RGB selector arrows could appear as white boxes in dark mode.

The custom CSS triangle arrows were removed; Qt now draws the native/Fusion arrows while the clickable button area remains styled for dark mode.

## Beta 8 fix

This build fixes an issue in the standalone EXE package where the up/down arrows on RGB spin boxes could be unreliable or invisible on some Windows/PyInstaller builds.

Changes:

```text
Use Fusion style for consistent Windows widget rendering
Force RGB spin boxes to use explicit Up/Down arrows
Give RGB spin boxes a larger clickable arrow area
Add dark-mode styling for spin box arrow buttons
```

## v1.1.2 fix

Fixed a missing `QSize` import used by the refined top toolbar.

## v1.1.1 top bar refinement

This build refines the Option 1 top toolbar to better match the mockup.

### Changes

```text
Toolbar buttons use a more card-like grouped style
File button is styled inline with the rest of the toolbar
Search label and search box are visually aligned with the toolbar buttons
Light and dark themes now use the same toolbar padding, margins, and control sizes
Theme switching no longer changes the top-bar spacing/layout
```

## v1.1 Option 1 UI update

This build applies the **Option 1 – Explorer + Canvas + Inspector** layout.

### Layout changes

```text
Left Explorer panel
- Zones quick access
- Layer visibility
- Bulk colour swatches
- Points/lines summary
- Pending changes summary

Center canvas
- Main map remains the largest area
- Existing pan/zoom/fit/search tools retained

Right Inspector
- Selected item editing remains on the right
- Existing tools are still available through Inspector tabs and left Explorer buttons
```

### Feature access retained

All current Beta 12 features remain in the build:

```text
File menu
Fit Map / Fit Selected / Clear Selection
Show Labels / Show Points
Light/Dark background
Toggle Sidebar
Global label search
Zone browser
Layer visibility
Bulk colour tools
Points search/bulk tools
Pending Changes
Preferences
Save Edits / Save As / Revert / Restore Backup
Keyboard shortcuts
```

## Important beta safety warning

This tool edits EverQuest map `.txt` files.

Before beta testing:

1. Make a copy of your entire EverQuest `maps` folder.
2. Prefer **File > Save As...** when testing edits.
3. Review **Pending Changes** before saving.
4. Keep the automatically created backups until you have verified the edited maps in-game.

The editor stores its support files in local folders next to the program:

```text
logs/
settings/
backups/
```

## Features

### Map loading and display

- Load one or more EQ map `.txt` files.
- Open zones from a selected map folder.
- Display `L` records as coloured lines.
- Display `P` records as coloured points and labels.
- Show/hide labels.
- Show/hide points.
- Light and dark backgrounds.
- Optional display-Y flip in Preferences.
- Layer visibility by map file.

### Editing

- Select points and lines.
- Edit point label, coordinates, colour, and size.
- Edit line endpoints and colour.
- Move points.
- Move whole lines.
- Move line endpoints.
- Add points.
- Add lines.
- Delete selected points/lines.
- Multi-select points/lines.
- Recolour multiple selected records at once.

### Bulk tools

- Bulk colour list for point colours.
- Bulk colour list for line colours.
- Select/highlight all records using one or more colours.
- Recolour all prepared matching records.
- Search point labels.
- Select all matching point labels.
- Bulk delete checked points.
- Bulk recolour checked points.

### Safety and recovery

- **Save As...** to write edited copies to another folder.
- **Save Edits** creates timestamped backups.
- **Revert Unsaved** reloads from disk.
- **Restore Backup...** restores from the local backups folder.
- **Open Backup Folder** opens the local backup folder.
- **Pending Changes** tab shows unsaved edits.
- Error log file for beta troubleshooting.

## Downloading from GitHub Actions

This repository includes a GitHub Actions workflow that builds a Windows portable `.exe` package.

1. Open the repository on GitHub.
2. Click **Actions**.
3. Click **Build Windows EXE**.
4. Click **Run workflow**.
5. Wait for the build to finish.
6. Download the artifact named **EQMapEditor-Windows**.
7. Extract `EQMapEditor-Windows.zip`.
8. Run:

```text
EQMapEditor.exe
```

## Building locally on Windows

Install Python 3.11 or newer, then run:

```text
build_windows.bat
```

The build output will appear here:

```text
dist/EQMapEditor/
```

The executable will be:

```text
dist/EQMapEditor/EQMapEditor.exe
```

## Running from source

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
python app/eq_map_editor.py
```

## Main window overview

![Main editor window](docs/screenshots/main_window_overview.png)

The top row contains the inline **File** menu, view controls, label/point toggles, background toggles, search, and sidebar toggle.

The right sidebar contains:

```text
Selected Item
Layers
Bulk Colours
Points
Zones
Pending Changes
```

## File menu

![File menu](docs/screenshots/file_menu.png)

The **File** menu contains:

```text
Open Map File(s)
Save Edits
Save As...
Revert Unsaved
Restore Backup...
Open Backup Folder
Preferences
Controls
Exit
```

### Open Map File(s)

Open one or more EQ map `.txt` files.

Common examples:

```text
poknowledge.txt
poknowledge_1.txt
poknowledge_2.txt
```

### Save Edits

Writes changes back to the loaded source files.

Before overwriting, the editor writes backups to:

```text
backups/
```

### Save As...

Writes edited copies to a folder you choose without changing the original source files.

This is the safest option for beta testing.

### Revert Unsaved

Reloads the current files from disk and discards unsaved edits.

### Restore Backup...

Restores a `.bak` file from the local backups folder.

### Open Backup Folder

Opens the local backups folder.

## Global label search

![Global search](docs/screenshots/global_search.png)

The toolbar search works on visible point labels.

### Find First

Selects the first visible point whose label contains the search text, centers on it, and shows its details.

### Select Matches

Selects and highlights all visible points whose labels contain the search text.

### Center Selected

Centers the view on the current selected point/line records.

## Preferences

![Preferences](docs/screenshots/preferences.png)

Open Preferences from:

```text
File > Preferences
```

Preferences include:

```text
Remember last loaded map
Auto-fit restored map on startup
Autosave settings on exit
Show beta safety warning on startup
Flip display Y
Default background
Default map folder
Warn before highlighting more than X records
Confirm bulk edits over X records
Confirm deletes over X records
```

Settings are saved to:

```text
settings/eq_map_editor_settings.json
```

## Zones tab

![Zones tab](docs/screenshots/zones_tab.png)

The **Zones** tab lets you choose your EQ map folder and open zones by name.

It shows zones as:

```text
Full Zone Name (shortname)
```

Example:

```text
Misty Thicket (misty)
Plane of Knowledge (poknowledge)
Acrylia Caverns (acrylia)
The Bazaar (bazaar)
```

Double-click a zone or click **Open Selected Zone** to load its map files.

The editor looks for files such as:

```text
misty.txt
misty_1.txt
misty_2.txt
misty_3.txt
misty_4.txt
```

## Pending Changes tab

![Pending changes](docs/screenshots/pending_changes.png)

The **Pending Changes** tab lists unsaved edits.

It helps you review changes before saving.

Buttons:

```text
Refresh
Revert All Unsaved
Save Edits
```

## Keyboard shortcuts

```text
Ctrl+O   Open map files
Ctrl+S   Save edits
Ctrl+Z   Undo
Ctrl+Y   Redo
Ctrl+F   Focus label search box
Esc      Clear selection/highlights
Del      Delete selected records
Ctrl+A   Select all visible records
F        Fit map
```

## Map record formats

The editor works with standard EQ map text records:

### Lines

```text
L x1, y1, z1, x2, y2, z2, r, g, b
```

### Points

```text
P x, y, z, r, g, b, size, label
```

## Known limitations

- This is beta software.
- Always keep backups of your map folder.
- Very large highlight operations can still take time if tens of thousands of records are highlighted.
- `Save As...` writes edited copies but does not switch the current editing session to the output folder.
- The zone full-name list is built in and may not include every custom/private server zone.
- The app does not yet detect if a map file was externally modified after being loaded.
- This release package builds a Windows executable using GitHub Actions or a local Windows Python environment.

## Repository structure

```text
app/
  eq_map_editor.py
  logs/
  settings/
  backups/

docs/
  screenshots/

.github/
  workflows/
    build-windows.yml

build_windows.bat
build_windows.ps1
eq_map_editor.spec
requirements.txt
README.md
```

## License

Add your preferred license before publishing publicly.

## NPC Match & Swap

The sidebar now includes an **NPC Match** tab for comparing the currently loaded zone against an NPC data workbook or CSV.

Workflow:

1. Load a zone map, such as `poknowledge.txt` or `poknowledge_1.txt`.
2. Open the **NPC Match** tab.
3. Click **Choose NPC Data** and select an `.xlsx` or `.csv` source containing NPC rows.
4. Click **Compare Current Zone**.
5. Review the table. The **NPC Label** column is editable before applying changes.
6. Click **Preview Selected** to show proposed NPC positions and labels on the map.
7. Click **Apply Selected** to update selected map points.
8. Click **Save Edits** when you are satisfied.

The feature filters NPC data to the currently loaded zone shortname only. Generated NPC labels use this format:

```text
npc_name_(npc_role)
```

If `npc_role` is blank or `\N`, the label uses only `npc_name`. Spaces are replaced with underscores. Applying swaps changes only the point label and XYZ coordinates; RGB colour, size, source file, and layer are preserved.

## NPC Match: Expansion / Era Cleanup

The NPC Match tab now includes an **Expansion / Era Cleanup** section. Choose your current EverQuest expansion, then click **Scan Era Labels** to compare the currently loaded map labels against the NPC data for the same zone.

The scan flags loaded map labels when either:

- the matched NPC has a `min_expansion_number` greater than the selected expansion; or
- the matched NPC has a `max_expansion_number` that is known and lower than the selected expansion.

Use **Preview Removals** to highlight the selected labels on the map before changing anything. **Remove Selected Labels** marks the selected point labels for deletion as one undoable action. The map is not saved until you click **Save Edits**.

Click **Save Expansion Setting** to store the current expansion in `settings/eq_map_editor_settings.json`, so the same expansion is preselected when you open the editor or change maps.

## NPC Match: Add Missing NPCs for Current Era

The NPC Match tab also includes **Add Missing NPCs for Current Era**. This finds NPC rows from the loaded NPC data that:

- are in the currently loaded zone;
- fit the selected current expansion using `min_expansion_number` and `max_expansion_number`; and
- do not already appear to be on the loaded map.

Workflow:

1. Load a zone map.
2. Choose or reload the NPC data source.
3. Set the current expansion in the **Expansion / Era Cleanup** section. You can save it as the default with **Save Expansion Setting**.
4. Click **Find Missing NPCs**.
5. Edit labels directly in the **NPC Label** column if needed.
6. Check the NPCs you want to add, or use **Select All**.
7. Optionally set the RGB and point size for the new map labels.
8. Click **Preview Adds** to show the proposed labels on the map.
9. Click **Add Selected NPCs** to append the checked NPCs to the active map file.
10. Click **Save Edits** when you are satisfied.

The missing-NPC scan uses the same match scoring as NPC Match & Swap, so it can recognize existing map labels even if the label format differs slightly. New NPC labels are appended as new `P` records with the NPC map XYZ coordinates, your chosen RGB/size, and the editable label from the table.

### v1.1.23 NPC Match tab layout refinements

The NPC Match tab now uses a scrollable layout with three collapsible, vertically resizable workflow boxes:

1. NPC Match & Swap
2. Expansion / Era Cleanup
3. Add Missing NPCs for Current Era

Each workflow can be expanded while the others are collapsed, and the vertical splitter lets the user adjust the visible height of the workflow boxes and their tables.

The Add Missing NPCs workflow now shows RGB and size controls on a single compact line. The same line includes a live colour preview and a **Match existing label style** dropdown/button. Choosing an existing map label and clicking **Match** copies that label's RGB and size values into the new-NPC style controls.

### v1.1.24 refinement

The Add Missing NPCs style row now shows two colour previews:

- the active colour/size that will be used for newly added NPC labels
- the selected existing label colour immediately before the **Match** button, so you can preview the source style before copying it


### v1.1.25 - Existing label style dropdown swatches

- The Add Missing NPCs style dropdown now shows a colour swatch beside every existing map label, making it easier to choose a label whose RGB/size should be copied.
- The separate source colour preview before the Match button remains and updates when the selected dropdown row changes.

### v1.1.26 NPC matching and layout fixes

- Updated the NPC matching logic to follow `extract_eq_map_points.py` more closely:
  - exact NPC-name matches are marked `Yes`
  - alias/fuzzy name matches are marked `Possible`
  - `Coordinate Match` is only assigned when the row was already a possible name match and the distance is within 20 units
  - unrelated nearby map labels are no longer matched by coordinates alone
- The NPC Match & Swap table now uses the script-style match statuses: `Yes`, `Coordinate Match`, `Possible`, `Map only`, and `NPC only`.
- Checked/default rows now follow the apply script behavior by selecting only `Yes` and `Coordinate Match` rows by default.
- Collapsing an NPC workflow box now shrinks it to a one-line header.
- When NPC workflow boxes are collapsed, the remaining open boxes are rebalanced so one open tool gets the available height, or two open tools split it evenly.
- The missing-NPC style dropdown now refreshes whenever it opens and also refreshes whenever a new map is loaded, so clicking **Match existing label style...** shows the loaded map labels.
- The Add Missing NPCs style row was tightened so the RGB, size, source-style dropdown, swatch, and Match button fit better on one line.

## v1.1.27 NPC Match table filters and deletion

The NPC Match & Swap workflow now includes table filtering and deletion helpers:

- Match Type filter: All, Yes, Coordinate Match, Possible, NPC only, Map only.
- Presence filter: All presence, Present on map, Missing from map.
- Search box over current label, NPC label, NPC name, NPC role, coordinates, and expansion text.
- Delete Selected From Map marks selected rows that already have a map point for deletion. NPC-only rows are ignored. The operation is undoable and still requires Save Edits to write the removal to the map text file.
- NPC Match, Era Cleanup, and Add Missing NPCs tables all use interactive column headers so columns can be widened or narrowed manually.

The NPC matching logic continues to mirror `extract_eq_map_points.py`: exact name matches become `Yes`; alias/fuzzy matches become `Possible`; a possible match within 20 units becomes `Coordinate Match`; unrelated nearby labels are not coordinate-matched.
