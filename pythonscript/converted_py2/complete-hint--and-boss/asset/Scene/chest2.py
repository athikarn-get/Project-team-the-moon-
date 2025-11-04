from typing import Optional, Any
try:
    from py4godot import gdclass, signal
    from py4godot.core import *
except Exception:
    from godot import exposed as gdclass, signal
    from godot import *  # type: ignore


@gdclass
class Chest2(Node2D):
    def __init__(self):
        super().__init__()
        self.area: Optional[Area2D] = None
        self.interact_label: Optional[Label] = None
        self.textbox_scene: Optional[PackedScene] = None
        self.sprite_closed: Optional[Node2D] = None
        self.sprite_opened: Optional[Node2D] = None
        self.in_range: bool = False
        self.player: Optional[Node] = None
        self.textbox_instance: Optional[Node] = None
        self.chest_opened: bool = False
        self.main: Optional[Node] = None

    def _ready(self) -> None:
        self.area = self.get_node_or_null("InteractionArea")
        self.interact_label = self.get_node_or_null("Label")
        self.sprite_closed = self.get_node_or_null("Sprite2D")
        self.sprite_opened = self.get_node_or_null("Sprite2D2")
        if self.sprite_opened:
            self.sprite_opened.visible = False
        if self.sprite_closed:
            self.sprite_closed.visible = True
        if self.interact_label:
            self.interact_label.visible = False
        if self.area:
            self.area.body_entered.connect(self._on_enter)
            self.area.body_exited.connect(self._on_exit)

    def _on_enter(self, body: Node) -> None:
        if self._is_player(body):
            self.in_range = True
            self.player = body
            if self.interact_label:
                self.interact_label.text = "You already open..." if self.chest_opened else "Press [E]"
                self.interact_label.visible = True

    def _on_exit(self, body: Node) -> None:
        if body == self.player:
            self.in_range = False
            self.player = None
            if self.interact_label:
                self.interact_label.visible = False

    def _unhandled_input(self, event: InputEvent) -> None:
        if self.chest_opened:
            return
        if self.in_range and self.player and event.is_action_pressed("interact"):
            self._run_textbox()

    def _run_textbox(self) -> None:
        if not self.textbox_scene or self.textbox_instance:
            return
        self.textbox_instance = self.textbox_scene.instantiate()
        get_tree().root.add_child(self.textbox_instance)
        if self.textbox_instance and self.player and self.textbox_instance.has_method("set_anchor_world_pos"):
            self.textbox_instance.set_anchor_world_pos(self.player.global_position)
        if self.player and self.player.has_method("set_movement_locked"):
            self.player.set_movement_locked(True)
        if self.interact_label:
            self.interact_label.visible = False
        if self.textbox_instance and self.textbox_instance.has_signal("finished"):
            self.textbox_instance.finished.connect(self._on_textbox_finished)
        if self.textbox_instance and self.textbox_instance.has_method("queue_text"):
            self.textbox_instance.queue_text("You found a chest!")
            self.textbox_instance.queue_text("It creaks open slowly...")
            self.textbox_instance.queue_text("You got a hint!")
        if self.textbox_instance and self.textbox_instance.has_method("display_text"):
            self.textbox_instance.display_text()

    def _on_textbox_finished(self) -> None:
        if self.player and self.player.has_method("set_movement_locked"):
            self.player.set_movement_locked(False)
        if self.textbox_instance and is_instance_valid(self.textbox_instance):
            self.textbox_instance.queue_free()
        self.textbox_instance = None
        self._on_chest_opened_final()

    def _on_chest_opened_final(self) -> None:
        self.chest_opened = True
        if self.sprite_closed:
            self.sprite_closed.visible = False
        if self.sprite_opened:
            self.sprite_opened.visible = True
        if self.interact_label and self.in_range:
            self.interact_label.text = "You already open..."
            self.interact_label.visible = True
        self._notify_main_chest_opened()

    def _is_player(self, body: Optional[Node]) -> bool:
        if not body:
            return False
        if hasattr(body, "is_in_group") and body.is_in_group("player"):
            return True
        return getattr(body, "name", "") == "Player"

    def _notify_main_chest_opened(self) -> None:
        if self.main and self.main.has_method("on_chest_opened_with_hint"):
            self.main.on_chest_opened_with_hint(
                "💡 คำใบ้ข้อที่ 2\n"
                "1) ช่วงยาว “คี่” ใช้ ซ้าย - ขวา, ช่วงยาว “คู่” ใช้ ซ้าย + ขวา\n"
                "2) [2, -3, 4] คือฝั่งซ้ายของการแบ่งใหญ่\n"
                "3) [1, 5] คือฝั่งขวา และจะถูกรวมแบบบวก\n"
                "4) ผลรวมสุดท้ายได้จาก “ฝั่งซ้ายลบฝั่งขวา”\n"
                "5) ค่าที่ได้เป็นจำนวนติดลบเล็ก ๆ\n"
            )
