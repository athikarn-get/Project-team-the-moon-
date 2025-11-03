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
class Checkpoint_Manager(Node):
    def __init__(self):
        super().__init__()
        self.current_checkpoint_position = Vector2.ZERO
        self.player = get_parent().get_node("Player")

    def _ready(self) -> None:
        pass



    def _ready(self):
    	if player:
    		current_checkpoint_position = player.global_position
    	for checkpoint in get_children():
    		if checkpoint is Area2D:
    			checkpoint.connect("checkpoint_reached", Callable(self, "_on_checkpoint_reached"))


    def _on_checkpoint_reached(self, position):
    	set_checkpoint(position)




    def set_checkpoint(self, position):
    	current_checkpoint_position = position
    	print("Checkpoint updated to: ", position)


    def get_checkpoint(self):
    	return current_checkpoint_position
