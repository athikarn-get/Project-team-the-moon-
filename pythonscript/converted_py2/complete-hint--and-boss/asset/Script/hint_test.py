from typing import Optional, Any
try:
	from py4godot import gdclass, signal
	from py4godot.core import *
except Exception:
	from godot import exposed as gdclass, signal
	from godot import *  # type: ignore


@gdclass
class Hint_Test(Node2D):
	def __init__(self):
		super().__init__()
		self.interaction_area: Optional[Area2D] = None
		self.sprite: Optional[AnimatedSprite2D] = None
		self.in_range: bool = False
		self.lines = ["Oat love tangmo"]

	def _ready(self) -> None:
		self.interaction_area = self.get_node_or_null("InteractionArea")
		self.sprite = self.get_node_or_null("AnimatedSprite2D")
		if self.interaction_area and hasattr(self.interaction_area, "interact"):
			self.interaction_area.interact = Callable(self, "_on_interact")
		if self.interaction_area:
			self.interaction_area.body_entered.connect(self._on_enter)
			self.interaction_area.body_exited.connect(self._on_exit)

	def _on_enter(self, body: Node) -> None:
		if hasattr(body, "is_in_group") and body.is_in_group("player"):
			self.in_range = True

	def _on_exit(self, body: Node) -> None:
		if hasattr(body, "is_in_group") and body.is_in_group("player"):
			self.in_range = False

	def _on_interact(self) -> None:
		try:
			if "DialogManager" in globals() and hasattr(globals()["DialogManager"], "start_dialog"):
				globals()["DialogManager"].start_dialog(self.global_position, self.lines)
		except Exception:
			pass
		if self.interaction_area and self.sprite:
			bodies = []
			try:
				bodies = self.interaction_area.get_overlapping_bodies()
			except Exception:
				bodies = []
			if bodies:
				px = getattr(bodies[0].global_position, "x", 0.0)
				self.sprite.flip_h = px < self.global_position.x

	def _unhandled_input(self, event: InputEvent) -> None:
		if self.in_range and event.is_action_pressed("interact"):
			self._on_interact()
