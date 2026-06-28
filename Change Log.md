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
