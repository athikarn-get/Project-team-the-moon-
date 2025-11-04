from typing import Optional, Any
try:
    from py4godot import gdclass, signal
    from py4godot.core import *
except Exception:
    from godot import exposed as gdclass, signal
    from godot import *  # type: ignore


@gdclass
class InteractArea(Area2D):
    def __init__(self):
        super().__init__()
        self.action_name: str = "interact"
        self.interact: Optional[Callable] = None
        self._manager: Optional[Node] = None

    def _ready(self) -> None:
        self._manager = get_tree().current_scene.get_node_or_null("InteractionManager")
        self.monitoring = True
        self.monitorable = True
        self.body_entered.connect(self._on_body_entered)
        self.body_exited.connect(self._on_body_exited)

    def _on_body_entered(self, body: Node) -> None:
        if not self._manager or not hasattr(self._manager, "active_areas"):
            return
        if hasattr(body, "is_in_group") and body.is_in_group("player"):
            arr = self._manager.active_areas
            if self not in arr:
                arr.append(self)

    def _on_body_exited(self, body: Node) -> None:
        if not self._manager or not hasattr(self._manager, "active_areas"):
            return
        if hasattr(body, "is_in_group") and body.is_in_group("player"):
            arr = self._manager.active_areas
            if self in arr:
                arr.erase(self) if hasattr(arr, "erase") else arr.remove(self)
