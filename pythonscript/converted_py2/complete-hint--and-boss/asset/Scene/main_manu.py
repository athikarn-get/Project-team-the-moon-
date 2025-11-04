from typing import Optional, Any
try:
    from py4godot import gdclass, signal
    from py4godot.core import *
except Exception:
    from godot import exposed as gdclass, signal
    from godot import *  # type: ignore


@gdclass
class MainMenu(Control):
    def __init__(self):
        super().__init__()
        self.start_button: Optional[Button] = None
        self.scene_path: String = "res://main.tscn"

    def _ready(self) -> None:
        self.start_button = self.get_node_or_null("StartButton")
        if self.start_button:
            self.start_button.pressed.connect(self._on_start_pressed)

    def _on_start_pressed(self) -> None:
        get_tree().change_scene_to_file(self.scene_path)
