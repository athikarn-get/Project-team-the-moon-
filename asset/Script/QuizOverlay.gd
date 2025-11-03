extends Control
class_name QuizOverlay

signal answered(correct: bool, given: String)

@export var question := "พิมพ์คำตอบของคุณที่นี่"
@export var answer := "print()"
@export var case_insensitive := true
@export var trim_whitespace := true

var _font: Font
var _label: Label
var _input: LineEdit

func _ready() -> void:
	anchor_left = 0; anchor_top = 0; anchor_right = 1; anchor_bottom = 1
	offset_left = 0; offset_top = 0; offset_right = 0; offset_bottom = 0
	mouse_filter = Control.MOUSE_FILTER_STOP
	visible = false

	_font = load("res://asset/font/2005_iannnnnCPU.ttf")

	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.45)
	dim.anchor_left = 0; dim.anchor_top = 0; dim.anchor_right = 1; dim.anchor_bottom = 1
	add_child(dim)

	var center := CenterContainer.new()
	center.anchor_left = 0; center.anchor_top = 0; center.anchor_right = 1; center.anchor_bottom = 1
	add_child(center)

	var panel := PanelContainer.new()
	panel.custom_minimum_size = Vector2(600, 260)
	center.add_child(panel)

	var root := VBoxContainer.new()
	root.add_theme_constant_override("separation", 12)
	root.custom_minimum_size = Vector2(560, 0)
	panel.add_child(root)

	var title := Label.new()
	title.text = "PSCP Quiz"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	if _font:
		title.add_theme_font_override("font", _font)
		title.add_theme_font_size_override("font_size", 26)
	root.add_child(title)

	_label = Label.new()
	_label.autowrap_mode = TextServer.AUTOWRAP_WORD
	if _font:
		_label.add_theme_font_override("font", _font)
		_label.add_theme_font_size_override("font_size", 22)
	_label.add_theme_constant_override("outline_size", 2)
	_label.add_theme_color_override("font_outline_color", Color.BLACK)
	root.add_child(_label)

	_input = LineEdit.new()
	_input.placeholder_text = "พิมพ์คำตอบ แล้วกด Enter หรือ Submit"
	if _font:
		_input.add_theme_font_override("font", _font)
		_input.add_theme_font_size_override("font_size", 22)
	_input.text_submitted.connect(_on_submit_text)
	root.add_child(_input)

	var btns := HBoxContainer.new()
	btns.alignment = BoxContainer.ALIGNMENT_END
	btns.add_theme_constant_override("separation", 10)
	root.add_child(btns)

	var cancel_btn := Button.new()
	cancel_btn.text = "Cancel"
	cancel_btn.pressed.connect(_on_cancel)
	btns.add_child(cancel_btn)

	var submit_btn := Button.new()
	submit_btn.text = "Submit"
	submit_btn.pressed.connect(func(): _on_submit_text(_input.text))
	btns.add_child(submit_btn)

func ask(new_q: String, expected: String) -> void:
	question = new_q
	answer = expected
	_label.text = question
	_input.text = ""
	visible = true
	await get_tree().process_frame
	_input.grab_focus()

func _on_submit_text(text: String) -> void:
	var given := text
	var expect := answer
	if trim_whitespace:
		given = given.strip_edges(); expect = expect.strip_edges()
	if case_insensitive:
		given = given.to_lower(); expect = expect.to_lower()
	var correct := (given == expect)
	visible = false
	answered.emit(correct, text)

func _on_cancel() -> void:
	visible = false
	answered.emit(false, _input.text)
