# EQ Map Editor

A standalone desktop editor for EverQuest map `.txt` files.

EQ Map Editor can load, inspect, edit, recolour, search, and safely save EverQuest map line/point records.

<img width="1644" height="1062" alt="image" src="https://github.com/user-attachments/assets/f7b9fae5-3161-450e-b71a-8b6966e89137" />

## Current version

```text
v1.0.0 beta12
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

<img width="1645" height="1028" alt="image" src="https://github.com/user-attachments/assets/7b0b8b37-c004-4d0b-b37b-2a3961f9267d" />

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

<img width="530" height="776" alt="image" src="https://github.com/user-attachments/assets/ec0de276-461c-4f78-8613-dc0613592d07" />

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

