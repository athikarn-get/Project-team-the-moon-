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
class InteractArea(Area2D):
    def __init__(self):
        super().__init__()
        self.action_name = "interact"  # @export
        self.interact = Callable()
        self._manager: Any = None  # onready; set in _ready
        self.idx = _manager.active_areas.find(self)  # ✅ ระบุชนิด int ให้ชัดเจน

    def _ready(self) -> None:
        self._manager = get_tree().current_scene.get_node_or_null("InteractionManager")




    def _ready(self):
    	# เปิดการตรวจจับชน
    	monitoring = True
    	monitorable = True

    	# เชื่อมสัญญาณเข้าฟังก์ชัน
    	body_entered.connect(_on_body_entered)
    	body_exited.connect(_on_body_exited)


    def _on_body_entered(self, body):
    	# เมื่อ Player เดินเข้ามาในพื้นที่ Interact
    	if body.is_in_group("player") and _manager:
    		if not _manager.active_areas.has(self):
    			_manager.active_areas.append(self)


    def _on_body_exited(self, body):
    	# เมื่อ Player เดินออกจากพื้นที่ Interact
    	if body.is_in_group("player") and _manager:
    		if idx != -1:
    			_manager.active_areas.remove_at(idx)
