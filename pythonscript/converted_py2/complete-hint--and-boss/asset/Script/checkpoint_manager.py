from typing import Optional, Any
try:
	from py4godot import gdclass, signal
	from py4godot.core import *
except Exception:
	from godot import exposed as gdclass, signal
	from godot import *  # type: ignore


@gdclass
class Checkpoint_Manager(Node):
	def __init__(self):
		super().__init__()
		self.current_checkpoint_position = Vector2.ZERO
		self.player = None

	def _ready(self) -> None:
		self.player = self.get_parent().get_node("Player")
		if self.player:
			self.current_checkpoint_position = self.player.global_position
		for checkpoint in self.get_children():
			if isinstance(checkpoint, Area2D):
				checkpoint.connect("checkpoint_reached", Callable(self, "_on_checkpoint_reached"))

	def _on_checkpoint_reached(self, position):
		self.set_checkpoint(position)

	def set_checkpoint(self, position):
		self.current_checkpoint_position = position
		print("Checkpoint updated to:", position)

	def get_checkpoint(self):
		return self.current_checkpoint_position
