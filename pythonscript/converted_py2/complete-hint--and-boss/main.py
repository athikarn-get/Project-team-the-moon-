from typing import Any, Optional, List
try:
    from py4godot import gdclass, signal
    from py4godot.core import *
except Exception:
    from godot import exposed as gdclass, signal
    from godot import *  # type: ignore


H_HINT1 = (
    "💡 คำใบ้ข้อที่ 1\n"
    "1) ลูปจะเช็กทุกค่าทีละตัวใน nums\n"
    "2) เงื่อนไข % 2 == 0 ผ่านเฉพาะบางค่า (เลขคู่เท่านั้น)\n"
    "3) total จะเพิ่มขึ้นเรื่อย ๆ ตามค่าที่ผ่านเงื่อนไข\n"
    "4) คำตอบออกมาเป็นเลขคู่บวก ที่ไม่ได้ใหญ่มาก\n"
    "5) ถ้าอยากรู้คำตอบไว ลองพิมพ์ค่าที่เข้า if ดูก่อนสิ\n"
)

H_HINT2 = (
    "💡 คำใบ้ข้อที่ 2\n"
    "1) ช่วงยาว “คี่” ใช้ ซ้าย - ขวา, ช่วงยาว “คู่” ใช้ ซ้าย + ขวา\n"
    "2) [2, -3, 4] คือฝั่งซ้ายของการแบ่งใหญ่\n"
    "3) [1, 5] คือฝั่งขวา และจะถูกรวมแบบบวก\n"
    "4) ผลรวมสุดท้ายได้จาก “ฝั่งซ้ายลบฝั่งขวา”\n"
    "5) ค่าที่ได้เป็นจำนวนติดลบเล็ก ๆ\n"
)

H_HINT3 = (
    "💡 คำใบ้ข้อที่ 3\n"
    "1) ลองมองแต่ละคำแล้วนับตัวที่ซ้ำ เช่น p, r, o, g...\n"
    "2) “programming” มีตัวซ้ำหลายตัว โดยเฉพาะ m กับ g\n"
    "3) “very” มีตัวซ้ำบ้างแต่ไม่มาก\n"
    "4) “Python” ไม่มีตัวซ้ำเลย\n"
    "5) ถ้ามีหลายคำซ้ำเท่ากัน ให้เลือกคำที่ “อยู่ก่อน” ในข้อความ\n"
)


@gdclass
class Main(Node2D):
    def __init__(self):
        super().__init__()
        self.hints: List[str] = []
        self._page: int = 0
        self.hint_open: bool = False
        self.new_hint_available: bool = False
        self.GLOW_SCALE: float = 1.25
        self.GLOW_OFFSET: Vector2 = Vector2(-6.9, -18)
        self.hint_button: Optional[Button] = None
        self.layer: Optional[CanvasLayer] = None
        self.hint_root: Optional[Control] = None
        self.dimmer: Optional[ColorRect] = None
        self.hint_panel: Optional[Panel] = None
        self.vbox: Optional[VBoxContainer] = None
        self.hint_label: Optional[RichTextLabel] = None
        self.nav_box: Optional[HBoxContainer] = None
        self.btn_prev: Optional[Button] = None
        self.btn_next: Optional[Button] = None
        self.page_label: Optional[Label] = None
        self.hint_close: Optional[Button] = None
        self.glow_rect: Optional[ColorRect] = None
        self.glow_tween: Optional[Tween] = None
        self.pulse_tween: Optional[Tween] = None

    def _ready(self) -> None:
        self.hint_button = self._get_or_make_hint_button()
        self._style_hint_button()
        self.hint_button.pressed.connect(self._on_hint_button_pressed)
        self._build_parchment_hint()
        self._create_glow_centered()
        self.hint_button.resized.connect(self._update_glow_size)
        self.hint_button.minimum_size_changed.connect(self._update_glow_size)
        self._update_glow_size()
        self.hint_button.mouse_entered.connect(self._on_hint_button_hover_in)
        self.hint_button.mouse_exited.connect(self._on_hint_button_hover_out)
        self._refresh_hint_view()

    def _get_or_make_hint_button(self) -> Button:
        n = self.find_child("HintButton", True, False)
        if isinstance(n, Button):
            return n
        layer = CanvasLayer.new()
        layer.layer = 50
        self.add_child(layer)
        root = Control.new()
        root.set_anchors_preset(Control.PRESET_FULL_RECT)
        layer.add_child(root)
        btn = Button.new()
        btn.name = "HintButton"
        root.add_child(btn)
        return btn

    def _style_hint_button(self) -> None:
        btn = self.hint_button
        if not btn:
            return
        btn.anchor_left = 1.0
        btn.anchor_top = 0.0
        btn.anchor_right = 1.0
        btn.anchor_bottom = 0.0
        btn.offset_left = -84
        btn.offset_right = -20
        btn.offset_top = 20
        btn.offset_bottom = 84
        btn.text = "💡"
        btn.custom_minimum_size = Vector2(64, 64)
        btn.add_theme_font_size_override("font_size", 36)
        btn.add_theme_color_override("font_color", Color(1, 1, 1))
        btn.focus_mode = Control.FOCUS_NONE
        self.get_viewport().gui_release_focus()

    def _build_parchment_hint(self) -> None:
        self.layer = CanvasLayer.new()
        self.layer.layer = 100
        self.add_child(self.layer)
        self.hint_root = Control.new()
        self.hint_root.name = "ParchmentHint"
        self.hint_root.visible = False
        self.hint_root.mouse_filter = Control.MOUSE_FILTER_STOP
        self.hint_root.set_anchors_preset(Control.PRESET_FULL_RECT)
        self.layer.add_child(self.hint_root)
        self.dimmer = ColorRect.new()
        self.dimmer.color = Color(0, 0, 0, 0.5)
        self.dimmer.set_anchors_preset(Control.PRESET_FULL_RECT)
        self.dimmer.mouse_filter = Control.MOUSE_FILTER_STOP
        self.dimmer.gui_input.connect(self._on_dimmer_gui_input)
        self.hint_root.add_child(self.dimmer)
        self.hint_panel = Panel.new()
        self.hint_panel.anchor_left = 0.5
        self.hint_panel.anchor_top = 0.5
        self.hint_panel.anchor_right = 0.5
        self.hint_panel.anchor_bottom = 0.5
        self.hint_panel.offset_left = -280
        self.hint_panel.offset_top = -180
        self.hint_panel.offset_right = 280
        self.hint_panel.offset_bottom = 180
        self.hint_root.add_child(self.hint_panel)
        self.vbox = VBoxContainer.new()
        self.vbox.set_anchors_preset(Control.PRESET_FULL_RECT)
        self.vbox.offset_left = 24
        self.vbox.offset_top = 28
        self.vbox.offset_right = -24
        self.vbox.offset_bottom = -24
        self.hint_panel.add_child(self.vbox)
        self.hint_label = RichTextLabel.new()
        self.hint_label.text = "ยังไม่มีคำใบ้ตอนนี้"
        self.hint_label.autowrap_mode = TextServer.AUTOWRAP_WORD
        self.vbox.add_child(self.hint_label)
        self.nav_box = HBoxContainer.new()
        self.vbox.add_child(self.nav_box)
        self.btn_prev = Button.new()
        self.btn_prev.text = "◀"
        self.btn_prev.pressed.connect(self._on_prev_pressed)
        self.nav_box.add_child(self.btn_prev)
        self.page_label = Label.new()
        self.page_label.text = "0/0"
        self.page_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
        self.nav_box.add_child(self.page_label)
        self.btn_next = Button.new()
        self.btn_next.text = "▶"
        self.btn_next.pressed.connect(self._on_next_pressed)
        self.nav_box.add_child(self.btn_next)
        self.hint_close = Button.new()
        self.hint_close.text = "✕"
        self.hint_close.anchor_left = 1.0
        self.hint_close.anchor_top = 0.0
        self.hint_close.anchor_right = 1.0
        self.hint_close.anchor_bottom = 0.0
        self.hint_close.offset_left = -40
        self.hint_close.offset_top = 8
        self.hint_close.offset_right = -8
        self.hint_close.offset_bottom = 38
        self.hint_close.focus_mode = Control.FOCUS_NONE
        self.hint_close.pressed.connect(self._close_hint)
        self.hint_panel.add_child(self.hint_close)

    def _on_dimmer_gui_input(self, ev: InputEvent) -> None:
        if isinstance(ev, InputEventMouseButton) and ev.pressed:
            self._close_hint()

    def _on_hint_button_pressed(self):
        if self.new_hint_available:
            self.new_hint_available = False
            self._stop_hint_pulse()
        if self.hint_open:
            self._close_hint()
        else:
            self._open_hint()

    def _open_hint(self):
        self.hint_root.visible = True
        self.hint_open = True
        self._refresh_hint_view()

    def _close_hint(self):
        self.hint_root.visible = False
        self.hint_open = False

    def _on_prev_pressed(self):
        if not self.hints:
            return
        self._page = (self._page - 1) % len(self.hints)
        self._refresh_hint_view()

    def _on_next_pressed(self):
        if not self.hints:
            return
        self._page = (self._page + 1) % len(self.hints)
        self._refresh_hint_view()

    def _refresh_hint_view(self):
        if not self.hints:
            self.hint_label.text = "ยังไม่มีคำใบ้ตอนนี้"
            self.page_label.text = "0/0"
            self.btn_prev.disabled = True
            self.btn_next.disabled = True
            return
        self._page = max(0, min(self._page, len(self.hints) - 1))
        self.hint_label.text = self.hints[self._page]
        self.page_label.text = f"{self._page + 1}/{len(self.hints)}"
        self.btn_prev.disabled = len(self.hints) <= 1
        self.btn_next.disabled = len(self.hints) <= 1

    def _add_hint_unique(self, text: str):
        if not text:
            return
        if text in self.hints:
            self._page = self.hints.index(text)
            self._refresh_hint_view()
            return
        self.hints.append(text)
        self._page = len(self.hints) - 1
        self._refresh_hint_view()
        self.new_hint_available = True
        self._start_hint_pulse()

    def on_chest_opened(self):
        self._add_hint_unique(H_HINT1)

    def on_chest2_opened(self):
        self._add_hint_unique(H_HINT2)

    def on_chest3_opened(self):
        self._add_hint_unique(H_HINT3)

    def _create_glow_centered(self):
        if not self.hint_button:
            return
        self.glow_rect = ColorRect.new()
        self.glow_rect.color = Color(1, 1, 0.5, 0.0)
        self.glow_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
        self.hint_button.add_child(self.glow_rect)
        self._update_glow_size()

    def _update_glow_size(self):
        if not self.glow_rect or not self.hint_button:
            return
        size = self.hint_button.size * self.GLOW_SCALE
        self.glow_rect.size = size
        self.glow_rect.position = Vector2(
            -size.x * 0.5 + self.hint_button.size.x * 0.5 + self.GLOW_OFFSET.x,
            -size.y * 0.5 + self.hint_button.size.y * 0.5 + self.GLOW_OFFSET.y,
        )

    def _on_hint_button_hover_in(self):
        self._animate_glow(0.8)

    def _on_hint_button_hover_out(self):
        self._animate_glow(0.0)

    def _animate_glow(self, alpha: float):
        if not self.glow_rect:
            return
        if self.glow_tween:
            self.glow_tween.kill()
        self.glow_tween = self.create_tween()
        self.glow_tween.tween_property(self.glow_rect, "modulate:a", alpha, 0.2)

    def _start_hint_pulse(self):
        if not self.glow_rect:
            return
        if self.pulse_tween:
            self.pulse_tween.kill()
        self.pulse_tween = self.create_tween()
        self.pulse_tween.set_loops()
        self.pulse_tween.tween_property(self.glow_rect, "modulate:a", 0.2, 0.4)
        self.pulse_tween.tween_property(self.glow_rect, "modulate:a", 0.9, 0.4)

    def _stop_hint_pulse(self):
        if self.pulse_tween:
            self.pulse_tween.kill()
        if self.glow_rect:
            self.glow_rect.modulate = Color(1, 1, 0.5, 0.0)
