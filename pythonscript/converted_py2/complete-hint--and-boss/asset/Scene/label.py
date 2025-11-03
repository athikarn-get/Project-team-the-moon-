# --- Godot Python bridge imports (py4godot primary) ---
from typing import Optional, Any

try:
    # py4godot (Godot 4.x Pluginscript)
    from py4godot import gdclass, signal
    from py4godot.core import *  # import all core Godot classes (Node2D, AcceptDialog, Area2D, Label, Button, etc.)
except Exception:
    # Fallback: godot-python (experimental for Godot 4, signatures may differ)
    from godot import exposed as gdclass, signal
    from godot import *  # type: ignore

@gdclass
class Label(Node):
    def __init__(self):
        super().__init__()
        self.label: Any = None  # onready; set in _ready
        self.f = None

    def _ready(self) -> None:
        self.label = self.get_node(\"\1\")


    def _ready(self):
    	f.load("res://fonts/Kanit-Regular.ttf") # ใส่พาธฟอนต์ของมีน
    	label.add_theme_font_override("font", f)
    	label.add_theme_color_override("font_outline_color", Color.BLACK)
    	label.add_theme_constant_override("outline_size", 3)
    	label.add_theme_font_size_override("font_size", 32) # Godot 4.x
