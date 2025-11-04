from typing import Optional, Any
try:
	from py4godot import gdclass, signal
	from py4godot.core import *
except Exception:
	from godot import exposed as gdclass, signal
	from godot import *  # type: ignore


@gdclass
class Item(Area2D):
	def __init__(self):
		super().__init__()
		self.object_name: str = "chest"
		self.description: str = "hint"
		self.player_in_range: bool = False

	def _ready(self) -> None:
		self.body_entered.connect(self._on_body_entered)
		self.body_exited.connect(self._on_body_exited)

	def _on_body_entered(self, body: Node) -> None:
		if hasattr(body, "is_in_group") and body.is_in_group("player"):
			self.player_in_range = True

	def _on_body_exited(self, body: Node) -> None:
		if hasattr(body, "is_in_group") and body.is_in_group("player"):
			self.player_in_range = False

	def _process(self, _delta: float) -> None:
		if self.player_in_range and Input.is_action_just_pressed("interact"):
			get_tree().call_group("ui", "show_popup", self.object_name, self.description)
