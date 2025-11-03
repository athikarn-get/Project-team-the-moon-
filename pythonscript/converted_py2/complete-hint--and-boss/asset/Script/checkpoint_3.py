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
class Checkpoint_3(Area2D):
    def __init__(self):
        super().__init__()

    def _ready(self) -> None:
        pass

    signal checkpoint_reached(position: Vector2)


    def _ready(self):
    	connect("body_entered", Callable(self, "_on_body_entered"))


    def _on_body_entered(self, body):
    	if body.name == "Player":
    		emit_signal("checkpoint_reached", global_position)
