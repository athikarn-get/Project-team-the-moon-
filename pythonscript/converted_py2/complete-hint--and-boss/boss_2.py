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
class Boss_2(Node2D):
    def __init__(self):
        super().__init__()
        self.quiz_question = None  # @export
        self.quiz_answer = None  # @export
        self.blocker_path = None  # @export
        self.show_hint_text = None  # @export
        self._player =  None
        self._in_range = None
        self._done = None
        self._quiz = QuizOverlayLite.new()
        self._area = None
        self.boss_label: Any = None  # onready; set in _ready
        self.layer = None
        self.wall2 = None
        self.wall = None

    def _ready(self) -> None:
        self.boss_label = self.get_node(\"\1\")   # <<< Label ของบอสตัวที่ 2

    # === Quiz config ==============================================================

    # === Internals ================================================================



    def _ready(self):
    	# --- Label ของบอสให้ซ่อนไว้ก่อน ---
    	if boss_label:
    		boss_label.visible = False
    		# กันกลับหัวเวลาสไปรต์พลิก (ถ้าไม่จำเป็นจะปิดบรรทัดนี้ได้)
    		# boss_label.top_level = True
    	else:
    		push_error("[Boss2] Missing Label node named 'bossdialog2'.")

    	# --- สร้าง Quiz Overlay ---
    	_quiz = QuizOverlayLite.new()
    	if layer:
    		layer.add_child(_quiz)
    	else:
    		get_tree().current_scene.add_child(_quiz)
    	_quiz.z_index = 9999
    	_quiz.answered.connect(_on_quiz_answered)

    	# --- ตั้งค่า InteractArea ---
    	_area = self.get_node(\"\1\")
    	if _area == None:
    		push_error("[Boss2] Missing InteractArea with InteractArea.gd attached.")
    		return
    	_area.action_name = "talk"
    	_area.interact = Callable(self, "_do_open_quiz")
    	_area.body_entered.connect(_on_enter)
    	_area.body_exited.connect(_on_exit)


    def _physics_process(self, _dt):
    	# Fallback: อยู่ในระยะแล้วกด E เพื่อเปิดกล่องคำถาม
    	if _in_range and not _quiz.visible and Input.is_action_just_pressed("interact"):
    		_do_open_quiz()

    # === Label helpers ============================================================

    def _boss_say(self, text, auto_hide_sec= -1.0):
    	if boss_label == None:
    		return
    	boss_label.text = text
    	boss_label.visible = True
    	if auto_hide_sec > 0.0:
    		_hide_label_later(auto_hide_sec)


    def _boss_clear(self):
    	if boss_label:
    		boss_label.text = ""
    		boss_label.visible = False


    def _hide_label_later(self, sec):
    # TODO: convert awaiting: 	await get_tree().create_timer(sec).timeout
    	_boss_clear()

    # === Triggers ================================================================

    def _on_enter(self, body):
    	if body.is_in_group("player"):
    		_player = body
    		_in_range = True
    		if show_hint_text:
    			if _done:
    				_boss_say("ไปต่อได้แล้ว...", 2.0)
    			else:
    				_boss_say("ทดสอบง่าย ๆ หน่อยสิ กด [E] เพื่อเริ่มนับ 0-9 ...")


    def _on_exit(self, body):
    	if body == _player:
    		_in_range = False
    		_player = None
    		_boss_clear()

    # === Quiz events =============================================================

    def _do_open_quiz(self):
    	if _done or not _in_range or _player == None or _quiz.visible:
    		return
    	_boss_clear()
    	if _player.has_method("set_movement_locked"):
    		_player.set_movement_locked(True)
    	# เปิดคำถาม
    	_quiz.ask(quiz_question, quiz_answer)


    def _on_quiz_answered(self, correct, _given):
    	# ปลดล็อกการเดิน
    	if _player and _player.has_method("set_movement_locked"):
    		_player.set_movement_locked(False)

    	if correct:
    		_done = True

    		# ---- เปิดทาง: ลบ Wall2 หากมีในฉากหลัก ----
    		if wall2:
    			wall2.queue_free()
    		else:
    			# เผื่อกรณีโอ๊ตตั้ง blocker_path ไว้ใน Inspector
    			if blocker_path != NodePath():
    				if wall:
    					wall.queue_free()

    		_boss_say("ดีมาก! ผ่านไปได้เลย...", 2.0)
    	else:
    		_boss_say("ยังไม่ใช่นะ ลองนับ 0 ถึง 9 ให้ถูกวิธีอีกครั้ง...", 2.0)
