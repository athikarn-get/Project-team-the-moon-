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
class QuizBox(AcceptDialog):
    def __init__(self):
        super().__init__()
        self.question = None  # @export
        self.answer = None  # @export
        self.case_insensitive = None  # @export
        self.trim_whitespace = None  # @export
        self._font = None
        self._label = None
        self._input = None
        self._built = None
        self._is_open = None
        self._cancel_btn = None
        self.ok_btn = None
        self.root = None
        self.given = None
        self.expect = None
        self.correct = None

    def _ready(self) -> None:
        pass

    signal answered(correct: bool, given: String)




    def _ready(self):
    	_build_ui()

    	# Basic dialog setup
    	title = "PSCP Quiz"
    	ok_button_text = "Submit"  # label the OK button

    	# Wire buttons explicitly (no signal name strings / no lambdas)
    	if ok_btn:
    		ok_btn.pressed.connect(_on_ok_pressed)

    	_cancel_btn = add_cancel_button("Cancel")
    	if _cancel_btn:
    		_cancel_btn.pressed.connect(_on_cancel)


    def _build_ui(self):
    	if _built:
    		return

    	# Load font (comment out if you don't have this file)
    	_font = load("res://asset/font/2005_iannnnnCPU.ttf")

    	# Clear any default children
    	for c in get_children():
    		remove_child(c)
    		c.queue_free()

    	# Root layout
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

    	_built = True


    def ask(self, new_q, expected):
    	_build_ui()

    	question = new_q
    	answer = expected

    	if _label == None or _input == None:
    		push_error("[QuizBox] UI not built; _label or _input is None.")
    		return

    	_label.text = question
    	_input.text = ""

    	_is_open = True
    	popup_centered()

    	# Focus the input safely next frame
    	if is_inside_tree():
    # TODO: convert awaiting: 		await get_tree().process_frame
    		if is_instance_valid(_input):
    			_input.grab_focus()
    	else:
    		call_deferred("_focus_input")


    def _focus_input(self):
    	if is_instance_valid(_input):
    		_input.grab_focus()


    def _on_submit_text(self, text):
    	_submit(text)


    def _on_ok_pressed(self):
    	_submit(_input.text if _input else "")


    def _submit(self, text):
    	if trim_whitespace:
    		given = given.strip_edges()
    		expect = expect.strip_edges()
    	if case_insensitive:
    		given = given.to_lower()
    		expect = expect.to_lower()

    	_is_open = False
    	hide()
    	answered.emit(correct, text)


    def _on_cancel(self):
    	_is_open = False
    	hide()
    	answered.emit(False, _input.text if _input else "")


    def is_open(self):
    	return _is_open
