extends Control
class_name QuizOverlayLite

signal answered(correct: bool, given: String)

const UI_FONT_PATH := "res://asset/font/2005_iannnnnCPU.ttf"

var _expected := ""
var _open := false

var _panel: Panel
var _question: RichTextLabel
var _answer: TextEdit
var _btn_ok: Button
var _btn_cancel: Button
var _ui_font: Font

# ===== Drag state =====
var _dragging := false
var _drag_offset := Vector2.ZERO

func _ready() -> void:
	# ฟอนต์
	_ui_font = load(UI_FONT_PATH)

	# วางตัวเองบน CanvasLayer
	var root := get_tree().current_scene
	var ui_layer := root.get_node_or_null("CanvasLayer")
	if ui_layer == null:
		ui_layer = CanvasLayer.new()
		ui_layer.name = "CanvasLayer"
		ui_layer.layer = 100
		root.add_child(ui_layer)
	if get_parent() != ui_layer:
		ui_layer.add_child(self)

	visible = false
	mouse_filter = Control.MOUSE_FILTER_STOP
	set_anchors_preset(Control.PRESET_FULL_RECT)
	z_index = 9999

	# Dimmer
	var dimmer := ColorRect.new()
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

	var vp := get_viewport_rect().size
	var target := Vector2(760, 520)     # ขนาดที่อยากได้
	var max_size := vp * 0.8            # ไม่เกิน 80% ของจอ
	_panel.size = Vector2(min(target.x, max_size.x), min(target.y, max_size.y))

	_panel.pivot_offset = _panel.size / 2
	_panel.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(_panel)

	# สไตล์แผง
	var panel_box := StyleBoxFlat.new()
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
	var margin := MarginContainer.new()
	margin.anchor_left = 0
	margin.anchor_top = 0
	margin.anchor_right = 1
	margin.anchor_bottom = 1
	margin.offset_left = 20
	margin.offset_top = 20
	margin.offset_right = -20
	margin.offset_bottom = -20
	_panel.add_child(margin)

	var vbox := VBoxContainer.new()
	vbox.size_flags_vertical = Control.SIZE_EXPAND_FILL
	vbox.add_theme_constant_override("separation", 12)
	margin.add_child(vbox)

	# ===== คำถาม: ใส่ ScrollContainer กันสูงเกิน =====
	var q_scroll := ScrollContainer.new()
	q_scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	q_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	q_scroll.custom_minimum_size = Vector2(0, 140)  # โซนคำถามขั้นต่ำ
	q_scroll.size_flags_stretch_ratio = 1.0
	vbox.add_child(q_scroll)

	var qwrap := VBoxContainer.new()
	qwrap.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	q_scroll.add_child(qwrap)

	_question = RichTextLabel.new()
	_question.bbcode_enabled = false
	_question.fit_content = true
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

	var te_normal := StyleBoxFlat.new()
	te_normal.bg_color = Color(0.07, 0.07, 0.08, 1.0)
	te_normal.set_corner_radius_all(10)
	te_normal.set_border_width_all(1)
	te_normal.border_color = Color(1, 1, 1, 0.12)
	te_normal.shadow_size = 12
	te_normal.shadow_color = Color(0, 0, 0, 0.25)
	te_normal.shadow_offset = Vector2(0, 3)

	var te_focus := te_normal.duplicate()
	te_focus.border_color = Color(0.55, 0.8, 1.0, 0.75)

	_answer.add_theme_stylebox_override("normal", te_normal)
	_answer.add_theme_stylebox_override("focus", te_focus)
	_answer.add_theme_color_override("font_color", Color(1, 1, 1, 0.98))
	_answer.add_theme_color_override("caret_color", Color(1, 1, 1, 1))
	_answer.add_theme_color_override("selection_color", Color(0.35, 0.65, 1.0, 0.35))

	if typeof(_answer.get("insert_text_on_tab")) != TYPE_NIL:
		_answer.set("insert_text_on_tab", true)
	elif typeof(_answer.get("accepts_tab")) != TYPE_NIL:
		_answer.set("accepts_tab", true)

	var has_lwm := typeof(_answer.get("line_wrapping_mode")) != TYPE_NIL
	var has_wm  := typeof(_answer.get("wrap_mode")) != TYPE_NIL
	var WRAP_WORD_SAFE := 2
	var WRAP_BOUNDARY_SAFE := 1
	if has_lwm:
		_answer.set("line_wrapping_mode", WRAP_WORD_SAFE)
	elif has_wm:
		_answer.set("wrap_mode", WRAP_BOUNDARY_SAFE)

	vbox.add_child(_answer)

	# ปุ่ม
	var buttons := HBoxContainer.new()
	buttons.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	buttons.add_theme_constant_override("separation", 10)
	var spacer := Control.new()
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
		var sb_normal := StyleBoxFlat.new()
		sb_normal.bg_color = Color(0.18, 0.18, 0.2, 1)
		sb_normal.set_corner_radius_all(10)
		sb_normal.set_border_width_all(1)
		sb_normal.border_color = Color(1, 1, 1, 0.12)
		var sb_hover := sb_normal.duplicate()
		sb_hover.bg_color = Color(0.24, 0.24, 0.28, 1)
		var sb_pressed := sb_normal.duplicate()
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
	set_process_unhandled_key_input(true)

func _on_answer_gui_input(e: InputEvent) -> void:
	if e is InputEventKey and e.pressed and e.keycode == KEY_ENTER:
		if e.shift_pressed:
			_answer.insert_text_at_caret("\n")
			_answer.accept_event()
		else:
			_submit()
			_answer.accept_event()

func _unhandled_key_input(e: InputEvent) -> void:
	if not _open: return
	if e is InputEventKey and e.pressed and e.keycode == KEY_ESCAPE:
		_cancel()

# ===== Drag handlers =====
func _on_panel_gui_input(e: InputEvent) -> void:
	# อย่าเริ่มลากถ้าคลิกลงใน TextEdit (ให้มันโฟกัสพิมพ์ได้ตามปกติ)
	if e is InputEventMouseButton and e.button_index == MOUSE_BUTTON_LEFT:
		if e.pressed:
			var gmp := get_viewport().get_mouse_position()
			if _answer.get_global_rect().has_point(gmp):
				return
			_dragging = true
			_drag_offset = _panel.global_position - gmp
			_panel.grab_focus()
			_panel.accept_event()
		else:
			_dragging = false
	elif e is InputEventMouseMotion and _dragging:
		var gmp := get_viewport().get_mouse_position()
		var pos := gmp + _drag_offset
		# จำกัดไม่ให้ออกนอกหน้าจอ
		var vp := get_viewport_rect().size
		pos.x = clamp(pos.x, 0.0, vp.x - _panel.size.x)
		pos.y = clamp(pos.y, 0.0, vp.y - _panel.size.y)
		_panel.global_position = pos
		_panel.accept_event()

func _center_panel() -> void:
	var vp := get_viewport_rect().size
	_panel.global_position = (vp - _panel.size) * 0.5

func ask(question: String, expected_answer: String) -> void:
	_question.text = question
	_expected = expected_answer
	visible = true
	_open = true
	_answer.text = ""
	await get_tree().process_frame
	_center_panel()         # เปิดใหม่ให้อยู่กลางทุกครั้ง
	_answer.grab_focus()

	# เปิดแบบนุ่ม ๆ
	_panel.modulate.a = 0.0
	_panel.scale = Vector2(0.9, 0.9)
	var tw := create_tween().set_parallel(true)
	tw.tween_property(_panel, "modulate:a", 1.0, 0.15)
	tw.tween_property(_panel, "scale", Vector2.ONE, 0.18)

func _submit() -> void:
	var given := _answer.text
	var ok := _compare_answer(given, _expected)
	_close()
	answered.emit(ok, given)

func _cancel() -> void:
	_close()
	answered.emit(false, _answer.text)

func _close() -> void:
	if not _open: return
	_open = false
	_dragging = false
	var tw := create_tween().set_parallel(true)
	tw.tween_property(_panel, "modulate:a", 0.0, 0.12)
	tw.tween_property(_panel, "scale", Vector2(0.95, 0.95), 0.12)
	await tw.finished
	visible = false

# ===== เปรียบเทียบคำตอบ =====
func _normalize(s: String) -> String:
	var t := s.strip_edges()
	t = t.replace("\r\n", "\n").replace("\r", "\n")
	t = t.replace("\t", "    ")
	var lines := t.split("\n")
	for i in lines.size():
		lines[i] = lines[i].rstrip(" ")
	return String("\n").join(lines)

func _compare_answer(given: String, expected: String) -> bool:
	return _normalize(given) == _normalize(expected)
