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
class Item(Area2D):
    def __init__(self):
        super().__init__()
        self.object_name = "chest"  # @export
        self.description = "hint"  # @export
        self.player_in_range =  False

    def _ready(self) -> None:
        pass



    def _ready(self):
    	connect("body_entered", Callable(self, "_on_body_entered"))
    	connect("body_exited", Callable(self, "_on_body_exited"))


    def _on_body_entered(self, body):
    	if body.name == "Player":
    		player_in_range = True


    def _on_body_exited(self, body):
    	if body.name == "Player":
    		player_in_range = False

    #func _process(delta):
    	#if player_in_range and Input.is_action_just_pressed("interact"):
    		#get_tree().call_group("ui", "show_popup", object_name, description)


    def _process(self, _delta):
    	if player_in_range and Input.is_action_just_pressed("interact"):
    		get_tree().call_group("ui", "show_popup", object_name, description)
