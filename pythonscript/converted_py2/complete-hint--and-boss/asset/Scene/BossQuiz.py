from typing import Optional, Any
try:
    from py4godot import gdclass, signal
    from py4godot.core import *
except Exception:
    from godot import exposed as gdclass, signal
    from godot import *  # type: ignore


@gdclass
class Bossquiz(Node2D):
    def __init__(self):
        super().__init__()
        self.quiz_question: str = ""
        self.quiz_answer: str = ""
        self.blocker_path: Optional[NodePath] = None
        self.show_hint_text: bool = True
        self._player: Optional[Node] = None
        self._in_range: bool = False
        self._done: bool = False
        self._quiz: Optional[Control] = None
        self._area: Optional[Node] = None
        self.boss_label: Optional[Label] = None
        self._hide_timer: Optional[Timer] = None

    def _ready(self) -> None:
        self.boss_label = self.get_node_or_null("bossdialog")
        if self.boss_label:
            self.boss_label.visible = False
        self._area = self.get_node_or_null("InteractArea")
        if self._area:
            if hasattr(self._area, "action_name"):
                self._area.action_name = "talk"
            if hasattr(self._area, "interact"):
                self._area.interact = Callable(self, "_do_open_quiz")
            if hasattr(self._area, "body_entered"):
                self._area.body_entered.connect(self._on_enter)
            if hasattr(self._area, "body_exited"):
                self._area.body_exited.connect(self._on_exit)
        self._ensure_quiz()
        self._hide_timer = Timer.new()
        self._hide_timer.one_shot = True
        self._hide_timer.timeout.connect(self._boss_clear)
        self.add_child(self._hide_timer)

    def _ensure_quiz(self) -> None:
        if self._quiz and is_instance_valid(self._quiz):
            return
        self._quiz = QuizOverlayLite.new()
        layer = get_tree().current_scene.get_node_or_null("CanvasLayer")
        if not layer:
            layer = CanvasLayer.new()
            layer.name = "CanvasLayer"
            layer.layer = 100
            get_tree().current_scene.add_child(layer)
        layer.add_child(self._quiz)
        self._quiz.z_index = 9999
        if hasattr(self._quiz, "answered") and not self._quiz.answered.is_connected(self._on_quiz_answered):
            self._quiz.answered.connect(self._on_quiz_answered)

    def _physics_process(self, _dt: float) -> None:
        if self._in_range and self._quiz and not self._quiz.visible and Input.is_action_just_pressed("interact"):
            self._do_open_quiz()

    def _boss_say(self, text: str, auto_hide_sec: float = -1.0) -> None:
        if not self.boss_label:
            return
        self.boss_label.text = text or ""
        self.boss_label.visible = True
        if auto_hide_sec > 0.0 and self._hide_timer:
            self._hide_timer.stop()
            self._hide_timer.start(auto_hide_sec)

    def _boss_clear(self) -> None:
        if self.boss_label:
            self.boss_label.text = ""
            self.boss_label.visible = False

    def _on_enter(self, body: Node) -> None:
        if hasattr(body, "is_in_group") and body.is_in_group("player"):
            self._player = body
            self._in_range = True
            if self.show_hint_text:
                if self._done:
                    self._boss_say("ไปต่อได้แล้ว...", 2.0)
                else:
                    self._boss_say("กด [E] เพื่อคุยกับบอส...", 2.0)

    def _on_exit(self, body: Node) -> None:
        if body == self._player:
            self._in_range = False
            self._player = None
            self._boss_clear()

    def _do_open_quiz(self) -> None:
        if self._done or not self._in_range or not self._player:
            return
        self._ensure_quiz()
        if not self._quiz or self._quiz.visible:
            return
        self._boss_clear()
        if self._player and hasattr(self._player, "set_movement_locked"):
            self._player.set_movement_locked(True)
        q = self.quiz_question or ""
        a = self.quiz_answer or ""
        if hasattr(self._quiz, "ask"):
            self._quiz.ask(q, a)

    def _on_quiz_answered(self, correct: bool, _given: str) -> None:
        if self._player and hasattr(self._player, "set_movement_locked"):
            self._player.set_movement_locked(False)
        if self._quiz and is_instance_valid(self._quiz):
            self._quiz.hide()
        if correct:
            self._done = True
            freed = False
            if isinstance(self.blocker_path, NodePath) and str(self.blocker_path) != "":
                wall = get_tree().current_scene.get_node_or_null(self.blocker_path)
                if wall:
                    wall.queue_free()
                    freed = True
            if not freed:
                auto_wall = get_tree().current_scene.get_node_or_null("Wall")
                if auto_wall:
                    auto_wall.queue_free()
            self._boss_say("ถูกต้อง! ทางข้างหน้าถูกเปิดแล้ว...", 2.0)
        else:
            self._boss_say("ยังไม่ถูก ลองใหม่นะ...", 2.0)
