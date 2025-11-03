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
class Interactionmanager(Node2D):
    def __init__(self):
        super().__init__()
        self.player: Any = None  # onready; set in _ready
        self.label: Any = None  # onready; set in _ready
        self.active_areas = []
        self.can_interact =  True
        self.a = active_areas[0]
        self.d1 = player.global_position.distance_to(a1.global_position)
        self.d2 = player.global_position.distance_to(a2.global_position)
        self.target = active_areas[0]

    def _ready(self) -> None:
        self.player = get_tree().get_first_node_in_group("player")
        self.label = self.get_node(\"\1\")


    const base_text = "[E] to "



    def _process(self, _delta):
    	if active_areas.size() > 0 and can_interact:
    		active_areas.sort_custom(_sort_by_distance_to_player)
    		label.text = base_text + a.action_name
    		label.global_position = a.global_position
    		label.global_position.y -= 36
    		label.global_position.x -= label.size.x / 2
    		label.show()
    	else:
    		label.hide()


    def _sort_by_distance_to_player(self, a1, a2):
    	return d1 < d2


    def _input(self, event):
    	if event.is_action_pressed("interact") and can_interact:
    		if active_areas.size() > 0:
    			can_interact = False
    			label.hide()
    			if target.interact.is_valid():
    # TODO: convert awaiting: 				await target.interact.call()
    			can_interact = True
