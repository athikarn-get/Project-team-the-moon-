from typing import Optional, Any
try:
	from py4godot import gdclass, signal
	from py4godot.core import *
except Exception:
	from godot import exposed as gdclass, signal
	from godot import *  # type: ignore


@gdclass
class Death_Zone(Area2D):
	def __init__(self):
		super().__init__()
		self.player = None
		self.checkpoint_manager = None

	def _ready(self) -> None:
		self.player = self.get_parent().get_node("Player")
		self.checkpoint_manager = self.get_parent().get_node("CheckpointManager")
		self.body_entered.connect(self._on_body_entered)

	def _on_body_entered(self, body: Node) -> None:
		if body == self.player and self.checkpoint_manager:
			respawn_pos = self.checkpoint_manager.get_checkpoint()
			self.player.global_position = respawn_pos
			print("Player respawned at checkpoint:", respawn_pos)
