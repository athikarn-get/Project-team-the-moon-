from typing import Optional, Any
try:
	from py4godot import gdclass, signal
	from py4godot.core import *
except Exception:
	from godot import exposed as gdclass, signal
	from godot import *  # type: ignore


@gdclass
class Checkpoint_1(Area2D):
	checkpoint_reached = signal()

	def __init__(self):
		super().__init__()

	def _ready(self) -> None:
		self.body_entered.connect(self._on_body_entered)

	def _on_body_entered(self, body: Node) -> None:
		if hasattr(body, "is_in_group") and body.is_in_group("player"):
			self.emit_signal("checkpoint_reached", self.global_position)
