from typing import Optional, Any
try:
    from py4godot import gdclass, signal
    from py4godot.core import *
except Exception:
    from godot import exposed as gdclass, signal
    from godot import *  # type: ignore


@gdclass
class Text_Box(MarginContainer):
    finished_displaying = signal()

    def __init__(self):
        super().__init__()
        self.label: Optional[Label] = None
        self.timer: Optional[Timer] = None
        self.text: str = ""
        self.letter_index: int = 0
        self.letter_time: float = 0.03
        self.space_time: float = 0.06
        self.punctuation_time: float = 0.2
        self.MAX_WIDTH: float = 200.0

    def _ready(self) -> None:
        self.label = self.get_node_or_null("Label")
        self.timer = self.get_node_or_null("LetterDisplayTimer")
        if self.timer:
            self.timer.one_shot = True
            self.timer.timeout.connect(self._on_letterdisplaytimer_timeout)

    def display_text(self, text_to_display: str) -> None:
        if not self.label or not self.timer:
            return
        self.text = text_to_display or ""
        self.letter_index = 0
        self.label.text = self.text
        self.call_deferred("_apply_layout_then_type")

    def _apply_layout_then_type(self) -> None:
        if not self.label:
            return
        self.custom_minimum_size = Vector2(min(self.size.x, self.MAX_WIDTH), self.custom_minimum_size.y)
        if self.size.x > self.MAX_WIDTH:
            self.label.autowrap_mode = TextServer.AUTOWRAP_WORD
        self.global_position = Vector2(self.global_position.x - self.size.x / 2.0, self.global_position.y - self.size.y - 24.0)
        self.label.text = ""
        self._display_letter()

    def _display_letter(self) -> None:
        if not self.label or not self.timer:
            return
        if self.letter_index >= len(self.text):
            self.emit_signal("finished_displaying")
            return
        self.label.text += self.text[self.letter_index]
        self.letter_index += 1
        if self.letter_index >= len(self.text):
            self.emit_signal("finished_displaying")
            return
        ch = self.text[self.letter_index]
        if ch in ("!", ".", ",", "?"):
            self.timer.start(self.punctuation_time)
        elif ch == " ":
            self.timer.start(self.space_time)
        else:
            self.timer.start(self.letter_time)

    def _on_letterdisplaytimer_timeout(self) -> None:
        self._display_letter()
