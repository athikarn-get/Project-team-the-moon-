# เชื่อม Godot ↔ Python (ใช้ py4godot เป็นหลัก)
from typing import Optional, Any
try:
    from py4godot import gdclass, signal
    from py4godot.core import *
except Exception:
    from godot import exposed as gdclass, signal
    from godot import *  # type: ignore


@gdclass
class Boss_3(Node2D):
    def __init__(self):
        super().__init__()
        self.quiz_question: str = "พิมพ์ฟังก์ชันที่ใช้แสดงผลใน Python"
        self.quiz_answer: str = "print()"
        self.blocker_path: str = "../Wall3"
        self.show_hint_text: bool = True

        self._player: Optional[Node] = None
        self._in_range: bool = False
        self._done: bool = False

        self.boss_label: Optional[Label] = None
        self._area: Optional[Area2D] = None
        self._quiz: Optional[Node] = None
        self._layer: Optional[CanvasLayer] = None

        self._dialog: Optional[AcceptDialog] = None
        self._line: Optional[LineEdit] = None

    def _ready(self) -> None:
        self.boss_label = self.get_node_or_null("bossdialog3")
        if self.boss_label:
            self.boss_label.visible = False

        self._area = self.get_node_or_null("InteractArea")
        if self._area:
            self._area.body_entered.connect(self._on_enter)
            self._area.body_exited.connect(self._on_exit)
            if hasattr(self._area, "action_name"):
                self._area.action_name = "talk"
            if hasattr(self._area, "interact"):
                self._area.interact = Callable(self, "_do_open_quiz")

        self._quiz = self._try_attach_quiz_overlay()
        if not self._quiz:
            self._build_fallback_dialog()

    def _physics_process(self, _dt: float) -> None:
        if self._done or not self._in_range:
            return
        if Input.is_action_just_pressed("interact") or Input.is_action_just_pressed("ui_accept"):
            if not self._is_quiz_visible():
                self._do_open_quiz()

    # ---------- UI helpers ----------
    def _ensure_layer(self) -> CanvasLayer:
        if self._layer and is_instance_valid(self._layer):
            return self._layer
        self._layer = CanvasLayer.new()
        self._layer.layer = 100
        self.add_child(self._layer)
        return self._layer

    def _try_attach_quiz_overlay(self) -> Optional[Node]:
        try:
            overlay_cls = globals().get("QuizOverlayLite", None)
            if overlay_cls is None:
                return None
            q = overlay_cls.new()
            self._ensure_layer().add_child(q)
            q.z_index = 9999
            if hasattr(q, "answered"):
                q.answered.connect(self._on_quiz_answered)
            return q
        except Exception as e:
            push_warning(f"[Boss_3] แนบ QuizOverlayLite ไม่สำเร็จ: {e}")
            return None

    def _build_fallback_dialog(self) -> None:
        d = AcceptDialog.new()
        d.title = "ตอบคำถาม"
        self._ensure_layer().add_child(d)

        box = VBoxContainer.new()
        box.set_anchors_preset(Control.PRESET_FULL_RECT)
        box.offset_left = 14
        box.offset_top = 12
        box.offset_right = -14
        box.offset_bottom = -12
        d.add_child(box)

        lbl = Label.new()
        lbl.text = self.quiz_question
        lbl.autowrap_mode = TextServer.AUTOWRAP_WORD
        box.add_child(lbl)

        self._line = LineEdit.new()
        self._line.placeholder_text = "พิมพ์คำตอบ เช่น print()"
        # ⬇ เพิ่ม Enter-submit
        self._line.text_submitted.connect(lambda _t: self._on_dialog_confirmed())
        box.add_child(self._line)

        d.confirmed.connect(self._on_dialog_confirmed)
        self._dialog = d

    def _is_quiz_visible(self) -> bool:
        try:
            if self._quiz and is_instance_valid(self._quiz) and hasattr(self._quiz, "visible"):
                return bool(self._quiz.visible)
        except Exception:
            pass
        if self._dialog and is_instance_valid(self._dialog):
            return self._dialog.visible
        return False

    # ---------- Range triggers ----------
    def _on_enter(self, body: Node) -> None:
        if not body or not hasattr(body, "is_in_group"):
            return
        if body.is_in_group("player"):
            self._player = body
            self._in_range = True
            if self.show_hint_text:
                if self._done:
                    self._boss_say("ผ่านแล้ว ไปต่อได้เลย", auto_hide_sec=2.0)
                else:
                    self._boss_say("กด [E] เพื่อเริ่มทำโจทย์")

    def _on_exit(self, body: Node) -> None:
        if body == self._player:
            self._in_range = False
            self._player = None
            self._boss_clear()
            # ปิดกล่องเมื่อออกระยะ
            if self._dialog and self._dialog.visible:
                self._dialog.hide()
            if self._quiz and hasattr(self._quiz, "hide"):
                self._quiz.hide()
            # ปลดล็อกการเดินเผื่อยังล็อกค้าง
            if self._player and self._player.has_method("set_movement_locked"):
                self._player.set_movement_locked(False)

    # ---------- Quiz flow ----------
    def _do_open_quiz(self) -> None:
        if self._done or not self._in_range:
            return

        # ล็อกการเดิน (ถ้าผู้เล่นรองรับ)
        if self._player and self._player.has_method("set_movement_locked"):
            self._player.set_movement_locked(True)

        self._boss_clear()

        if self._quiz and hasattr(self._quiz, "ask"):
            try:
                self._quiz.ask(self.quiz_question, self.quiz_answer)
                return
            except Exception as e:
                push_warning(f"[Boss_3] เรียก QuizOverlayLite.ask ล้มเหลว: {e}")

        if self._dialog and self._line:
            self._line.text = ""
            self._dialog.popup_centered()
            # ⬇ โฟกัสช่องตอบทันที
            self._line.grab_focus()

    def _on_dialog_confirmed(self) -> None:
        if self._done:
            return
        ans = (self._line.text if self._line else "").strip()
        is_correct = self._is_answer_correct(ans)
        self._on_quiz_answered(is_correct, ans)

    def _is_answer_correct(self, ans: str) -> bool:
        if ans == self.quiz_answer:
            return True
        a = ans.replace(" ", "").lower()
        b = self.quiz_answer.replace(" ", "").lower()
        return a == b

    def _on_quiz_answered(self, correct: bool, *_unused) -> None:
        # ซ่อน overlay ถ้ามี
        try:
            if self._quiz and is_instance_valid(self._quiz) and hasattr(self._quiz, "hide"):
                self._quiz.hide()
        except Exception:
            pass

        # ปลดล็อกการเดิน
        if self._player and self._player.has_method("set_movement_locked"):
            self._player.set_movement_locked(False)

        if correct:
            self._done = True
            self._boss_say("ถูกต้อง! ไปต่อได้", auto_hide_sec=2.0)
            self._unlock_blocker()
            if self._dialog and self._dialog.visible:
                self._dialog.hide()
        else:
            self._boss_say("ยังไม่ถูก ลองใหม่อีกครั้ง")

    def _unlock_blocker(self) -> None:
        if not self.blocker_path:
            return
        node = self.get_node_or_null(self.blocker_path)
        if node:
            node.queue_free()
        else:
            push_warning(f"[Boss_3] หา blocker ที่ '{self.blocker_path}' ไม่พบ")

    # ---------- Boss label ----------
    def _boss_say(self, text: str, auto_hide_sec: float = -1.0) -> None:
        if not self.boss_label:
            return
        self.boss_label.text = text
        self.boss_label.visible = True
        if auto_hide_sec > 0.0:
            self._hide_label_later(auto_hide_sec)

    def _boss_clear(self) -> None:
        if self.boss_label:
            self.boss_label.text = ""
            self.boss_label.visible = False

    def _hide_label_later(self, sec: float) -> None:
        t = Timer.new()
        t.one_shot = True
        t.wait_time = max(0.01, sec)
        self.add_child(t)
        t.timeout.connect(self._boss_clear)
        t.start()
