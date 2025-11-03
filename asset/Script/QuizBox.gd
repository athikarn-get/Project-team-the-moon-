extends AcceptDialog
class_name QuizBox

signal answered(correct: bool, given: String)

@export var question := "พิมพ์คำตอบของคุณที่นี่"
@export var answer := "print()"
@export var case_insensitive := true
@export var trim_whitespace := true

var _font: Font
var _label: Label
var _input: LineEdit
var _built := false
var _is_open := false
var _cancel_btn: Button

func _ready() -> void:
	_build_ui()

	# Basic dialog setup
	title = "PSCP Quiz"
	ok_button_text = "Submit"  # label the OK button

	# Wire buttons explicitly (no signal name strings / no lambdas)
	var ok_btn := get_ok_button()
	if ok_btn:
		ok_btn.pressed.connect(_on_ok_pressed)

	_cancel_btn = add_cancel_button("Cancel")
	if _cancel_btn:
		_cancel_btn.pressed.connect(_on_cancel)

func _build_ui() -> void:
	if _built:
		return

	# Load font (comment out if you don't have this file)
	_font = load("res://asset/font/2005_iannnnnCPU.ttf")

	# Clear any default children
	for c in get_children():
		remove_child(c)
		c.queue_free()

	# Root layout
	var root := VBoxContainer.new()
	root.custom_minimum_size = Vector2(600, 0)
	root.add_theme_constant_override("separation", 10)
	add_child(root)

	# Question label
	_label = Label.new()
	_label.autowrap_mode = TextServer.AUTOWRAP_WORD
	if _font:
		_label.add_theme_font_override("font", _font)
		_label.add_theme_font_size_override("font_size", 22)
	_label.add_theme_constant_override("outline_size", 2)
	_label.add_theme_color_override("font_outline_color", Color.BLACK)
	root.add_child(_label)

	# Input
	_input = LineEdit.new()
	_input.placeholder_text = "พิมพ์คำตอบ แล้วกด Enter หรือปุ่ม Submit"
	if _font:
		_input.add_theme_font_override("font", _font)
		_input.add_theme_font_size_override("font_size", 22)
	_input.text_submitted.connect(_on_submit_text)
	root.add_child(_input)

	# Make sure it’s a sensible size
	size = Vector2(620, 240)

	_built = true

func ask(new_q: String, expected: String) -> void:
	_build_ui()

	question = new_q
	answer = expected

	if _label == null or _input == null:
		push_error("[QuizBox] UI not built; _label or _input is null.")
		return

	_label.text = question
	_input.text = ""

	_is_open = true
	popup_centered()

	# Focus the input safely next frame
	if is_inside_tree():
		await get_tree().process_frame
		if is_instance_valid(_input):
			_input.grab_focus()
	else:
		call_deferred("_focus_input")

func _focus_input() -> void:
	if is_instance_valid(_input):
		_input.grab_focus()

func _on_submit_text(text: String) -> void:
	_submit(text)

func _on_ok_pressed() -> void:
	_submit(_input.text if _input else "")

func _submit(text: String) -> void:
	var given := text
	var expect := answer
	if trim_whitespace:
		given = given.strip_edges()
		expect = expect.strip_edges()
	if case_insensitive:
		given = given.to_lower()
		expect = expect.to_lower()

	var correct := (given == expect)
	_is_open = false
	hide()
	answered.emit(correct, text)

func _on_cancel() -> void:
	_is_open = false
	hide()
	answered.emit(false, _input.text if _input else "")

func is_open() -> bool:
	return _is_open
