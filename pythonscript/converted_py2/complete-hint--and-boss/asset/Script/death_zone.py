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
class Death_Zone(Area2D):
    def __init__(self):
        super().__init__()
        self.player = None
        self.checkpoint_manager = None
        self.respawn_pos = checkpoint_manager.get_checkpoint()

    def _ready(self) -> None:
        pass



    def _ready(self):
    # TODO: convert awaiting: 	await get_tree().process_frame
    	player = get_parent().get_node("Player")
    	checkpoint_manager = get_parent().get_node("CheckpointManager")
    	connect("body_entered", Callable(self, "_on_body_entered"))


    def _on_body_entered(self, body):
    	if body == player and checkpoint_manager:
    		player.global_position = respawn_pos
    		print("Player respawned at checkpoint: ", respawn_pos)
