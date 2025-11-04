from typing import Optional, Any
try:
    from py4godot import gdclass, signal
    from py4godot.core import *
except Exception:
    from godot import exposed as gdclass, signal
    from godot import *  # type: ignore


@gdclass
class QuizBox(AcceptDialog):
    answered = signal()

    def __init__(self):
        super().__init__()
        self.question: str = ""
        self.answer: str = ""
        self.case_insensitive: bool = True
        self.trim_whitespace: bool = True
        self._font: Optional[Font] = None
        self._label: Optional[Label] = None
        self._input: Optional[LineEdit] = None
        self._built: bool = False
        self._is_open: bool = False
        self._cancel_btn: Optional[Button] = None
        self._root: Optional[VBoxContainer] = None

    def _ready(self) -> None:
        self._build_ui()
        self.title = "PSCP Quiz"
        ok_btn = None
        try:
            ok_btn = self.get_ok_button()
        except Exception:
            ok_btn = None
        if ok_btn:
            ok_btn.pressed.connect(self._on_ok_pressed)
        self._cancel_btn = self.add_cancel_button("Cancel")
        if self._cancel_btn:
            self._cancel_btn.pressed.connect(self._on_cancel)

    def _build_ui(self) -> None:
        if self._built:
            return
        self._font = load("res://asset/font/2005_iannnnnCPU.ttf")
        for c in list(self.get_children()):
            self.remove_child(c)
            c.queue_free()
        self._root = VBoxContainer.new()
        self._root.custom_minimum_size = Vector2(600, 0)
        self._root.add_theme_constant_override("separation", 10)
        self.add_child(self._root)
        self._label = Label.new()
        self._label.autowrap_mode = TextServer.AUTOWRAP_WORD
        if self._font:
            self._label.add_theme_font_override("font", self._font)
            self._label.add_theme_font_size_override("font_size", 22)
        self._label.add_theme_constant_override("outline_size", 2)
        self._label.add_theme_color_override("font_outline_color", Color.BLACK)
        self._root.add_child(self._label)
        self._input = LineEdit.new()
        self._input.placeholder_text = "พิมพ์คำตอบ แล้วกด Enter หรือปุ่ม Submit"
        if self._font:
            self._input.add_theme_font_override("font", self._font)
            self._input.add_theme_font_size_override("font_size", 22)
        self._input.text_submitted.connect(self._on_submit_text)
        self._root.add_child(self._input)
        self.custom_minimum_size = Vector2(620, 240)
        self._built = True

    def ask(self, new_q: str, expected: str) -> None:
        self._build_ui()
        self.question = new_q or ""
        self.answer = expected or ""
        if not self._label or not self._input:
            push_error("[QuizBox] UI not built.")
            return
        self._label.text = self.question
        self._input.text = ""
        self._is_open = True
        self.popup_centered()
        self.call_deferred("_focus_input")

    def _focus_input(self) -> None:
        if self._input and is_instance_valid(self._input):
            self._input.grab_focus()

    def _on_submit_text(self, text: str) -> None:
        self._submit(text)

    def _on_ok_pressed(self) -> None:
        self._submit(self._input.text if self._input else "")

    def _submit(self, text: str) -> None:
        given = text or ""
        expect = self.answer or ""
        if self.trim_whitespace:
            given = given.strip()
            expect = expect.strip()
        if self.case_insensitive:
            given = given.lower()
            expect = expect.lower()
        correct = (given == expect)
        self._is_open = False
        self.hide()
        self.emit_signal("answered", correct, text)

    def _on_cancel(self) -> None:
        self._is_open = False
        self.hide()
        self.emit_signal("answered", False, self._input.text if self._input else "")

    def is_open(self) -> bool:
        return self._is_open
