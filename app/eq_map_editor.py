#!/usr/bin/env python3
"""
EQ Map Editor v0.4

This version starts from the v0.3 feature set and adds:

- Edit Mode safety toggle:
  - Select Only
  - Move Points
  - Move Lines
  - Move Line Endpoints
- Click a line and move the whole line segment.
- Show draggable endpoint handles on selected lines.
- Move endpoint 1 or endpoint 2 separately.
- Save moved line records back to the source text file.
- Undo / Redo for:
  - Move point
  - Edit point label
  - Edit point colour
  - Move line
  - Move line endpoint
  - Edit line colour
- Dirty-file indicator.
- Prompt before closing with unsaved edits.
- Reload from disk.
- Restore from timestamped backup.
- Light/dark background.
- Display-only Y flip.
"""

from __future__ import annotations

import argparse
import json
import os
import traceback
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional, Any

from PySide6.QtCore import Qt, QPointF, QRectF, QTimer
from PySide6.QtGui import QAction, QActionGroup, QColor, QPainter, QPen, QBrush, QFont, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QColorDialog,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsLineItem,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QDoubleSpinBox,
    QSpinBox,
    QAbstractSpinBox,
    QSplitter,
    QStatusBar,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QGroupBox,
    QCheckBox,
    QInputDialog,
    QListWidget,
    QListWidgetItem,
    QDialog,
    QDialogButtonBox,
    QTabWidget,
    QMenu,
)


VERSION = "v1.0.0-beta12"
APP_ROOT = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
LOGS_DIR = APP_ROOT / "logs"
SETTINGS_DIR = APP_ROOT / "settings"
BACKUPS_DIR = APP_ROOT / "backups"
RESOURCES_DIR = APP_ROOT / "resources"
SETTINGS_PATH = SETTINGS_DIR / "eq_map_editor_settings.json"
LOG_PATH = LOGS_DIR / "eq_map_editor.log"

for _folder in (LOGS_DIR, SETTINGS_DIR, BACKUPS_DIR, RESOURCES_DIR):
    _folder.mkdir(parents=True, exist_ok=True)

# Built-in zone display names. Based on the RedGuides / ReadGuides zone short-name reference.
# The folder scanner also includes unknown shortnames it finds in the selected map folder.
ZONE_SHORTNAME_TO_FULLNAME = {
    "qeynos": "South Qeynos", "qeynos2": "North Qeynos", "qrg": "Surefall Glade",
    "qeytoqrg": "Qeynos Hills", "highkeep": "HighKeep", "freportn": "North Freeport",
    "freportw": "West Freeport", "freporte": "East Freeport", "runnyeye": "Clan RunnyEye",
    "qey2hh1": "West Karana", "northkarana": "North Karana", "southkarana": "South Karana",
    "eastkarana": "East Karana", "beholder": "Gorge of King Xorbb", "blackburrow": "BlackBurrow",
    "paw": "Infected Paw", "rivervale": "Rivervale", "kithicor": "Kithicor Forest (A)",
    "commons": "West Commonlands", "ecommons": "East Commonlands", "erudnint": "Erudin Palace",
    "erudnext": "Erudin", "nektulos": "Nektulos Forest", "cshome": "Sunset Home",
    "lavastorm": "Lavastorm Mountains", "nektropos": "Nektropos", "halas": "Halas",
    "everfrost": "Everfrost Peaks", "soldunga": "Solusek's Eye", "soldungb": "Nagafen's Lair",
    "misty": "Misty Thicket (A)", "nro": "North Ro (A)", "sro": "South Ro (A)",
    "befallen": "Befallen (A)", "oasis": "Oasis of Marr", "tox": "Toxxulia Forest",
    "hole": "The Ruins of Old Paineel", "neriaka": "Neriak Foreign Quarter", "neriakb": "Neriak Commons",
    "neriakc": "Neriak Third Gate", "neriakd": "Neriak Palace", "najena": "Najena",
    "qcat": "Qeynos Catacombs", "innothule": "Innothule Swamp (A)", "feerrott": "The Feerrott (A)",
    "cazicthule": "Cazic-Thule", "oggok": "Oggok", "rathemtn": "Mountains of Rathe",
    "lakerathe": "Lake Rathetear", "grobb": "Grobb", "aviak": "Aviak Village",
    "gfaydark": "The Greater Faydark", "akanon": "Ak'Anon", "steamfont": "Steamfont Mountains",
    "lfaydark": "The Lesser Faydark", "crushbone": "Clan Crushbone", "mistmoore": "Castle Mistmoore",
    "kaladima": "Kaladim (A)", "felwithea": "Felwithe (A)", "felwitheb": "Felwithe (B)",
    "unrest": "Estate of Unrest", "kedge": "Kedge Keep", "guktop": "Upper Guk",
    "gukbottom": "Lower Guk", "kaladimb": "Kaladim (B)", "butcher": "Butcherblock Mountains",
    "oot": "Ocean of Tears", "cauldron": "Dagnor's Cauldron", "airplane": "Plane of Sky",
    "fearplane": "Plane of Fear", "permafrost": "Permafrost Keep", "kerraridge": "Kerra Isle",
    "paineel": "Paineel", "hateplane": "The Plane of Hate", "arena": "The Arena (A)",
    "soltemple": "Temple of Solusek Ro", "erudsxing": "Erud's Crossing", "stonebrunt": "Stonebrunt Mountains",
    "warrens": "The Warrens", "bazaar": "The Bazaar", "bazaar2": "The Bazaar (2)",
    "arena2": "The Arena (B)", "jaggedpine": "The Jaggedpine Forest", "nedaria": "Nedaria's Landing",
    "tutorial": "Tutorial Zone", "load": "Loading (A)", "load2": "Loading (B)", "hateplaneb": "The Plane of Hate",
    "shadowrest": "Shadowrest", "tutoriala": "The Mines of Gloomingdeep (A)",
    "tutorialb": "The Mines of Gloomingdeep (B)", "clz": "Loading (C)", "poknowledge": "Plane of Knowledge",
    "soldungc": "The Caverns of Exile", "guildlobby": "The Guild Lobby", "barter": "The Barter Hall",
    "takishruins": "Ruins of Takish-Hiz", "freeporteast": "East Freeport", "freeportwest": "West Freeport",
    "freeportsewers": "Freeport Sewers", "northro": "North Ro (B)", "southro": "South Ro (B)",
    "highpasshold": "Highpass Hold", "commonlands": "Commonlands", "oceanoftears": "Ocean Of Tears",
    "kithforest": "Kithicor Forest (B)", "befallenb": "Befallen (B)", "highpasskeep": "Highpass Keep",
    "innothuleb": "Innothule Swamp (B)", "toxxulia": "Toxxulia Forest", "mistythicket": "Misty Thicket (B)",
    "steamfontmts": "Steamfont Mountains", "dragonscalea": "Tinmizer's Wunderwerks",
    "crafthalls": "Ngreth's Den", "weddingchapel": "Wedding Chapel", "weddingchapeldark": "Wedding Chapel",
    "dragoncrypt": "Lair of the Fallen", "arttest": "Art Testing Domain", "fhalls": "The Forgotten Halls",
    "fieldofbone": "The Field of Bone", "warslikswood": "Warsliks Wood", "droga": "Temple of Droga",
    "cabwest": "West Cabilis", "swampofnohope": "Swamp of No Hope", "firiona": "Firiona Vie",
    "lakeofillomen": "Lake of Ill Omen", "dreadlands": "Dreadlands", "burningwood": "Burning Woods",
    "kaesora": "Kaesora", "sebilis": "Old Sebilis", "citymist": "City of Mist",
    "skyfire": "Skyfire Mountains", "frontiermtns": "Frontier Mountains", "overthere": "The Overthere",
    "emeraldjungle": "The Emerald Jungle", "trakanon": "Trakanon's Teeth", "timorous": "Timorous Deep",
    "kurn": "Kurn's Tower", "karnor": "Karnor's Castle", "chardok": "Chardok",
    "dalnir": "Dalnir", "charasis": "Howling Stones", "cabeast": "East Cabilis",
    "nurga": "Mines of Nurga", "veeshan": "Veeshan's Peak", "veksar": "Veksar",
    "chardokb": "The Halls of Betrayal", "iceclad": "Iceclad Ocean", "frozenshadow": "Tower of Frozen Shadow",
    "velketor": "Velketor's Labyrinth", "kael": "Kael Drakkal", "skyshrine": "Skyshrine",
    "thurgadina": "Thurgadin", "eastwastes": "Eastern Wastes", "cobaltscar": "Cobalt Scar",
    "greatdivide": "Great Divide", "wakening": "The Wakening Land", "westwastes": "Western Wastes",
    "crystal": "Crystal Caverns", "necropolis": "Dragon Necropolis", "templeveeshan": "Temple of Veeshan",
    "sirens": "Siren's Grotto", "mischiefplane": "Plane of Mischief", "growthplane": "Plane of Growth",
    "sleeper": "Sleeper's Tomb", "thurgadinb": "Icewell Keep", "shadowhaven": "Shadow Haven",
    "nexus": "The Nexus", "echo": "Echo Caverns", "acrylia": "Acrylia Caverns",
    "sharvahl": "Shar Vahl", "paludal": "Paludal Caverns", "fungusgrove": "Fungus Grove",
    "vexthal": "Vex Thal", "sseru": "Sanctus Seru", "katta": "Katta Castellum",
    "netherbian": "Netherbian Lair", "ssratemple": "Ssraeshza Temple", "griegsend": "Grieg's End",
    "thedeep": "The Deep", "shadeweaver": "Shadeweaver's Thicket", "hollowshade": "Hollowshade Moor",
    "grimling": "Grimling Forest", "mseru": "Marus Seru", "letalis": "Mons Letalis",
    "twilight": "The Twilight Sea", "thegrey": "The Grey", "tenebrous": "The Tenebrous Mountains",
    "maiden": "The Maiden's Eye", "dawnshroud": "Dawnshroud Peaks", "scarlet": "The Scarlet Desert",
    "umbral": "The Umbral Plains", "akheva": "Akheva Ruins", "codecay": "Ruins of Lxanvom",
    "pojustice": "Plane of Justice", "potranquility": "Plane of Tranquility",
    "ponightmare": "Plane of Nightmare", "podisease": "Plane of Disease", "poinnovation": "Plane of Innovation",
    "potorment": "Plane of Torment", "povalor": "Plane of Valor", "bothunder": "Torden, The Bastion of Thunder",
    "postorms": "Plane of Storms", "hohonora": "Halls of Honor", "solrotower": "Solusek Ro's Tower",
    "powar": "Plane of War", "potactics": "Drunder, Fortress of Zek", "poair": "Eryslai, the Kingdom of Wind",
    "powater": "Reef of Coirnav", "pofire": "Doomfire, The Burning Lands",
    "poeartha": "Vegarlson, The Earthen Badlands", "potimea": "Plane of Time (A)",
    "hohonorb": "Temple of Marr (A)", "nightmareb": "Lair of Terris Thule",
    "poearthb": "Stronghold of the Twelve", "potimeb": "Plane of Time (B)",
    "gunthak": "Gulf of Gunthak", "dulak": "Dulak's Harbor", "torgiran": "Torgiran Mines",
    "nadox": "Crypt of Nadox", "hatesfury": "Hate's Fury, The Scorned Maiden",
    "abysmal": "Abysmal Sea", "natimbi": "Natimbi, The Broken Shores", "qinimi": "Qinimi, Court of Nihilia",
    "riwwi": "Riwwi, Coliseum of Games", "barindu": "Barindu, Hanging Gardens",
    "ferubi": "Ferubi, Forgotten Temple of Taelosia", "tipt": "Tipt, Treacherous Crags",
    "vxed": "Vxed, The Crumbling Caverns", "yxtta": "Yxtta, Pulpit of Exiles",
    "uqua": "Uqua, The Ocean God Chantry", "kodtaz": "Kod'Taz, Broken Trial Grounds",
    "qvic": "Qvic, Prayer Grounds of Calling", "inktuta": "Inktu`Ta, The Unmasked Chapel",
    "txevu": "Txevu, Lair of the Elite", "tacvi": "Tacvi, Seat of the Slaver",
    "wallofslaughter": "Wall of Slaughter", "bloodfields": "The Bloodfields",
    "draniksscar": "Dranik's Scar", "causeway": "Nobles' Causeway",
    "provinggrounds": "Muramite Proving Grounds", "anguish": "Asylum of Anguish",
    "crescent": "Crescent Reach", "moors": "Blightfire Moors", "stonehive": "Stone Hive",
    "mesa": "Goru`kar Mesa", "roost": "Blackfeather Roost", "steppes": "The Steppes",
    "icefall": "Icefall Glacier", "valdeholm": "Valdeholm", "frostcrypt": "Frostcrypt, Throne of the Shade King",
    "sunderock": "Sunderock Springs", "vergalid": "Vergalid Mines", "direwind": "Direwind Cliffs",
    "ashengate": "Ashengate, Reliquary of the Scale",
}
MAX_BULK_HIGHLIGHTS = 0  # 0 means highlight all matching records


@dataclass
class MapLineRecord:
    file_path: Path
    line_index: int
    raw_text: str
    x1: float
    y1: float
    z1: float
    x2: float
    y2: float
    z2: float
    r: int
    g: int
    b: int
    dirty: bool = False
    deleted: bool = False

    @property
    def color(self) -> QColor:
        return QColor(self.r, self.g, self.b)

    def to_map_line(self) -> str:
        return (
            f"L {self.x1:.4f}, {self.y1:.4f}, {self.z1:.4f}, "
            f"{self.x2:.4f}, {self.y2:.4f}, {self.z2:.4f}, "
            f"{self.r}, {self.g}, {self.b}"
        )


@dataclass
class MapPointRecord:
    file_path: Path
    line_index: int
    raw_text: str
    x: float
    y: float
    z: float
    r: int
    g: int
    b: int
    size: float
    label: str
    dirty: bool = False
    deleted: bool = False

    @property
    def color(self) -> QColor:
        return QColor(self.r, self.g, self.b)

    def to_map_line(self) -> str:
        return (
            f"P {self.x:.4f}, {self.y:.4f}, {self.z:.4f}, "
            f"{self.r}, {self.g}, {self.b}, {self.size:g}, {self.label}"
        )


@dataclass
class LoadedMap:
    lines: list[MapLineRecord]
    points: list[MapPointRecord]


def clamp_rgb(value: str | int) -> int:
    number = int(float(str(value).strip()))
    return max(0, min(255, number))


def parse_l_record(row: str, file_path: Path, line_index: int) -> Optional[MapLineRecord]:
    stripped = row.strip()
    if not stripped.startswith("L "):
        return None
    parts = [part.strip() for part in stripped[2:].split(",")]
    if len(parts) < 9:
        return None
    try:
        x1, y1, z1, x2, y2, z2 = [float(value) for value in parts[:6]]
        r, g, b = [clamp_rgb(value) for value in parts[6:9]]
    except ValueError:
        return None
    return MapLineRecord(file_path, line_index, row.rstrip("\n"), x1, y1, z1, x2, y2, z2, r, g, b)


def parse_p_record(row: str, file_path: Path, line_index: int) -> Optional[MapPointRecord]:
    stripped = row.rstrip("\n")
    if not stripped.startswith("P "):
        return None
    parts = [part.strip() for part in stripped[2:].split(",", 7)]
    if len(parts) < 8:
        return None
    try:
        x, y, z = [float(value) for value in parts[:3]]
        r, g, b = [clamp_rgb(value) for value in parts[3:6]]
        size = float(parts[6])
        label = parts[7].strip()
    except ValueError:
        return None
    return MapPointRecord(file_path, line_index, row.rstrip("\n"), x, y, z, r, g, b, size, label)


def load_map_files(file_paths: Iterable[Path]) -> LoadedMap:
    lines: list[MapLineRecord] = []
    points: list[MapPointRecord] = []

    for file_path in file_paths:
        file_path = Path(file_path)
        with file_path.open("r", encoding="utf-8", errors="replace") as handle:
            for line_index, row in enumerate(handle):
                line_record = parse_l_record(row, file_path, line_index)
                if line_record is not None:
                    lines.append(line_record)
                    continue

                point_record = parse_p_record(row, file_path, line_index)
                if point_record is not None:
                    points.append(point_record)

    return LoadedMap(lines=lines, points=points)


class CoordinateMapper:
    def __init__(self, flip_display_y: bool = False) -> None:
        self.flip_display_y = flip_display_y

    def map_to_scene(self, x: float, y: float) -> QPointF:
        return QPointF(x, -y if self.flip_display_y else y)

    def scene_to_map(self, point: QPointF) -> tuple[float, float]:
        return point.x(), -point.y() if self.flip_display_y else point.y()


class UndoCommand:
    def __init__(self, label: str, record: Any, before: dict[str, Any], after: dict[str, Any]) -> None:
        self.label = label
        self.record = record
        self.before = before
        self.after = after

    def undo(self) -> None:
        for key, value in self.before.items():
            setattr(self.record, key, value)
        self.record.dirty = True

    def redo(self) -> None:
        for key, value in self.after.items():
            setattr(self.record, key, value)
        self.record.dirty = True



class AddRecordCommand:
    def __init__(self, label: str, main_window: "EqMapMainWindow", record: Any, collection_name: str) -> None:
        self.label = label
        self.main_window = main_window
        self.record = record
        self.collection_name = collection_name

    @property
    def collection(self):
        return getattr(self.main_window.loaded_map, self.collection_name)

    def undo(self) -> None:
        if self.record in self.collection:
            self.collection.remove(self.record)
        self.main_window.render_map(keep_view=True)
        self.main_window.side_panel.rebuild_layers()
        self.main_window.update_dirty_indicator()

    def redo(self) -> None:
        if self.record not in self.collection:
            self.collection.append(self.record)
        self.record.dirty = True
        self.main_window.render_map(keep_view=True)
        self.main_window.side_panel.rebuild_layers()
        self.main_window.update_dirty_indicator()



class BulkEditCommand:
    def __init__(self, label: str, records: list[Any], before: list[dict[str, Any]], after: list[dict[str, Any]]) -> None:
        self.label = label
        self.records = records
        self.before = before
        self.after = after

    def undo(self) -> None:
        for record, values in zip(self.records, self.before):
            for key, value in values.items():
                setattr(record, key, value)
            record.dirty = True

    def redo(self) -> None:
        for record, values in zip(self.records, self.after):
            for key, value in values.items():
                setattr(record, key, value)
            record.dirty = True


class PointDetailsDialog(QDialog):
    def __init__(self, parent=None, title="Add Point", label="", r=255, g=255, b=255, size=2.0, files: Optional[list[Path]] = None, active_file: Optional[Path] = None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.files = files or []
        layout = QVBoxLayout(self)
        form = QFormLayout()
        layout.addLayout(form)

        self.file_combo = QComboBox()
        for file_path in self.files:
            self.file_combo.addItem(file_path.name, str(file_path))
        if active_file is not None:
            for index in range(self.file_combo.count()):
                if self.file_combo.itemData(index) == str(active_file):
                    self.file_combo.setCurrentIndex(index)
                    break
        form.addRow("Target file", self.file_combo)

        self.label_edit = QLineEdit(label)
        form.addRow("Label", self.label_edit)

        self.r_spin = QSpinBox(); self.r_spin.setRange(0, 255); self.r_spin.setValue(r)
        self.g_spin = QSpinBox(); self.g_spin.setRange(0, 255); self.g_spin.setValue(g)
        self.b_spin = QSpinBox(); self.b_spin.setRange(0, 255); self.b_spin.setValue(b)
        form.addRow("R", self.r_spin)
        form.addRow("G", self.g_spin)
        form.addRow("B", self.b_spin)

        self.size_spin = QDoubleSpinBox()
        self.size_spin.setRange(0.1, 99.0)
        self.size_spin.setDecimals(2)
        self.size_spin.setValue(size)
        form.addRow("Size", self.size_spin)

        self.pick_button = QPushButton("Pick Colour")
        self.pick_button.clicked.connect(self.pick_colour)
        layout.addWidget(self.pick_button)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def pick_colour(self):
        c = choose_colour_dialog(QColor(self.r_spin.value(), self.g_spin.value(), self.b_spin.value()), self, "Choose point colour")
        if c.isValid():
            self.r_spin.setValue(c.red())
            self.g_spin.setValue(c.green())
            self.b_spin.setValue(c.blue())

    def values(self):
        return {
            "file_path": Path(self.file_combo.currentData()) if self.file_combo.currentData() else None,
            "label": self.label_edit.text().strip() or "New_Point",
            "r": self.r_spin.value(),
            "g": self.g_spin.value(),
            "b": self.b_spin.value(),
            "size": self.size_spin.value(),
        }


class LineColorDialog(QDialog):
    def __init__(self, parent=None, r=255, g=255, b=255, files: Optional[list[Path]] = None, active_file: Optional[Path] = None):
        super().__init__(parent)
        self.setWindowTitle("Line Colour")
        self.files = files or []
        layout = QVBoxLayout(self)
        form = QFormLayout()
        layout.addLayout(form)

        self.file_combo = QComboBox()
        for file_path in self.files:
            self.file_combo.addItem(file_path.name, str(file_path))
        if active_file is not None:
            for index in range(self.file_combo.count()):
                if self.file_combo.itemData(index) == str(active_file):
                    self.file_combo.setCurrentIndex(index)
                    break
        form.addRow("Target file", self.file_combo)

        self.r_spin = QSpinBox(); self.r_spin.setRange(0, 255); self.r_spin.setValue(r)
        self.g_spin = QSpinBox(); self.g_spin.setRange(0, 255); self.g_spin.setValue(g)
        self.b_spin = QSpinBox(); self.b_spin.setRange(0, 255); self.b_spin.setValue(b)
        form.addRow("R", self.r_spin)
        form.addRow("G", self.g_spin)
        form.addRow("B", self.b_spin)

        self.pick_button = QPushButton("Pick Colour")
        self.pick_button.clicked.connect(self.pick_colour)
        layout.addWidget(self.pick_button)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def pick_colour(self):
        c = choose_colour_dialog(QColor(self.r_spin.value(), self.g_spin.value(), self.b_spin.value()), self, "Choose line colour")
        if c.isValid():
            self.r_spin.setValue(c.red())
            self.g_spin.setValue(c.green())
            self.b_spin.setValue(c.blue())

    def values(self):
        return {
            "file_path": Path(self.file_combo.currentData()) if self.file_combo.currentData() else None,
            "r": self.r_spin.value(),
            "g": self.g_spin.value(),
            "b": self.b_spin.value(),
        }


def snapshot_point(point: MapPointRecord) -> dict[str, Any]:
    return {
        "x": point.x,
        "y": point.y,
        "z": point.z,
        "r": point.r,
        "g": point.g,
        "b": point.b,
        "size": point.size,
        "label": point.label,
    }


def snapshot_line(line: MapLineRecord) -> dict[str, Any]:
    return {
        "x1": line.x1,
        "y1": line.y1,
        "z1": line.z1,
        "x2": line.x2,
        "y2": line.y2,
        "z2": line.z2,
        "r": line.r,
        "g": line.g,
        "b": line.b,
    }


class EqMapView(QGraphicsView):
    def __init__(self, main_window: "EqMapMainWindow") -> None:
        super().__init__(main_window)
        self.main_window = main_window
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setRubberBandSelectionMode(Qt.IntersectsItemShape)
        self._is_panning = False
        self._last_pan_point = QPointF()

    def wheelEvent(self, event):
        factor = 1.2 if event.angleDelta().y() > 0 else 1 / 1.2
        self.scale(factor, factor)

    def mousePressEvent(self, event):
        if event.button() in (Qt.MiddleButton, Qt.RightButton):
            self._is_panning = True
            self._last_pan_point = event.position()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.main_window.show_map_context_menu(event.globalPosition().toPoint(), self.mapToScene(event.position().toPoint()))
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event):
        if self._is_panning:
            delta = event.position() - self._last_pan_point
            self._last_pan_point = event.position()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - int(delta.x()))
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - int(delta.y()))
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() in (Qt.MiddleButton, Qt.RightButton) and self._is_panning:
            self._is_panning = False
            self.setCursor(Qt.ArrowCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)


class MovablePointMarker(QGraphicsEllipseItem):
    def __init__(self, main_window: "EqMapMainWindow", record: MapPointRecord):
        super().__init__()
        self.main_window = main_window
        self.record = record
        self._drag_before: Optional[dict[str, Any]] = None
        self.setData(0, record)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

    def mousePressEvent(self, event):
        if self.main_window.edit_mode() == "Move Points":
            self._drag_before = snapshot_point(self.record)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self._drag_before is not None:
            after = snapshot_point(self.record)
            if self._drag_before != after:
                self.main_window.add_undo("Move point", self.record, self._drag_before, after)
            self._drag_before = None
        super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged and self.scene() is not None:
            self.main_window.on_marker_dragged(self.record, self.pos())
        return super().itemChange(change, value)


class MovableLineItem(QGraphicsLineItem):
    def __init__(self, main_window: "EqMapMainWindow", record: MapLineRecord):
        super().__init__()
        self.main_window = main_window
        self.record = record
        self._drag_before: Optional[dict[str, Any]] = None
        self.setData(0, record)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

    def mousePressEvent(self, event):
        if self.main_window.edit_mode() == "Move Lines":
            self._drag_before = snapshot_line(self.record)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self._drag_before is not None:
            after = snapshot_line(self.record)
            if self._drag_before != after:
                self.main_window.add_undo("Move line", self.record, self._drag_before, after)
            self._drag_before = None
        super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged and self.scene() is not None:
            self.main_window.on_line_dragged(self.record, self.pos())
        return super().itemChange(change, value)


class EndpointHandle(QGraphicsEllipseItem):
    def __init__(self, main_window: "EqMapMainWindow", record: MapLineRecord, endpoint: int):
        super().__init__(-5, -5, 10, 10)
        self.main_window = main_window
        self.record = record
        self.endpoint = endpoint
        self._drag_before: Optional[dict[str, Any]] = None
        self.setBrush(QBrush(QColor(255, 255, 0)))
        self.setPen(QPen(QColor(0, 0, 0), 1))
        self.setZValue(100000)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

    def mousePressEvent(self, event):
        self._drag_before = snapshot_line(self.record)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self._drag_before is not None:
            after = snapshot_line(self.record)
            if self._drag_before != after:
                self.main_window.add_undo("Move line endpoint", self.record, self._drag_before, after)
            self._drag_before = None
        super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged and self.scene() is not None:
            self.main_window.on_endpoint_dragged(self.record, self.endpoint, self.pos())
        return super().itemChange(change, value)




def ensure_spinbox_arrow_images() -> tuple[str, str]:
    """Create tiny light-coloured arrow PNGs for dark-mode spin boxes.

    Qt stylesheet triangle borders can render as squares on some Windows/PyInstaller builds.
    Real image arrows are much more reliable.
    """
    up_path = RESOURCES_DIR / "spinbox_arrow_up_light.png"
    down_path = RESOURCES_DIR / "spinbox_arrow_down_light.png"

    if not up_path.exists() or not down_path.exists():
        up = QPixmap(9, 9)
        up.fill(Qt.transparent)
        painter = QPainter(up)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setBrush(QBrush(QColor(245, 245, 245)))
        painter.setPen(Qt.NoPen)
        painter.drawPolygon([
            QPointF(4.5, 1.5),
            QPointF(8.0, 6.5),
            QPointF(1.0, 6.5),
        ])
        painter.end()
        up.save(str(up_path), "PNG")

        down = QPixmap(9, 9)
        down.fill(Qt.transparent)
        painter = QPainter(down)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setBrush(QBrush(QColor(245, 245, 245)))
        painter.setPen(Qt.NoPen)
        painter.drawPolygon([
            QPointF(1.0, 2.5),
            QPointF(8.0, 2.5),
            QPointF(4.5, 7.5),
        ])
        painter.end()
        down.save(str(down_path), "PNG")

    # Qt stylesheets prefer forward slashes, even on Windows.
    return up_path.as_posix(), down_path.as_posix()


def choose_colour_dialog(initial: QColor, parent=None, title: str = "Choose colour") -> QColor:
    dialog = QColorDialog(initial, parent)
    dialog.setWindowTitle(title)
    dialog.setOption(QColorDialog.DontUseNativeDialog, True)
    dialog.setStyle(QApplication.style())

    up_arrow, down_arrow = ensure_spinbox_arrow_images()

    # Dark-mode colour dialog with explicit image arrows.
    # This keeps the dialog visually consistent with the app while avoiding the missing-arrow
    # behavior that can happen when Qt has to draw stylesheet-modified spinbox arrows itself.
    dialog.setStyleSheet(f"""
        QColorDialog, QWidget {{
            background-color: #242424;
            color: #f0f0f0;
        }}
        QLabel {{
            color: #f0f0f0;
        }}
        QLineEdit, QSpinBox, QDoubleSpinBox {{
            background-color: #1b1b1b;
            color: #f0f0f0;
            border: 1px solid #666;
            min-height: 22px;
            padding-right: 22px;
        }}
        QSpinBox::up-button, QDoubleSpinBox::up-button {{
            subcontrol-origin: border;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid #777;
            border-bottom: 1px solid #555;
            background-color: #3a3a3a;
        }}
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            subcontrol-origin: border;
            subcontrol-position: bottom right;
            width: 20px;
            border-left: 1px solid #777;
            border-top: 1px solid #555;
            background-color: #3a3a3a;
        }}
        QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
        QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
            background-color: #505050;
        }}
        QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
            image: url("{up_arrow}");
            width: 9px;
            height: 9px;
        }}
        QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
            image: url("{down_arrow}");
            width: 9px;
            height: 9px;
        }}
        QPushButton {{
            background-color: #333;
            color: #f0f0f0;
            border: 1px solid #777;
            padding: 4px 8px;
        }}
        QPushButton:hover {{
            background-color: #444;
        }}
    """)
    if dialog.exec() == QDialog.Accepted:
        return dialog.selectedColor()
    return QColor()


class ColorChoiceDialog(QDialog):
    def __init__(self, colours: list[tuple[tuple[int, int, int], int, int]], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Match Colour from Map")
        self.selected_rgb: Optional[tuple[int, int, int]] = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Choose a colour currently used on the map:"))

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        for rgb, point_count, line_count in colours:
            total = point_count + line_count
            item = QListWidgetItem(f"■ RGB {rgb}    Points: {point_count}    Lines: {line_count}    Total: {total}")
            item.setData(Qt.UserRole, rgb)
            item.setForeground(QColor(*rgb))
            self.list_widget.addItem(item)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self) -> None:
        item = self.list_widget.currentItem()
        if item is not None:
            self.selected_rgb = item.data(Qt.UserRole)
        super().accept()


class PreferencesDialog(QDialog):
    def __init__(self, main_window: "EqMapMainWindow") -> None:
        super().__init__(main_window)
        self.main_window = main_window
        self.setWindowTitle("Preferences")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        layout.addLayout(form)

        self.remember_last_checkbox = QCheckBox("Remember last loaded map")
        self.remember_last_checkbox.setChecked(main_window.remember_last_loaded_map)
        form.addRow(self.remember_last_checkbox)

        self.auto_fit_checkbox = QCheckBox("Auto-fit restored map on startup")
        self.auto_fit_checkbox.setChecked(main_window.auto_fit_restored_map)
        form.addRow(self.auto_fit_checkbox)

        self.autosave_settings_checkbox = QCheckBox("Autosave settings on exit")
        self.autosave_settings_checkbox.setChecked(main_window.autosave_settings_on_exit)
        form.addRow(self.autosave_settings_checkbox)

        self.show_warning_checkbox = QCheckBox("Show beta safety warning on startup")
        self.show_warning_checkbox.setChecked(main_window.show_beta_warning)
        form.addRow(self.show_warning_checkbox)

        self.flip_y_checkbox = QCheckBox("Flip display Y")
        self.flip_y_checkbox.setChecked(main_window.mapper.flip_display_y)
        form.addRow(self.flip_y_checkbox)

        self.default_background_combo = QComboBox()
        self.default_background_combo.addItems(["Remember Last", "Light", "Dark"])
        bg_value = main_window.default_background_mode
        if bg_value == "light":
            self.default_background_combo.setCurrentText("Light")
        elif bg_value == "dark":
            self.default_background_combo.setCurrentText("Dark")
        else:
            self.default_background_combo.setCurrentText("Remember Last")
        form.addRow("Default background", self.default_background_combo)

        folder_row = QHBoxLayout()
        self.map_folder_edit = QLineEdit(main_window.map_folder)
        self.map_folder_button = QPushButton("Choose...")
        self.map_folder_button.clicked.connect(self.choose_folder)
        folder_row.addWidget(self.map_folder_edit)
        folder_row.addWidget(self.map_folder_button)
        form.addRow("Default map folder", folder_row)

        self.max_highlights_spin = QSpinBox()
        self.max_highlights_spin.setRange(0, 1000000)
        self.max_highlights_spin.setValue(main_window.max_highlights_before_warning)
        self.max_highlights_spin.setToolTip("0 = never warn before highlighting")
        form.addRow("Warn before highlighting more than", self.max_highlights_spin)

        self.confirm_edit_over_spin = QSpinBox()
        self.confirm_edit_over_spin.setRange(0, 1000000)
        self.confirm_edit_over_spin.setValue(main_window.confirm_bulk_edit_over)
        form.addRow("Confirm bulk edits over", self.confirm_edit_over_spin)

        self.confirm_delete_over_spin = QSpinBox()
        self.confirm_delete_over_spin.setRange(0, 1000000)
        self.confirm_delete_over_spin.setValue(main_window.confirm_bulk_delete_over)
        form.addRow("Confirm deletes over", self.confirm_delete_over_spin)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def choose_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Choose Default Map Folder", self.map_folder_edit.text())
        if folder:
            self.map_folder_edit.setText(folder)

    def accept(self) -> None:
        bg_text = self.default_background_combo.currentText()
        bg_value = "remember"
        if bg_text == "Light":
            bg_value = "light"
        elif bg_text == "Dark":
            bg_value = "dark"

        self.main_window.remember_last_loaded_map = self.remember_last_checkbox.isChecked()
        self.main_window.auto_fit_restored_map = self.auto_fit_checkbox.isChecked()
        self.main_window.autosave_settings_on_exit = self.autosave_settings_checkbox.isChecked()
        self.main_window.show_beta_warning = self.show_warning_checkbox.isChecked()
        self.main_window.default_background_mode = bg_value
        self.main_window.map_folder = self.map_folder_edit.text().strip()
        self.main_window.max_highlights_before_warning = self.max_highlights_spin.value()
        self.main_window.confirm_bulk_edit_over = self.confirm_edit_over_spin.value()
        self.main_window.confirm_bulk_delete_over = self.confirm_delete_over_spin.value()

        self.main_window.mapper.flip_display_y = self.flip_y_checkbox.isChecked()
        if hasattr(self.main_window, "flip_y_action"):
            self.main_window.flip_y_action.setChecked(self.main_window.mapper.flip_display_y)
        self.main_window.render_map(keep_view=True)

        if self.main_window.default_background_mode == "light":
            self.main_window.set_background("light")
        elif self.main_window.default_background_mode == "dark":
            self.main_window.set_background("dark")

        if self.main_window.map_folder and hasattr(self.main_window, "side_panel"):
            self.main_window.side_panel.map_folder_edit.setText(self.main_window.map_folder)
            self.main_window.rebuild_zone_list()

        self.main_window.save_settings()
        super().accept()


class SidePanel(QWidget):
    def __init__(self, main_window: "EqMapMainWindow") -> None:
        super().__init__(main_window)
        self.main_window = main_window
        self.current_record: Optional[Any] = None
        self._loading = False
        self.layer_checkboxes: dict[Path, QCheckBox] = {}
        self._build_ui()
        self.set_record(None)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        controls_group = QGroupBox("Map Controls")
        controls_layout = QVBoxLayout(controls_group)

        controls_layout.addWidget(QLabel("Edit Mode"))
        self.edit_mode_combo = QComboBox()
        self.edit_mode_combo.addItems([
            "Select Only",
            "Move Points",
            "Move Lines",
            "Move Line Endpoints",
        ])
        controls_layout.addWidget(self.edit_mode_combo)

        controls_layout.addWidget(QLabel("Active File for New Records"))
        self.active_file_combo = QComboBox()
        controls_layout.addWidget(self.active_file_combo)

        undo_row = QHBoxLayout()
        self.undo_button = QPushButton("Undo")
        self.redo_button = QPushButton("Redo")
        undo_row.addWidget(self.undo_button)
        undo_row.addWidget(self.redo_button)
        controls_layout.addLayout(undo_row)

        restore_row = QHBoxLayout()
        self.reload_button = QPushButton("Reload from Disk")
        self.restore_button = QPushButton("Restore Backup")
        restore_row.addWidget(self.reload_button)
        restore_row.addWidget(self.restore_button)
        controls_layout.addLayout(restore_row)

        layout.addWidget(controls_group)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        selection_tab = QWidget()
        selection_layout = QVBoxLayout(selection_tab)

        self.title_label = QLabel("No selection")
        self.title_label.setStyleSheet("font-weight: bold;")
        selection_layout.addWidget(self.title_label)

        self.source_label = QLabel("")
        self.source_label.setWordWrap(True)
        selection_layout.addWidget(self.source_label)

        form = QFormLayout()
        selection_layout.addLayout(form)

        self.label_edit = QLineEdit()
        form.addRow("Label", self.label_edit)

        self.point_coords_label = QLabel("Point Coordinates")
        self.point_coords_label.setStyleSheet("font-weight: bold; margin-top: 8px;")
        form.addRow(self.point_coords_label)

        self.x_spin = self.coord_spin()
        self.y_spin = self.coord_spin()
        self.z_spin = self.coord_spin()
        form.addRow("X", self.x_spin)
        form.addRow("Y", self.y_spin)
        form.addRow("Z", self.z_spin)

        self.endpoint1_label = QLabel("Line Endpoint 1 Coordinates")
        self.endpoint1_label.setStyleSheet("font-weight: bold; margin-top: 8px;")
        form.addRow(self.endpoint1_label)

        self.x1_spin = self.coord_spin()
        self.y1_spin = self.coord_spin()
        self.z1_spin = self.coord_spin()
        form.addRow("X1", self.x1_spin)
        form.addRow("Y1", self.y1_spin)
        form.addRow("Z1", self.z1_spin)

        self.endpoint2_label = QLabel("Line Endpoint 2 Coordinates")
        self.endpoint2_label.setStyleSheet("font-weight: bold; margin-top: 8px;")
        form.addRow(self.endpoint2_label)

        self.x2_spin = self.coord_spin()
        self.y2_spin = self.coord_spin()
        self.z2_spin = self.coord_spin()
        form.addRow("X2", self.x2_spin)
        form.addRow("Y2", self.y2_spin)
        form.addRow("Z2", self.z2_spin)

        self.color_label = QLabel("Color")
        self.color_label.setStyleSheet("font-weight: bold; margin-top: 8px;")
        form.addRow(self.color_label)

        self.r_spin = self.rgb_spin()
        self.g_spin = self.rgb_spin()
        self.b_spin = self.rgb_spin()
        form.addRow("R", self.r_spin)
        form.addRow("G", self.g_spin)
        form.addRow("B", self.b_spin)

        self.size_spin = QDoubleSpinBox()
        self.size_spin.setRange(0.1, 99.0)
        self.size_spin.setSingleStep(0.5)
        self.size_spin.setDecimals(2)
        form.addRow("Point Size", self.size_spin)

        color_row = QHBoxLayout()
        self.color_preview = QLabel("      ")
        self.color_preview.setMinimumWidth(60)
        self.pick_color_btn = QPushButton("Pick Colour")
        color_row.addWidget(self.color_preview)
        color_row.addWidget(self.pick_color_btn)
        selection_layout.addLayout(color_row)

        self.apply_button = QPushButton("Apply Changes")
        selection_layout.addWidget(self.apply_button)

        self.raw_label = QLabel("")
        self.raw_label.setWordWrap(True)
        self.raw_label.setStyleSheet("font-size: 10px;")
        selection_layout.addWidget(self.raw_label)

        self.multi_select_label = QLabel("Multi-select: none")
        self.multi_select_label.setWordWrap(True)
        self.multi_select_label.setStyleSheet("font-weight: bold; margin-top: 8px;")
        selection_layout.addWidget(self.multi_select_label)

        self.delete_selected_button = QPushButton("Delete Selected Points/Lines")
        self.delete_selected_button.setEnabled(False)
        selection_layout.addWidget(self.delete_selected_button)

        selection_layout.addStretch(1)
        self.tabs.addTab(selection_tab, "Selected Item")

        layers_tab = QWidget()
        self.layers_layout = QVBoxLayout(layers_tab)
        self.layers_hint = QLabel("Open files to show layer toggles.")
        self.layers_hint.setWordWrap(True)
        self.layers_layout.addWidget(self.layers_hint)
        self.tabs.addTab(layers_tab, "Layers")

        bulk_tab = QWidget()
        bulk_layout = QVBoxLayout(bulk_tab)
        bulk_layout.addWidget(QLabel("Colours used by visible map records"))

        self.point_colour_list = QListWidget()
        self.point_colour_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.line_colour_list = QListWidget()
        self.line_colour_list.setSelectionMode(QListWidget.ExtendedSelection)

        bulk_layout.addWidget(QLabel("Point Colours"))
        bulk_layout.addWidget(self.point_colour_list)
        bulk_layout.addWidget(QLabel("Line Colours"))
        bulk_layout.addWidget(self.line_colour_list)

        recolour_group = QGroupBox("Change Selected Matching Colour")
        recolour_layout = QFormLayout(recolour_group)
        self.bulk_old_rgb_label = QLabel("No colour selected")
        recolour_layout.addRow("Selected colour", self.bulk_old_rgb_label)
        self.bulk_new_r = self.rgb_spin()
        self.bulk_new_g = self.rgb_spin()
        self.bulk_new_b = self.rgb_spin()
        recolour_layout.addRow("New R", self.bulk_new_r)
        recolour_layout.addRow("New G", self.bulk_new_g)
        recolour_layout.addRow("New B", self.bulk_new_b)
        self.bulk_pick_colour_button = QPushButton("Pick New Colour")
        self.bulk_match_colour_button = QPushButton("Match Colour from Other Point/Line")
        self.bulk_apply_colour_button = QPushButton("Apply to Selected Matching Records")
        recolour_layout.addRow(self.bulk_pick_colour_button)
        recolour_layout.addRow(self.bulk_match_colour_button)
        recolour_layout.addRow(self.bulk_apply_colour_button)
        bulk_layout.addWidget(recolour_group)
        self.tabs.addTab(bulk_tab, "Bulk Colours")

        points_tab = QWidget()
        points_layout = QVBoxLayout(points_tab)
        self.point_search_edit = QLineEdit()
        self.point_search_edit.setPlaceholderText("Search point labels...")
        points_layout.addWidget(self.point_search_edit)

        point_search_buttons = QHBoxLayout()
        self.point_search_button = QPushButton("Search")
        self.point_select_matches_button = QPushButton("Select All Matching")
        self.point_reset_search_button = QPushButton("Reset Search")
        point_search_buttons.addWidget(self.point_search_button)
        point_search_buttons.addWidget(self.point_select_matches_button)
        point_search_buttons.addWidget(self.point_reset_search_button)
        points_layout.addLayout(point_search_buttons)

        self.points_list = QListWidget()
        points_layout.addWidget(self.points_list)

        point_bulk_group = QGroupBox("Bulk Edit Checked / Matching Points")
        point_bulk_layout = QFormLayout(point_bulk_group)
        self.point_bulk_r = self.rgb_spin()
        self.point_bulk_g = self.rgb_spin()
        self.point_bulk_b = self.rgb_spin()
        point_bulk_layout.addRow("New R", self.point_bulk_r)
        point_bulk_layout.addRow("New G", self.point_bulk_g)
        point_bulk_layout.addRow("New B", self.point_bulk_b)
        self.point_bulk_pick_colour_button = QPushButton("Pick New Colour")
        self.point_bulk_apply_colour_button = QPushButton("Change Colour of Checked Points")
        self.point_bulk_delete_button = QPushButton("Delete Checked Points")
        point_bulk_layout.addRow(self.point_bulk_pick_colour_button)
        point_bulk_layout.addRow(self.point_bulk_apply_colour_button)
        point_bulk_layout.addRow(self.point_bulk_delete_button)
        points_layout.addWidget(point_bulk_group)
        self.tabs.addTab(points_tab, "Points")

        zones_tab = QWidget()
        zones_layout = QVBoxLayout(zones_tab)

        folder_row = QHBoxLayout()
        self.map_folder_edit = QLineEdit()
        self.map_folder_edit.setPlaceholderText("Choose your EQ maps folder...")
        self.choose_map_folder_button = QPushButton("Choose Map Folder")
        folder_row.addWidget(self.map_folder_edit)
        folder_row.addWidget(self.choose_map_folder_button)
        zones_layout.addLayout(folder_row)

        zone_search_row = QHBoxLayout()
        self.zone_search_edit = QLineEdit()
        self.zone_search_edit.setPlaceholderText("Search zones by full name or shortname...")
        self.zone_search_button = QPushButton("Search")
        self.zone_reset_button = QPushButton("Reset")
        zone_search_row.addWidget(self.zone_search_edit)
        zone_search_row.addWidget(self.zone_search_button)
        zone_search_row.addWidget(self.zone_reset_button)
        zones_layout.addLayout(zone_search_row)

        self.zones_list = QListWidget()
        zones_layout.addWidget(self.zones_list)
        self.open_selected_zone_button = QPushButton("Open Selected Zone")
        zones_layout.addWidget(self.open_selected_zone_button)
        self.tabs.addTab(zones_tab, "Zones")

        pending_tab = QWidget()
        pending_layout = QVBoxLayout(pending_tab)
        pending_layout.addWidget(QLabel("Unsaved changes"))
        self.pending_changes_list = QListWidget()
        pending_layout.addWidget(self.pending_changes_list)
        pending_buttons = QHBoxLayout()
        self.pending_refresh_button = QPushButton("Refresh")
        self.pending_revert_all_button = QPushButton("Revert All Unsaved")
        self.pending_save_button = QPushButton("Save Edits")
        pending_buttons.addWidget(self.pending_refresh_button)
        pending_buttons.addWidget(self.pending_revert_all_button)
        pending_buttons.addWidget(self.pending_save_button)
        pending_layout.addLayout(pending_buttons)
        self.tabs.addTab(pending_tab, "Pending Changes")


        layout.addStretch(1)

        self.edit_mode_combo.currentTextChanged.connect(self.main_window.on_edit_mode_changed)
        self.undo_button.clicked.connect(self.main_window.undo)
        self.redo_button.clicked.connect(self.main_window.redo)
        self.reload_button.clicked.connect(self.main_window.reload_from_disk)
        self.restore_button.clicked.connect(self.main_window.restore_from_backup)
        self.pick_color_btn.clicked.connect(self.pick_color)
        self.apply_button.clicked.connect(self.apply_changes)
        self.delete_selected_button.clicked.connect(self.main_window.delete_selected_records)
        self.point_colour_list.itemSelectionChanged.connect(lambda: self.on_colour_selection_changed("points"))
        self.line_colour_list.itemSelectionChanged.connect(lambda: self.on_colour_selection_changed("lines"))
        self.bulk_pick_colour_button.clicked.connect(self.pick_bulk_colour)
        self.bulk_match_colour_button.clicked.connect(self.match_bulk_colour_from_list)
        self.bulk_apply_colour_button.clicked.connect(self.main_window.apply_bulk_colour_to_selected_matching)
        self.point_search_button.clicked.connect(self.rebuild_points_list)
        self.point_search_edit.returnPressed.connect(self.rebuild_points_list)
        self.point_select_matches_button.clicked.connect(self.check_matching_points)
        self.point_reset_search_button.clicked.connect(self.reset_point_search)
        self.point_bulk_pick_colour_button.clicked.connect(self.pick_point_bulk_colour)
        self.point_bulk_apply_colour_button.clicked.connect(self.main_window.bulk_recolour_checked_points)
        self.point_bulk_delete_button.clicked.connect(self.main_window.bulk_delete_checked_points)
        self.choose_map_folder_button.clicked.connect(self.main_window.choose_map_folder)
        self.zone_search_button.clicked.connect(self.main_window.rebuild_zone_list)
        self.zone_search_edit.returnPressed.connect(self.main_window.rebuild_zone_list)
        self.zone_reset_button.clicked.connect(self.main_window.reset_zone_search)
        self.open_selected_zone_button.clicked.connect(self.main_window.open_selected_zone)
        self.zones_list.itemDoubleClicked.connect(lambda item: self.main_window.open_selected_zone())
        self.pending_refresh_button.clicked.connect(self.rebuild_pending_changes)
        self.pending_revert_all_button.clicked.connect(self.main_window.reload_from_disk)
        self.pending_save_button.clicked.connect(self.main_window.save_edits)

    def coord_spin(self) -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setRange(-100000.0, 100000.0)
        spin.setDecimals(4)
        spin.setSingleStep(1.0)
        spin.setButtonSymbols(QAbstractSpinBox.UpDownArrows)
        spin.setMinimumHeight(24)
        return spin

    def rgb_spin(self) -> QSpinBox:
        spin = QSpinBox()
        spin.setRange(0, 255)
        spin.setButtonSymbols(QAbstractSpinBox.UpDownArrows)
        spin.setMinimumHeight(24)
        spin.setMinimumWidth(78)
        return spin

    def all_controls(self):
        return [
            self.label_edit,
            self.x_spin, self.y_spin, self.z_spin,
            self.x1_spin, self.y1_spin, self.z1_spin,
            self.x2_spin, self.y2_spin, self.z2_spin,
            self.r_spin, self.g_spin, self.b_spin,
            self.size_spin,
            self.pick_color_btn,
            self.apply_button,
        ]

    def edit_mode(self) -> str:
        return self.edit_mode_combo.currentText()

    def set_record(self, record: Optional[Any]) -> None:
        self._loading = True
        self.current_record = record

        for widget in self.all_controls():
            widget.setEnabled(record is not None)

        is_point = isinstance(record, MapPointRecord)
        is_line = isinstance(record, MapLineRecord)

        self.label_edit.setEnabled(is_point)
        self.size_spin.setEnabled(is_point)
        for widget in [self.x_spin, self.y_spin, self.z_spin]:
            widget.setEnabled(is_point)
        for widget in [self.x1_spin, self.y1_spin, self.z1_spin, self.x2_spin, self.y2_spin, self.z2_spin]:
            widget.setEnabled(is_line)

        if record is None:
            self.title_label.setText("No selection")
            self.source_label.setText("")
            self.label_edit.setText("")
            self.raw_label.setText("")
        elif is_point:
            self.title_label.setText("Selected Point / Label")
            self.source_label.setText(f"{record.file_path.name}:{record.line_index + 1 if record.line_index >= 0 else 'new'}")
            self.label_edit.setText(record.label)
            self.x_spin.setValue(record.x)
            self.y_spin.setValue(record.y)
            self.z_spin.setValue(record.z)
            self.r_spin.setValue(record.r)
            self.g_spin.setValue(record.g)
            self.b_spin.setValue(record.b)
            self.size_spin.setValue(record.size)
            self.raw_label.setText(record.to_map_line())
        elif is_line:
            self.title_label.setText("Selected Line")
            self.source_label.setText(f"{record.file_path.name}:{record.line_index + 1 if record.line_index >= 0 else 'new'}")
            self.label_edit.setText("")
            self.x1_spin.setValue(record.x1)
            self.y1_spin.setValue(record.y1)
            self.z1_spin.setValue(record.z1)
            self.x2_spin.setValue(record.x2)
            self.y2_spin.setValue(record.y2)
            self.z2_spin.setValue(record.z2)
            self.r_spin.setValue(record.r)
            self.g_spin.setValue(record.g)
            self.b_spin.setValue(record.b)
            self.raw_label.setText(record.to_map_line())

        if record is None:
            # Do not clear a multi-select message when show_multi_selection() intentionally sets one afterwards.
            if self.title_label.text() != "Multiple Items Selected":
                self.set_multi_selection_summary(0, 0)
        else:
            is_point_summary = 1 if isinstance(record, MapPointRecord) else 0
            is_line_summary = 1 if isinstance(record, MapLineRecord) else 0
            self.set_multi_selection_summary(is_point_summary, is_line_summary)

        self.update_color_preview()
        self._loading = False

    def update_color_preview(self) -> None:
        color = QColor(self.r_spin.value(), self.g_spin.value(), self.b_spin.value())
        self.color_preview.setStyleSheet(
            f"background-color: rgb({color.red()}, {color.green()}, {color.blue()}); border: 1px solid #888;"
        )

    def pick_color(self) -> None:
        start = QColor(self.r_spin.value(), self.g_spin.value(), self.b_spin.value())
        color = choose_colour_dialog(start, self, "Choose colour")
        if not color.isValid():
            return
        self.r_spin.setValue(color.red())
        self.g_spin.setValue(color.green())
        self.b_spin.setValue(color.blue())
        self.update_color_preview()

    def apply_changes(self) -> None:
        record = self.current_record
        if record is None:
            if self.title_label.text() == "Multiple Items Selected":
                self.main_window.recolour_selected_records_from_panel()
            return

        if isinstance(record, MapPointRecord):
            before = snapshot_point(record)
            record.label = self.label_edit.text().strip()
            record.x = self.x_spin.value()
            record.y = self.y_spin.value()
            record.z = self.z_spin.value()
            record.r = self.r_spin.value()
            record.g = self.g_spin.value()
            record.b = self.b_spin.value()
            record.size = self.size_spin.value()
            after = snapshot_point(record)

            if before != after:
                if before["label"] != after["label"]:
                    action = "Edit point label"
                elif (before["r"], before["g"], before["b"]) != (after["r"], after["g"], after["b"]):
                    action = "Edit point colour"
                else:
                    action = "Edit point"
                self.main_window.add_undo(action, record, before, after)
                record.dirty = True
                self.main_window.update_record_items(record)

        elif isinstance(record, MapLineRecord):
            before = snapshot_line(record)
            record.x1 = self.x1_spin.value()
            record.y1 = self.y1_spin.value()
            record.z1 = self.z1_spin.value()
            record.x2 = self.x2_spin.value()
            record.y2 = self.y2_spin.value()
            record.z2 = self.z2_spin.value()
            record.r = self.r_spin.value()
            record.g = self.g_spin.value()
            record.b = self.b_spin.value()
            after = snapshot_line(record)

            if before != after:
                if (before["r"], before["g"], before["b"]) != (after["r"], after["g"], after["b"]):
                    action = "Edit line colour"
                else:
                    action = "Edit line"
                self.main_window.add_undo(action, record, before, after)
                record.dirty = True
                self.main_window.update_record_items(record)

        self.set_record(record)
        self.main_window.update_dirty_indicator()

    def rebuild_layers(self) -> None:
        while self.layers_layout.count():
            item = self.layers_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.layer_checkboxes.clear()
        self.active_file_combo.blockSignals(True)
        self.active_file_combo.clear()

        if not self.main_window.loaded_files:
            self.layers_layout.addWidget(QLabel("Open files to show layer toggles."))
            self.active_file_combo.blockSignals(False)
            return

        for file_path in self.main_window.loaded_files:
            line_count = sum(1 for r in self.main_window.loaded_map.lines if r.file_path == file_path)
            point_count = sum(1 for r in self.main_window.loaded_map.points if r.file_path == file_path)
            cb = QCheckBox(f"{file_path.name}  ({line_count} L, {point_count} P)")
            cb.setChecked(self.main_window.layer_visible.get(file_path, True))
            cb.toggled.connect(lambda checked, fp=file_path: self.main_window.set_layer_visible(fp, checked))
            self.layers_layout.addWidget(cb)
            self.layer_checkboxes[file_path] = cb
            self.active_file_combo.addItem(file_path.name, str(file_path))

        self.layers_layout.addStretch(1)
        self.active_file_combo.blockSignals(False)
        self.rebuild_colour_list()
        self.rebuild_points_list()



    def rebuild_pending_changes(self) -> None:
        if not hasattr(self, "pending_changes_list"):
            return
        self.pending_changes_list.clear()
        for record in self.main_window.dirty_records():
            if isinstance(record, MapPointRecord):
                record_type = "Point"
                label = record.label
                colour = f"RGB ({record.r}, {record.g}, {record.b})"
            else:
                record_type = "Line"
                label = ""
                colour = f"RGB ({record.r}, {record.g}, {record.b})"
            action = "Deleted" if getattr(record, "deleted", False) else ("Added" if record.line_index < 0 else "Edited")
            line_num = "new" if record.line_index < 0 else str(record.line_index + 1)
            item = QListWidgetItem(f"{action:7} {record_type:5} {record.file_path.name}:{line_num} {colour} {label}")
            item.setData(Qt.UserRole, id(record))
            self.pending_changes_list.addItem(item)

    def set_multi_selection_summary(self, point_count: int, line_count: int) -> None:
        total = point_count + line_count
        if total <= 0:
            self.multi_select_label.setText("Multi-select: none")
            self.delete_selected_button.setEnabled(False)
        elif total == 1:
            self.multi_select_label.setText(f"Selected: {point_count} point(s), {line_count} line(s)")
            self.delete_selected_button.setEnabled(True)
        else:
            self.multi_select_label.setText(f"Multi-select: {total} item(s) — {point_count} point(s), {line_count} line(s)")
            self.delete_selected_button.setEnabled(True)

    def show_multi_selection(self, point_count: int, line_count: int) -> None:
        self.set_record(None)
        self.title_label.setText("Multiple Items Selected")
        self.source_label.setText(f"{point_count} point(s), {line_count} line(s)")
        self.raw_label.setText(
            "Coordinate fields are disabled for multi-select. "
            "Set RGB and click Apply Changes to recolour all selected records, "
            "or use Delete Selected Points/Lines to mark them for deletion."
        )

        # Coordinates, label, and point size stay greyed out for mixed selections.
        for widget in [
            self.label_edit,
            self.x_spin, self.y_spin, self.z_spin,
            self.x1_spin, self.y1_spin, self.z1_spin,
            self.x2_spin, self.y2_spin, self.z2_spin,
            self.size_spin,
        ]:
            widget.setEnabled(False)

        # Colour editing remains available for multi-select.
        for widget in [self.r_spin, self.g_spin, self.b_spin, self.pick_color_btn, self.apply_button]:
            widget.setEnabled(True)

        selected_records = self.main_window.selected_map_records()
        if selected_records:
            first = selected_records[0]
            if hasattr(first, "r"):
                self.r_spin.setValue(first.r)
                self.g_spin.setValue(first.g)
                self.b_spin.setValue(first.b)
                colours = {(record.r, record.g, record.b) for record in selected_records if hasattr(record, "r")}
                if len(colours) == 1:
                    self.raw_label.setText(self.raw_label.text() + f"\nCurrent selection colour: {next(iter(colours))}")
                else:
                    self.raw_label.setText(self.raw_label.text() + f"\nMixed colours selected. RGB fields start from the first selected record: {(first.r, first.g, first.b)}")
                self.update_color_preview()

        self.set_multi_selection_summary(point_count, line_count)

    def on_colour_selection_changed(self, record_type: str) -> None:
        colours = self.main_window.selected_colours_from_bulk_tab(record_type)
        if colours:
            self.bulk_old_rgb_label.setText(f"{record_type}: {', '.join(str(c) for c in colours)}")
            self.main_window.current_bulk_colour_type = record_type
            self.main_window.select_records_by_colour(record_type)

    def colour_icon(self, rgb: tuple[int, int, int]) -> QPixmap:
        pixmap = QPixmap(18, 18)
        pixmap.fill(QColor(*rgb))
        return pixmap

    def list_text_colour(self) -> QColor:
        return QColor(245, 245, 245) if getattr(self.main_window, "dark_ui", False) else QColor(0, 0, 0)

    def pick_bulk_colour(self) -> None:
        c = choose_colour_dialog(QColor(self.bulk_new_r.value(), self.bulk_new_g.value(), self.bulk_new_b.value()), self, "Choose new colour")
        if c.isValid():
            self.bulk_new_r.setValue(c.red())
            self.bulk_new_g.setValue(c.green())
            self.bulk_new_b.setValue(c.blue())

    def match_bulk_colour_from_list(self) -> None:
        colours = self.main_window.all_colour_counts()
        dialog = ColorChoiceDialog(colours, self)
        if dialog.exec() == QDialog.Accepted and dialog.selected_rgb is not None:
            r, g, b = dialog.selected_rgb
            self.bulk_new_r.setValue(r)
            self.bulk_new_g.setValue(g)
            self.bulk_new_b.setValue(b)

    def pick_point_bulk_colour(self) -> None:
        c = choose_colour_dialog(QColor(self.point_bulk_r.value(), self.point_bulk_g.value(), self.point_bulk_b.value()), self, "Choose new point colour")
        if c.isValid():
            self.point_bulk_r.setValue(c.red())
            self.point_bulk_g.setValue(c.green())
            self.point_bulk_b.setValue(c.blue())

    def rebuild_colour_list(self) -> None:
        self.point_colour_list.clear()
        self.line_colour_list.clear()

        point_counts: dict[tuple[int, int, int], int] = {}
        line_counts: dict[tuple[int, int, int], int] = {}

        for point in self.main_window.loaded_map.points:
            if getattr(point, "deleted", False) or not self.main_window.layer_visible.get(point.file_path, True):
                continue
            rgb = (point.r, point.g, point.b)
            point_counts[rgb] = point_counts.get(rgb, 0) + 1

        for line in self.main_window.loaded_map.lines:
            if getattr(line, "deleted", False) or not self.main_window.layer_visible.get(line.file_path, True):
                continue
            rgb = (line.r, line.g, line.b)
            line_counts[rgb] = line_counts.get(rgb, 0) + 1

        for rgb, count in sorted(point_counts.items(), key=lambda item: item[1], reverse=True):
            item = QListWidgetItem(f"RGB {rgb}    Points: {count}")
            item.setIcon(self.colour_icon(rgb))
            item.setData(Qt.UserRole, rgb)
            item.setForeground(self.list_text_colour())
            self.point_colour_list.addItem(item)

        for rgb, count in sorted(line_counts.items(), key=lambda item: item[1], reverse=True):
            item = QListWidgetItem(f"RGB {rgb}    Lines: {count}")
            item.setIcon(self.colour_icon(rgb))
            item.setData(Qt.UserRole, rgb)
            item.setForeground(self.list_text_colour())
            self.line_colour_list.addItem(item)

    def reset_point_search(self) -> None:
        self.point_search_edit.clear()
        self.rebuild_points_list()

    def rebuild_points_list(self) -> None:
        search = self.point_search_edit.text().strip().lower()
        self.points_list.clear()
        for point in self.main_window.loaded_map.points:
            if getattr(point, "deleted", False) or not self.main_window.layer_visible.get(point.file_path, True):
                continue
            if search and search not in point.label.lower():
                continue
            item = QListWidgetItem(f"{point.label}    RGB ({point.r}, {point.g}, {point.b})    {point.file_path.name}:{point.line_index + 1 if point.line_index >= 0 else 'new'}")
            item.setData(Qt.UserRole, id(point))
            item.setIcon(self.colour_icon((point.r, point.g, point.b)))
            item.setForeground(self.list_text_colour())
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.points_list.addItem(item)

    def check_matching_points(self) -> None:
        self.rebuild_points_list()
        for index in range(self.points_list.count()):
            self.points_list.item(index).setCheckState(Qt.Checked)

    def checked_point_records(self) -> list[MapPointRecord]:
        ids = set()
        for index in range(self.points_list.count()):
            item = self.points_list.item(index)
            if item.checkState() == Qt.Checked:
                ids.add(item.data(Qt.UserRole))
        return [point for point in self.main_window.loaded_map.points if id(point) in ids and not getattr(point, "deleted", False)]

class EqMapMainWindow(QMainWindow):
    def __init__(self, initial_files: Optional[list[Path]] = None) -> None:
        super().__init__()
        self.setWindowTitle(f"EQ Map Editor {VERSION}")
        self.mapper = CoordinateMapper(flip_display_y=False)

        self.scene = QGraphicsScene(self)
        self.view = EqMapView(self)
        self.view.setScene(self.scene)

        self.loaded_files: list[Path] = []
        self.loaded_map = LoadedMap(lines=[], points=[])
        self.layer_visible: dict[Path, bool] = {}

        self.line_items_by_record: dict[int, MovableLineItem] = {}
        self.point_items_by_record: dict[int, MovablePointMarker] = {}
        self.label_items_by_record: dict[int, QGraphicsTextItem] = {}
        self.endpoint_handles: list[EndpointHandle] = []
        self.selection_highlights: list[QGraphicsItem] = []
        self.bulk_selected_records: list[Any] = []
        self.search_matches: list[MapPointRecord] = []
        self.search_index: int = -1

        self.show_labels = True
        self.show_points = True
        self.dark_ui = False
        self.current_bulk_colour_type = "points"
        self.map_folder = ""
        self.remember_last_loaded_map = True
        self.auto_fit_restored_map = True
        self.autosave_settings_on_exit = True
        self.show_beta_warning = True
        self.default_background_mode = "remember"
        self.max_highlights_before_warning = 5000
        self.confirm_bulk_edit_over = 1
        self.confirm_bulk_delete_over = 1
        self.confirm_bulk_actions = True
        self._fit_last_map_after_show = False
        self._drag_update_lock = False
        self.pending_line_start: Optional[QPointF] = None

        self.undo_stack: list[UndoCommand] = []
        self.redo_stack: list[UndoCommand] = []

        self.side_panel = SidePanel(self)

        self._build_ui()

        if initial_files:
            self.load_files(initial_files)
        else:
            self.load_last_session()

    def _build_ui(self) -> None:
        toolbar = QToolBar("Main Toolbar", self)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        file_menu = QMenu("File", self)
        file_menu.setMinimumWidth(190)

        file_button = QToolButton(self)
        file_button.setText("File")
        file_button.setMenu(file_menu)
        file_button.setPopupMode(QToolButton.InstantPopup)
        toolbar.addWidget(file_button)

        open_action = QAction("Open Map File(s)", self)
        open_action.triggered.connect(self.open_files_dialog)
        file_menu.addAction(open_action)

        save_action = QAction("Save Edits", self)
        save_action.triggered.connect(self.save_edits)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save As...", self)
        save_as_action.triggered.connect(self.save_as_folder)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        revert_action = QAction("Revert Unsaved", self)
        revert_action.triggered.connect(self.reload_from_disk)
        file_menu.addAction(revert_action)

        restore_backup_action = QAction("Restore Backup...", self)
        restore_backup_action.triggered.connect(self.restore_from_backup)
        file_menu.addAction(restore_backup_action)

        open_backup_action = QAction("Open Backup Folder", self)
        open_backup_action.triggered.connect(self.open_backup_folder)
        file_menu.addAction(open_backup_action)

        file_menu.addSeparator()

        preferences_action = QAction("Preferences", self)
        preferences_action.triggered.connect(self.open_preferences)
        file_menu.addAction(preferences_action)

        help_action = QAction("Controls", self)
        help_action.triggered.connect(self.show_controls)
        file_menu.addAction(help_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.confirm_exit)
        file_menu.addAction(exit_action)

        toolbar.addSeparator()

        fit_action = QAction("Fit Map", self)
        fit_action.triggered.connect(self.fit_map)
        toolbar.addAction(fit_action)

        fit_selected_action = QAction("Fit Selected", self)
        fit_selected_action.triggered.connect(self.fit_selected)
        toolbar.addAction(fit_selected_action)

        clear_selection_action = QAction("Clear Selection", self)
        clear_selection_action.triggered.connect(self.clear_selection_and_highlights)
        toolbar.addAction(clear_selection_action)

        self.toggle_labels_action = QAction("Show Labels", self)
        self.toggle_labels_action.setCheckable(True)
        self.toggle_labels_action.setChecked(True)
        self.toggle_labels_action.triggered.connect(self.toggle_labels)
        toolbar.addAction(self.toggle_labels_action)

        self.toggle_points_action = QAction("Show Points", self)
        self.toggle_points_action.setCheckable(True)
        self.toggle_points_action.setChecked(True)
        self.toggle_points_action.triggered.connect(self.toggle_points)
        toolbar.addAction(self.toggle_points_action)

        self.background_action_group = QActionGroup(self)
        self.background_action_group.setExclusive(True)

        self.light_bg_action = QAction("Light Background", self)
        self.light_bg_action.setCheckable(True)
        self.light_bg_action.setChecked(True)
        self.light_bg_action.triggered.connect(lambda: self.set_background("light"))
        self.background_action_group.addAction(self.light_bg_action)
        toolbar.addAction(self.light_bg_action)

        self.dark_bg_action = QAction("Dark Background", self)
        self.dark_bg_action.setCheckable(True)
        self.dark_bg_action.triggered.connect(lambda: self.set_background("dark"))
        self.background_action_group.addAction(self.dark_bg_action)
        toolbar.addAction(self.dark_bg_action)

        toggle_sidebar_action = QAction("Toggle Sidebar", self)
        toggle_sidebar_action.triggered.connect(self.toggle_sidebar)
        toolbar.addAction(toggle_sidebar_action)

        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Search Labels:"))
        self.global_search_edit = QLineEdit()
        self.global_search_edit.setPlaceholderText("Point label text...")
        self.global_search_edit.setMaximumWidth(220)
        self.global_search_edit.returnPressed.connect(self.search_select_first_label_match)
        toolbar.addWidget(self.global_search_edit)

        search_first_action = QAction("Find First", self)
        search_first_action.triggered.connect(self.search_select_first_label_match)
        toolbar.addAction(search_first_action)

        search_all_action = QAction("Select Matches", self)
        search_all_action.triggered.connect(self.search_select_all_label_matches)
        toolbar.addAction(search_all_action)

        center_selected_action = QAction("Center Selected", self)
        center_selected_action.triggered.connect(self.center_selected)
        toolbar.addAction(center_selected_action)

        self.setup_shortcuts(
            open_action,
            save_action,
            self.undo,
            self.redo,
            self.fit_map,
            self.clear_selection_and_highlights,
            self.delete_selected_records,
            self.select_all_visible_records,
            self.global_search_edit,
        )

        self.splitter = QSplitter(Qt.Horizontal, self)
        self.splitter.addWidget(self.view)
        self.splitter.addWidget(self.side_panel)
        self.splitter.setStretchFactor(0, 5)
        self.splitter.setStretchFactor(1, 1)
        self.setCentralWidget(self.splitter)

        self.status_label = QLabel("Open one or more EQ map text files.")
        self.dirty_label = QLabel("Clean")
        status = QStatusBar(self)
        status.addWidget(self.status_label)
        status.addPermanentWidget(self.dirty_label)
        self.setStatusBar(status)

        self.set_background("light")

    def edit_mode(self) -> str:
        return self.side_panel.edit_mode()

    def show_controls(self) -> None:
        QMessageBox.information(
            self,
            "Controls",
            (
                f"EQ Map Editor {VERSION} controls:\n\n"
                "- Mouse wheel: zoom in/out\n"
                "- Middle/right mouse drag: pan\n"
                "- Select Only: inspect records without moving them\n"
                "- Move Points: drag point markers\n"
                "- Move Lines: drag whole line segments\n"
                "- Move Line Endpoints: select a line, then drag yellow endpoint handles\n"
                "- Add New Point: double-click the map to create a P record\n"
                "- Add New Line: double-click once for endpoint 1, again for endpoint 2\n"
                "- Side panel checkboxes toggle file/layer visibility\n"
                "- Save Edits: writes dirty L/P records to source files with timestamped backups\n"
                "- Flip Display Y: flips display only; saved coordinate meaning does not change"
            ),
        )

    def set_background(self, mode: str) -> None:
        self.dark_ui = mode == "dark"
        color = QColor(18, 18, 18) if self.dark_ui else QColor(255, 255, 255)
        self.view.setBackgroundBrush(QBrush(color))
        self.scene.setBackgroundBrush(QBrush(color))
        if hasattr(self, "light_bg_action"):
            self.light_bg_action.setChecked(mode == "light")
        if hasattr(self, "dark_bg_action"):
            self.dark_bg_action.setChecked(mode == "dark")

        if self.dark_ui:
            up_arrow, down_arrow = ensure_spinbox_arrow_images()
            self.setStyleSheet(f"""
                QWidget {{ background-color: #242424; color: #f0f0f0; }}
                QGroupBox {{ border: 1px solid #555; margin-top: 8px; padding-top: 8px; }}
                QGroupBox::title {{ subcontrol-origin: margin; left: 8px; padding: 0 3px; }}
                QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QListWidget {{
                    background-color: #1b1b1b;
                    color: #f0f0f0;
                    border: 1px solid #555;
                }}
                QSpinBox, QDoubleSpinBox {{
                    padding-right: 22px;
                    min-height: 22px;
                }}
                QSpinBox::up-button, QDoubleSpinBox::up-button {{
                    subcontrol-origin: border;
                    subcontrol-position: top right;
                    width: 20px;
                    border-left: 1px solid #777;
                    border-bottom: 1px solid #555;
                    background-color: #3a3a3a;
                }}
                QSpinBox::down-button, QDoubleSpinBox::down-button {{
                    subcontrol-origin: border;
                    subcontrol-position: bottom right;
                    width: 20px;
                    border-left: 1px solid #777;
                    border-top: 1px solid #555;
                    background-color: #3a3a3a;
                }}
                QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
                QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
                    background-color: #505050;
                }}
                QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
                    image: url("{up_arrow}");
                    width: 9px;
                    height: 9px;
                }}
                QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
                    image: url("{down_arrow}");
                    width: 9px;
                    height: 9px;
                }}
                QPushButton {{ background-color: #333; color: #f0f0f0; border: 1px solid #666; padding: 3px; }}
                QPushButton:hover {{ background-color: #444; }}
                QTabWidget::pane {{ border: 1px solid #555; }}
                QTabBar::tab {{ background: #333; color: #f0f0f0; padding: 4px; }}
                QTabBar::tab:selected {{ background: #555; }}
                QToolButton {{
                    background-color: #242424;
                    color: #f0f0f0;
                    border: 0px;
                    padding: 4px 10px;
                }}
                QToolButton:hover {{
                    background-color: #444;
                }}
                QToolButton:checked {{
                    background-color: #4f6fa8;
                    color: #ffffff;
                    border: 1px solid #9db8ff;
                    font-weight: bold;
                }}
                QMenuBar {{ background-color: #242424; color: #f0f0f0; }}
                QMenuBar::item:selected {{ background-color: #444; }}
                QMenu {{ background-color: #242424; color: #f0f0f0; border: 1px solid #555; }}
                QMenu::item {{ padding: 5px 28px 5px 18px; }}
                QMenu::item:selected {{ background-color: #4f6fa8; }}
            """)
        else:
            self.setStyleSheet("")

        if hasattr(self, "side_panel"):
            self.side_panel.rebuild_colour_list()
            self.side_panel.rebuild_points_list()

    def log_event(self, message: str) -> None:
        try:
            LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with LOG_PATH.open("a", encoding="utf-8") as log_file:
                log_file.write(f"[{timestamp}] {message}\n")
        except Exception:
            pass

    def open_log_location(self) -> None:
        try:
            LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            if not LOG_PATH.exists():
                LOG_PATH.write_text("", encoding="utf-8")
            os.startfile(str(LOG_PATH.parent))
        except Exception as exc:
            QMessageBox.warning(self, "Log Location", f"Could not open log location:\n{exc}")

    def apply_preferences_to_panel(self) -> None:
        return

    def read_preferences_from_panel(self) -> None:
        return

    def confirm_bulk_action(self, title: str, message: str, record_count: int, action_type: str = "edit") -> bool:
        if not self.confirm_bulk_actions:
            return True
        threshold = self.confirm_bulk_delete_over if action_type == "delete" else self.confirm_bulk_edit_over
        if record_count <= 0 or record_count < threshold:
            return True
        result = QMessageBox.question(
            self,
            title,
            message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        return result == QMessageBox.Yes

    def collect_settings(self) -> dict[str, Any]:
        self.read_preferences_from_panel()
        return {
            "last_files": [str(path) for path in self.loaded_files] if self.remember_last_loaded_map else [],
            "dark_mode": bool(getattr(self, "dark_ui", False)),
            "sidebar_sizes": self.splitter.sizes() if hasattr(self, "splitter") else [],
            "map_folder": getattr(self, "map_folder", ""),
            "remember_last_loaded_map": bool(self.remember_last_loaded_map),
            "auto_fit_restored_map": bool(self.auto_fit_restored_map),
            "autosave_settings_on_exit": bool(self.autosave_settings_on_exit),
            "show_beta_warning": bool(self.show_beta_warning),
            "default_background_mode": self.default_background_mode,
            "flip_display_y": bool(self.mapper.flip_display_y),
            "max_highlights_before_warning": int(self.max_highlights_before_warning),
            "confirm_bulk_edit_over": int(self.confirm_bulk_edit_over),
            "confirm_bulk_delete_over": int(self.confirm_bulk_delete_over),
            "confirm_bulk_actions": bool(self.confirm_bulk_actions),
        }

    def save_settings(self) -> None:
        try:
            SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
            SETTINGS_PATH.write_text(json.dumps(self.collect_settings(), indent=2), encoding="utf-8")
            self.log_event("Settings saved.")
        except Exception as exc:
            self.log_event(f"Settings save failed: {exc}")

    def save_last_session(self) -> None:
        self.save_settings()

    def load_settings_data(self) -> dict[str, Any]:
        try:
            if SETTINGS_PATH.exists():
                return json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
        return {}

    def load_last_session(self) -> None:
        data = self.load_settings_data()
        try:
            self.remember_last_loaded_map = data.get("remember_last_loaded_map", True)
            self.auto_fit_restored_map = data.get("auto_fit_restored_map", True)
            self.autosave_settings_on_exit = data.get("autosave_settings_on_exit", True)
            self.show_beta_warning = data.get("show_beta_warning", True)
            self.default_background_mode = data.get("default_background_mode", "remember")
            self.max_highlights_before_warning = int(data.get("max_highlights_before_warning", 5000))
            self.confirm_bulk_edit_over = int(data.get("confirm_bulk_edit_over", 1))
            self.confirm_bulk_delete_over = int(data.get("confirm_bulk_delete_over", 1))
            self.confirm_bulk_actions = data.get("confirm_bulk_actions", True)
            self.mapper.flip_display_y = bool(data.get("flip_display_y", False))
            if hasattr(self, "flip_y_action"):
                self.flip_y_action.setChecked(self.mapper.flip_display_y)
            self.apply_preferences_to_panel()

            if self.default_background_mode == "light":
                self.set_background("light")
            elif self.default_background_mode == "dark":
                self.set_background("dark")
            elif data.get("dark_mode"):
                self.set_background("dark")
            else:
                self.set_background("light")

            self.map_folder = data.get("map_folder", "")
            if self.map_folder and hasattr(self, "side_panel"):
                self.side_panel.map_folder_edit.setText(self.map_folder)
                self.rebuild_zone_list()

            files = [Path(path) for path in data.get("last_files", [])] if self.remember_last_loaded_map else []
            files = [path for path in files if path.exists()]
            if files:
                self.load_files(files, remember=False)
                self._fit_last_map_after_show = bool(self.auto_fit_restored_map)
                self.status_label.setText("Restored last loaded map files." + (" Fit will run after the window is shown." if self.auto_fit_restored_map else ""))

            sizes = data.get("sidebar_sizes", [])
            if sizes and hasattr(self, "splitter"):
                self.splitter.setSizes([int(x) for x in sizes])
        except Exception:
            pass

    def open_preferences(self) -> None:
        dialog = PreferencesDialog(self)
        dialog.exec()

    def open_backup_folder(self) -> None:
        try:
            BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
            os.startfile(str(BACKUPS_DIR))
        except Exception as exc:
            QMessageBox.warning(self, "Backup Folder", f"Could not open backup folder:\n{exc}")

    def maybe_show_startup_warning(self) -> None:
        if not self.show_beta_warning:
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Beta Safety Warning")
        layout = QVBoxLayout(dialog)
        warning = QLabel(
            "This tool edits EverQuest map .txt files.\n\n"
            "Before saving edits, make sure you have backups of your map folder.\n"
            "For beta testing, use Save As... or work from a copied map folder."
        )
        warning.setWordWrap(True)
        layout.addWidget(warning)
        checkbox = QCheckBox("Do not show this again")
        layout.addWidget(checkbox)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)
        dialog.exec()
        if checkbox.isChecked():
            self.show_beta_warning = False
            self.save_settings()

    def open_files_dialog(self) -> None:
        if not self.confirm_discard_unsaved():
            return
        file_names, _ = QFileDialog.getOpenFileNames(
            self,
            "Open EQ Map Text File(s)",
            "",
            "Text files (*.txt);;All files (*.*)",
        )
        if file_names:
            self.load_files([Path(name) for name in file_names])

    def load_files(self, file_paths: list[Path], remember: bool = True) -> None:
        try:
            loaded_map = load_map_files(file_paths)
        except OSError as exc:
            QMessageBox.critical(self, "Load Error", f"Could not load map files:\n{exc}")
            return

        self.loaded_files = [Path(path) for path in file_paths]
        self.layer_visible = {path: True for path in self.loaded_files}
        self.loaded_map = loaded_map
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.pending_line_start = None
        self.render_map()
        self.side_panel.rebuild_layers()
        self.update_dirty_indicator()
        if remember:
            self.save_last_session()

        file_list = ", ".join(path.name for path in self.loaded_files)
        self.status_label.setText(
            f"Loaded {len(loaded_map.lines):,} lines and {len(loaded_map.points):,} points from {file_list}"
        )
        self.log_event(f"Loaded files: {file_list}")

    def render_map(self, keep_view: bool = False) -> None:
        old_transform = self.view.transform()
        old_center = self.view.mapToScene(self.view.viewport().rect().center())

        self.scene.clear()
        self.line_items_by_record.clear()
        self.point_items_by_record.clear()
        self.label_items_by_record.clear()
        self.endpoint_handles.clear()
        self.selection_highlights.clear()
        self.bulk_selected_records = []
        self.side_panel.set_record(None)

        for record in self.loaded_map.lines:
            if not getattr(record, "deleted", False) and self.layer_visible.get(record.file_path, True):
                self.add_or_update_line_item(record)

        for record in self.loaded_map.points:
            if not getattr(record, "deleted", False) and self.layer_visible.get(record.file_path, True):
                self.add_or_update_point_items(record)

        self.scene.selectionChanged.connect(self.on_selection_changed)
        self.on_edit_mode_changed(self.edit_mode())

        if keep_view:
            self.view.setTransform(old_transform)
            self.view.centerOn(old_center)
        else:
            self.fit_map()

    def line_tooltip(self, record: MapLineRecord) -> str:
        return f"{record.file_path.name}:{record.line_index + 1 if record.line_index >= 0 else 'new'}\n{record.to_map_line()}"

    def point_tooltip(self, record: MapPointRecord) -> str:
        return f"{record.file_path.name}:{record.line_index + 1 if record.line_index >= 0 else 'new'}\n{record.to_map_line()}"

    def add_or_update_line_item(self, record: MapLineRecord) -> None:
        if not self.layer_visible.get(record.file_path, True):
            self.render_map(keep_view=True)
            return

        key = id(record)
        p1 = self.mapper.map_to_scene(record.x1, record.y1)
        p2 = self.mapper.map_to_scene(record.x2, record.y2)

        item = self.line_items_by_record.get(key)
        if item is None:
            item = MovableLineItem(self, record)
            self.scene.addItem(item)
            self.line_items_by_record[key] = item

        self._drag_update_lock = True
        item.setLine(0, 0, p2.x() - p1.x(), p2.y() - p1.y())
        item.setPos(p1)
        self._drag_update_lock = False

        item.setPen(QPen(record.color, 1.0))
        item.setToolTip(self.line_tooltip(record))
        item.setFlag(QGraphicsItem.ItemIsMovable, self.edit_mode() == "Move Lines")

    def add_or_update_point_items(self, record: MapPointRecord) -> None:
        if not self.layer_visible.get(record.file_path, True):
            self.render_map(keep_view=True)
            return

        key = id(record)
        point = self.mapper.map_to_scene(record.x, record.y)
        radius = max(2.0, record.size * 1.8)

        marker = self.point_items_by_record.get(key)
        if marker is None:
            marker = MovablePointMarker(self, record)
            self.scene.addItem(marker)
            self.point_items_by_record[key] = marker

        self._drag_update_lock = True
        marker.setRect(-radius, -radius, radius * 2, radius * 2)
        marker.setPos(point)
        self._drag_update_lock = False

        marker.setPen(QPen(record.color, 0.8))
        marker.setBrush(QBrush(record.color))
        marker.setVisible(self.show_points)
        marker.setToolTip(self.point_tooltip(record))
        marker.setFlag(QGraphicsItem.ItemIsMovable, self.edit_mode() == "Move Points")

        text = self.label_items_by_record.get(key)
        if text is None:
            text = QGraphicsTextItem()
            text.setData(0, record)
            text.setFlag(QGraphicsItem.ItemIsSelectable, True)
            self.scene.addItem(text)
            self.label_items_by_record[key] = text

        text.setPlainText(record.label.replace("_", " "))
        text.setDefaultTextColor(record.color)
        text.setFont(QFont("Arial", 6))
        text.setPos(point.x() + radius + 1, point.y() - 5)
        text.setVisible(self.show_labels)
        text.setToolTip(self.point_tooltip(record))

    def update_record_items(self, record: Any) -> None:
        if isinstance(record, MapPointRecord):
            self.add_or_update_point_items(record)
        elif isinstance(record, MapLineRecord):
            self.add_or_update_line_item(record)
            if self.side_panel.current_record is record and self.edit_mode() == "Move Line Endpoints":
                self.show_endpoint_handles(record)
        self.update_dirty_indicator()

    def setup_shortcuts(
        self,
        open_action: QAction,
        save_action: QAction,
        undo_callable,
        redo_callable,
        fit_callable,
        clear_callable,
        delete_callable,
        select_all_callable,
        search_widget: QLineEdit,
    ) -> None:
        open_action.setShortcut("Ctrl+O")
        save_action.setShortcut("Ctrl+S")

        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(undo_callable)
        self.addAction(undo_action)

        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(redo_callable)
        self.addAction(redo_action)

        focus_search_action = QAction("Focus Search", self)
        focus_search_action.setShortcut("Ctrl+F")
        focus_search_action.triggered.connect(lambda: (search_widget.setFocus(), search_widget.selectAll()))
        self.addAction(focus_search_action)

        fit_action = QAction("Fit Map Shortcut", self)
        fit_action.setShortcut("F")
        fit_action.triggered.connect(fit_callable)
        self.addAction(fit_action)

        clear_action = QAction("Clear Selection Shortcut", self)
        clear_action.setShortcut("Esc")
        clear_action.triggered.connect(clear_callable)
        self.addAction(clear_action)

        delete_action = QAction("Delete Selected Shortcut", self)
        delete_action.setShortcut("Del")
        delete_action.triggered.connect(delete_callable)
        self.addAction(delete_action)

        select_all_action = QAction("Select All Visible Records Shortcut", self)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(select_all_callable)
        self.addAction(select_all_action)

    def visible_point_records(self) -> list[MapPointRecord]:
        return [
            point for point in self.loaded_map.points
            if not getattr(point, "deleted", False)
            and self.layer_visible.get(point.file_path, True)
        ]

    def label_search_text(self) -> str:
        return self.global_search_edit.text().strip().lower() if hasattr(self, "global_search_edit") else ""

    def find_label_matches(self) -> list[MapPointRecord]:
        search = self.label_search_text()
        if not search:
            return []
        return [point for point in self.visible_point_records() if search in point.label.lower()]

    def search_select_first_label_match(self) -> None:
        matches = self.find_label_matches()
        self.search_matches = matches
        self.search_index = 0 if matches else -1
        if not matches:
            self.status_label.setText("No point labels matched the search text.")
            return

        record = matches[0]
        self.scene.blockSignals(True)
        self.scene.clearSelection()
        item = self.point_items_by_record.get(id(record))
        if item:
            item.setSelected(True)
        self.scene.blockSignals(False)
        self.refresh_selection_highlights()
        self.side_panel.set_record(record)
        self.center_on_record(record)
        self.status_label.setText(f"Found 1 of {len(matches)} matching point label(s): {record.label}")

    def search_select_all_label_matches(self) -> None:
        matches = self.find_label_matches()
        self.search_matches = matches
        if not matches:
            self.status_label.setText("No point labels matched the search text.")
            return

        self.scene.blockSignals(True)
        self.scene.clearSelection()
        for record in matches:
            item = self.point_items_by_record.get(id(record))
            if item:
                item.setSelected(True)
        self.scene.blockSignals(False)
        self.refresh_selection_highlights()
        point_count = len(matches)
        self.side_panel.show_multi_selection(point_count, 0)
        self.fit_selected()
        self.status_label.setText(f"Selected {len(matches)} matching point label(s).")

    def center_on_record(self, record: Any) -> None:
        if isinstance(record, MapPointRecord):
            point = self.mapper.map_to_scene(record.x, record.y)
            self.view.centerOn(point)
        elif isinstance(record, MapLineRecord):
            p1 = self.mapper.map_to_scene(record.x1, record.y1)
            p2 = self.mapper.map_to_scene(record.x2, record.y2)
            self.view.centerOn((p1.x() + p2.x()) / 2, (p1.y() + p2.y()) / 2)

    def center_selected(self) -> None:
        records = self.selected_map_records() or self.bulk_selected_records
        if not records:
            self.status_label.setText("No selected records to center.")
            return

        rect = self.bounding_rect_for_records(records)
        if rect.isNull():
            self.center_on_record(records[0])
        else:
            self.view.centerOn(rect.center())
        self.status_label.setText(f"Centered on {len(records)} selected record(s).")

    def bounding_rect_for_records(self, records: list[Any]) -> QRectF:
        rect = QRectF()
        for record in records:
            if isinstance(record, MapPointRecord):
                point = self.mapper.map_to_scene(record.x, record.y)
                radius = max(10.0, record.size * 4.0)
                item_rect = QRectF(point.x() - radius, point.y() - radius, radius * 2, radius * 2)
            elif isinstance(record, MapLineRecord):
                p1 = self.mapper.map_to_scene(record.x1, record.y1)
                p2 = self.mapper.map_to_scene(record.x2, record.y2)
                item_rect = QRectF(p1, p2).normalized()
            else:
                continue
            rect = item_rect if rect.isNull() else rect.united(item_rect)
        return rect

    def select_all_visible_records(self) -> None:
        records: list[Any] = []
        records.extend([
            line for line in self.loaded_map.lines
            if not getattr(line, "deleted", False)
            and self.layer_visible.get(line.file_path, True)
        ])
        records.extend(self.visible_point_records())

        if not records:
            self.status_label.setText("No visible records to select.")
            return

        if self.confirm_bulk_actions and len(records) > 2500:
            if QMessageBox.question(
                self,
                "Select All Visible Records",
                f"Select {len(records)} visible records? This may take a moment.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            ) != QMessageBox.Yes:
                return

        self.scene.blockSignals(True)
        self.scene.clearSelection()
        for record in records:
            item = self.line_items_by_record.get(id(record)) or self.point_items_by_record.get(id(record))
            if item:
                item.setSelected(True)
        self.scene.blockSignals(False)
        self.refresh_selection_highlights()
        point_count = sum(1 for record in records if isinstance(record, MapPointRecord))
        line_count = sum(1 for record in records if isinstance(record, MapLineRecord))
        self.side_panel.show_multi_selection(point_count, line_count)
        self.status_label.setText(f"Selected all visible records: {point_count} point(s), {line_count} line(s).")

    def clear_selection_and_highlights(self) -> None:
        self.scene.clearSelection()
        self.clear_selection_highlights()
        self.bulk_selected_records = []
        self.side_panel.set_record(None)
        self.status_label.setText("Selection and highlights cleared.")

    def fit_selected(self) -> None:
        records = self.selected_map_records() or self.bulk_selected_records
        rect = self.bounding_rect_for_records(records)
        if rect.isNull():
            self.status_label.setText("No selected records to fit.")
            return

        margin = 75
        padded = QRectF(rect.x() - margin, rect.y() - margin, rect.width() + margin * 2, rect.height() + margin * 2)
        self.view.fitInView(padded, Qt.KeepAspectRatio)
        self.status_label.setText("Fit selected records.")

    def save_as_folder(self) -> None:
        if not self.loaded_files:
            QMessageBox.information(self, "No Files", "Open map files before using Save As.")
            return
        folder = QFileDialog.getExistingDirectory(self, "Choose Output Folder for Edited Map Files", str(self.loaded_files[0].parent))
        if not folder:
            return
        try:
            self.write_map_files_to_folder(Path(folder))
            self.log_event(f"Save As completed to {folder}")
            QMessageBox.information(self, "Save As Complete", f"Edited map files were written to:\n{folder}\n\nYour original map files were not changed.")
        except Exception as exc:
            self.log_event(f"Save As failed: {exc}")
            QMessageBox.critical(self, "Save As Error", f"Could not save edited copies:\n{exc}")

    def write_map_files_to_folder(self, output_folder: Path) -> None:
        output_folder.mkdir(parents=True, exist_ok=True)
        dirty_records = self.dirty_records()
        by_file: dict[Path, list[Any]] = {}
        for record in dirty_records:
            by_file.setdefault(record.file_path, []).append(record)

        for file_path in self.loaded_files:
            original_lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines() if file_path.exists() else []
            records = by_file.get(file_path, [])
            append_records = []
            for record in records:
                if record.line_index < 0:
                    append_records.append(record)
                    continue
                if record.line_index >= len(original_lines):
                    raise IndexError(f"Line index out of range for {record.file_path.name}:{record.line_index + 1}")
                if getattr(record, "deleted", False):
                    original_lines[record.line_index] = None
                else:
                    original_lines[record.line_index] = record.to_map_line()

            original_lines = [line for line in original_lines if line is not None]
            for record in append_records:
                if not getattr(record, "deleted", False):
                    original_lines.append(record.to_map_line())

            (output_folder / file_path.name).write_text("\n".join(original_lines) + "\n", encoding="utf-8")

    def fit_map(self) -> None:
        rect = self.scene.itemsBoundingRect()
        if rect.isNull():
            return
        margin = 50
        padded = QRectF(
            rect.x() - margin,
            rect.y() - margin,
            rect.width() + margin * 2,
            rect.height() + margin * 2,
        )
        self.view.fitInView(padded, Qt.KeepAspectRatio)

    def toggle_labels(self, checked: bool) -> None:
        self.show_labels = checked
        for item in self.label_items_by_record.values():
            item.setVisible(checked)

    def toggle_points(self, checked: bool) -> None:
        self.show_points = checked
        for item in self.point_items_by_record.values():
            item.setVisible(checked)

    def toggle_display_y_flip(self, checked: bool) -> None:
        self.mapper.flip_display_y = checked
        self.render_map(keep_view=False)
        self.status_label.setText("Display Y flipped." if checked else "Display Y normal.")

    def set_layer_visible(self, file_path: Path, visible: bool) -> None:
        self.layer_visible[file_path] = visible
        self.render_map(keep_view=True)
        self.side_panel.rebuild_layers()
        self.status_label.setText(f"{file_path.name} visible: {visible}")

    def on_edit_mode_changed(self, mode: str) -> None:
        for item in self.point_items_by_record.values():
            item.setFlag(QGraphicsItem.ItemIsMovable, mode == "Move Points")
        for item in self.line_items_by_record.values():
            item.setFlag(QGraphicsItem.ItemIsMovable, mode == "Move Lines")

        self.clear_endpoint_handles()
        selected = self.scene.selectedItems()
        if mode == "Move Line Endpoints" and selected:
            record = selected[0].data(0)
            if isinstance(record, MapLineRecord):
                self.show_endpoint_handles(record)

        self.pending_line_start = None
        self.status_label.setText(f"Edit mode: {mode}")

    def clear_selection_highlights(self) -> None:
        for item in self.selection_highlights:
            try:
                self.scene.removeItem(item)
            except RuntimeError:
                pass
        self.selection_highlights.clear()

    def add_highlights_for_records(self, records: list[Any], max_items: int = 0) -> int:
        self.clear_selection_highlights()
        glow_colour = QColor(255, 230, 80, 130)
        glow_pen = QPen(glow_colour, 7.0)
        glow_brush = QBrush(QColor(255, 230, 80, 70))

        highlighted = 0
        records_to_draw = records if not max_items else records[:max_items]
        for record in records_to_draw:
            if isinstance(record, MapPointRecord):
                point = self.mapper.map_to_scene(record.x, record.y)
                radius = max(7.0, record.size * 3.2)
                glow = QGraphicsEllipseItem(point.x() - radius, point.y() - radius, radius * 2, radius * 2)
                glow.setBrush(glow_brush)
                glow.setPen(QPen(glow_colour, 2.0))
                glow.setZValue(-500)
                self.scene.addItem(glow)
                self.selection_highlights.append(glow)
                highlighted += 1

            elif isinstance(record, MapLineRecord):
                p1 = self.mapper.map_to_scene(record.x1, record.y1)
                p2 = self.mapper.map_to_scene(record.x2, record.y2)
                glow = QGraphicsLineItem(p1.x(), p1.y(), p2.x(), p2.y())
                glow.setPen(glow_pen)
                glow.setZValue(-500)
                self.scene.addItem(glow)
                self.selection_highlights.append(glow)
                highlighted += 1

        return highlighted

    def refresh_selection_highlights(self) -> None:
        records = []
        records_seen = set()
        for item in self.scene.selectedItems():
            record = item.data(0)
            if id(record) in records_seen:
                continue
            if isinstance(record, (MapPointRecord, MapLineRecord)):
                records_seen.add(id(record))
                records.append(record)
        self.add_highlights_for_records(records)

    def on_selection_changed(self) -> None:
        selected = self.scene.selectedItems()
        self.refresh_selection_highlights()
        if not selected:
            self.side_panel.set_record(None)
            self.side_panel.set_multi_selection_summary(0, 0)
            self.clear_endpoint_handles()
            return

        if len(selected) > 1:
            point_count = sum(1 for item in selected if isinstance(item.data(0), MapPointRecord))
            line_count = sum(1 for item in selected if isinstance(item.data(0), MapLineRecord))
            self.side_panel.show_multi_selection(point_count, line_count)
            self.clear_endpoint_handles()
            self.status_label.setText(f"Selected {point_count} point(s) and {line_count} line(s).")
            return

        record = selected[0].data(0)
        self.side_panel.set_record(record)
        self.clear_endpoint_handles()

        if isinstance(record, MapPointRecord):
            self.status_label.setText(
                f"Point: {record.label} | X={record.x:.4f}, Y={record.y:.4f}, Z={record.z:.4f} | "
                f"RGB=({record.r}, {record.g}, {record.b}) | {record.file_path.name}:{record.line_index + 1 if record.line_index >= 0 else 'new'}"
            )
        elif isinstance(record, MapLineRecord):
            self.status_label.setText(
                f"Line | RGB=({record.r}, {record.g}, {record.b}) | {record.file_path.name}:{record.line_index + 1 if record.line_index >= 0 else 'new'}"
            )
            if self.edit_mode() == "Move Line Endpoints":
                self.show_endpoint_handles(record)

    def clear_endpoint_handles(self) -> None:
        for handle in self.endpoint_handles:
            self.scene.removeItem(handle)
        self.endpoint_handles.clear()

    def show_endpoint_handles(self, record: MapLineRecord) -> None:
        self.clear_endpoint_handles()
        for endpoint, x, y in [(1, record.x1, record.y1), (2, record.x2, record.y2)]:
            handle = EndpointHandle(self, record, endpoint)
            handle.setPos(self.mapper.map_to_scene(x, y))
            self.scene.addItem(handle)
            self.endpoint_handles.append(handle)

    def on_marker_dragged(self, point: MapPointRecord, scene_pos: QPointF) -> None:
        if self._drag_update_lock or self.edit_mode() != "Move Points":
            return

        point.x, point.y = self.mapper.scene_to_map(scene_pos)
        point.dirty = True

        label = self.label_items_by_record.get(id(point))
        if label is not None:
            radius = max(2.0, point.size * 1.8)
            label.setPos(scene_pos.x() + radius + 1, scene_pos.y() - 5)

        if self.side_panel.current_record is point:
            self.side_panel.set_record(point)

        self.update_dirty_indicator()
        self.status_label.setText(f"Moved point: {point.label} | X={point.x:.4f}, Y={point.y:.4f}")

    def on_line_dragged(self, line: MapLineRecord, scene_pos: QPointF) -> None:
        if self._drag_update_lock or self.edit_mode() != "Move Lines":
            return

        new_x1, new_y1 = self.mapper.scene_to_map(scene_pos)
        dx = new_x1 - line.x1
        dy = new_y1 - line.y1

        line.x1 += dx
        line.y1 += dy
        line.x2 += dx
        line.y2 += dy
        line.dirty = True

        if self.side_panel.current_record is line:
            self.side_panel.set_record(line)

        self.update_dirty_indicator()
        self.status_label.setText(
            f"Moved line | ({line.x1:.2f}, {line.y1:.2f}) -> ({line.x2:.2f}, {line.y2:.2f})"
        )

    def on_endpoint_dragged(self, line: MapLineRecord, endpoint: int, scene_pos: QPointF) -> None:
        if self._drag_update_lock or self.edit_mode() != "Move Line Endpoints":
            return

        x, y = self.mapper.scene_to_map(scene_pos)
        if endpoint == 1:
            line.x1 = x
            line.y1 = y
        else:
            line.x2 = x
            line.y2 = y

        line.dirty = True
        self.add_or_update_line_item(line)

        if self.side_panel.current_record is line:
            self.side_panel.set_record(line)

        self.update_dirty_indicator()
        self.status_label.setText(f"Moved line endpoint {endpoint} | X={x:.2f}, Y={y:.2f}")

    def active_file_for_new_records(self) -> Optional[Path]:
        if not self.loaded_files:
            return None
        index = self.side_panel.active_file_combo.currentIndex()
        if index >= 0:
            data = self.side_panel.active_file_combo.itemData(index)
            if data:
                return Path(data)
        return self.loaded_files[0]

    def handle_canvas_double_click(self, scene_pos: QPointF) -> None:
        mode = self.edit_mode()
        active_file = self.active_file_for_new_records()
        if active_file is None:
            return

        if mode == "Add New Point":
            label, ok = QInputDialog.getText(self, "Add New Point", "Point label:")
            if not ok:
                return
            x, y = self.mapper.scene_to_map(scene_pos)
            point = MapPointRecord(
                file_path=active_file,
                line_index=-1,
                raw_text="",
                x=x,
                y=y,
                z=0.0,
                r=255,
                g=255,
                b=255,
                size=2.0,
                label=label.strip() or "New_Point",
                dirty=True,
            )
            self.loaded_map.points.append(point)
            self.add_or_update_point_items(point)
            self.side_panel.rebuild_layers()
            self.update_dirty_indicator()
            self.status_label.setText(f"Added point to {target_file.name}. Save Edits will append it.")

        elif mode == "Add New Line":
            if self.pending_line_start is None:
                self.pending_line_start = scene_pos
                self.status_label.setText("Add New Line: double-click the second endpoint.")
                return

            x1, y1 = self.mapper.scene_to_map(self.pending_line_start)
            x2, y2 = self.mapper.scene_to_map(scene_pos)
            line = MapLineRecord(
                file_path=active_file,
                line_index=-1,
                raw_text="",
                x1=x1,
                y1=y1,
                z1=0.0,
                x2=x2,
                y2=y2,
                z2=0.0,
                r=255,
                g=255,
                b=255,
                dirty=True,
            )
            self.pending_line_start = None
            self.loaded_map.lines.append(line)
            self.add_or_update_line_item(line)
            self.side_panel.rebuild_layers()
            self.update_dirty_indicator()
            self.status_label.setText(f"Added line to {target_file.name}. Save Edits will append it.")

    def show_map_context_menu(self, global_pos, scene_pos: QPointF) -> None:
        if not self.loaded_files:
            return
        menu = QMenu(self)
        add_point_action = menu.addAction("Add Point Here")
        add_line_start_action = menu.addAction("Start New Line Here")
        if self.pending_line_start is not None:
            add_line_finish_action = menu.addAction("Finish New Line Here")
        else:
            add_line_finish_action = None

        chosen = menu.exec(global_pos)
        if chosen == add_point_action:
            self.add_point_at(scene_pos)
        elif chosen == add_line_start_action:
            self.start_line_at(scene_pos)
        elif add_line_finish_action is not None and chosen == add_line_finish_action:
            self.finish_line_at(scene_pos)

    def add_point_at(self, scene_pos: QPointF) -> None:
        active_file = self.active_file_for_new_records()
        if active_file is None:
            return

        dialog = PointDetailsDialog(self, title="Add Point", files=self.loaded_files, active_file=active_file)
        if dialog.exec() != QDialog.Accepted:
            return
        values = dialog.values()
        target_file = values.get("file_path") or active_file
        x, y = self.mapper.scene_to_map(scene_pos)
        point = MapPointRecord(
            file_path=target_file,
            line_index=-1,
            raw_text="",
            x=x,
            y=y,
            z=0.0,
            r=values["r"],
            g=values["g"],
            b=values["b"],
            size=values["size"],
            label=values["label"],
            dirty=True,
        )
        self.loaded_map.points.append(point)
        self.undo_stack.append(AddRecordCommand("Add point", self, point, "points"))
        self.redo_stack.clear()
        self.add_or_update_point_items(point)
        self.side_panel.rebuild_layers()
        self.update_dirty_indicator()
        self.status_label.setText(f"Added point to {target_file.name}. Save Edits will append it.")

    def start_line_at(self, scene_pos: QPointF) -> None:
        self.pending_line_start = scene_pos
        QMessageBox.information(
            self,
            "Add Line",
            "First endpoint has been set. Double-left-click the second endpoint and choose 'Finish New Line Here'.",
        )
        self.status_label.setText("New line endpoint 1 set. Double-left-click endpoint 2 and choose Finish New Line Here.")

    def finish_line_at(self, scene_pos: QPointF) -> None:
        active_file = self.active_file_for_new_records()
        if active_file is None or self.pending_line_start is None:
            return

        dialog = LineColorDialog(self, files=self.loaded_files, active_file=active_file)
        if dialog.exec() != QDialog.Accepted:
            return
        values = dialog.values()
        target_file = values.get("file_path") or active_file

        x1, y1 = self.mapper.scene_to_map(self.pending_line_start)
        x2, y2 = self.mapper.scene_to_map(scene_pos)
        self.pending_line_start = None

        line = MapLineRecord(
            file_path=target_file,
            line_index=-1,
            raw_text="",
            x1=x1,
            y1=y1,
            z1=0.0,
            x2=x2,
            y2=y2,
            z2=0.0,
            r=values["r"],
            g=values["g"],
            b=values["b"],
            dirty=True,
        )
        self.loaded_map.lines.append(line)
        self.undo_stack.append(AddRecordCommand("Add line", self, line, "lines"))
        self.redo_stack.clear()
        self.add_or_update_line_item(line)
        self.side_panel.rebuild_layers()
        self.update_dirty_indicator()
        self.status_label.setText(f"Added line to {target_file.name}. Save Edits will append it.")

    def selected_colours_from_bulk_tab(self, record_type: Optional[str] = None) -> list[tuple[int, int, int]]:
        record_type = record_type or self.current_bulk_colour_type
        list_widget = self.side_panel.point_colour_list if record_type == "points" else self.side_panel.line_colour_list
        colours = [item.data(Qt.UserRole) for item in list_widget.selectedItems()]
        return [colour for colour in colours if colour is not None]

    def selected_colour_from_bulk_tab(self) -> Optional[tuple[int, int, int]]:
        colours = self.selected_colours_from_bulk_tab()
        return colours[0] if colours else None

    def all_colour_counts(self) -> list[tuple[tuple[int, int, int], int, int]]:
        counts: dict[tuple[int, int, int], dict[str, int]] = {}
        for point in self.loaded_map.points:
            if getattr(point, "deleted", False) or not self.layer_visible.get(point.file_path, True):
                continue
            rgb = (point.r, point.g, point.b)
            counts.setdefault(rgb, {"points": 0, "lines": 0})["points"] += 1
        for line in self.loaded_map.lines:
            if getattr(line, "deleted", False) or not self.layer_visible.get(line.file_path, True):
                continue
            rgb = (line.r, line.g, line.b)
            counts.setdefault(rgb, {"points": 0, "lines": 0})["lines"] += 1

        rows = [(rgb, values["points"], values["lines"]) for rgb, values in counts.items()]
        return sorted(rows, key=lambda row: row[1] + row[2], reverse=True)

    def select_records_by_colour(self, record_type: str) -> None:
        self.current_bulk_colour_type = record_type
        colours = set(self.selected_colours_from_bulk_tab(record_type))
        if not colours:
            return

        # Do not call item.setSelected(True) for thousands of records. It triggers many
        # selection-change events and can be extremely slow/crashy with large EQ map files.
        self.scene.blockSignals(True)
        self.scene.clearSelection()
        self.scene.blockSignals(False)

        records: list[Any] = []
        if record_type == "points":
            for point in self.loaded_map.points:
                if getattr(point, "deleted", False) or not self.layer_visible.get(point.file_path, True):
                    continue
                if (point.r, point.g, point.b) in colours:
                    records.append(point)
        elif record_type == "lines":
            for line in self.loaded_map.lines:
                if getattr(line, "deleted", False) or not self.layer_visible.get(line.file_path, True):
                    continue
                if (line.r, line.g, line.b) in colours:
                    records.append(line)

        self.bulk_selected_records = records
        if (
            self.max_highlights_before_warning
            and len(records) > self.max_highlights_before_warning
            and QMessageBox.question(
                self,
                "Highlight Many Records",
                f"This will highlight {len(records)} {record_type}. Continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            ) != QMessageBox.Yes
        ):
            self.status_label.setText(f"Prepared {len(records)} {record_type}, but highlights were not drawn.")
            return
        highlighted = self.add_highlights_for_records(records)
        self.status_label.setText(f"Prepared and highlighted {highlighted} {record_type} matching {len(colours)} colour(s).")

    def apply_bulk_colour_to_selected_matching(self) -> None:
        colours = set(self.selected_colours_from_bulk_tab(self.current_bulk_colour_type))
        if not colours:
            return

        records = [
            record for record in self.bulk_selected_records
            if isinstance(record, (MapPointRecord, MapLineRecord))
            and not getattr(record, "deleted", False)
            and (record.r, record.g, record.b) in colours
        ]

        # Fallback for normal manually selected records.
        if not records:
            for item in self.scene.selectedItems():
                record = item.data(0)
                if isinstance(record, (MapPointRecord, MapLineRecord)) and not getattr(record, "deleted", False):
                    if (record.r, record.g, record.b) in colours and record not in records:
                        records.append(record)

        if not records:
            self.status_label.setText("No prepared or selected records match the selected colour(s).")
            return

        point_count = sum(1 for record in records if isinstance(record, MapPointRecord))
        line_count = sum(1 for record in records if isinstance(record, MapLineRecord))
        new_rgb_preview = (self.side_panel.bulk_new_r.value(), self.side_panel.bulk_new_g.value(), self.side_panel.bulk_new_b.value())
        if not self.confirm_bulk_action(
            "Confirm Bulk Recolour",
            f"Recolour {len(records)} record(s)?\n\nPoints: {point_count}\nLines: {line_count}\nNew colour: RGB {new_rgb_preview}",
            len(records),
            action_type="edit",
        ):
            return

        before = [snapshot_point(r) if isinstance(r, MapPointRecord) else snapshot_line(r) for r in records]
        new_rgb = (self.side_panel.bulk_new_r.value(), self.side_panel.bulk_new_g.value(), self.side_panel.bulk_new_b.value())
        for record in records:
            record.r, record.g, record.b = new_rgb
            record.dirty = True
        after = [snapshot_point(r) if isinstance(r, MapPointRecord) else snapshot_line(r) for r in records]
        self.undo_stack.append(BulkEditCommand("Bulk recolour selected matching records", records, before, after))
        self.redo_stack.clear()
        self.bulk_selected_records = []
        self.render_map(keep_view=True)
        self.update_dirty_indicator()
        self.status_label.setText(f"Recoloured {len(records)} record(s).")

    def recolour_selected_records_from_panel(self) -> None:
        records = self.selected_map_records()
        if not records:
            self.status_label.setText("No selected points or lines to recolour.")
            return

        point_count = sum(1 for record in records if isinstance(record, MapPointRecord))
        line_count = sum(1 for record in records if isinstance(record, MapLineRecord))
        preview_rgb = (
            self.side_panel.r_spin.value(),
            self.side_panel.g_spin.value(),
            self.side_panel.b_spin.value(),
        )
        if not self.confirm_bulk_action(
            "Confirm Selected Recolour",
            f"Recolour {len(records)} selected record(s)?\n\nPoints: {point_count}\nLines: {line_count}\nNew colour: RGB {preview_rgb}",
            len(records),
            action_type="edit",
        ):
            return

        before = []
        for record in records:
            if isinstance(record, MapPointRecord):
                before.append(snapshot_point(record))
            else:
                before.append(snapshot_line(record))

        new_rgb = (
            self.side_panel.r_spin.value(),
            self.side_panel.g_spin.value(),
            self.side_panel.b_spin.value(),
        )

        for record in records:
            record.r, record.g, record.b = new_rgb
            record.dirty = True

        after = []
        for record in records:
            if isinstance(record, MapPointRecord):
                after.append(snapshot_point(record))
            else:
                after.append(snapshot_line(record))

        self.undo_stack.append(BulkEditCommand("Recolour selected records", records, before, after))
        self.redo_stack.clear()
        self.render_map(keep_view=True)
        self.update_dirty_indicator()
        self.status_label.setText(f"Recoloured {len(records)} selected record(s) to RGB {new_rgb}.")

    def selected_map_records(self) -> list[Any]:
        records: list[Any] = []
        seen = set()
        for item in self.scene.selectedItems():
            record = item.data(0)
            if isinstance(record, (MapPointRecord, MapLineRecord)) and not getattr(record, "deleted", False):
                if id(record) not in seen:
                    seen.add(id(record))
                    records.append(record)
        return records

    def delete_selected_records(self) -> None:
        records = self.selected_map_records()
        if not records:
            self.status_label.setText("No selected points or lines to delete.")
            return

        point_count = sum(1 for record in records if isinstance(record, MapPointRecord))
        line_count = sum(1 for record in records if isinstance(record, MapLineRecord))

        if not self.confirm_bulk_action(
            "Delete Selected Records",
            f"Mark {len(records)} selected record(s) for deletion?\n\n"
            f"Points: {point_count}\nLines: {line_count}\n\n"
            "Save Edits will remove them from the map text files.",
            len(records),
            action_type="delete",
        ):
            return

        before = []
        for record in records:
            if isinstance(record, MapPointRecord):
                before.append(snapshot_point(record) | {"deleted": getattr(record, "deleted", False)})
            else:
                before.append(snapshot_line(record) | {"deleted": getattr(record, "deleted", False)})

        for record in records:
            record.deleted = True
            record.dirty = True

        after = []
        for record in records:
            if isinstance(record, MapPointRecord):
                after.append(snapshot_point(record) | {"deleted": getattr(record, "deleted", False)})
            else:
                after.append(snapshot_line(record) | {"deleted": getattr(record, "deleted", False)})

        self.undo_stack.append(BulkEditCommand("Delete selected records", records, before, after))
        self.redo_stack.clear()
        self.render_map(keep_view=True)
        self.side_panel.rebuild_layers()
        self.update_dirty_indicator()
        self.status_label.setText(f"Marked {point_count} point(s) and {line_count} line(s) for deletion.")

    def bulk_recolour_checked_points(self) -> None:
        points = self.side_panel.checked_point_records()
        if not points:
            self.status_label.setText("No checked points to recolour.")
            return
        before = [snapshot_point(point) for point in points]
        new_rgb = (self.side_panel.point_bulk_r.value(), self.side_panel.point_bulk_g.value(), self.side_panel.point_bulk_b.value())
        for point in points:
            point.r, point.g, point.b = new_rgb
            point.dirty = True
            self.update_record_items(point)
        after = [snapshot_point(point) for point in points]
        self.undo_stack.append(BulkEditCommand("Bulk recolour checked points", points, before, after))
        self.redo_stack.clear()
        self.render_map(keep_view=True)
        self.update_dirty_indicator()
        self.status_label.setText(f"Recoloured {len(points)} checked point(s).")

    def bulk_delete_checked_points(self) -> None:
        points = self.side_panel.checked_point_records()
        if not points:
            self.status_label.setText("No checked points to delete.")
            return
        if not self.confirm_bulk_action(
            "Delete Checked Points",
            f"Mark {len(points)} checked point(s) for deletion?",
            len(points),
            action_type="delete",
        ):
            return
        before = [snapshot_point(point) | {"deleted": getattr(point, "deleted", False)} for point in points]
        for point in points:
            point.deleted = True
            point.dirty = True
        after = [snapshot_point(point) | {"deleted": getattr(point, "deleted", False)} for point in points]
        self.undo_stack.append(BulkEditCommand("Bulk delete checked points", points, before, after))
        self.redo_stack.clear()
        self.render_map(keep_view=True)
        self.side_panel.rebuild_layers()
        self.update_dirty_indicator()
        self.status_label.setText(f"Marked {len(points)} point(s) for deletion. Save Edits will remove them.")

    def choose_map_folder(self) -> None:
        start_dir = getattr(self, "map_folder", "") or (str(self.loaded_files[0].parent) if self.loaded_files else "")
        folder = QFileDialog.getExistingDirectory(self, "Choose EQ Maps Folder", start_dir)
        if not folder:
            return
        self.map_folder = folder
        self.side_panel.map_folder_edit.setText(folder)
        self.rebuild_zone_list()
        self.save_settings()

    def available_zone_shortnames(self) -> list[str]:
        folder = getattr(self, "map_folder", "") or self.side_panel.map_folder_edit.text().strip()
        if not folder:
            return []
        path = Path(folder)
        if not path.exists() or not path.is_dir():
            return []

        shortnames = set()
        for file_path in path.glob("*.txt"):
            stem = file_path.stem
            shortname = stem.split("_", 1)[0]
            if shortname:
                shortnames.add(shortname.lower())
        return sorted(shortnames)

    def zone_display_name(self, shortname: str) -> str:
        full = ZONE_SHORTNAME_TO_FULLNAME.get(shortname.lower(), shortname)
        return f"{full} ({shortname})"

    def zone_files_for_shortname(self, shortname: str) -> list[Path]:
        folder = Path(getattr(self, "map_folder", "") or self.side_panel.map_folder_edit.text().strip())
        if not folder.exists():
            return []
        files = []
        base = folder / f"{shortname}.txt"
        if base.exists():
            files.append(base)
        for idx in range(1, 5):
            layer = folder / f"{shortname}_{idx}.txt"
            if layer.exists():
                files.append(layer)
        # Include any other matching layers without duplicate.
        for file_path in sorted(folder.glob(f"{shortname}_*.txt")):
            if file_path not in files:
                files.append(file_path)
        return files

    def rebuild_zone_list(self) -> None:
        if not hasattr(self.side_panel, "zones_list"):
            return
        search = self.side_panel.zone_search_edit.text().strip().lower()
        self.side_panel.zones_list.clear()

        for shortname in self.available_zone_shortnames():
            display = self.zone_display_name(shortname)
            if search and search not in display.lower() and search not in shortname.lower():
                continue
            item = QListWidgetItem(display)
            item.setData(Qt.UserRole, shortname)
            self.side_panel.zones_list.addItem(item)

        self.status_label.setText(f"Found {self.side_panel.zones_list.count()} zone(s) in map folder.")

    def reset_zone_search(self) -> None:
        self.side_panel.zone_search_edit.clear()
        self.rebuild_zone_list()

    def open_selected_zone(self) -> None:
        item = self.side_panel.zones_list.currentItem()
        if item is None:
            return
        shortname = item.data(Qt.UserRole)
        files = self.zone_files_for_shortname(shortname)
        if not files:
            QMessageBox.warning(self, "No Map Files", f"No map files found for {shortname}.")
            return
        if not self.confirm_discard_unsaved():
            return
        self.load_files(files)
        self.status_label.setText(f"Opened {self.zone_display_name(shortname)}.")

    def toggle_sidebar(self) -> None:
        if not hasattr(self, "splitter"):
            return
        sizes = self.splitter.sizes()
        if len(sizes) < 2:
            return
        total = max(sum(sizes), 1)
        if sizes[1] < 80:
            self.splitter.setSizes([max(total - 360, 200), 360])
        else:
            self.splitter.setSizes([total, 0])
        self.save_settings()

    def confirm_exit(self) -> None:
        self.save_settings()
        self.close()

    def add_undo(self, label: str, record: Any, before: dict[str, Any], after: dict[str, Any]) -> None:
        if before == after:
            return
        self.undo_stack.append(UndoCommand(label, record, before.copy(), after.copy()))
        self.redo_stack.clear()
        if len(self.undo_stack) > 100:
            self.undo_stack.pop(0)
        self.update_dirty_indicator()

    def undo(self) -> None:
        if not self.undo_stack:
            self.status_label.setText("Nothing to undo.")
            return
        command = self.undo_stack.pop()
        command.undo()
        self.redo_stack.append(command)
        if hasattr(command, "record") and command.record in (self.loaded_map.lines + self.loaded_map.points):
            self.update_record_items(command.record)
            self.side_panel.set_record(command.record)
        self.status_label.setText(f"Undo: {command.label}")

    def redo(self) -> None:
        if not self.redo_stack:
            self.status_label.setText("Nothing to redo.")
            return
        command = self.redo_stack.pop()
        command.redo()
        self.undo_stack.append(command)
        if hasattr(command, "record") and command.record in (self.loaded_map.lines + self.loaded_map.points):
            self.update_record_items(command.record)
            self.side_panel.set_record(command.record)
        self.status_label.setText(f"Redo: {command.label}")

    def dirty_records(self) -> list[Any]:
        return [record for record in self.loaded_map.lines + self.loaded_map.points if record.dirty]

    def dirty_files(self) -> list[Path]:
        return sorted({record.file_path for record in self.dirty_records()})

    def update_dirty_indicator(self) -> None:
        if hasattr(self, "side_panel"):
            try:
                self.side_panel.rebuild_colour_list()
                self.side_panel.rebuild_points_list()
                self.side_panel.rebuild_pending_changes()
            except Exception:
                pass
        dirty_files = self.dirty_files()
        if dirty_files:
            names = ", ".join(path.name for path in dirty_files)
            self.dirty_label.setText(f"Unsaved: {names}")
            self.setWindowTitle(f"EQ Map Editor {VERSION} *")
        else:
            self.dirty_label.setText("Clean")
            self.setWindowTitle(f"EQ Map Editor {VERSION}")

    def save_edits(self) -> None:
        dirty_records = self.dirty_records()
        if not dirty_records:
            QMessageBox.information(self, "No Changes", "There are no edited records to save.")
            return

        by_file: dict[Path, list[Any]] = {}
        for record in dirty_records:
            by_file.setdefault(record.file_path, []).append(record)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_files: list[str] = []

        try:
            for file_path, records in by_file.items():
                original_lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines() if file_path.exists() else []
                backup_path = BACKUPS_DIR / f"{file_path.name}.{timestamp}.bak"
                if file_path.exists():
                    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, backup_path)

                append_records = []
                for record in records:
                    if record.line_index < 0:
                        append_records.append(record)
                        continue
                    if record.line_index >= len(original_lines):
                        raise IndexError(f"Line index out of range for {record.file_path.name}:{record.line_index + 1}")
                    if getattr(record, "deleted", False):
                        original_lines[record.line_index] = None
                    else:
                        original_lines[record.line_index] = record.to_map_line()

                original_lines = [line for line in original_lines if line is not None]

                for record in append_records:
                    if getattr(record, "deleted", False):
                        continue
                    record.line_index = len(original_lines)
                    original_lines.append(record.to_map_line())

                file_path.write_text("\n".join(original_lines) + "\n", encoding="utf-8")
                saved_files.append(f"{file_path.name} (backup: {backup_path.name if backup_path.exists() else 'none'})")

            for record in dirty_records:
                record.dirty = False
                record.raw_text = "" if getattr(record, "deleted", False) else record.to_map_line()

            self.loaded_map.lines = [record for record in self.loaded_map.lines if not getattr(record, "deleted", False)]
            self.loaded_map.points = [record for record in self.loaded_map.points if not getattr(record, "deleted", False)]

        except Exception as exc:
            QMessageBox.critical(self, "Save Error", f"Could not save edits:\n{exc}")
            return

        self.undo_stack.clear()
        self.redo_stack.clear()
        self.side_panel.rebuild_layers()
        self.side_panel.rebuild_pending_changes()
        self.update_dirty_indicator()
        self.log_event(f"Saved {len(dirty_records)} edited record(s): " + ", ".join(saved_files))
        QMessageBox.information(self, "Saved", "Saved edits:\n\n" + "\n".join(saved_files))
        self.status_label.setText(f"Saved {len(dirty_records)} edited record(s).")

    def confirm_discard_unsaved(self) -> bool:
        if not self.dirty_records():
            return True

        result = QMessageBox.question(
            self,
            "Unsaved Changes",
            "You have unsaved map edits. Continue and discard them?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        return result == QMessageBox.Yes

    def reload_from_disk(self) -> None:
        if not self.loaded_files:
            return
        if not self.confirm_discard_unsaved():
            return
        self.load_files(self.loaded_files)

    def restore_from_backup(self) -> None:
        if not self.loaded_files:
            QMessageBox.information(self, "No Files", "Open a map file before restoring from backup.")
            return
        if not self.confirm_discard_unsaved():
            return

        backup_name, _ = QFileDialog.getOpenFileName(
            self,
            "Choose Backup File to Restore",
            str(BACKUPS_DIR),
            "Backup files (*.bak);;All files (*.*)",
        )
        if not backup_name:
            return

        backup_path = Path(backup_name)

        target_candidates = []
        backup_name_text = backup_path.name
        for source in self.loaded_files:
            if backup_name_text.startswith(source.name + ".") or backup_name_text == source.name + ".bak":
                target_candidates.append(source)

        if len(target_candidates) == 1:
            target_path = target_candidates[0]
        else:
            target_name, _ = QFileDialog.getOpenFileName(
                self,
                "Choose Source File to Overwrite with Backup",
                str(backup_path.parent),
                "Text files (*.txt);;All files (*.*)",
            )
            if not target_name:
                return
            target_path = Path(target_name)

        result = QMessageBox.question(
            self,
            "Restore Backup",
            f"Restore:\n{backup_path.name}\n\nover:\n{target_path.name}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if result != QMessageBox.Yes:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pre_restore_backup = BACKUPS_DIR / f"{target_path.name}.pre_restore_{timestamp}.bak"
        BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target_path, pre_restore_backup)
        shutil.copy2(backup_path, target_path)

        QMessageBox.information(
            self,
            "Restored",
            f"Restored {backup_path.name} over {target_path.name}.\n\n"
            f"Previous current file was backed up as:\n{pre_restore_backup.name}",
        )
        self.reload_from_disk()

    def run_deferred_startup_fit(self) -> None:
        if self._fit_last_map_after_show:
            self._fit_last_map_after_show = False
            self.fit_map()
            self.status_label.setText("Restored last loaded map files and fit map to screen.")

    def showEvent(self, event) -> None:
        super().showEvent(event)
        if self._fit_last_map_after_show:
            QTimer.singleShot(0, self.run_deferred_startup_fit)
            QTimer.singleShot(150, self.run_deferred_startup_fit)

    def closeEvent(self, event) -> None:
        if self.dirty_records():
            result = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved map edits. Close anyway?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if result != QMessageBox.Yes:
                event.ignore()
                return
        if self.autosave_settings_on_exit:
            self.save_settings()
        event.accept()


def expand_input_paths(paths: list[str]) -> list[Path]:
    expanded: list[Path] = []
    for raw_path in paths:
        path = Path(raw_path)
        if path.is_dir():
            expanded.extend(sorted(path.glob("*.txt")))
        else:
            expanded.append(path)
    return expanded


def install_exception_hook() -> None:
    def handle_exception(exc_type, exc_value, exc_traceback):
        try:
            LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with LOG_PATH.open("a", encoding="utf-8") as log_file:
                log_file.write("\n--- Unhandled exception ---\n")
                traceback.print_exception(exc_type, exc_value, exc_traceback, file=log_file)
        except Exception:
            pass

        try:
            QMessageBox.critical(
                None,
                "EQ Map Editor Error",
                f"An unexpected error occurred:\n\n{exc_value}\n\nA log was written to:\n{LOG_PATH}",
            )
        except Exception:
            pass

        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    sys.excepthook = handle_exception


def main() -> int:
    parser = argparse.ArgumentParser(description=f"EQ Map Editor {VERSION}")
    parser.add_argument("paths", nargs="*", help="One or more EQ map .txt files, or a folder containing .txt files.")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    install_exception_hook()
    initial_files = expand_input_paths(args.paths) if args.paths else []
    window = EqMapMainWindow(initial_files=initial_files)
    window.resize(1650, 950)
    window.show()
    QTimer.singleShot(0, window.run_deferred_startup_fit)
    QTimer.singleShot(250, window.run_deferred_startup_fit)
    QTimer.singleShot(350, window.maybe_show_startup_warning)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
