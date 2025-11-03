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
class Hint_Test(Node2D):
    def __init__(self):
        super().__init__()
        self.interaction_area: Any = None  # onready; set in _ready
        self.sprite: Any = None  # onready; set in _ready

    def _ready(self) -> None:
        self.interaction_area = self.get_node(\"\1\")
        self.sprite = self.get_node(\"\1\")


    const lines: Array[String] = [
    	"Oat love tangmo"
    ]


    def _ready(self):
    	interaction_area.interact = Callable(self, "_on_interact")


    def _on_interact(self):
    	DialogManager.start_dialog(global_position, lines)
    	sprite.flip_h = True if interaction_area.get_overlapping_bodies()[0].global_position.x < global_position.x else False
    # TODO: convert awaiting: 	await DialogManager.dialog_finished

    def _unhandled_input(self, event):
    	if event.is_action_pressed("interact"):
    		DialogManager.start_dialog(global_position, lines)
