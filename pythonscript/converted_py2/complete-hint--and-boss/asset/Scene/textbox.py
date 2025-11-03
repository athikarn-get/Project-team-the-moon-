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
class Textbox(CanvasLayer):
    def __init__(self):
        super().__init__()
        self.textbox_container: Any = None  # onready; set in _ready
        self.start_symbol: Any = None  # onready; set in _ready
        self.end_symbol: Any = None  # onready; set in _ready
        self.label: Any = None  # onready; set in _ready
        self.current_state = State.READY
        self.reveal_tween =  None
        self.text_queue = []
        self.anchor_world_pos = Vector2.ZERO
        self.t = text_queue.pop_front() as String
        self.duration = float(t.length()) * CHAR_READ_RATE
        self.xform = get_viewport().get_canvas_transform()
        self.screen_pos = xform * world_pos
        self.box = textbox_container
        self.box_size = box.size
        self.margin = 40.0
        self.vp = get_viewport().get_visible_rect().size

    def _ready(self) -> None:
        self.textbox_container = self.get_node(\"\1\")
        self.start_symbol = self.get_node(\"\1\")
        self.end_symbol = self.get_node(\"\1\")
        self.label = self.get_node(\"\1\")
    signal finished

    const CHAR_READ_RATE := 0.03


    enum State { READY, READING, FINISHED }



    def _ready(self):
    	hide_textbox()
    	label.autowrap_mode = TextServer.AUTOWRAP_WORD


    def _process(self, _delta):
    	match current_state:
    		State.READY:
    			if not text_queue.is_empty():
    				display_text()
    		State.READING:
    			if Input.is_action_just_pressed("ui_accept") or Input.is_action_just_pressed("interact"):
    				if reveal_tween:
    					reveal_tween.kill()
    					reveal_tween = None
    				label.visible_characters = label.text.length()
    				end_symbol.text = "_"
    				change_state(State.FINISHED)
    		State.FINISHED:
    			if Input.is_action_just_pressed("ui_accept") or Input.is_action_just_pressed("interact"):
    				if not text_queue.is_empty():
    					display_text()
    				else:
    					change_state(State.READY)
    					hide_textbox()
    					emit_signal("finished")

    # ====== เพิ่มส่วนนี้ ======
    # เรียกจาก chest เพื่อกำหนดตำแหน่งของ textbox

    def set_anchor_world_pos(self, p):
    	# ขยับให้ต่ำกว่า player นิดหน่อย (ค่าบวก = ลงล่าง)
    	anchor_world_pos = p + Vector2(0, 64)
    # ========================

    # ---- Public API ----

    def queue_text(self, t):
    	text_queue.push_back(t)


    def display_text(self):
    	if reveal_tween:
    		reveal_tween.kill()
    		reveal_tween = None

    	start_symbol.text = ""
    	end_symbol.text = ""
    	label.text = t
    	label.visible_characters = 0

    	_set_popup_screen_pos(anchor_world_pos)
    	change_state(State.READING)
    	show_textbox()

    	reveal_tween = create_tween()
    	reveal_tween.tween_method(
    		func(v): label.visible_characters = int(v),
    		0, t.length(), duration
    	).set_trans(Tween.TRANS_LINEAR).set_ease(Tween.EASE_IN_OUT)

    	reveal_tween.finished.connect(func():
    		end_symbol.text = "_"
    		change_state(State.FINISHED)
    		reveal_tween = None
    	)


    def hide_textbox(self):
    	start_symbol.text = ""
    	end_symbol.text = ""
    	label.text = ""
    	textbox_container.hide()


    def show_textbox(self):
    	textbox_container.show()


    def _set_popup_screen_pos(self, world_pos):

    	if box_size == Vector2.ZERO:
    		box_size = Vector2(360, 120)

    	box.global_position = screen_pos - Vector2(box_size.x * 0.5, -margin)  # อยู่ใต้ Player

    	box.global_position.x = clampf(box.global_position.x, 8.0, vp.x - box_size.x - 8.0)
    	box.global_position.y = clampf(box.global_position.y, 8.0, vp.y - box_size.y - 8.0)


    def change_state(self, s):
    	current_state = s
