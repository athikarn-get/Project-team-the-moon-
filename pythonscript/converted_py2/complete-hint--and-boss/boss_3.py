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
class Boss_3(Node2D):
    def __init__(self):
        super().__init__()
        self.quiz_question = None  # @export
        self.quiz_answer = None  # @export
        self.blocker_path = None  # @export
        self.show_hint_text = None  # @export
        self._player =  None
        self._in_range = None
        self._done = None
        self._quiz =  None
        self._area = None
        self.boss_label: Any = None  # onready; set in _ready
        self.layer = None
        self.quiz_visible = None
        self.wall3 = None
        self.wall = None

    def _ready(self) -> None:
        self.boss_label = self.get_node(\"\1\")





    def _ready(self):
    	if boss_label:
    		boss_label.visible = False
    	else:
    		push_error("[Boss3] Missing Label 'bossdialog3'.")

    	# ตั้งค่า InteractArea
    	_area = self.get_node(\"\1\")
    	if _area == None:
    		push_error("[Boss3] Missing InteractArea.")
    		return
    	_area.action_name = "talk"
    	_area.interact = Callable(self, "_do_open_quiz")
    	_area.body_entered.connect(_on_enter)
    	_area.body_exited.connect(_on_exit)

    	# เตรียม Quiz ครั้งแรก (แต่ยังไม่แสดง)
    	_ensure_quiz()


    def _ensure_quiz(self):
    	# สร้าง overlay ถ้ายังไม่มีหรือถูกลบไปแล้ว
    	if not is_instance_valid(_quiz):
    		_quiz = QuizOverlayLite.new()
    		if layer == None:
    			layer = CanvasLayer.new()
    			layer.name = "CanvasLayer"
    			layer.layer = 100
    			get_tree().current_scene.add_child(layer)
    		layer.add_child(_quiz)
    		_quiz.z_index = 9999
    		# กันต่อสัญญาณซ้ำ
    		if not _quiz.answered.is_connected(_on_quiz_answered):
    			_quiz.answered.connect(_on_quiz_answered)


    def _physics_process(self, _dt):
    	# ✅ เช็คด้วย is_instance_valid ก่อนแตะ _quiz.visible
    	if _in_range and (not quiz_visible) and Input.is_action_just_pressed("interact"):
    		_do_open_quiz()

    # ========== Label helpers ==========

    def _boss_say(self, text, auto_hide_sec= -1.0):
    	if boss_label == None: return
    	boss_label.text = text
    	boss_label.visible = True
    	if auto_hide_sec > 0.0:
    # TODO: convert awaiting: 		await get_tree().create_timer(auto_hide_sec).timeout
    		_boss_clear()


    def _boss_clear(self):
    	if boss_label:
    		boss_label.text = ""
    		boss_label.visible = False

    # ========== Triggers ==========

    def _on_enter(self, body):
    	if body.is_in_group("player"):
    		_player = body
    		_in_range = True
    		if show_hint_text:
    			if _done:
    				_boss_say("ไปต่อได้แล้ว...", 2.0)
    			else:
    				_boss_say("กล้าทดสอบไหม? กด [E] เพื่อเริ่มทำโจทย์!")


    def _on_exit(self, body):
    	if body == _player:
    		_in_range = False
    		_player = None
    		_boss_clear()

    # ========== Quiz flow ==========

    def _do_open_quiz(self):
    	if _done or not _in_range or _player == None:
    		return
    	_ensure_quiz()
    	# ถ้าเปิดอยู่แล้ว ไม่ต้องทำซ้ำ
    	if _quiz.visible:
    		return
    	_boss_clear()
    	if _player.has_method("set_movement_locked"):
    		_player.set_movement_locked(True)
    	_quiz.ask(quiz_question, quiz_answer)


    def _on_quiz_answered(self, correct, _given):
    	# ปลดล็อกการเดิน
    	if _player and _player.has_method("set_movement_locked"):
    		_player.set_movement_locked(False)

    	# ✅ ไม่ free ทันที — ซ่อนไว้แทน
    	if is_instance_valid(_quiz):
    		_quiz.hide()

    	if correct:
    		_done = True
    		# เปิดทาง: ลบ Wall3 ถ้ามี หรือใช้ blocker_path ถ้าตั้งไว้
    		if wall3:
    			wall3.queue_free()
    		elif blocker_path != NodePath():
    			if wall:
    				wall.queue_free()
    		_boss_say("ยอดเยี่ยม! ผ่านไปได้เลย...", 2.5)
    	else:
    		_boss_say("ยังไม่ถูกนะ… ลองใหม่อีกครั้ง!", 2.2)
