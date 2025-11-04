from typing import Optional, Any
try:
    from py4godot import gdclass, signal
    from py4godot.core import *
except Exception:
    from godot import exposed as gdclass, signal
    from godot import *  # type: ignore


@gdclass
class Textbox(CanvasLayer):
    finished = signal()

    READY = 0
    READING = 1
    FINISHED = 2
    CHAR_READ_RATE = 0.03

    def __init__(self):
        super().__init__()
        self.textbox_container: Optional[Control] = None
        self.start_symbol: Optional[Label] = None
        self.end_symbol: Optional[Label] = None
        self.label: Optional[Label] = None
        self.current_state: int = Textbox.READY
        self.reveal_tween: Optional[Tween] = None
        self.text_queue: list[str] = []
        self.anchor_world_pos: Vector2 = Vector2.ZERO
        self._current_text: str = ""
        self._duration: float = 0.0

    def _ready(self) -> None:
        self.textbox_container = self.get_node_or_null("TextboxContainer")
        self.start_symbol = self.get_node_or_null("StartSymbol")
        self.end_symbol = self.get_node_or_null("EndSymbol")
        self.label = self.get_node_or_null("Label")
        self.hide_textbox()
        if self.label:
            self.label.autowrap_mode = TextServer.AUTOWRAP_WORD

    def _process(self, _dt: float) -> None:
        if self.current_state == Textbox.READY:
            if self.text_queue:
                self.display_text()
        elif self.current_state == Textbox.READING:
            if Input.is_action_just_pressed("ui_accept") or Input.is_action_just_pressed("interact"):
                if self.reveal_tween and self.reveal_tween.is_running():
                    self.reveal_tween.kill()
                    self.reveal_tween = None
                if self.label:
                    self.label.visible_characters = len(self._current_text)
                if self.end_symbol:
                    self.end_symbol.text = "_"
                self.change_state(Textbox.FINISHED)
        elif self.current_state == Textbox.FINISHED:
            if Input.is_action_just_pressed("ui_accept") or Input.is_action_just_pressed("interact"):
                if self.text_queue:
                    self.display_text()
                else:
                    self.change_state(Textbox.READY)
                    self.hide_textbox()
                    self.finished.emit()

    def set_anchor_world_pos(self, p: Vector2) -> None:
        self.anchor_world_pos = p + Vector2(0, 64)

    def queue_text(self, t: str) -> None:
        if t is None:
            t = ""
        self.text_queue.append(t)

    def display_text(self) -> None:
        if not self.label or not self.textbox_container:
            return
        if self.reveal_tween and self.reveal_tween.is_running():
            self.reveal_tween.kill()
        self.reveal_tween = None
        if self.start_symbol:
            self.start_symbol.text = ""
        if self.end_symbol:
            self.end_symbol.text = ""
        if not self.text_queue:
            return
        self._current_text = self.text_queue.pop(0)
        self._duration = float(len(self._current_text)) * Textbox.CHAR_READ_RATE
        self.label.text = ""
        self._set_popup_screen_pos(self.anchor_world_pos)
        self.change_state(Textbox.READING)
        self.show_textbox()
        self.reveal_tween = self.create_tween()
        def _set_vis(v):
            if self.label:
                self.label.visible_characters = int(v)
        self.reveal_tween.tween_method(_set_vis, 0, len(self._current_text), self._duration)\
            .set_trans(Tween.TRANS_LINEAR).set_ease(Tween.EASE_IN_OUT)
        self.reveal_tween.finished.connect(self._on_reveal_finished)

    def _on_reveal_finished(self) -> None:
        if self.end_symbol:
            self.end_symbol.text = "_"
        self.change_state(Textbox.FINISHED)
        self.reveal_tween = None

    def hide_textbox(self) -> None:
        if self.start_symbol:
            self.start_symbol.text = ""
        if self.end_symbol:
            self.end_symbol.text = ""
        if self.label:
            self.label.text = ""
        if self.textbox_container:
            self.textbox_container.hide()

    def show_textbox(self) -> None:
        if self.textbox_container:
            self.textbox_container.show()

    def _set_popup_screen_pos(self, world_pos: Vector2) -> None:
        if not self.textbox_container:
            return
        xform: Transform2D = self.get_viewport().get_canvas_transform()
        screen_pos: Vector2 = xform * world_pos
        box_size = getattr(self.textbox_container, "size", Vector2(360, 120))
        if box_size == Vector2.ZERO:
            box_size = Vector2(360, 120)
        margin = 40.0
        pos = screen_pos - Vector2(box_size.x * 0.5, -margin)
        vp_size: Vector2 = self.get_viewport().get_visible_rect().size
        pos.x = clamp(pos.x, 8.0, vp_size.x - box_size.x - 8.0)
        pos.y = clamp(pos.y, 8.0, vp_size.y - box_size.y - 8.0)
        self.textbox_container.global_position = pos

    def change_state(self, s: int) -> None:
        self.current_state = s
