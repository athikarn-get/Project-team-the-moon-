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
class Dialogmanager(Node2D):
    def __init__(self):
        super().__init__()
        self.area: Any = None  # onready; set in _ready
        self.interact_label: Any = None  # onready; set in _ready
        self.textbox_scene = None  # @export
        self.in_range = None
        self.player =  None
        self.textbox_instance =  None

    def _ready(self) -> None:
        self.area = self.get_node(\"\1\")
        self.interact_label = self.get_node(\"\1\")




    def _ready(self):
    	if not area:
    		push_error("No Area2D found (parent of CollisionShape2D). Make sure CollisionShape2D is under an Area2D.")
    		return

    	interact_label.visible = False

    	if not area.is_connected("body_entered", Callable(self, "_on_enter")):
    		area.body_entered.connect(_on_enter)
    	if not area.is_connected("body_exited", Callable(self, "_on_exit")):
    		area.body_exited.connect(_on_exit)


    def _on_enter(self, body):
    	if _is_player(body):
    		in_range = True
    		player = body
    		interact_label.text = "Press [E]"
    		interact_label.visible = True


    def _on_exit(self, body):
    	if body == player:
    		in_range = False
    		player = None
    		interact_label.visible = False


    def _unhandled_input(self, event):
    	if in_range and player and event.is_action_pressed("interact"):
    		_run_textbox()


    def _run_textbox(self):
    	if not textbox_scene:
    		push_error("Assign the textbox_scene in the Inspector.")
    		return

    	textbox_instance = textbox_scene.instantiate()
    	get_tree().root.add_child(textbox_instance)

    	if textbox_instance.has_method("set_anchor_world_pos"):
    		textbox_instance.set_anchor_world_pos(player.global_position)

    	if player and player.has_method("set_movement_locked"):
    		player.set_movement_locked(True)

    	interact_label.visible = False

    	if textbox_instance.has_signal("finished"):
    		textbox_instance.finished.connect(func ():
    			if player and player.has_method("set_movement_locked"):
    				player.set_movement_locked(False)
    			if is_instance_valid(textbox_instance):
    				textbox_instance.queue_free()
    			textbox_instance = None
    			if in_range:
    				interact_label.visible = True
    		)

    	if textbox_instance.has_method("queue_text"):
    		textbox_instance.queue_text("You found a chest!")
    		textbox_instance.queue_text("It creaks open slowly...")
    		textbox_instance.queue_text("Inside... just dust.")
    	if textbox_instance.has_method("display_text"):
    		textbox_instance.display_text()


    def _is_player(self, body):
    	return body != None and (body.is_in_group("player") or body.name == "Player")
