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
class Popupui(PopupPanel):
    def __init__(self):
        super().__init__()
        self.label: Any = None  # onready; set in _ready
        self.close_button: Any = None  # onready; set in _ready
        self.color_rect: Any = None  # onready; set in _ready

    def _ready(self) -> None:
        self.label = self.get_node(\"\1\")
        self.close_button = self.get_node(\"\1\")
        self.color_rect = get_node_or_null("../ColorRect")  # now linked to ColorRect



    def _ready(self):
    	add_to_group("ui")
    	close_button.pressed.connect(_on_close_pressed)
    	hide()
    	if color_rect:
    		color_rect.visible = False


    def show_popup(self, title, desc):
    	label.bbcode_enabled = True
    	label.text = "[b]" + title + "[/b]\n" + desc
    	popup_centered()
    	show()
    	if color_rect:
    		color_rect.visible = True


    def _on_close_pressed(self):
    	hide()
    	if color_rect:
    		color_rect.visible = False
