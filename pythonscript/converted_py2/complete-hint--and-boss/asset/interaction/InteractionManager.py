from typing import Optional, Any
try:
    from py4godot import gdclass, signal
    from py4godot.core import *
except Exception:
    from godot import exposed as gdclass, signal
    from godot import *  # type: ignore


@gdclass
class InteractionManager(Node2D):
    def __init__(self):
        super().__init__()
        self.player: Optional[Node] = None
        self.label: Optional[Label] = None
        self.active_areas: list[Any] = []
        self.can_interact: bool = True
        self.target: Optional[Any] = None
        self.base_text: str = "[E] to "

    def _ready(self) -> None:
        self.player = get_tree().get_first_node_in_group("player")
        self.label = self.get_node_or_null("Label")
        if self.label:
            self.label.hide()

    def _process(self, _delta: float) -> None:
        if not (self.player and self.label and self.can_interact and self.active_areas):
            if self.label:
                self.label.hide()
            return
        self.active_areas.sort(
            key=lambda a: a.global_position.distance_to(self.player.global_position)
        )
        self.target = self.active_areas[0]
        action = getattr(self.target, "action_name", "interact")
        self.label.text = self.base_text + action
        pos = self.target.global_position
        self.label.global_position = Vector2(pos.x, pos.y - 36.0)
        if hasattr(self.label, "size"):
            self.label.global_position.x -= self.label.size.x * 0.5
        self.label.show()

    def _input(self, event: InputEvent) -> None:
        if not (self.can_interact and self.target and self.label):
            return
        if event.is_action_pressed("interact"):
            self.can_interact = False
            self.label.hide()
            fn = getattr(self.target, "interact", None)
            if callable(fn):
                try:
                    fn()
                except Exception:
                    pass
            self.can_interact = True
