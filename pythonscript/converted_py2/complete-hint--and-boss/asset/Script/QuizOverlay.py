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
class QuizOverlayLite(Control):
    def __init__(self):
        super().__init__()
        self._expected = None
        self._open = None
        self._panel = None
        self._question = None
        self._answer = None
        self._btn_ok = None
        self._btn_cancel = None
        self._ui_font = None
        self._dragging = None
        self._drag_offset = None
        self.root = None
        self.ui_layer = None
        self.dimmer = None
        self.vp = None
        self.target = None
        self.max_size = None
        self.panel_box = None
        self.margin = None
        self.vbox = None
        self.q_scroll = None
        self.qwrap = None
        self.te_normal = None
        self.te_focus = None
        self.has_lwm = None
        self.has_wm = None
        self.WRAP_WORD_SAFE = None
        self.WRAP_BOUNDARY_SAFE = None
        self.buttons = None
        self.spacer = None
        self.sb_normal = None
        self.sb_hover = None
        self.sb_pressed = None
        self.gmp = None
        self.gmp = None
        self.pos = None
        self.vp = None
        self.vp = None
        self.tw = None
        self.given = None
        self.ok = None
        self.tw = None
        self.t = None
        self.lines = None

    def _ready(self) -> None:
        pass

    signal answered(correct: bool, given: String)

    const UI_FONT_PATH := "res://asset/font/2005_iannnnnCPU.ttf"



    # ===== Drag state =====


    def _ready(self):
    	# ฟอนต์
    	_ui_font = load(UI_FONT_PATH)

    	# วางตัวเองบน CanvasLayer
    	if ui_layer == None:
    		ui_layer = CanvasLayer.new()
    		ui_layer.name = "CanvasLayer"
    		ui_layer.layer = 100
    		root.add_child(ui_layer)
    	if get_parent() != ui_layer:
    		ui_layer.add_child(self)

    	visible = False
    	mouse_filter = Control.MOUSE_FILTER_STOP
    	set_anchors_preset(Control.PRESET_FULL_RECT)
    	z_index = 9999

    	# Dimmer
    	dimmer.color = Color(0, 0, 0, 0.55)
    	dimmer.set_anchors_preset(Control.PRESET_FULL_RECT)
    	dimmer.mouse_filter = Control.MOUSE_FILTER_STOP
    	dimmer.gui_input.connect(func(e):
    		if e is InputEventMouseButton and e.pressed:
    			_cancel()
    	)
    	add_child(dimmer)

    	# Panel (กำหนดขนาดแบบตอบสนอง ไม่ล้นจอ)
    	_panel = Panel.new()
    	_panel.set_anchors_preset(Control.PRESET_CENTER)   # เริ่มกลางจอ

    	_panel.size = Vector2(min(target.x, max_size.x), min(target.y, max_size.y))

    	_panel.pivot_offset = _panel.size / 2
    	_panel.mouse_filter = Control.MOUSE_FILTER_STOP
    	add_child(_panel)

    	# สไตล์แผง
    	panel_box.bg_color = Color(0.09, 0.09, 0.10, 0.96)
    	panel_box.set_corner_radius_all(16)
    	panel_box.set_border_width_all(2)
    	panel_box.border_color = Color(1, 1, 1, 0.12)
    	panel_box.shadow_size = 20
    	panel_box.shadow_color = Color(0, 0, 0, 0.45)
    	panel_box.shadow_offset = Vector2(0, 6)
    	_panel.add_theme_stylebox_override("panel", panel_box)

    	# ←— ทำให้ลากย้ายได้ —→
    	_panel.gui_input.connect(_on_panel_gui_input)

    	# Layout
    	margin.anchor_left = 0
    	margin.anchor_top = 0
    	margin.anchor_right = 1
    	margin.anchor_bottom = 1
    	margin.offset_left = 20
    	margin.offset_top = 20
    	margin.offset_right = -20
    	margin.offset_bottom = -20
    	_panel.add_child(margin)

    	vbox.size_flags_vertical = Control.SIZE_EXPAND_FILL
    	vbox.add_theme_constant_override("separation", 12)
    	margin.add_child(vbox)

    	# ===== คำถาม: ใส่ ScrollContainer กันสูงเกิน =====
    	q_scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    	q_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
    	q_scroll.custom_minimum_size = Vector2(0, 140)  # โซนคำถามขั้นต่ำ
    	q_scroll.size_flags_stretch_ratio = 1.0
    	vbox.add_child(q_scroll)

    	qwrap.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    	q_scroll.add_child(qwrap)

    	_question = RichTextLabel.new()
    	_question.bbcode_enabled = False
    	_question.fit_content = True
    	_question.autowrap_mode = TextServer.AUTOWRAP_WORD
    	_question.add_theme_color_override("default_color", Color(1, 1, 1, 0.96))
    	_question.add_theme_font_size_override("normal_font_size", 26)
    	_question.add_theme_font_override("normal_font", _ui_font)
    	qwrap.add_child(_question)

    	vbox.add_child(HSeparator.new())

    	# ===== กล่องคำตอบ =====
    	_answer = TextEdit.new()
    	_answer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    	_answer.size_flags_vertical = Control.SIZE_EXPAND_FILL
    	_answer.size_flags_stretch_ratio = 1.2         # ให้พื้นที่คำตอบมากกว่าคำถามนิดนึง
    	_answer.custom_minimum_size = Vector2(0, 140)   # เดิม 270 → ลดเพื่อไม่ล้น
    	_answer.add_theme_font_override("font", _ui_font)
    	_answer.add_theme_font_size_override("font_size", 22)

    	te_normal.bg_color = Color(0.07, 0.07, 0.08, 1.0)
    	te_normal.set_corner_radius_all(10)
    	te_normal.set_border_width_all(1)
    	te_normal.border_color = Color(1, 1, 1, 0.12)
    	te_normal.shadow_size = 12
    	te_normal.shadow_color = Color(0, 0, 0, 0.25)
    	te_normal.shadow_offset = Vector2(0, 3)

    	te_focus.border_color = Color(0.55, 0.8, 1.0, 0.75)

    	_answer.add_theme_stylebox_override("normal", te_normal)
    	_answer.add_theme_stylebox_override("focus", te_focus)
    	_answer.add_theme_color_override("font_color", Color(1, 1, 1, 0.98))
    	_answer.add_theme_color_override("caret_color", Color(1, 1, 1, 1))
    	_answer.add_theme_color_override("selection_color", Color(0.35, 0.65, 1.0, 0.35))

    	if typeof(_answer.get("insert_text_on_tab")) != TYPE_NIL:
    		_answer.set("insert_text_on_tab", True)
    	elif typeof(_answer.get("accepts_tab")) != TYPE_NIL:
    		_answer.set("accepts_tab", True)

    	if has_lwm:
    		_answer.set("line_wrapping_mode", WRAP_WORD_SAFE)
    	elif has_wm:
    		_answer.set("wrap_mode", WRAP_BOUNDARY_SAFE)

    	vbox.add_child(_answer)

    	# ปุ่ม
    	buttons.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    	buttons.add_theme_constant_override("separation", 10)
    	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    	buttons.add_child(spacer)

    	_btn_cancel = Button.new()
    	_btn_cancel.text = "Cancel"
    	_btn_ok = Button.new()
    	_btn_ok.text = "Submit"

    	for b in [_btn_cancel, _btn_ok]:
    		b.custom_minimum_size = Vector2(120, 38)
    		b.add_theme_font_override("font", _ui_font)
    		b.add_theme_font_size_override("font_size", 22)
    		sb_normal.bg_color = Color(0.18, 0.18, 0.2, 1)
    		sb_normal.set_corner_radius_all(10)
    		sb_normal.set_border_width_all(1)
    		sb_normal.border_color = Color(1, 1, 1, 0.12)
    		sb_hover.bg_color = Color(0.24, 0.24, 0.28, 1)
    		sb_pressed.bg_color = Color(0.12, 0.12, 0.14, 1)
    		b.add_theme_stylebox_override("normal", sb_normal)
    		b.add_theme_stylebox_override("hover", sb_hover)
    		b.add_theme_stylebox_override("pressed", sb_pressed)
    		b.add_theme_color_override("font_color", Color(1,1,1))
    		b.add_theme_color_override("font_focus_color", Color(1,1,1))

    	_btn_cancel.pressed.connect(_cancel)
    	_btn_ok.pressed.connect(_submit)
    	buttons.add_child(_btn_cancel)
    	buttons.add_child(_btn_ok)
    	vbox.add_child(buttons)

    	# คีย์บอร์ด
    	_answer.gui_input.connect(_on_answer_gui_input)
    	set_process_unhandled_key_input(True)


    def _on_answer_gui_input(self, e):
    	if e is InputEventKey and e.pressed and e.keycode == KEY_ENTER:
    		if e.shift_pressed:
    			_answer.insert_text_at_caret("\n")
    			_answer.accept_event()
    		else:
    			_submit()
    			_answer.accept_event()


    def _unhandled_key_input(self, e):
    	if not _open: return
    	if e is InputEventKey and e.pressed and e.keycode == KEY_ESCAPE:
    		_cancel()

    # ===== Drag handlers =====

    def _on_panel_gui_input(self, e):
    	# อย่าเริ่มลากถ้าคลิกลงใน TextEdit (ให้มันโฟกัสพิมพ์ได้ตามปกติ)
    	if e is InputEventMouseButton and e.button_index == MOUSE_BUTTON_LEFT:
    		if e.pressed:
    			if _answer.get_global_rect().has_point(gmp):
    				return
    			_dragging = True
    			_drag_offset = _panel.global_position - gmp
    			_panel.grab_focus()
    			_panel.accept_event()
    		else:
    			_dragging = False
    	elif e is InputEventMouseMotion and _dragging:
    		# จำกัดไม่ให้ออกนอกหน้าจอ
    		pos.x = clamp(pos.x, 0.0, vp.x - _panel.size.x)
    		pos.y = clamp(pos.y, 0.0, vp.y - _panel.size.y)
    		_panel.global_position = pos
    		_panel.accept_event()


    def _center_panel(self):
    	_panel.global_position = (vp - _panel.size) * 0.5


    def ask(self, question, expected_answer):
    	_question.text = question
    	_expected = expected_answer
    	visible = True
    	_open = True
    	_answer.text = ""
    # TODO: convert awaiting: 	await get_tree().process_frame
    	_center_panel()         # เปิดใหม่ให้อยู่กลางทุกครั้ง
    	_answer.grab_focus()

    	# เปิดแบบนุ่ม ๆ
    	_panel.modulate.a = 0.0
    	_panel.scale = Vector2(0.9, 0.9)
    	tw.tween_property(_panel, "modulate:a", 1.0, 0.15)
    	tw.tween_property(_panel, "scale", Vector2.ONE, 0.18)


    def _submit(self):
    	_close()
    	answered.emit(ok, given)


    def _cancel(self):
    	_close()
    	answered.emit(False, _answer.text)


    def _close(self):
    	if not _open: return
    	_open = False
    	_dragging = False
    	tw.tween_property(_panel, "modulate:a", 0.0, 0.12)
    	tw.tween_property(_panel, "scale", Vector2(0.95, 0.95), 0.12)
    # TODO: convert awaiting: 	await tw.finished
    	visible = False

    # ===== เปรียบเทียบคำตอบ =====

    def _normalize(self, s):
    	t = t.replace("\r\n", "\n").replace("\r", "\n")
    	t = t.replace("\t", "    ")
    	for i in lines.size():
    		lines[i] = lines[i].rstrip(" ")
    	return String("\n").join(lines)


    def _compare_answer(self, given, expected):
    	return _normalize(given) == _normalize(expected)
